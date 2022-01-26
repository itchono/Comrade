# Arbitrary execution of bot commands

from dis_snek.models.discord import User, Guild
from dis_snek.models.snek import MessageContext, Context
from dis_snek.api.events import MessageCreate
from pymongo.database import Database
import asyncio
from datetime import datetime
from effectors.nonlocal_executor import execute_slash_command
from random import choice


MAXIMUM_RECURSION_DEPTH = 5


def macro_id(locale: User | Guild | int, macro_name: str) -> str:
    """
    Returns the ID of a macro given the name and the locale.
    This ensures a unique ID for each macro.
    """
    if isinstance(locale, int):
        locale_id =  locale
    elif isinstance(locale, User):
        locale_id = locale.id
    elif isinstance(locale, Guild):
        locale_id = locale.id
    else:
        raise TypeError(f"locale must be a User, Guild, or int, not {type(locale)}")
    
    return f"{locale_id}:{macro_name}"



class Macro:
    def __init__(self, name, locale, guild, author_id, instructions, exclusions):
        self.name: str = name  # Name of the macro
        self.locale: int = locale  # Locale of the macro
        self.guild: bool = guild  # Whether the macro is guild-specific
        self.author_id: int = author_id  # ID of the author of the macro
        self.exclusions: list = exclusions  # List of user ids who will not activate the macro
        
        # Clean the instructions
        split_instructions = instructions.split("\n")
        instructions = "\n".join([i.strip() for i in split_instructions if i.strip()])
        self.instructions: str = instructions  # instructions to execute
        
    def __repr__(self):
        return f"<Macro {self.name}>:\n" +\
            self.instructions

    def as_dict(self):
        return {
            "_id": self.id,
            "name": self.name,
            "locale": self.locale,
            "guild": self.guild,
            "author_id": self.author_id,
            "instructions": self.instructions,
            "exclusions": self.exclusions
        }
    
    @classmethod
    def create_from_dict(cls, data: dict):
        return Macro(
            data["name"],
            data["locale"],
            data["guild"],
            data["author_id"],
            data["instructions"],
            data["exclusions"])
    
    @classmethod
    def create_from_id(cls, ctx: Context, id: str):
        db: Database = ctx.bot.db
        if macro_data := db.macros.find_one({"_id": id}):
            return cls.create_from_dict(macro_data)
        return None
    
    @classmethod
    def create_from_id_msg(cls, event: MessageCreate, id: str):
        db: Database = event.bot.db
        if macro_data := db.macros.find_one({"_id": id}):
            return cls.create_from_dict(macro_data)
        return None
    
    @property
    def id(self):
        return macro_id(self.locale, self.name)
    
    
    async def execute_from_msg(self, event: MessageCreate):
        self_length = len(self.name.split(" "))
        arg = " ".join(event.message.content.split(" ")[self_length:])
        
        try:
            await self.execute(MessageContext.from_message(
                event.bot, event.message), arg)
        except Exception as e:
            await event.message.channel.send(f"An error occurred while executing the macro.\n`{e}`")
    
    
    async def execute(self, ctx: MessageContext, arg: str):
        """
        Executes the macro.
        """
        if hasattr(ctx, "recusion_depth"):
            ctx.recursion_depth += 1
        else:
            ctx.recursion_depth = 1
        
        if ctx.recursion_depth > MAXIMUM_RECURSION_DEPTH:
            await ctx.channel.send(
                f"Recursion depth limit exceeded {MAXIMUM_RECURSION_DEPTH}.")
            return
        
        # Tokens to replace in the macro with contextual elements
        SUB_TOKENS = {
            "${author}": ctx.author.nick if ctx.guild else ctx.author.name,
            "${ping}": ctx.author.mention,
            "${arg}": arg,
            "${channelping}" : ctx.channel.mention,
            "${channel}": ctx.channel.name,
            "${depth}" : str(ctx.recursion_depth),
            # Format current time as unix timestamp
            "${time}": f"<t:{int(datetime.now().timestamp())}>"
        }
        
        VALID_OPERATIONS = ["$run", "$wait", "$if", "$else", "$endif", "$random", "$endrandom"]
        control_stack = []
        state = "send"
        random_buffer = []  # Buffer for random operations
         
        async def execute_instruction(instruction: str, state: str) -> str:         
            # Replace tokens with contextual elements
            for token, value in SUB_TOKENS.items():
                instruction = instruction.replace(token, value)
            
            operation = instruction.split(" ")[0]
            
            # Check control flow to see if we need to skip lines
            if control_stack and control_stack[-1] == "skip"\
                    and operation not in ["$else", "$endif"]:
                return state

            # Check operations
            if operation not in VALID_OPERATIONS:
                match state:
                    case "send":
                        # Simply send the message if the operation is not valid
                        print(f"Sending {instruction}")
                        await ctx.channel.send(instruction)
                    case "random":
                        # Add instruction to random buffer
                        random_buffer.append(instruction)
            else:
                # Process operation
                argument = " ".join(instruction.split(" ")[1:])
                
                match operation:
                    case "$run":
                        args = argument.split(":")
                        command_name = args.pop(0)
                        args = [s.strip() for s in args]
                        await execute_slash_command(ctx, command_name, args)
                    case "$wait":
                        await asyncio.sleep(int(argument))
                    case "$if":
                        control_stack.append("if")
                        comp1, operand, comp2 = argument.split(" ")
                        if operand == "==":
                            control_stack.append("exec" if comp1 == comp2 else "skip")
                    case "$else":
                        if control_stack and control_stack[-2] == "if"\
                                and control_stack[-1] == "skip":
                           control_stack[-2] = "else"
                           control_stack[-1] = "exec"
                        elif control_stack and control_stack[-2] == "if"\
                                and control_stack[-1] == "exec":
                            control_stack[-2] = "else"
                            control_stack[-1] = "skip"
                    case "$endif":
                        if control_stack and control_stack[-2] == "if" \
                                or control_stack[-2] == "else":
                            control_stack.pop()
                            control_stack.pop()
                        else:
                            raise RuntimeError("$endif without $if detected.")
                    case "$random":
                        if state == "send":
                            return "random"
                        else:
                            raise RuntimeError("$random cannot be used in a random block.")
                    case "$endrandom":
                        if state == "random":
                            state = "send"
                            await execute_instruction(choice(random_buffer), state)
                            random_buffer.clear()
                            return state
                        else:
                            raise RuntimeError("$endrandom cannot be used outside of a random block.")
            return state
                          
        # Parse macro instructions
        for instruction in self.instructions.split("\n"):
            try:
                state = await asyncio.wait_for(execute_instruction(instruction, state), timeout=5)
            except asyncio.TimeoutError:
                await ctx.channel.send("Macro execution timed out.")
                return
