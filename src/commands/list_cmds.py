from utils.utilities import *

import math


class CustomList():

    def __init__(self, json):
        self.name = json["name"]
        self.arr = json["list"]
        self.owner = json["owner"]
        self.server = json["server"]

    def __repr__(self):
        s = f"**__{self.name}__:**\n"
        
        if len(self.arr): s += "*(Empty)*"

        else:
            s += "\n".join([f"- {s}" for s in arr])
            s += f"({len(self.arr)} elements total.)"

        return s

    def __len__(self): return len(self.arr)

    def todict(self): return {"name":self.name, "list":self.list, "owner":self.owner, "server":self.server}

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name = "list", invoke_without_command=True)
    @commands.guild_only()
    async def customlist(self, ctx: commands.Context, listname:str):
        '''
        Displays a lists with the given name
        '''

        if lst := DBfind_one(LIST_COL, {"server":ctx.guild.id, "name":title}):
            await ctx.send(CustomList(lst))

    @customlist.command()
    async def addto(self, ctx: commands.Context, listname, *, value):
        '''
        Adds an item to the list.
        '''
        if lst := DBfind_one(LIST_COL, {"server":ctx.guild.id, "name":title}):

            if not lst["private"] or ctx.author.id == lst["owner"]:
            
            else:

        
        else:
            await ctx.send(f"List with name `{listname}` not found.")

            



    @customlist.command()
    async def removefrom(self, ctx: commands.Context, listname, *, value):
        '''
        Removes an item from a given list.
        '''

    @customlist.group(invoke_without_command=True)
    async def make(self, ctx: commands.Context, listname):
        '''
        Makes a new [publicly editable] list 
        Preferrably don't put spaces in the name!
        
        '''
        DBupdate(LIST_COL, {"server":ctx.guild.id, "name":title}, {"server":ctx.guild.id, "name":title, "list":[], "owner":ctx.author.id, "private":False, "creation-time":localTime()})
        await reactOK(ctx)

    @make.command()
    async def private()
        '''
        Makes a private list. 
        Only you can edit it [but, it's still viewable by everyone else]
        '''
        DBupdate(LIST_COL, {"server":ctx.guild.id, "name":title}, {"server":ctx.guild.id, "name":title, "list":[], "owner":ctx.author.id, "private":True, "creation-time":localTime()})
        await reactOK(ctx)


    @customlist.command()
    async def addto(self, ctx: commands.Context, listname, value):
    



        # TODO turn into command-subcommand deal
        if operation in {"make", "makefrom", "add", "remove", "show", "all"}:

            if operation == "make":
                l = []

                DBupdate(LIST_COL, {"server":ctx.guild.id, "name":title}, {"server":ctx.guild.id, "name":title, "list":l})
                await reactOK(ctx)
                
            elif operation == "makefrom":
                try:
                    msg = await commands.MessageConverter().convert(ctx, value)

                    l = []

                    for rxn in msg.reactions: l += [i.display_name for i in await rxn.users().flatten()]
                    
                    DBupdate(LIST_COL, {"server":ctx.guild.id, "name":title}, {"server":ctx.guild.id, "name":title, "list":l})
                    await reactOK(ctx)
                
                except:
                    await ctx.send("Please specify a message to base list from.")

            elif operation == "show":
                try: 
                    l = DBfind_one(LIST_COL, {"server":ctx.guild.id, "name":title})["list"]
                    await ctx.send("{}:\n{}".format(title, l))
                except:
                    await delSend(ctx, "List not found.")
            elif operation == "add":
                try: 
                    l = DBfind_one(LIST_COL, {"server":ctx.guild.id, "name":title})["list"]
                    l.append(value)

                    DBupdate(LIST_COL, {"server":ctx.guild.id, "name":title}, {"server":ctx.guild.id, "name":title, "list":l})

                    await reactOK(ctx)
                except:
                    await delSend(ctx, "List not found.")

            elif operation == "remove":
                try: 
                    l = DBfind_one(LIST_COL, {"server":ctx.guild.id, "name":title})["list"]
                    try:
                        l.remove(value)
                        DBupdate(LIST_COL, {"server":ctx.guild.id, "name":title}, {"server":ctx.guild.id, "name":title, "list":l})
                        await reactOK(ctx)
                    except:
                        await delSend(ctx, "Element {} not found.".format(value))
                except:
                    await delSend(ctx, "List not found.")

            elif operation == "all":
                await ctx.send("{}".format([i["name"] for i in DBfind(LIST_COL, {"server":ctx.guild.id})]))