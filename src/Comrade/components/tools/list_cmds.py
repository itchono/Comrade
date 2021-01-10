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

from collections import defaultdict
from db import collection


class CustomList():

    def __init__(self, json):
        self.name: str = json["name"]
        self.arr: list = json["list"]
        self.owner = json["owner"]
        self.server = json["server"]
        self.private = json["private"]

    def __repr__(self):
        s = f"**__{self.name}__:**\n"

        if not len(self.arr):
            s += "*(Empty)*"

        else:
            s += "\n".join([f"- {s}" for s in self.arr])
            s += f"\n({len(self.arr)} elements total.)"

        return s

    def add(self, item):
        self.arr.append(item)
        self.arr.sort()

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
                "private": self.private}


class Lists(commands.Cog):
    '''
    Lists for writing things down
    NOT IMPLEMENTED YET
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.active = defaultdict(lambda: defaultdict(CustomList))

    @commands.command()
    @commands.guild_only()
    async def lists(self, ctx: commands.Context):
        '''
        Shows all lists in this server.
        '''
        all_lists = collection("lists").find({"server": ctx.guild.id})

        names = ["- " + L["name"] for L in all_lists]

        embed = discord.Embed("\n".join(names))

        embed.set_author(
            name=f"Lists in {ctx.guild.name}", icon_url=ctx.guild.icon_url)

        await ctx.send(embed=embed)


    @commands.group(invoke_without_subcommand=True, name="list")
    @commands.guild_only()
    async def custom_list(self, ctx: commands.Context, list_name: str):
        '''
        Displays a list with the given name, opening it for editing.
        Creates a new list if the name doesn't exist.

        Opens a new list if you already have one open
        '''
        if L := collection("lists").find_one(
            {"server": ctx.guild.id, "name": list_name}):
            self.active[ctx.guild.id][ctx.author.id] = CustomList(L)

            # You have opened it!
        else:
            L = {}
            collection("lists").insert_one(L)
            self.active[ctx.guild.id][ctx.author.id] = CustomList(L)
            # New list


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
        self.active[ctx.guild.id][ctx.author.id].add(content)

    @add.command(name="many")
    @commands.guild_only()
    async def add_many(self, ctx: commands.Context, *items):
        '''
        Adds multiple items to the currently open list
        '''
        for item in items:
            self.active[ctx.guild.id][ctx.author.id].add(item)

    @custom_list.group()
    @commands.guild_only()
    async def remove(self, ctx: commands.Context, *, content: str):
        '''
        Removes a single item from the currently open list
        '''
        self.active[ctx.guild.id][ctx.author.id].remove(content)

    @remove.command(name="many")
    @commands.guild_only()
    async def remove_many(self, ctx: commands.Context, *items):
        '''
        Removes multiple items from the currently open list
        '''
        for item in items:
            self.active[ctx.guild.id][ctx.author.id].remove(item)

    @custom_list.command()
    @commands.guild_only()
    async def delete(self, ctx: commands.Context):
        '''
        Removes this list from the database
        '''
        collection("lists").delete_one(
            {"server": ctx.guild.id, "name": self.active[ctx.guild.id][ctx.author.id].name,
            "owner": ctx.author.id})

    @custom_list.command()
    @commands.guild_only()
    async def close(self, ctx: commands.Context):
        '''
        Closes the currently open list
        Might be a useless function
        '''
        pass
