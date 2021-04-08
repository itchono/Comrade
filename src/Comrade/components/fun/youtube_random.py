import discord
from discord.ext import commands
from pyyoutube import Api
import os
import random

SIPS_CHANNEL_ID = "UCD4INvKvy83OXwAkRjaQKtw"
SIPS_PLAYLIST = "UUD4INvKvy83OXwAkRjaQKtw"


class Youtube(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.api: Api = Api(api_key=os.environ.get("YOUTUBEKEY"))
        self.pagetoken = None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        '''
        Sends a sips video
        '''

        if message.content.lower() == "sips":
            results = self.api.get_playlist_items(playlist_id=SIPS_PLAYLIST, parts="snippet", count=25)
            single_result = random.choice(results.items).to_dict()
            vidid = single_result["snippet"]["resourceId"]["videoId"]
            await message.channel.send(f"https://www.youtube.com/watch?v={vidid}")
