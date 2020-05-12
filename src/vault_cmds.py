from utils.utilities import *
from utils.mongo_interface import *

from pybooru import Danbooru

class Vault(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    #@commands.command()