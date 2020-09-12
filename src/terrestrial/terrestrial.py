import discord
from discord.ext import commands

from terrestrial.game_objects import Game

class Terrestrial(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command()
    async def startgame(self, ctx:commands.Context):
        '''
        Starts a game of terrestrial
        '''
        game = Game()

        intro_splash = "`Terrestrial v1 -- use arrow reactions to move, use ⛏ to transform into mining mode, use 🛑 to stop."

        m = await ctx.send(game.rendered + game.describe)

        for r in ["⬅", "➡", "⬆", "⬇", "⛏", "🛑"]: await m.add_reaction(r)

        def check(reaction, user):
            return str(reaction) in ["⬅", "➡", "⬆", "⬇", "⛏", "🛑"] and user == ctx.author and reaction.message.id == m.id

        # Add a thing that's like twitch plays, where you collect multiple inputs over the course, of say 5 seconds

        while 1:
            reaction, user = await self.bot.wait_for("reaction_add", check=check)

            await m.remove_reaction(reaction, user)

            if str(reaction) == "🛑": 
                for r in ["⬅", "➡", "⬆", "⬇", "⛏"]: await m.remove_reaction(r, self.bot.user)
                break

            elif str(reaction) == "⛏": game.action()
            else: game.moveplayer({"⬅":"LEFT", "➡":"RIGHT", "⬆":"UP", "⬇":"DOWN"}[str(reaction)])

            await m.edit(content=game.rendered + game.describe)              