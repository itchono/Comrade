from utils.utilities import *


class BPCGame():
    def __init__(self, players, ctx, bot):
        self.players = players
        self.round_number = 0
        self.ctx = ctx # discord context used for the game
        self.bot = bot # discord bot used for the game


        self.prompts = {}
        self.drawings = {}
        self.mapped_drawings = {}

    def __repr__(self):
        return f"Broken Picture Game\nPlayers ({len(self.players)}): {', '.join([p.display_name for p in self.players])}\nRound Number: {self.round_number}"

    async def get_prompts(self):
        '''
        Sends out prompts to players
        '''
        pending = [p.id for p in self.players]

        for player in self.players:
            await DM(f"Round {self.round_number}: Please type in your prompt below.", player)

        def check(m): return m.content and m.author.id in pending

        while pending:
            msg = await self.bot.wait_for('message', check=check)
            self.prompts[msg.author.id] = msg.content
            await msg.add_reaction("👍")
            pending.remove(msg.author.id)

            await self.ctx.send(f"{self.ctx.guild.get_member(msg.author.id).display_name} has submitted their prompt! ({len(self.players) -len(pending)}/{len(self.players)})")

    async def draw(self):
        '''
        Sends out queries to draw
        '''
        pending = [p.id for p in self.players]
        rolled_ids = pending[1:] + [pending[0]]

        mapping = dict(zip(pending, rolled_ids))

        for i in mapping:
            await DM(f"Round {self.round_number}: Draw something that describes the following prompt ```{self.prompts[mapping[i]]}```", self.ctx.guild.get_member(i))

        def check(m): return len(m.attachments) > 0 and m.author.id in pending

        while pending:
            msg = await self.bot.wait_for('message', check=check)
            self.drawings[msg.author.id] = msg.attachments[0].url
            await msg.add_reaction("👍")
            pending.remove(msg.author.id)

            await self.ctx.send(f"{self.ctx.guild.get_member(msg.author.id).display_name} has submitted their drawing! ({len(self.players) -len(pending)}/{len(self.players)})")

        mapped_drawings = {}
        for author_id in self.drawings:
            mapped_drawings[self.prompts[mapping[author_id]]] = self.drawings[author_id]
        return mapped_drawings


class BPC(commands.Cog):
    '''
    Broken Picture Phone Game
    '''
    def __init__(self, bot):
        self.bot = bot
        self.active = False
        self.game = None

        self._last_member = None

    @commands.group()
    async def bpc(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(f'```=========================\nBROKEN PICTURE PHONE v1.0\n=========================```\nDo {BOT_PREFIX}bpc start to start a game!')

    @bpc.command()
    async def start(self, ctx: commands.Context, members: commands.Greedy[discord.Member]):
        '''
        Starts a game of Broken Picture Phone.
        '''

        self.game = BPCGame(members, ctx, self.bot)

        print(self.game)

        await ctx.send(str(self.game))

        await self.game.get_prompts()

        await ctx.send("Prompts are in!")

        self.game.round_number += 1

        drawings = await self.game.draw()

        await ctx.send("Drawings are in!")

        for prompt in drawings:
            await asyncio.sleep(2)
            e = discord.Embed(title=f"Prompt: {prompt}")
            e.set_image(url=drawings[prompt])
            await ctx.send(embed=e)
