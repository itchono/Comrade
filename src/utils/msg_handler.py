from utils.utilities import *
from utils.mongo_interface import *

class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_message(self, message:discord.message):
        if not message.author.bot:
            if "hello" in message.content.lower():
                await delSend("Henlo", message.channel)

            if "wait" in message.content.lower():
                await delSend("https://www.youtube.com/watch?v=sBl9qcaQos4", message.channel)

            if "approved" in message.content.lower():
                with open("vid\meme_approved.mp4", "rb") as f:
                    await message.channel.send(file=discord.File(f, "meme_approved.mp4"))
                
                #await delSend("https://youtu.be/LabIat9t-uY", message.channel)

            Knuckles_VD = ["meme_approved.mp4", "meme_what.mp4", "meme_denied.mp4", "meme_huh.mp4", "meme_illegal.mov", "no_meme_no_meme_no_meme.mp4", "meme_no.mp4", "meme_already_approved.mp4", "meme_wait.mp4", "meme_purple.mp4", "meme_eggman_steal.mp4", "Meme_failed.mp4"]

            if message.channel.id == getCFG(message.guild.id)["meme channel"]:

                fn = "meme_what.mp4" # default safety

                if len(message.attachments) > 0:
                    attach = message.attachments[0].filename
                    fn = Knuckles_VD[hash(attach) % len(Knuckles_VD)]
                    with open("vid\{}".format(fn), "rb") as f:
                        await message.channel.send(file=discord.File(f, fn))

                elif len(message.embeds) > 0:
                    attach = message.embeds[0].url
                    fn = Knuckles_VD[hash(attach) % len(Knuckles_VD)]
                    with open("vid\{}".format(fn), "rb") as f:
                        await message.channel.send(file=discord.File(f, fn))

                elif "http" in message.content.lower():
                    fn = Knuckles_VD[hash(message.content.lower()) % len(Knuckles_VD)]
                    with open("vid\{}".format(fn), "rb") as f:
                        await message.channel.send(file=discord.File(f, fn))                
                
                
