'''
Comrade Bot - V3.0 Tritium

More versatile and Adaptable Version of Comrade, Rewritten from the ground up
Mingde Yin

With Help from
- Sean D'Souza
- Nuha Sahraoui
- Victor Wang
- Vimal Gunasegaran
- Kevin Zhao
- Nick Hewko
- Anthony Luo

April - June 2020

CONFIGURE LOCAL VARIABLES IN cfg.py

For inviting the bot to your server,
Note: Perms integer 536083799
'''
import os
import dotenv
import time

# internal imports
from utils.utilities import *
from utils.msg_handler import *
from utils.aux_listeners import *
from utils.optimus_prime import *
from utils.mongo_interface import *
from utils.time_wizard import *

from polymorph.text_gen import *
from polymorph.model_gen import *

from crimson.command_assembler import *

# command modules
from commands.general_cmds import *
from commands.setup_cmds import *
from commands.nsfw_cmds import *
from commands.vault_cmds import *
from commands.echo_cmds import *
from commands.user_cmds import *
from commands.fun_cmds import *
from commands.emote_cmds import *
from commands.polymorph_cmds import *
from commands.mod_cmds import *

from cfg import *

'''
For Repl.it hosted version:
from utils.keep_alive import *
'''
start_time = time.perf_counter()

# Private Variable Loading
dotenv.load_dotenv()
TOKEN = os.environ.get('TOKEN')  # bot token; kept private

# Bot initialization
client = commands.Bot(command_prefix=BOT_PREFIX, case_insensitive=True,
                      help_command=commands.MinimalHelpCommand(
                          no_category="Other"
                      ))

cogs = [
    AuxilliaryListener, MessageHandler, General, Setup, Vault, Echo,
    Users, Prime, Fun, TimeWizard, Emotes, Polymorph, Moderation, CustomCommands
]
# NOTE: NSFW is temporarily unloaded for hosting purposes.

for c in cogs: client.add_cog(c(client))
print("Bot components initialized, awaiting login.")

@client.event
async def on_ready():
    '''
    On successful login
    '''
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game("[{}] Testing Communism".format(BOT_PREFIX)))
    
    print("{} is online, logged into {} server(s).\nServer List:".format(client.user, len(client.guilds)))

    for server in client.guilds: print("\t{} ({} members)".format(server.name, len(server.members)))

    print("Startup completed in {:.2f} seconds.\nCurrent Local Time: {}".format(time.perf_counter() - start_time, 
                                                                    localTime().strftime("%I:%M:%S %p %Z")))

    for server in client.guilds: await log(server, "Comrade is online, logged in from {}.".format(getHost()))

@client.check
async def notUltraThreat(ctx):
    '''
    Users with threat level >2 cannot use Comrade's features.
    '''
    return isnotUltraThreat(ctx)

'''
For Repl.it hosted version:
keep_alive()
'''
client.run(TOKEN)