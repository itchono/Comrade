from utils.utilities import *

import random

class RandomEvents(commands.Cog):
    '''
    Random event
    '''
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    async def triggerevent(self, ctx:commands.Context, event_name):
        '''
        Manually triggers an event for testing
        '''

        await getattr(self, event_name)(ctx)


    async def nameswap(self, ctx:commands.Context):
        '''
        Changes the nickname of the above person
        '''

        await ctx.send(f"__**~RANDOM EVENT~**__\nThe person above (Current name: {ctx.author.display_name}) will have their name changed to the first thing that the next person below says.")

        def check(m): return not m.author.bot and m.content and m.author != ctx.author

        msg = await client.wait_for('message', check=check)

        try:    
            await ctx.author.edit(nick=msg.content, reason="Comrade name change")
            await ctx.send(f"{ctx.author.mention}, your name has been changed to `{msg.content}`!")
        except:
            await ctx.send(f"{ctx.author.mention}, you must change your name to `{msg.content}`!")

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.guild and not message.author.bot: 

            if random.random() <= 0.01: await self.nameswap(await self.bot.get_context(message))
            # E(X) is 100 messages
