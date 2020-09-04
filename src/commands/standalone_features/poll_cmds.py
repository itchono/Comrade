from utils.core_dependencies.utilities import *
from utils.additional.emoji_converter import *

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def poll(self, ctx: commands.Context, prompt:str, *options):
        '''
        Creates a poll.
        Specify a prompt, and then split options by spaces.

        ex. $c poll "apples or bananas?" "apples are better" "bananas are the best!"
        '''

        if len(options) < 36:

            lines = "\n".join([f"{i+1}) {options[i]}" for i in range(len(options))])

            msg = await ctx.send(f"**__POLL__:\n{prompt}**\n{lines}\n\n {ctx.author.mention}, react to this post with :octagonal_sign: to stop the poll.")

            reacts = "123456789abcdefghijklmnopqrstuvwxyz"

            ## Apply reactions
            for i in range(len(options)): await msg.add_reaction(textToEmoji(reacts[i]))
            await msg.add_reaction("🛑")

            ## Await Responses
            def check(reaction, user): return user == ctx.author and reaction.emoji == "🛑"

            await self.bot.wait_for('reaction_add', check=check)

            e = discord.Embed(title=f"**__POLL RESULT__:\n{prompt}**")

            for i in range(len(options)):

                reaction = (await ctx.channel.fetch_message(msg.id)).reactions[i]

                users = [u.mention for u in await reaction.users().flatten() if u != self.bot.user]

                people = " ".join(users)

                e.add_field(name=f"{i+1}) {options[i]}: {len(users)}", value = people if people else "No one", inline=False)

            await ctx.send(embed=e)

        else: await ctx.send("Sorry, you can only choose up to 35 options at a time.")   
