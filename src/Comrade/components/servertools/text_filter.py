import discord
from discord.ext import commands

# Text Filtering
import re
import unidecode

from fuzzywuzzy import fuzz
# install python-Levenshtein for faster results.
# pip install python-levenshtein ==> * needs C++ build tools installed

from collections import defaultdict

from utils.emoji_converter import emojiToText
from db import collection

from utils.logger import logger
from config import cfg
from utils.utilities import ufil


def content_filter(message: discord.Message) -> bool:
    '''
    Checks a message for additional offending characteristics based on member
    Filters pings and images
    '''
    u = collection("users").find_one(ufil(message.author))
    return (u["moderation"]["stop-pings"] and message.mentions) or (
        u["moderation"]["stop-images"] and (
            message.attachments or message.embeds))


def text_filter(content: str,
                author: discord.Member,
                guild: discord.Guild) -> bool:
    '''
    Detects banned words in a string
    '''
    spaced_query = unidecode.unidecode(emojiToText(content.lower()))
    # remove non-ascii, attempt to decode unicode,
    # get into formattable form
    query = re.sub(r"\W+", '', spaced_query)  # spaces

    server_words: dict = collection(
        "servers").find_one(guild.id)["global-banned-words"]
    words: dict = collection(
        "users").find_one(ufil(author))["moderation"]["banned-words"]

    words.update(server_words)

    # TODO with python 3.9 -- dictionary union
    for w in words:

        if words[w] < 100 and (
            len(query) > 2 and fuzz.partial_ratio(query, w) >= words[w]) or query == w:
            return True

        for word in spaced_query.split(" "):
            if word[0] == w[0] and word[-1] == w[-1] and fuzz.partial_ratio(word, w) >= words[w]:
                return True
            # checking endcap letters
    return False


class TextFilter(commands.Cog):
    '''
    Comrade moderation module
    '''
    def __init__(self, bot):
        self.bot = bot

        self.bucket = defaultdict(lambda: defaultdict(list))
        # stores a bunch of messages

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if not message.author.bot and message.guild:
            # moderation system
            if text_filter(message.content, message.author, message.guild) or \
                    content_filter(message):
                await message.delete()

            else:
                message_chain: list = self.bucket[
                    message.guild.id][message.author.id]
                message_chain.append(message)

                joined = " ".join([m.content for m in message_chain])

                if text_filter(joined, message.author, message.guild):
                    for m in message_chain:
                        try:
                            await m.delete()
                        except Exception:
                            logger.exception(
                                f"Cannot delete message {m.content}")
                    message_chain.clear()

                elif len(message_chain) > int(
                        cfg["Performance"]["moderation-buffer-limit"]):
                    message_chain.pop(0)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        '''
        Catch people trying to edit messages
        '''
        message = await self.bot.get_channel(
            payload.channel_id).fetch_message(
                payload.message_id) if not \
            payload.cached_message else payload.cached_message

        if message:
            await self.on_message(message)
