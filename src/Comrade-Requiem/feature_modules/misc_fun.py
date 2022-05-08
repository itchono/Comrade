from dis_snek.models.snek import (Scale, slash_command,
                                  OptionTypes, slash_option,
                                  context_menu, InteractionContext,
                                  CommandTypes)
from dis_snek.models.discord import Member, Message, Embed
from dis_snek.models.discord import FlatUIColours

import random

from effectors.echo_webhook import echo
from effectors.request_file import request_file
from logger import log


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

    @context_menu(name="sex2",
                  context_type=CommandTypes.MESSAGE,
                  scopes=[419214713252216848])
    async def futa(self, ctx: InteractionContext):
        await ctx.defer(ephemeral=True)

        target_message: Message = await ctx.channel.get_message(ctx.target_id)

        # Check if message is a link to a tenor gif
        if target_message.content.startswith("https://tenor.com/view/"):

            modified_string = target_message.content.replace("tenor", "txnor")

            await echo(ctx, target_message.author, modified_string)

            await ctx.send("Congratulations, you found the funni", ephemeral=True)
        else:
            await ctx.send("No gif was found in this message", ephemeral=True)

def setup(bot):
    MiscFun(bot)
    log.info("Module misc_fun.py loaded.")
