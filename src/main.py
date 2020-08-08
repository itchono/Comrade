'''
Comrade Bot - V3.2

Versatile and Adaptable Version of Comrade, Rewritten from the ground up
Created by Mingde Yin

With Help from:
Sean D'Souza, Nuha Sahraoui, Victor Wang, Vimal Gunasegaran,
Maggie Wang, Kevin Hu, Kevin Zhao, Nick Hewko, Stephen Luu, Anthony Luo

Post-v3 Development
v3 Developed from April - June 2020
Originally started in October 2019

CONFIGURE LOCAL VARIABLES IN cfg.py

For inviting the bot to your server complete set up shown below and use the link:
https://discord.com/api/oauth2/authorize?client_id=707042278132154408&permissions=536083799&scope=bot

Requires MongoDB Set Up, with Database called Comrade, and Collections: 
[ChannelCache, CustomCommands, CustomLists, CustomUsers, UserData, announcements, cfg, favourites]
'''
import sys
from utils import *
from polymorph import *
from cosmo import *
from commands import *
from cfg import *

start_time = time.perf_counter()

dotenv.load_dotenv()
TOKEN = os.environ.get('TOKEN')  # bot token; kept private

cogs = [
    AuxilliaryListener, MessageHandler, General, Databases, Vault, Echo,
    Users, TextFilter, Fun, TimeWizard, Emotes, Polymorph, Moderation, Cosmo, 
    BPC, RandomEvents, Waifu
]

'''
For Repl.it hosted version:
cogs = [NSFW, SelfPing]

On fully hosted version, add NSFW module

'''
for c in cogs: client.add_cog(c(client))
print(f"Running discord.py version {discord.__version__}.")

@client.event
async def on_connect():
    '''
    Connected to Discord
    '''
    await client.change_presence(status=discord.Status.online, activity=discord.Game(DEFAULT_STATUS))
    print(f"{client.user} is online, logged into {len(client.guilds)} server(s).")

@client.event
async def on_ready():
    '''
    When bot is ready to go
    '''
    print("Server List:")
    for server in client.guilds: print(f"\t{server.name} ({len(server.members)} members)")

    print("Loading Cogs:")
    for name in ["Databases", "Users", "Vault", "Polymorph", "Emotes"]: # load cogs in order
        print(f"\t{name}: ", end="")
        await client.get_cog(name).on_load() # Initialize cogs

    print("Startup completed in {:.2f} seconds.\nCurrent Local Time: {}".format(time.perf_counter() - start_time, localTime().strftime("%I:%M:%S %p %Z")))

    for server in client.guilds: await log(server, "Comrade {} is online.\nLogged in from {}.\nStartup done in {:.2f} seconds".format(VERSION, getHost(), time.perf_counter() - start_time))

    if NOTIFY_OWNER_ON_STARTUP:
        embed = discord.Embed(title="Comrade is Online", description="Version {}\nLogged in from {}.\nStartup done in {:.2f} seconds".format(VERSION, getHost(), time.perf_counter() - start_time))
        embed.add_field(name="Time", value=(localTime().strftime("%I:%M:%S %p %Z")))
        await DM("", (await client.application_info()).owner, embed)

@client.event
async def on_disconnect():
    '''
    Bot crashes because of loss of connection
    '''
    try: 
        dc_time = time.perf_counter()
        await client.wait_for("connect", timeout=300.0)
        await client.wait_for("ready")
        await DM(f"Bot reconnected after {time.perf_counter() - dc_time} of downtime.", (await client.application_info()).owner)

    except asyncio.TimeoutError: sys.exit(0)  

'''
Users with threat-level >2 cannot use Comrade's features.
'''
@client.check_once
async def globalcheck(ctx): return isNotThreat(2)(ctx)

'''
For Repl.it hosted version:
keep_alive()
'''
client.run(TOKEN)