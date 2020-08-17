from utils.utilities import *

class PictoChain():
    '''
    Object to store drawings and prompts
    '''

    def __init__(self, owner):
        self.owner = []
        self.prompts = []
        self.prompt_authors = []

        self.images = []
        self.image_authors = []

    def __len__(self):
        return max(len(self.prompts), len(self.images))

    def isdrawing(self):
        return len(self.prompts) > len(self.images)

    def draw(self, author, url):
        self.images.append(url)
        self.image_authors.append(author)

    def write(self, author, prompt):
        self.prompts.append(prompt)
        self.prompt_authors.append(author)

    def export(self):
        '''
        Sends out a mapped list of prompts and drawings
        '''
        return zip(range(len(self.prompts)),self.prompts, self.prompt_authors, self.images, self.image_authors)

    def prompt(self):
        '''
        Returns the most recent prompt
        '''
        return self.prompts[-1]

    def image(self):
        '''
        Returns the most recent image
        '''
        return self.images[-1]


class BPCGame():
    def __init__(self, players, ctx, bot):
        self.players = players
        self.round_number = 0
        self.ctx = ctx # discord context used for the game
        self.bot = bot # discord bot used for the game


        self.pictochains = {}

    def __repr__(self):
        return f"Broken Picture Game\nPlayers ({len(self.players)}): {', '.join([p.display_name for p in self.players])}\nRound Number: {self.round_number}"

    def roll(self, users, n):
        '''
        returns a n-rolled forwards list, with rollover back to the start
        '''
        n = n % len(users)
        return users[n:] + users[:n]

    async def draw(self):
        '''
        Sends out queries to draw
        '''
        pending = [p.id for p in self.players]
        rolled_ids = self.roll(pending, 2*self.round_number+1)

        mapping = dict(zip(pending, rolled_ids))

        for i in mapping: await DM(f"Round {self.round_number}: Draw something that describes the following prompt ```{self.pictochains[mapping[i]].prompt()}```", self.ctx.guild.get_member(i))

        def check(m): return (len(m.attachments) > 0 or len(m.embeds) > 0) and m.author.id in pending
        # also tolerate embed

        while pending:
            msg = await self.bot.wait_for('message', check=check)

            if len(msg.attachments) > 0:
                self.pictochains[mapping[msg.author.id]].draw(self.ctx.guild.get_member(msg.author.id), msg.attachments[0].url)
            else:
                self.pictochains[mapping[msg.author.id]].draw(self.ctx.guild.get_member(msg.author.id), msg.embeds[0].url)
            await msg.add_reaction("👍")
            pending.remove(msg.author.id)

            await self.ctx.send(f"{self.ctx.guild.get_member(msg.author.id).display_name} has submitted their drawing! ({len(self.players) -len(pending)}/{len(self.players)})")

    async def write(self):
        '''
        Describe images.
        '''
        pending = [p.id for p in self.players]
        rolled_ids = self.roll(pending, 2*self.round_number)

        mapping = dict(zip(pending, rolled_ids))

        for i in mapping: 

            if self.round_number == 0:
                await DM(f"Round {self.round_number}: Please type in your prompt below.", self.ctx.guild.get_member(i))
            else:
                e = discord.Embed(title=f"Describe this drawing!", url=self.pictochains[mapping[i]].image())
                e.set_image(url=self.pictochains[mapping[i]].image())
                await DM(f"Round {self.round_number}: Write something that describes the following drawing:", self.ctx.guild.get_member(i), e)

        def check(m): return m.content and m.author.id in pending

        while pending:
            msg = await self.bot.wait_for('message', check=check)

            self.pictochains[mapping[msg.author.id]].write(self.ctx.guild.get_member(msg.author.id), msg.content)
            await msg.add_reaction("👍")
            pending.remove(msg.author.id)

            await self.ctx.send(f"{self.ctx.guild.get_member(msg.author.id).display_name} has submitted their {'prompt' if self.round_number == 0 else 'description'}! ({len(self.players) -len(pending)}/{len(self.players)})")
            
    async def start(self, rounds=None):
        '''
        Starts the game
        '''

        if not rounds: rounds = int(len(self.players)/2)

        for p in self.players:
            self.pictochains[p.id] = PictoChain(p)

        while self.round_number < rounds:
            await self.ctx.send(f"Preparing to start round {self.round_number}")
            await self.write()
            await asyncio.sleep(2)
            await self.draw()
            await asyncio.sleep(2)
            self.round_number += 1


        ### End of game
        
        for p in self.players:
            await self.ctx.send(f"**Here is {p.display_name}'s story chain:**")
            for round_number, prompt, prompt_author, drawing, drawing_author in self.pictochains[p.id].export():
                await self.ctx.send(f"Round {round_number} - {'Prompt' if round_number == 0 else 'Description'} by {prompt_author.display_name}: ```{prompt}```")

                await asyncio.sleep(1)

                e = discord.Embed()
                e.set_image(url=drawing)
                await self.ctx.send(f"Round {round_number} - Drawing by {drawing_author.display_name}:", embed=e)

                await asyncio.sleep(1)

        await self.ctx.send("That's all folks! Thanks for playing!")

            


class BPC(commands.Cog):
    '''
    Broken Picture Phone Game
    '''
    def __init__(self, bot):
        self.bot = bot
        self.active = False
        self.game = None

        

    @commands.group()
    async def bpc(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(f'```=========================\nBROKEN PICTURE PHONE v1.0\n=========================```\nDo `{BOT_PREFIX}bpc start` to start a game!')

    @bpc.command()
    async def start(self, ctx: commands.Context, members: commands.Greedy[discord.Member]):
        '''
        Starts a game of Broken Picture Phone.
        '''

        if len(members) < 2:
            await ctx.send("Sorry, we need at least 2 players to start!")
        else:
            self.game = BPCGame(members, ctx, self.bot)

            print(self.game)

            await ctx.send(str(self.game))

            await self.game.start()