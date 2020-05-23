'''
Comrade Bot - V3.0 Tritium

More versatile and Adaptable Version of Comrade, Rewritten from the ground up
Mingde Yin

April - May 2020

CONFIGURE LOCAL VARIABLES IN utils.utilities.py

'''
import os
import dotenv

import time

# internal imports
from utils.utilities import *
from utils.msg_handler import *
from utils.aux_listeners import *
from utils.keep_alive import *
from utils.optimus_prime import *
from utils.mongo_interface import *
from utils.time_wizard import *

from polymorph.text_gen import *
from polymorph.model_gen import *

# command modules
from general_cmds import *
from setup_cmds import *
from nsfw_cmds import *
from vault_cmds import *
from echo_cmds import *
from user_cmds import *
from fun_cmds import *
from emote_cmds import *
from polymorph_cmds import *
'''

VARIABLES
Note: Perms integer 536083799
'''

start_time = time.perf_counter()

# private variable loading
dotenv.load_dotenv()
TOKEN = os.environ.get('TOKEN')  # bot token; kept private
'''
INIT
'''



client = commands.Bot(command_prefix=BOT_PREFIX,
                      case_insensitive=True,
                      help_command=commands.MinimalHelpCommand())

cogs = [
    AuxilliaryListener, MessageHandler, General, Setup, NSFW, Vault, Echo,
    Users, Prime, Fun, TimeWizard, Emotes, Polymorph
]

for c in cogs: client.add_cog(c(client))

print("Bot components initialized, awaiting login.")

@client.event
async def on_ready():
    '''
    On successful login
    '''
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game("[{}] Testing Communism".format(BOT_PREFIX)))
    print("{} is online, logged into {} server(s).".format(
        client.user, len(client.guilds)))

    print("Server List:")
    for server in client.guilds:
        print("\t{} ({} members)".format(server.name, len(server.members)))
    
    print("Startup completed in {:.2f} seconds.".format(time.perf_counter() -
                                                        start_time))
    print("Current Local Time: {}".format(localTime().strftime("%I:%M:%S %p %Z")))

    for server in client.guilds:
        await log(server, "Comrade is online, logged in from {}.".format(getHost()))

keep_alive()
client.run(TOKEN)
