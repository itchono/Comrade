from utils.core_dependencies.utilities import *
from utils.core_dependencies.db_utils import *

import math

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
        
        if not len(self.arr): s += "*(Empty)*"

        else:
            s += "\n".join([f"- {s}" for s in self.arr])
            s += f"\n({len(self.arr)} elements total.)"

        return s

    def add(self, item): self.arr.append(item)

    def remove(self, item):
        try: self.arr.remove(item)
        except: return 1

    def __len__(self): return len(self.arr)

    def todict(self): return {"name":self.name, "list":self.arr, "owner":self.owner, "server":self.server, "private":self.private, "creation-time":self.create_time}

class Lists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name = "list", invoke_without_command=True)
    @commands.guild_only()
    async def customlist(self, ctx: commands.Context, listname:str=None):
        '''
        Displays a list with the given name
        '''

        if listname:
            if lst := DBfind_one(LIST_COL, {"server":ctx.guild.id, "name":listname}): await ctx.send(CustomList(lst))
            else: await ctx.send(f"List with name `{listname}` not found.")
        
        else: await ctx.send(f"**__Comrade List System:__**\nType `{BOT_PREFIX}help list` for more info")

    @commands.command()
    @commands.guild_only()
    async def allLists(self, ctx:commands.Context):
        '''
        Displays all the lists on the server.
        '''

        if lsts := DBfind(LIST_COL, {"server":ctx.guild.id}):
            s = f"__All lists in {ctx.guild}:__\n"

            for i in lsts:
                s += f"{i['name']} [{len(i['list'])} items]\n"
            await ctx.send(s)
        else:
            await ctx.send("No lists in this server")

    @customlist.command()
    async def all(self, ctx:commands.Context):
        '''
        Displays all the lists on the server.
        '''
        await self.allLists(ctx)

    @customlist.command()
    async def addto(self, ctx: commands.Context, listname, *, value):
        '''
        Adds an item to the list.
        '''
        if lst := DBfind_one(LIST_COL, {"server":ctx.guild.id, "name":listname}):

            if not lst["private"] or ctx.author.id == lst["owner"]:

                l = CustomList(lst)

                l.add(value)

                DBupdate(LIST_COL, {"server":ctx.guild.id, "name":listname}, l.todict())

                await reactOK(ctx)
            
            else: await ctx.send(f"You don't have permission to modify this list.")
        else: await ctx.send(f"List with name `{listname}` not found.")

    @customlist.command()
    async def addmultiple(self, ctx: commands.Context, listname, *values):
        '''
        Add multiple items from the list.
        '''
        if lst := DBfind_one(LIST_COL, {"server":ctx.guild.id, "name":listname}):

            if not lst["private"] or ctx.author.id == lst["owner"]:

                l = CustomList(lst)

                for value in values: l.add(value)

                DBupdate(LIST_COL, {"server":ctx.guild.id, "name":listname}, l.todict())

                await reactOK(ctx)
            
            else: await ctx.send(f"You don't have permission to modify this list.")
        else: await ctx.send(f"List with name `{listname}` not found.")

    @customlist.command()
    async def removefrom(self, ctx: commands.Context, listname, *, value):
        '''
        Removes an item from a given list.
        '''
        if lst := DBfind_one(LIST_COL, {"server":ctx.guild.id, "name":listname}):

            if not lst["private"] or ctx.author.id == lst["owner"]:

                l = CustomList(lst)

                if l.remove(value): await ctx.send(f"Item {value} does not exist in {listname}.")

                else:
                    DBupdate(LIST_COL, {"server":ctx.guild.id, "name":listname}, l.todict())
                    await reactOK(ctx)
        
            else: await ctx.send(f"You don't have permission to modify this list.")
        else: await ctx.send(f"List with name `{listname}` not found.")

    @customlist.command()
    async def removemultiple(self, ctx: commands.Context, listname, *values):
        '''
        Removes an item from a given list.
        '''
        if lst := DBfind_one(LIST_COL, {"server":ctx.guild.id, "name":listname}):

            if not lst["private"] or ctx.author.id == lst["owner"]:

                l = CustomList(lst)

                for value in values:
                    if l.remove(value): await ctx.send(f"Item {value} does not exist in {listname}.")
                    else:
                        DBupdate(LIST_COL, {"server":ctx.guild.id, "name":listname}, l.todict())
                        await reactOK(ctx)
        
            else: await ctx.send(f"You don't have permission to modify this list.")
        else: await ctx.send(f"List with name `{listname}` not found.")

    @customlist.group(invoke_without_command=True)
    async def make(self, ctx: commands.Context, listname, initial_list=[]):
        '''
        Makes a new [publicly editable] list 
        Preferrably don't put spaces in the name!
        
        '''
        if lst := DBfind_one(LIST_COL, {"server":ctx.guild.id, "name":listname}):
            await ctx.send(f"A list with the name `{listname}` already exists!")
        else:
            DBupdate(LIST_COL, {"server":ctx.guild.id, "name":listname}, {"server":ctx.guild.id, "name":listname, "list":initial_list, "owner":ctx.author.id, "private":False, "creation-time":localTime()})
            await reactOK(ctx)

    @make.command()
    async def private(self, ctx: commands.Context, listname, initial_list=[]):
        '''
        Makes a private list. 
        Only you can edit it [but, it's still viewable by everyone else]
        '''
        if lst := DBfind_one(LIST_COL, {"server":ctx.guild.id, "name":listname}):
            await ctx.send(f"A list with the name `{listname}` already exists!")
        else:
            DBupdate(LIST_COL, {"server":ctx.guild.id, "name":listname}, {"server":ctx.guild.id, "name":listname, "list":initial_list, "owner":ctx.author.id, "private":True, "creation-time":localTime()})
            await reactOK(ctx)

    @customlist.command()
    async def delete(self, ctx:commands.Context, listname):
        '''
        Deletes a list
        '''
        if lst := DBfind_one(LIST_COL, {"server":ctx.guild.id, "name":listname}):

            if not lst["private"] or ctx.author.id == lst["owner"]:
                DBremove_one(LIST_COL, {"server":ctx.guild.id, "name":listname})
                await reactOK(ctx)
        
            else: await ctx.send(f"You don't have permission to modify this list.")
        else: await ctx.send(f"List with name `{listname}` not found.")

    @customlist.command()
    async def fromreactions(self, ctx: commands.Context, listname, reaction:typing.Optional[discord.PartialEmoji]=None, msg=None):
        '''
        Makes a list from a message's reactions
        '''
        try:
            msg = await commands.MessageConverter().convert(ctx, msg)

            l = []

            for rxn in msg.reactions: 
                if rxn.emoji == reaction or not reaction: l += [i.display_name for i in await rxn.users().flatten()]
            DBupdate(LIST_COL, {"server":ctx.guild.id, "name":listname}, {"server":ctx.guild.id, "name":listname, "list":l, "owner":ctx.author.id, "private":False, "creation-time":localTime()})
            await reactOK(ctx)
        except: await ctx.send("Please specify a message to base list from.")