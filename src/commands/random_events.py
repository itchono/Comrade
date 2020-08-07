from utils.utilities import *

import random

class RandomEvents(commands.Cog):
    '''
    Random event
    '''
    def __init__(self, bot):
        self.bot = bot
        self.lastroll = []
        self.probabilities = {"nameswap":0.007, "rickroll":0.01}

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    async def triggerevent(self, ctx:commands.Context, event_name):
        '''
        Manually triggers an event for testing
        '''

        await getattr(self, event_name)(ctx)

    @commands.command()
    @commands.check_any(commands.is_owner(), isUser("littlebear"))
    async def probability(self, ctx:commands.Context, event_name:str, probability:float=None):
        '''
        Changes the probability of an event, or displays it if there is no second argument.
        '''
        if probability is None:
            try: await ctx.send(f"P({event_name}): {self.probabilities[event_name]*100}%")
            except: pass
        else:
            try: 
                self.probabilities[event_name] = probability/100
                await reactOK(ctx)
                await ctx.send(f"Probability for {event_name} set to {probability}%.")

                servers = DBfind(SERVERCFG_COL)

                for s in servers:
                    c = self.bot.get_channel(s["announcements-channel"])
                    await c.send(f"{ctx.author.mention} has set the probability for {event_name} to {probability}%.")


            except: pass

    async def rickroll(self, ctx:commands.Context):
        '''
        Assigns the rick role
        '''

        rickrole = await rickRole(ctx.guild)

        for m in rickrole.members:
            # remove bearer of previous rick role
            roles = m.roles
            roles.remove(rickrole)
            await m.edit(roles=roles)
        
        roles = ctx.author.roles
        roles.append(rickrole)
        await ctx.author.edit(roles=roles)
        await ctx.send(f"{ctx.author.mention} got rick roled.")

    async def nameswap(self, ctx:commands.Context):
        '''
        Changes the nickname of the above person
        '''
        e = discord.Embed()
        e.set_image(url="https://i.kym-cdn.com/entries/icons/original/000/026/104/marioTestRender2.jpg")

        await ctx.send(f"__**~RANDOM EVENT~**__\nThe person above (Current name: {ctx.author.display_name}) will have their name changed to the first thing that the next person below says.", embed=e)

        def check(m): return not m.author.bot and m.content and m.author != ctx.author and m.channel == ctx.channel

        msg = await client.wait_for('message', check=check)

        try:    
            await ctx.author.edit(nick=msg.content[:32], reason="Comrade name change") # Note: must be less than 32 char
            await ctx.send(f"{ctx.author.mention}, your name has been changed to `{msg.content}`!")
        except Exception as e:
            await ctx.send(f"{ctx.author.mention}, you must change your name to `{msg.content}`!")
            await ctx.send(e)

    @commands.command()
    async def previousrolls(self, ctx:commands.Context):
        '''
        Shows roll probabilities on last 10 rolls
        '''
        await ctx.send(f"Last 10 rolls: {', '.join(['{:.2f}%'.format((1-p)*100) for p in self.lastroll])}\nThreshold for Name Swap: ")

    def roll(self):
        '''
        Randomly rolls and updates internal roll counter
        '''
        r = random.random()

        self.lastroll.append(r)

        if len(self.lastroll) > 10: self.lastroll.pop(0)

        return r

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.guild and not message.author.bot: 

            r = self.roll()

            if r <= self.probabilities["nameswap"]: await self.nameswap(await self.bot.get_context(message))
            elif r <= self.probabilities["rickroll"]: await self.rickroll(await self.bot.get_context(message))
