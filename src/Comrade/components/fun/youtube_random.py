import discord
from discord.ext import commands
from pyyoutube import Api
import os
import random
from collections import defaultdict

SIPS_CHANNEL_ID = "UCD4INvKvy83OXwAkRjaQKtw"
SIPS_PLAYLIST = "UUD4INvKvy83OXwAkRjaQKtw"


class Youtube(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.api: Api = Api(api_key=os.environ.get("YOUTUBEKEY"))
        self.pagetoken = None
        self.randompool = defaultdict(list)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        '''
        Sends a sips video
        '''
        if message.content.lower() == "sips":
            results = self.api.get_playlist_items(playlist_id=SIPS_PLAYLIST, parts="snippet", count=25, page_token=self.pagetoken)

            if results.nextPageToken:
                self.pagetoken = results.nextPageToken

            self.randompool[SIPS_PLAYLIST] += list(results.items)

            single_result = random.choice(
                self.randompool[SIPS_PLAYLIST]).to_dict()
            vidid = single_result["snippet"]["resourceId"]["videoId"]
            await message.channel.send(f"https://www.youtube.com/watch?v={vidid}")
