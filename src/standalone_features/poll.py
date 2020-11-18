import discord, typing, asyncio
from discord.ext import commands
from utils import *
from utils.additional.emoji_converter import *

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def poll(self, ctx: commands.Context, prompt:str, timeout:typing.Optional[int] = 60, *options):
        '''
        Creates a poll, with an optional timeout.
        Specify a prompt, and then split options by spaces.

        ex. `$c poll "apples or bananas?" "apples are better" "bananas are the best!"`

        Polls automatically time out after 60 minutes by default.
        '''

        if len(options) < 36:

            lines = "\n".join([f"{i+1}) {options[i]}" for i in range(len(options))])

            msg = await ctx.send(f"**__POLL:__ {prompt}**\n{lines}\n {ctx.author.mention}, react to this post with :octagonal_sign: to stop the poll.")

            reacts = "123456789abcdefghijklmnopqrstuvwxyz"

            cont = True

            ## Apply reactions
            for i in range(len(options)): await msg.add_reaction(textToEmoji(reacts[i]))
            await msg.add_reaction("🛑")

            while cont:
                ## Await Responses
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60 * timeout)

                    if reaction.emoji == "🛑" and user == ctx.author: raise asyncio.TimeoutError

                    e = discord.Embed(title=f"**__RESULTS__**")

                    for i in range(len(options)):

                        reaction = reaction.message.reactions[i]

                        users = [u.mention for u in await reaction.users().flatten() if u != self.bot.user]

                        people = " ".join(users)

                        e.add_field(name=f"{i+1}) {options[i]}: {len(users)}", value = people if people else "No one", inline=False)

                    await msg.edit(embed=e)

                except asyncio.TimeoutError:
                    cont = False

                    e = discord.Embed(title=f"**__POLL (Closed)__:\n{prompt}**")

                    for i in range(len(options)):

                        reaction = (await ctx.channel.fetch_message(msg.id)).reactions[i]

                        users = [u.mention for u in await reaction.users().flatten() if u != self.bot.user]

                        people = " ".join(users)

                        e.add_field(name=f"{i+1}) {options[i]}: {len(users)}", value = people if people else "No one", inline=False)

                    await msg.edit(content = "", embed=e)

        else: await ctx.send("Sorry, you can only choose up to 35 options at a time.")   
