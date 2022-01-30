from dis_snek.models.snek import (InteractionContext, Scale,
                                  slash_command, OptionTypes, slash_option,
                                  Listener)
from dis_snek.models.discord import Embed
from dis_snek.api.events import MessageCreate
from logger import log

from processors.macro_parser import Macro, macro_id
from processors.macro_input import request_macro_input


class Macros(Scale):
    @slash_command(name="macro",
                   sub_cmd_name="run",
                   sub_cmd_description="Run a macro",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="macro", description="Macro to run",
                  opt_type=OptionTypes.STRING, required=True)
    @slash_option(name="arg", description="Argument to pass to the macro",
                  opt_type=OptionTypes.STRING, required=False)
    async def macro_run(self, ctx: InteractionContext, macro: str, arg: str = ""):
        '''
        Executes any slash command registered with the bot.
        '''
        if macro := Macro.create_from_id(ctx, macro_id(ctx.guild_id, macro)):
            await macro.execute(ctx, arg)
            if not ctx.responded:
                await ctx.send(f"{macro.name} executed.")
        else:
            await ctx.send(f"Macro {macro} not found.", ephemeral=True)
            
    @slash_command(name="macro",
                   sub_cmd_name="add",
                   sub_cmd_description="Add a macro; input instructions in a following message.",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="name", description="Macro will run when the message starts with this.",
                  opt_type=OptionTypes.STRING, required=True)
    async def macro_add(self, ctx: InteractionContext, name: str):
        await ctx.defer()
        macro_instructions = await request_macro_input(ctx)
        macro = Macro(name.lower(), ctx.guild_id, True,
                      ctx.author.id, macro_instructions, [])
        collection = self.bot.db.macros
        result = collection.insert_one(macro.as_dict())
        await ctx.send(f"Macro {macro.name} added with ID {result.inserted_id}.")
        
    @slash_command(name="macro",
                   sub_cmd_name="remove",
                   sub_cmd_description="Remove a macro that you own",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="name", description="Name of macro to remove",
                  opt_type=OptionTypes.STRING, required=True)
    async def macro_remove(self, ctx: InteractionContext, name: str):
        collection = self.bot.db.macros
        result = collection.delete_one({"_id": macro_id(ctx.guild_id, name.lower()), "author_id": ctx.author.id})
        
        if result.deleted_count == 1:
            await ctx.send(f"Macro was deleted.", ephemeral=True)
        else:
            await ctx.send(f"Either the macro was not found, or you are not the owner.", ephemeral=True)
            
    @slash_command(name="macro",
                   sub_cmd_name="view",
                   sub_cmd_description="View the code for a macro",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="name", description="Name of macro to view",
                  opt_type=OptionTypes.STRING, required=True)
    async def macro_show(self, ctx: InteractionContext, name: str):     
        if macro := Macro.create_from_id(ctx, macro_id(ctx.guild_id, name.lower())):
            pretty_instructions = ';\n'.join(macro.instructions.split(';'))
            e = Embed(title=macro.name,
                      description=f"```{pretty_instructions}```" + "\n"
                      + f"Author: <@{macro.author_id}>")
            e.set_author(name="Macro")
            e.set_footer(text="Make your own macro using /macro add")
            await ctx.send(embed=e)
        else:
            await ctx.send(f"Macro {name} not found.", ephemeral=True)
            
    @slash_command(name="macro",
                   sub_cmd_name="showall",
                   sub_cmd_description="Show all macros that can be called.",
                   scopes=[419214713252216848, 709954286376976425])
    async def macro_showall(self, ctx: InteractionContext):
        db = self.bot.db
        
        results = db.macros.find({"locale": ctx.guild_id})
        
        e = Embed(title="All Macros in this Guild",
                  description="\n".join([f"{macro['name']} - <@{macro['author_id']}>" for macro in results]))
        await ctx.send(embed=e)
            
    @slash_command(name="macro",
                   sub_cmd_name="guide",
                   sub_cmd_description="View the guide for macros",
                   scopes=[419214713252216848, 709954286376976425])
    async def macro_guide(self, ctx: InteractionContext):
        e = Embed(title="How to use macros")
        with open("static/macro_guide.md", "r") as f:
            e.description = f.read()
        e.set_author(name="Comrade Macro System",
                     icon_url=ctx.bot.user.avatar.url)
        e.set_footer(text="Make your own macro using /macro add")
        await ctx.send(embed=e)
            
    @slash_command(name="opt",
                   sub_cmd_name="out",
                   sub_cmd_description="Opt out of activating a macro",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="name", description="Name of macro to opt out of",
                  opt_type=OptionTypes.STRING, required=True)
    async def opt_out(self, ctx: InteractionContext, name: str):
        pass

async def msg_macro(event: MessageCreate):
    # Try to identify macros
    message = event.message
    locale = message._guild_id if message._guild_id else message._author_id
    
    # Try exact match for non-argument macros
    if macro := Macro.create_from_id_msg(
            event,
            macro_id(locale, message.content.lower())):
        await macro.execute_from_msg(event)
    
    # Try single word macro as well
    elif macro := Macro.create_from_id_msg(
            event,
            macro_id(locale, message.content.split(" ")[0].lower())):
        await macro.execute_from_msg(event)
        
def setup(bot):
    Macros(bot)
    bot.add_listener(Listener(msg_macro, "message_create"))
    log.info("Module macros.py loaded.")
