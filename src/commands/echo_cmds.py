from utils.utilities import *
from utils.db_utils import *

def isWebhook(message: discord.Message):
    '''
    Checks if it's a webhook
    '''
    return message.author.discriminator == "0000"

class ComradeUser(commands.Converter):

    async def convert(self, ctx, argument):
        '''
        Attempts to convert either using memberconverter or custom user converter.
        '''
        if "\\" in argument: raise Exception # allow user to escape mentions

        if customuser := DBfind_one(CUSTOMUSER_COL, {"name":argument, "server":ctx.guild.id}): return ("custom", customuser)
        
        elif member := await getUser(ctx, argument, False): return ("member", member)

        raise Exception # parsing error; intentional

class Echo(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command()
    @commands.check(isNotThreat())
    @commands.guild_only()
    async def echo(self, ctx: commands.Context, target: typing.Optional[ComradeUser] = None, 
                    deleteMsg: typing.Optional[bool] = True, channelOverride: typing.Optional[discord.TextChannel] = None, 
                    *, text: str):
        '''
        Echoes a block of text as if it were sent by someone else [server member, custom user]
        Can mention people by nickname or user ID too.

        Defaults to self if no user specified. Use \ to escape mentioning names if you want this case.
        
        Ex. $c echo itchono HELLO THERE SIR 
        >>> Impersonates itchono, sending a message with content `HELLO THERE SIR`
        '''

        channel = ctx.channel if not channelOverride else channelOverride

        '''
        Set up the webhook
        '''
        # is there a webhook named Comrade?
        webhook = None
        for wh in await channel.webhooks():
            if wh.name == "Comrade": webhook = wh

        if not webhook: webhook = await channel.create_webhook(name="Comrade", avatar=None)

        '''
        Send the actual webhook
        '''
        if target:
            if target[0] == "custom": await webhook.send(text.lstrip("\\"), username=target[1]["name"], avatar_url=target[1]["url"])
            elif target[0] == "member": await webhook.send(text.lstrip("\\"), username=target[1].display_name, avatar_url=target[1].avatar_url)
        
        else: await webhook.send(text.lstrip("\\"), username=ctx.author.display_name, avatar_url=ctx.author.avatar_url)
            
        if deleteMsg and target: await log(ctx.guild, "Echo for {} sent by {} ({})".format(target[1],ctx.author.mention, ctx.author)); await ctx.message.delete()
            
    async def extecho(self, ctx: commands.Context, text, target, deleteMsg=True):
        '''
        For external calls to echo.
        '''
        try: target = await ComradeUser().convert(ctx, target)
        except: target = None

        await self.echo(ctx, target=target, text=text, deleteMsg=deleteMsg)


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

            for m in random.sample(online_humans, count): await self.extecho(ctx, text, str(m.id), False)

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