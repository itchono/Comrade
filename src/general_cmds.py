from utils.utilities import *
from utils.mongo_interface import *

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def version(self, ctx:commands.Context):
        '''
        Logs version of the bot.
        '''
        await ctx.send("Comrade is running version: 3.0alpha build May 15")

    @commands.command()
    async def clearcommands(self, ctx:commands.Context):
        '''
        Cleans up commands from sent from users in a channel.
        '''
        await ctx.channel.purge(check=isCommand, bulk=True)

    @commands.command()
    @commands.check(isOwner)
    async def shutdown(self, ctx:commands.Context):
        '''
        Logs out the user.
        '''
        await self.bot.logout()

    @commands.command()
    async def buymefood(self, ctx: commands.Context):
        '''
        Maybe buys you food
        '''
        await delSend("Enter Your Credit Card Info...", ctx.channel)

    @commands.command()
    @commands.check(isnotThreat)
    async def dmUser(self, ctx: commands.Context, target, message:str):
        '''
        DM given user
        Made by vdoubleu
        '''
        await ctx.trigger_typing()
        
        if u := await extractUser(self.bot, ctx, target):

            e = discord.Embed(title="", description = "Sent by {}".format(ctx.author))
            
            await DM(message, u, e)
            await reactOK(ctx)
            await timedSend("DM sent to {}".format(target), ctx.channel)

    @commands.command()
    async def msgInfo(self, ctx, msgid):
        '''
        Gets information about a specific message given an ID.
        '''
        msg = await ctx.channel.fetch_message(msgid)
        await ctx.send("Author: {}".format(msg.author))

    @commands.command()
    async def addEmote(self, ctx, name, *args):
        if len(ctx.message.attachments) > 0:
            u = ctx.message.attachments[0].url
        else:
            u = args[(len(args)-1)]

        emoteDirectory = await getChannel(ctx.guild, 'emote directory')
        await emoteDirectory.send('{}\n{}'.format(name.lower(), u))
        await ctx.send('Emote {} was added'.format(name.lower()))
        
    @commands.command()
    async def emoteCall(self, ctx, name):
        directory = await getChannel(ctx.guild, 'emote directory')
        async for e in directory.history(limit=None):
            if name.lower() in e.content.split("\n")[0]:
                emote = e.content.split("\n")[1]
                await ctx.send(emote)
            else:
                await ctx.send('{} exist not'.format(name))
    

