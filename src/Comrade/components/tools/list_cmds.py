'''
List 3.0

Like a text editor

High Level:
$c list <title>
>>> You have opened <title> (New File)

$c list add <data>

$c list remove <data>

$c list close
>>> You have closed <title>


///


$c lists
>>> Lists in IRAQ BTW



'''
import discord
from discord.ext import commands


class CustomList():

    def __init__(self, json):
        self.name = json["name"]
        self.arr = json["list"]
        self.owner = json["owner"]
        self.server = json["server"]
        self.private = json["private"]
        self.create_time = json["creation-time"]

    def __repr__(self):
        s = f"**__{self.name}__:**\n"

        if not len(self.arr):
            s += "*(Empty)*"

        else:
            s += "\n".join([f"- {s}" for s in self.arr])
            s += f"\n({len(self.arr)} elements total.)"

        return s

    def add(self, item): self.arr.append(item)

    def remove(self, item):
        try:
            self.arr.remove(item)
        except Exception:
            return 1

    def __len__(self): return len(self.arr)

    def todict(self):
        return {"name": self.name,
                "list": self.arr,
                "owner": self.owner,
                "server": self.server,
                "private": self.private,
                "creation-time": self.create_time}


class Lists(commands.Cog):
    '''
    Lists for writing things down
    '''
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def lists(self, ctx: commands.Context):
        '''
        Shows all lists in this server.
        '''

    @commands.group(invoke_without_subcommand=True, name="list")
    @commands.guild_only()
    async def custom_list(self, ctx: commands.Context, list_name: str):
        '''
        Displays a list with the given name, opening it for editing.
        Creates a new list if the name doesn't exist.

        Opens a new list if you already have one open
        '''

    @custom_list.group()
    @commands.guild_only()
    async def all(self, ctx: commands.Context, *, content: str):
        '''
        Shows all lists in this server.
        '''
        await self.lists(ctx)

    @custom_list.group()
    @commands.guild_only()
    async def add(self, ctx: commands.Context, *, content: str):
        '''
        Adds a single item to the currently open list
        '''
        pass

    @add.command(name="many")
    @commands.guild_only()
    async def add_many(self, ctx: commands.Context, *items):
        '''
        Adds multiple items to the currently open list
        '''
        pass

    @custom_list.group()
    @commands.guild_only()
    async def remove(self, ctx: commands.Context, *, content: str):
        '''
        Removes a single item from the currently open list
        '''
        pass

    @remove.command(name="many")
    @commands.guild_only()
    async def remove_many(self, ctx: commands.Context, *items):
        '''
        Removes multiple items from the currently open list
        '''
        pass

    @custom_list.command()
    @commands.guild_only()
    async def delete(self, ctx: commands.Context):
        '''
        Removes this list from the database
        '''
        pass

    @custom_list.command()
    @commands.guild_only()
    async def close(self, ctx: commands.Context):
        '''
        Closes the currently open list
        Might be a useless function
        '''
        pass
