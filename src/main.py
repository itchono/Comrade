'''
Comrade Bot - V3.0 Tritium

More versatile and Adaptable Version of Comrade, Rewritten from the ground up
Mingde Yin

April - May 2020

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

# command modules
from general_cmds import *
from setup_cmds import *
from nsfw_cmds import *
from vault_cmds import *
from echo_cmds import *
from user_cmds import *

'''

VARIABLES
Note: Perms integer 536083799
'''

start_time = time.perf_counter()
print("Comrade v3.0_alpha Starting.")

# private variable loading
dotenv.load_dotenv()
TOKEN = os.environ.get('TOKEN') # bot token; kept private
from utils.mongo_interface import *

'''
INIT
'''
client = commands.Bot(command_prefix="$canary ", case_insensitive=True) # declare bot with prefix $c

cogs = [AuxilliaryListener, MessageHandler, General, Setup, NSFW, Vault, Echo, Users, Prime]

for c in cogs: client.add_cog(c(client))
    
print("Bot components initialized, awaiting login.")

@client.event
async def on_ready():
    '''
    On successful login
    '''
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Testing Communism"))
    print("{} is online, logged into {} server(s).".format(client.user, len(client.guilds)))
    
    print("Server List:")
    for server in client.guilds: print("\t{} ({} members)".format(server.name, len(server.members)))
    
    print("Startup completed in {:.2f} seconds.".format(time.perf_counter() - start_time))

keep_alive()
client.run(TOKEN)
