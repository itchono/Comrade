'''
Hentai.
Credits to Sunekku (Nuha Sahraoui).
'''
import discord
from discord.ext import commands

from utils.reactions import reactOK
from db import collection


class NSFW(commands.Cog):
    '''
    NSFW Commands
    (Hentai, lewd doujins)
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.is_nsfw()
    async def favourite(
            self, ctx: commands.Context, imageName: str, url: str = None):
        '''
        Adds an image to the favourites list

        Category naming system:
        type as `$c favourite category:name <URL>`
        ex. `$c favourite neko:kurumi <URL>` saves an entry under the "neko" category, titled "kurumi

        '''
        if ctx.invoked_subcommand is None:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url

            tokens = imageName.split(":")  # split tokens

            if len(tokens) > 1:
                collection("favouritensfw").insert_one(
                    {"imageID": tokens[1],
                             "URL": url,
                             "server": ctx.guild.id,
                             "user": ctx.author.id,
                             "category": tokens[0]}
                )
                fullname = f"{tokens[0]}:{tokens[1]}"
            else:

                collection("favouritensfw").insert_one(
                     {"imageID": imageName,
                          "URL": url,
                          "server": ctx.guild.id,
                          "user": ctx.author.id,
                          "category": ""}
                )
                fullname = f"{tokens[0]}"
            await ctx.send(f"Image favourited as `{fullname}`.")

    @favourite.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def view(self, ctx: commands.Context, imageName: str):
        '''
        Retrieves a favourite based on ID
        To view a post, you can either specify a name, category, or both.
        ex. `$c favourite neko:kurumi` or `$c favourite kurumi` will get you identical results,
        UNLESS you have multiple posts under different catergories with the same name, in which case it will be based on the most recent entry.

        You can view other people's favourites by specifying their name when you call the command.
        ex. `$c favourite itchono:neko:kurumi`
        '''
        try:
            tokens = imageName.split(":")  # split tokens

            fav = None

            if len(tokens) == 1:

                if fav := collection(
                    "favouritensfw").find_one({"server": ctx.guild.id,
                                               "imageID": tokens[0],
                                               "user": ctx.author.id,
                                               "category": ""}):
                    pass
                else:
                    fav = collection(
                            "favouritensfw").find_one({
                            "server": ctx.guild.id, "imageID": tokens[0], "user": ctx.author.id})

            elif len(tokens) == 2:

                if fav := collection(
                            "favouritensfw").find_one({"server": ctx.guild.id,
                                        "imageID": tokens[1],
                                            "user": ctx.author.id,
                                            "category": tokens[0]}):
                    pass
                else:
                    member = ctx.guild.get_member(tokens[0])

                    fav = collection(
                    "favouritensfw").find_one({"server": ctx.guild.id, "imageID": tokens[1], "user": member.id})

            elif len(tokens) == 3:

                member = ctx.guild.get_member(tokens[0])

                fav = collection(
                    "favouritensfw").find_one({"server": ctx.guild.id, "imageID": tokens[2], "user": await member.id, "category": tokens[1] if tokens[1] else ""})

            e = discord.Embed()
            e.set_image(url=fav["URL"])
            await ctx.send(embed=e)
        except BaseException:
            await ctx.send("Image not found.")

    @favourite.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def remove(self, ctx: commands.Context, imageName: str):
        '''
        removes an image from the favourites list
        '''
        try:
            tokens = imageName.split(":")  # split tokens

            if len(tokens) > 1:
                collection("favouritensfw").delete_one({"server": ctx.guild.id,
                              "imageID": tokens[1],
                                 "user": ctx.author.id,
                                 "category": tokens[0]})
                fullname = f"{tokens[1]}:{tokens[0]}"
            else:
                collection("favouritensfw").delete_one({"server": ctx.guild.id,
                              "imageID": tokens[0],
                                 "user": ctx.author.id,
                                 "category": ""})
                fullname = f"{tokens[0]}"

            await reactOK(ctx)
            await ctx.send(f"`{fullname}` has been removed.", delete_after=10)

        except BaseException:
            await ctx.send("Image not found.")

    @favourite.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def rename(self, ctx: commands.Context,
                     oldimageName: str, newimageName: str):
        '''
        renames an image in the favourites list
        '''
        tokens = oldimageName.split(":")  # split tokens

        fav = None

        if len(tokens) == 1:
            fav = collection("favouritensfw").find_one({"server": ctx.guild.id,
                              "imageID": tokens[0],
                                 "user": ctx.author.id,
                                 "category": ""})
        elif len(tokens) == 2:
            fav = collection("favouritensfw").find_one({"server": ctx.guild.id,
                              "imageID": tokens[1],
                                 "user": ctx.author.id,
                                 "category": tokens[0]})
        if fav:
            await self.unfavourite(ctx, oldimageName)
            await self.favourite(ctx, newimageName, fav["URL"])

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def favourites(self, ctx: commands.Context,
                         user: discord.Member = None, category: str = None):
        '''
        Lists all favourited images. Can specify another user, or a category.
        '''
        def construct(fav): return f"• **[{fav['imageID']}]({fav['URL']})**\n"

        if not user:
            user = ctx.author

        if category:
            favs = collection("favouritensfw").find({
                    "server": ctx.guild.id, "user": user.id, "category": category})
        else:
            favs = collection("favouritensfw").find({
                    "server": ctx.guild.id, "user": user.id})

        # Sort favourites by category

        categories = {}

        for fav in favs:
            try:
                categories[fav["category"]].append(fav)
            except BaseException:
                categories[fav["category"]] = [fav]

        embeds = [
            discord.Embed(
                title=f"All Favourites for {user.display_name} in {ctx.guild}")]
        category_count = 0

        for category in categories:
            s, s_prev = "", ""  # declare string variables
            embeds[-1].add_field(name=category if category else "Uncategorized",
                                 value="filler", inline=False)

            for item in categories[category]:
                s_prev = s
                s += construct(item)

                embeds[-1].set_field_at(category_count,
                                        name=embeds[-1].fields[category_count].name,
                                        value=s,
                                        inline=False)

                if len(s) > 1024:

                    embeds[-1].set_field_at(category_count,
                                            name=embeds[-1].fields[category_count].name,
                                            value=s_prev,
                                            inline=False)  # fall back to previous string set

                    if len(embeds[-1]) >= 6000:
                        embeds.append(
                            discord.Embed(
                                title=f"All Favourites for {user.display_name} in {ctx.guild} (cont.)"))
                        category_count = 0

                    else:
                        category_count += 1  # advance count

                    embeds[-1].add_field(
                        name=f'{category if category else "Uncategorized"} (cont.)', value="filler", inline=False)
                    s_prev, s = s, construct(item)  # rotate strings

            category_count += 1

        for e in embeds:
            await ctx.send(embed=e)
