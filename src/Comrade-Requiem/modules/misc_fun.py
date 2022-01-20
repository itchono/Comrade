from dis_snek.models.scale import Scale
from dis_snek.models.application_commands import (slash_command,
                                                  OptionTypes, slash_option,
                                                  context_menu)
from dis_snek.models.context import InteractionContext
from dis_snek.models.discord_objects.user import Member
from dis_snek.models.enums import CommandTypes
from dis_snek.models.discord_objects.message import Message
from dis_snek.models.discord_objects.embed import Embed
from dis_snek.models.color import FlatUIColours

import random

from effectors.echo_webhook import echo
from effectors.request_file import request_file
from logger import logger


class MiscFun(Scale):
    @slash_command(name="echo",
                   description="echoes a message as another person",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="message", opt_type=OptionTypes.STRING,
                  description="the message to echo", required=True)
    @slash_option(name="author", opt_type=OptionTypes.USER,
                  description="user to impersonate", required=False)
    async def echo_command(self, ctx: InteractionContext,
                           message: str, author: Member = None):
        if not author:
            author = ctx.author
        await echo(ctx, author, message)

    @context_menu(name="Futa",
                  context_type=CommandTypes.MESSAGE,
                  scopes=[419214713252216848])
    async def futa(self, ctx: InteractionContext):
        await ctx.defer(ephemeral=True)

        target_message: Message = await ctx.channel.get_message(ctx.target_id)

        emoji_sequence = [
            u"\U0001F1EB", u"\U0001F1FA", u"\U0001F1F9", u"\U0001F1E6",
            u"\U0001F1F3", "🅰️", u"\U0001F1F7", u"\U0001F1EE",
            "▪️", u"\U0001F1FE", "4️⃣", "0️⃣", "ℹ️", "◼️", "♀️", "♂️", "🍆", "💦"
        ]

        for emoji in emoji_sequence:
            await target_message.add_reaction(emoji)

        await ctx.send("Congratulations, you found the funni", ephemeral=True)
        
    @slash_command(name="8ball",
                   description="Ask your questions to the 8 ball!",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="question",
                  description="question to ask the 8 ball",
                  opt_type=OptionTypes.STRING, required=True)
    async def eightball(self, ctx: InteractionContext, question: str):

        # 8 ball responses
        responses = [
            "It is certain", "It is decidedly so", "Without a doubt",
            "Yes, definitely", "You may rely on it", "As I see it, yes",
            "Most likely", "Outlook good", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.",
            "Better not tell you now.", "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.",
            "My sources say no.", "Outlook not so good.",
            "Very doubtful."
        ]

        choicenumber = random.randint(0, 19)

        if choicenumber <= 9:
            colour = FlatUIColours.EMERLAND
        elif choicenumber <= 14:
            colour = FlatUIColours.CONCRETE
        else:
            colour = FlatUIColours.ALIZARIN

        e = Embed(title=responses[choicenumber],
                  color=colour, description="Question: " + question)
        e.set_author(name=ctx.author.display_name,
                     icon_url=ctx.author.avatar.url)
        await ctx.send(embed=e)

    @slash_command(name="fileupload",
                   description="test file upload",
                   scopes=[419214713252216848, 709954286376976425])
    async def file_upload(self, ctx: InteractionContext):
        await request_file(ctx)


def setup(bot):
    MiscFun(bot)
    logger.info("Module misc_fun.py loaded.")