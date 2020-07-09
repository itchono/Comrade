from utils.utilities import *
from utils.mongo_interface import *

class Echo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    @commands.check(isNotThreat())
    @commands.guild_only()
    async def echo(self, ctx: commands.Context, text: str, target=None, deleteMsg=True):
        '''
        Echoes a block of text as if it were sent by someone else.
        Defaults to the author of the message is no target is given.
        Can mention people by nickname or user ID too.

        Ex. $c echo "HELLO THERE SIR" @itchono
        '''

        '''
        Set up the webhook
        '''
        # is there a webhook named Comrade?
        webhook = None
        for wh in await ctx.channel.webhooks():
            if wh.name == "Comrade": webhook = wh

        if not webhook: webhook = await ctx.channel.create_webhook(name="Comrade", avatar=None)

        '''
        Send the actual webhook
        '''
        if u := getCustomUser(target, ctx.guild.id):
            await webhook.send(text, username=u["name"], avatar_url=u["url"])
        else:
            if u := (await extractUser(ctx, target, verbose=False) if target else ctx.author):
                # uses self if no target given
                await webhook.send(text, username=u.display_name, avatar_url=u.avatar_url)
            else:
                await webhook.send(text, username=target, avatar_url=ctx.author.default_avatar_url)
            
        if deleteMsg: 
            await log(ctx.guild, "Echo for {} sent by {} ({})".format(target,ctx.author.display_name, ctx.author))
            await ctx.message.delete()
            
    @commands.command()
    @commands.check(isNotThreat())
    @commands.guild_only()
    async def everyonesays(self, ctx: commands.Context, text: str, count: int = 0):
        '''
        Says something a lot of times.
        '''
        online_humans = [m for m in ctx.guild.members if (str(m.status) != "offline" and not m.bot)]

        onlinecount = len(online_humans)
        # number of online human members

        if count > onlinecount:
            await delSend(ctx, f"That's too many members! Only {onlinecount} human members are online right now!")
        else:
            if not count: count = 5 if onlinecount >= 5 else onlinecount

            for m in random.sample(online_humans, count): await self.echo(ctx, text, m.display_name, False)

            await asyncio.sleep(30)

            if count > 5: await self.cleanwebhooks(ctx)
    
    @commands.command()
    @commands.guild_only()
    async def cleanwebhooks(self, ctx:commands.Context):
        '''
        Deletes echoed messages from Comrade and cleans up Webhooks.
        '''
        for wh in await ctx.channel.webhooks(): await wh.delete()
        await ctx.channel.purge(check=isWebhook, bulk=True)