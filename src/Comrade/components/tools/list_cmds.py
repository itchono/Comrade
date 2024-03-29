'''
List 3.1

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
        print("bruh")
        self.arr.append(item)
        print(self)
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
    Writing things down
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.active = defaultdict(lambda: CustomList({}))

    @commands.command()
    @commands.guild_only()
    async def lists(self, ctx: commands.Context):
        '''
        Shows all lists in this server.
        '''
        all_lists = collection("lists").find({"server": ctx.guild.id})

        names = ["- " + L["name"] for L in all_lists]

        embed = discord.Embed(color=0xd7342a, description="\n".join(names))

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
            if self.active[ctx.channel.id]:
                await self.close(ctx)  # close list

            if L := collection("lists").find_one(
                    {"server": ctx.guild.id, "name": list_name}):
                self.active[ctx.channel.id] = CustomList(L)

                await self.print_list(ctx)
                await ctx.send(
                    f"You have opened the list `{list_name}`.\nMake sure to `{bot_prefix}list close` to save your list.")
            else:
                # New list
                L = {
                    "server": ctx.guild.id,
                    "name": list_name, "author": ctx.author.id, "list": []}
                self.active[ctx.channel.id] = CustomList(L)
                collection("lists").insert_one(L)
                await ctx.send(
                    f"You have created the list `{list_name}`.\nMake sure to `{bot_prefix}list close` to save your list.")

    async def print_list(self, ctx):
        await ctx.send(str(self.active[ctx.channel.id]) +
                f"\n(Author: {ctx.guild.get_member(self.active[ctx.channel.id].author)})")

    @custom_list.group()
    @commands.after_invoke(print_list)
    @commands.guild_only()
    async def all(self, ctx: commands.Context):
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
        if self.active[ctx.channel.id] is not None:
            self.active[ctx.channel.id].add(content)

    @add.command()
    @commands.after_invoke(print_list)
    @commands.guild_only()
    async def add_many(self, ctx: commands.Context, *items):
        '''
        Adds multiple items to the currently open list
        '''
        if self.active[ctx.channel.id] is not None:
            for item in items:
                self.active[ctx.channel.id].add(item)

    @custom_list.group()
    @commands.after_invoke(print_list)
    @commands.guild_only()
    async def remove(self, ctx: commands.Context, *, content: str):
        '''
        Removes a single item from the currently open list
        '''
        if self.active[ctx.channel.id] is not None:
            self.active[ctx.channel.id].remove(content)

    @remove.command(name="many")
    @commands.after_invoke(print_list)
    @commands.guild_only()
    async def remove_many(self, ctx: commands.Context, *items):
        '''
        Removes multiple items from the currently open list
        '''
        if self.active[ctx.channel.id] is not None:
            for item in items:
                self.active[ctx.channel.id].remove(item)

    @custom_list.command()
    @commands.guild_only()
    async def delete(self, ctx: commands.Context):
        '''
        Removes this list from the database
        '''
        if self.active[ctx.channel.id] is not None:
            try:
                name = self.active[ctx.channel.id].name
                result = collection("lists").delete_one(
                    {"server": ctx.guild.id, "name": self.active[ctx.channel.id].name,
                    "author": ctx.author.id})
                self.active[ctx.channel.id] = None
                if result.acknowledged:
                    await ctx.send(f"`{name}` has been deleted.")
            except AttributeError:
                await ctx.send("This list has not been saved yet.")

    @custom_list.command()
    @commands.after_invoke(print_list)
    @commands.guild_only()
    async def close(self, ctx: commands.Context):
        '''
        Closes the currently open list and saves it to MongoDB
        '''
        if self.active[ctx.channel.id] is not None and self.active[ctx.channel.id].arr:

            collection("lists").update_one(
                {"server": ctx.guild.id, "name": self.active[ctx.channel.id].name},
                {"$set":{"list":self.active[ctx.channel.id].arr}})

            await ctx.send(f"`{self.active[ctx.channel.id].name}` saved.")
            self.active[ctx.channel.id] = None
        else:
            await ctx.send("You do not have a list currently open.")
