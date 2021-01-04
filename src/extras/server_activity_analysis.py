import discord
from discord.ext import commands

import pickle, os, dotenv

dotenv.load_dotenv()

client = discord.Client()

SERVER = 419214713252216848

@client.event
async def on_ready():

    server = client.get_guild(SERVER)

    id2name = {}

    for m in server.members:
        print(m.id)
        id2name[m.id] = m.display_name

    with open("names", "wb") as f:
        pickle.dump(id2name, f)

    exit()

client.run(os.environ.get('TOKEN'))