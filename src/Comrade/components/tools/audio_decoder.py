import discord
from discord.ext import commands
import wave
import io


class PCM2WAV(commands.Cog):
    '''
    decodes PCM to WAV (stereo 16 bit, 48000 Hz)
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        '''
        Listens for messages asking the bot to convert a file
        '''
        if message.author != self.bot.user and self.bot.user in message.mentions \
                and message.attachments and "convert" in message.content:

            f = io.BytesIO()
            size = await message.attachments[0].save(f)
            f.seek(0)
            # Create file stream object which we can write to

            if size > 8e6:
                await message.channel.send(f"File is too large! ({size/1e6} vs 8.00 MB limit)")
                return

            pcmdata = f.read()

            f.flush()
            f.seek(0)

            with wave.open(f, 'wb') as wavfile:
                wavfile.setparams((2, 2, 48000, 0, 'NONE', 'NONE'))
                wavfile.writeframes(pcmdata)

            f.seek(0)
            await message.channel.send(
                content=f"{message.author.mention}, here's your file:", file=discord.File(f, "audio.wav"))
