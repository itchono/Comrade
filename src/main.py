'''
Comrade Bot - V3.0

Versatile and Adaptable Version of Comrade, Rewritten from the ground up
Created by Mingde Yin

With Help from:
Sean D'Souza, Nuha Sahraoui, Victor Wang, Vimal Gunasegaran
Kevin Zhao, Nick Hewko, Stephen Luu, Anthony Luo

Developed from April - June 2020
Originally started in October 2019

CONFIGURE LOCAL VARIABLES IN cfg.py

For inviting the bot to your server complete set up shown below and use the link:
https://discord.com/api/oauth2/authorize?client_id=707042278132154408&permissions=536083799&scope=bot

Requires MongoDB Set Up, with Database called Comrade, and Collections: 
[ChannelCache, CustomCommands, CustomLists, CustomUsers, UserData, announcements, cfg, favourites]
'''

# Internal Imports
from utils import *
from polymorph import *
from crimson import *
from commands import *
from cfg import *

start_time = time.perf_counter()

dotenv.load_dotenv()
TOKEN = os.environ.get('TOKEN')  # bot token; kept private

# Bot initialization
client = commands.Bot(command_prefix=BOT_PREFIX, case_insensitive=True,
                      help_command=commands.MinimalHelpCommand(
                          no_category="Other"))

cogs = [
    AuxilliaryListener, MessageHandler, General, Setup, Vault, Echo,
    Users, Prime, Fun, TimeWizard, Emotes, Polymorph, Moderation, CustomCommands
]

'''
For Repl.it hosted version:
cogs = [NSFW, SelfPing]

On fully hosted version, add NSFW module
'''
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

    for server in client.guilds: 
        await log(server, "Comrade {} is online, logged in from {}.\nStartup done in {:.2f} seconds".format(VERSION, getHost(), time.perf_counter() - start_time))

'''
Users with threat level >2 cannot use Comrade's features.
'''
@client.check
async def globalcheck(ctx): return isnotUltraThreat(ctx)

'''
For Repl.it hosted version:
keep_alive()
'''
client.run(TOKEN)