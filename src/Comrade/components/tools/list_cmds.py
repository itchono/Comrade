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

from utils.utilities import bot_prefix


class CustomList():

    def __init__(self, json):
        if json:
            self.name: str = json["name"]
            self.arr: list = json["list"]
            self.author = json["author"]
            self.server = json["server"]
        else:
            self.name: str = ""
            self.arr: list = []
            self.author = None
            self.server = None

    def __repr__(self):
        s = f"**__{self.name}__**\n"

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
                "author": self.author,
                "server": self.server}


class Lists(commands.Cog):
    '''
    Lists for writing things down
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.active = defaultdict(lambda: defaultdict(lambda: CustomList({})))

    @commands.command()
    @commands.guild_only()
    async def lists(self, ctx: commands.Context):
        '''
        Shows all lists in this server.
        '''
        all_lists = collection("lists").find({"server": ctx.guild.id})

        names = ["- " + L["name"] for L in all_lists]

        embed = discord.Embed(description="\n".join(names))

        embed.set_author(
            name=f"Lists in {ctx.guild.name}", icon_url=ctx.guild.icon_url)

        await ctx.send(embed=embed)


    @commands.group(invoke_without_command=True, name="list")
    @commands.guild_only()
    async def custom_list(self, ctx: commands.Context, list_name: str):
        '''
        Displays a list with the given name, opening it for editing.
        Creates a new list if the name doesn't exist.
        Opens a new list if you already have one open
        '''
        if ctx.invoked_subcommand is None:
            if self.active[ctx.guild.id][ctx.author.id]:
                await self.close(ctx)  # close list

            if L := collection("lists").find_one(
                    {"server": ctx.guild.id, "name": list_name}):
                self.active[ctx.guild.id][ctx.author.id] = CustomList(L)

                await self.print_list(ctx)
                await ctx.send(
                    f"You have opened the list `{list_name}`.\nMake sure to `{bot_prefix}list close` to save your list.")
            else:
                # New list
                L = {
                    "server": ctx.guild.id,
                    "name": list_name, "author": ctx.author.id, "list": []}
                self.active[ctx.guild.id][ctx.author.id] = CustomList(L)
                collection("lists").insert_one(L)
                await ctx.send(
                    f"You have created the list `{list_name}`.\nMake sure to `{bot_prefix}list close` to save your list.")

    async def print_list(self, ctx):
        await ctx.send(str(self.active[ctx.guild.id][ctx.author.id]) +
                f"\n(Author: {ctx.guild.get_member(self.active[ctx.guild.id][ctx.author.id].author)})")

    @custom_list.group()
    @commands.after_invoke(print_list)
    @commands.guild_only()
    async def all(self, ctx: commands.Context, *, content: str):
        '''
        Shows all lists in this server.
        '''
        await self.lists(ctx)

    @custom_list.group()
    @commands.after_invoke(print_list)
    @commands.guild_only()
    async def add(self, ctx: commands.Context, *, content: str):
        '''
        Adds a single item to the currently open list
        '''
        self.active[ctx.guild.id][ctx.author.id].add(content)

    @add.command(name="many")
    @commands.after_invoke(print_list)
    @commands.guild_only()
    async def add_many(self, ctx: commands.Context, *items):
        '''
        Adds multiple items to the currently open list
        '''
        for item in items:
            self.active[ctx.guild.id][ctx.author.id].add(item)

    @custom_list.group()
    @commands.after_invoke(print_list)
    @commands.guild_only()
    async def remove(self, ctx: commands.Context, *, content: str):
        '''
        Removes a single item from the currently open list
        '''
        self.active[ctx.guild.id][ctx.author.id].remove(content)

    @remove.command(name="many")
    @commands.after_invoke(print_list)
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
        result = collection("lists").delete_one(
            {"server": ctx.guild.id, "name": self.active[ctx.guild.id][ctx.author.id].name,
            "author": ctx.author.id})
        await ctx.send(result)

    @custom_list.command()
    @commands.after_invoke(print_list)
    @commands.guild_only()
    async def close(self, ctx: commands.Context):
        '''
        Closes the currently open list and saves it to MongoDB
        '''
        if self.active[ctx.guild.id][ctx.author.id] and self.active[ctx.guild.id][ctx.author.id].arr:

            collection("lists").update_one(
                {"server": ctx.guild.id, "name": self.active[ctx.guild.id][ctx.author.id].name},
                {"$set":{"list":self.active[ctx.guild.id][ctx.author.id].arr}})

            await ctx.send(f"`{self.active[ctx.guild.id][ctx.author.id].name}` saved.")
            self.active[ctx.guild.id][ctx.author.id] = None
        else:
            await ctx.send("You do not have a list currently open.")
