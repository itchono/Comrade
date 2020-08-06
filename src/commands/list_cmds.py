from utils.utilities import *

import math


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name = "list")
    @commands.guild_only()
    async def customlist(self, ctx: commands.Context, operation, title=None, value=None):
        '''
        Displays a lists, or adds.

        Commands: "make", "makefrom", "add", "remove", "show", "all"
        '''

        if ctx.invoked_subcommand is None:
            await ctx.send("Comrade List System.")

    @customlist.command()
    async def addto(self, ctx: commands.Context, listname, value):

    @customlist.command()
    async def removefrom(self, ctx: commands.Context, listname, value):

    @customlist.command()
    async def make(self, ctx: commands.Context, listname):
        '''
        Makes a new list
        '''

        DBupdate(LIST_COL, {"server":ctx.guild.id, "name":title}, {"server":ctx.guild.id, "name":title, "list":[], "owner":ctx.author.id})
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