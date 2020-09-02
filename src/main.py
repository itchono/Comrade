'''
Comrade Bot

By Mingde Yin
'''
import sys, dotenv
from utils import *
from polymorph import *
from cosmo import *
from commands import *
from cfg import *

first_start = True
online = False

start_time = time.perf_counter()
dotenv.load_dotenv()

REDUCED_INSTRUCTION_SET = [AuxilliaryListener, MessageHandler,  Databases,  Echo, Lists]

# Databases MUST load first, otherwise things will NOT work
cogs = [ Databases, AuxilliaryListener, MessageHandler, General, Vault, Echo,
    Users, TextFilter, Fun, Announcements, Emotes, Polymorph, Moderation, Cosmo, 
    BPC, RandomEvents, Lists, Polls, NSFW, SelfPing, TexRender, Shoujo, Graphing
] if not DEVELOPMENT_MODE else REDUCED_INSTRUCTION_SET # for use with development to get faster start

for c in cogs: client.add_cog(c(client))
print(f"Running discord.py version {discord.__version__}.")

@client.event
async def on_connect():
    '''
    Connected to Discord
    '''
    global online
    await client.change_presence(status=discord.Status.online, activity=discord.Game(DEFAULT_STATUS))
    print(f"{client.user} is online, logged into {len(client.guilds)} server(s).")
    online = True

@client.event
async def on_ready():
    '''
    When bot is ready to go
    '''
    global first_start
    if first_start:
        print("Server List:")
        for server in client.guilds: print(f"\t{server.name} ({len(server.members)} members)")

        print("Loading Cogs:")
        for name in ["Databases", "Users", "Vault", "Polymorph", "Emotes"]: # load cogs in order
            try: print(f"\t{name}: ", end=""); await client.get_cog(name).on_load() # Initialize cogs
            except: print(f"WARN: Cog not loaded {name}")

        print("Startup completed in {:.2f} seconds.\nCurrent Local Time: {}".format(time.perf_counter() - start_time, localTime().strftime("%I:%M:%S %p %Z")))

        for server in client.guilds: await log(server, "Comrade {} is online.\nLogged in from {}.\nStartup done in {:.2f} seconds".format(VERSION, getHost(), time.perf_counter() - start_time))

        if NOTIFY_OWNER_ON_STARTUP:
            embed = discord.Embed(title="Comrade is Online", description="Version {}\nLogged in from {}.\nStartup done in {:.2f} seconds".format(VERSION, getHost(), time.perf_counter() - start_time))
            embed.add_field(name="Time", value=(localTime().strftime("%I:%M:%S %p %Z")))
            await DM("", (await client.application_info()).owner, embed)
        
        first_start = False

    elif NOTIFY_OWNER_ON_STARTUP:
        embed = discord.Embed(title="Comrade has reconnected", description="Version {}\nLogged in from {}.\nReconnection done in {:.2f} seconds".format(VERSION, getHost(), time.perf_counter() - start_time))
        embed.add_field(name="Time", value=(localTime().strftime("%I:%M:%S %p %Z")))
        await DM("", (await client.application_info()).owner, embed)

@client.event
async def on_disconnect():
    '''
    Bot crashes because of loss of connection
    '''
    global online
    global start_time
    if online:
        print("WARN: Bot has disconnected from Discord.")
        try: 
            start_time = time.perf_counter()
            # online = False
            # await client.wait_for("connect", timeout=300.0)
            # await client.wait_for("ready")
            # print(f"Bot reconnected after {time.perf_counter() - start_time} of downtime.")
            # await DM(f"Bot reconnected after {time.perf_counter() - start_time} of downtime.", (await client.application_info()).owner)
            # online = True
            # TODO re-enable once docker host comes back online
        except asyncio.TimeoutError: sys.exit(0)  

# Users with threat-level >2 cannot use Comrade's features.
@client.check_once
async def globalcheck(ctx): return isNotThreat(2)(ctx)

if SELFPING_REQUIRED: keep_alive()
client.run(os.environ.get('TOKEN')) # Run bot with loaded password