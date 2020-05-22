from utils.utilities import *
from utils.mongo_interface import *

class Echo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    @commands.check(isnotThreat)
    @commands.check(isServer)
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
            if u := (await extractUser(ctx, target) if target else ctx.author):
                # uses self if no target given
                await webhook.send(text, username=u.display_name, avatar_url=u.avatar_url)
            
        if deleteMsg: 
            await log(ctx.guild, "Echo for {} sent by {} ({})".format(target,ctx.author.display_name, ctx.author))
            await ctx.message.delete()
            
    @commands.command()
    @commands.check(isnotThreat)
    @commands.check(isServer)
    async def everyonesays(self, ctx: commands.Context, text: str, count: int = 5):
        '''
        Says something a lot of times.
        '''
        onlinecount = 0

        for member in ctx.guild.members:
            if str(member.status) != "offline":
                onlinecount += 1

        if count > onlinecount:
            await delSend("Are you fucking serious", ctx.channel)
        else:
            mems = list(ctx.guild.members)
            random.shuffle(mems)

            for member in mems:
                await self.echo(ctx, text, member.display_name, False)
                count -= 1
                if count <= 0: break

            await asyncio.sleep(30)

            if count > 5:
                await self.cleanwebhooks(ctx)
    
    @commands.command()
    @commands.check(isServer)
    async def cleanwebhooks(self, ctx:commands.Context):
        '''
        Deletes echoed messages from Comrade andn cleans up Webhooks.
        '''
        for wh in await ctx.channel.webhooks():
            await wh.delete()
        await ctx.channel.purge(check=isWebhook, bulk=True)