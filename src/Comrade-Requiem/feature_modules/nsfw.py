from dis_snek.models.snek import (Scale, slash_command,
                                     OptionTypes, slash_option,
                                     SlashCommandChoice,
                                     ComponentCommand, InteractionContext,
                                     ComponentContext)
from dis_snek.models.discord import Button, ButtonStyles
from logger import log

from processors import gelbooru_api, e621_api


gelbooru_sessions = {}
genderbend_sessions = {}


async def e621_button_next(ctx: ComponentContext):
    # Disable the previous button
    await ctx.edit_origin(components=[])
    
    if ctx.channel.id not in genderbend_sessions:
        await ctx.channel.send(
            "Sorry, the session attached to this button has expired.",
            reply_to = ctx.message)
    
    session = genderbend_sessions[ctx.channel.id]
    
    if data := await e621_api.e621_get_next_post_data(session):
        embeds = [e621_api.e621_formatted_embed(post, session)
            for post in data["posts"]]
        
        next_button = Button(style=ButtonStyles.GREY, label="Next", emoji="🔽", custom_id="e621_next")
        await ctx.channel.send(embeds=embeds, components=[next_button])
    else:
        await ctx.send("No more posts.")


async def gb_button_next(ctx: ComponentContext):
    # Disable the previous button
    await ctx.edit_origin(components=[])
    
    if ctx.channel.id not in genderbend_sessions:
        await ctx.channel.send(
            "Sorry, the session attached to this button has expired.",
            reply_to = ctx.message)
    
    session = genderbend_sessions[ctx.channel.id]
    
    if data := await e621_api.gb_get_next_post_data(session):
        embeds = [e621_api.gb_formatted_embed(post, session)
            for post in data["posts"]]
        
        next_button = Button(style=ButtonStyles.GREY, label="Next", emoji="🔽", custom_id="gb_next")
        await ctx.channel.send(embeds=embeds, components=[next_button])
    else:
        await ctx.send("No more posts.")


async def hentai_button_next(ctx: ComponentContext):
    # Disable the previous button
    await ctx.edit_origin(components=[])
    
    if ctx.channel.id not in gelbooru_sessions:
        await ctx.channel.send(
            "Sorry, the session attached to this button has expired.",
            reply_to = ctx.message)
    
    session = gelbooru_sessions[ctx.channel.id]
    
    if data := await gelbooru_api.get_next_post_data(session):
        attrs = data["@attributes"]
        embeds = [gelbooru_api.formatted_embed(post, attrs, session)
            for post in data["post"]]
        
        next_button = Button(style=ButtonStyles.GREY, label="Next", emoji="🔽", custom_id="hentai_next")
        await ctx.channel.send(embeds=embeds, components=[next_button])
    else:
        await ctx.send("No more posts.")
 

class NSFW(Scale):
    @slash_command(name="hentai",
                   description="Retrieves a post from gelbooru.",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="tags", description="tags to search for",
                  opt_type=OptionTypes.STRING, required=False)
    @slash_option(name="count", description="Number of posts to return per message, default 1",
                  opt_type=OptionTypes.INTEGER, required=False,
                  min_value=1, max_value=20)
    @slash_option(name="sorting", description="Sorting method, default random",
                  opt_type=OptionTypes.STRING, choices=
                  [
                      SlashCommandChoice(name="random", value="random:0"),
                      SlashCommandChoice(name="highest score", value="score"),
                      SlashCommandChoice(name="most recent", value="id")
                  ], required=False)
    async def hentai(self, ctx: InteractionContext, tags: str = None, count: int = 1, sorting: str = "random:0"):
        await ctx.defer()
        if tags:
            # Clean up tags such that they're joined by +
            tags = "+".join(tags.split())
        
        # Save Session
        gelbooru_sessions[ctx.channel.id] = gelbooru_api.GelbooruSession(
            tags if tags else "", count, sorting, 0)
        
        if data := await gelbooru_api.get_next_post_data(gelbooru_sessions[ctx.channel.id]):
            attrs = data["@attributes"]
            embeds = [
                gelbooru_api.formatted_embed(post, attrs, gelbooru_sessions[ctx.channel.id])
                for post in data["post"]]
            
            video_urls = [
                post["file_url"] for post in data["post"]
                if ("webm" in post["file_url"] or "mp4" in post["file_url"]) ]
            
            next_button = Button(style=ButtonStyles.GREY, label="Next", emoji="🔽", custom_id="hentai_next")
            await ctx.send(
                embeds=embeds, components=[next_button],
                content="\n".join(video_urls) if video_urls else None)
        else:
            await ctx.send("No posts were found.")
            
            
    @slash_command(name="genderbend",
                   description="Retrieves a post from genderbend.me.",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="tags", description="tags to search for",
                  opt_type=OptionTypes.STRING, required=False)
    @slash_option(name="count", description="Number of posts to return per message, default 1",
                  opt_type=OptionTypes.INTEGER, required=False,
                  min_value=1, max_value=20)
    @slash_option(name="sorting", description="Sorting method, default random",
                  opt_type=OptionTypes.STRING, choices=
                  [
                      SlashCommandChoice(name="random", value="random"),
                      SlashCommandChoice(name="highest score", value="score"),
                      SlashCommandChoice(name="most recent", value="id")
                  ], required=False)
    async def genderbend(self, ctx: InteractionContext, tags: str = None, count: int = 1, sorting: str = "random"):
        await ctx.defer()
        if tags:
            # Clean up tags such that they're joined by +
            tags = "+".join(tags.split())
        
        # Save Session
        genderbend_sessions[ctx.channel.id] = e621_api.GBSession(
            tags if tags else "", count, sorting, 0)
        
        if data := await e621_api.gb_get_next_post_data(genderbend_sessions[ctx.channel.id]):
            embeds = [
                e621_api.gb_formatted_embed(post, genderbend_sessions[ctx.channel.id])
                for post in data["posts"]]
            
            next_button = Button(style=ButtonStyles.GREY, label="Next", emoji="🔽", custom_id="gb_next")
            await ctx.send(embeds=embeds, components=[next_button])
        else:
            await ctx.send("No posts were found.")
            
    @slash_command(name="e621",
                   description="Retrieves a post from e621.net.",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="tags", description="tags to search for",
                  opt_type=OptionTypes.STRING, required=False)
    @slash_option(name="count", description="Number of posts to return per message, default 1",
                  opt_type=OptionTypes.INTEGER, required=False,
                  min_value=1, max_value=20)
    @slash_option(name="sorting", description="Sorting method, default random",
                  opt_type=OptionTypes.STRING, choices=
                  [
                      SlashCommandChoice(name="random", value="random"),
                      SlashCommandChoice(name="highest score", value="score"),
                      SlashCommandChoice(name="most recent", value="id")
                  ], required=False)
    async def e621(self, ctx: InteractionContext, tags: str = None, count: int = 1, sorting: str = "random"):
        await ctx.defer()
        if tags:
            # Clean up tags such that they're joined by +
            tags = "+".join(tags.split())
        
        # Save Session
        genderbend_sessions[ctx.channel.id] = e621_api.GBSession(
            tags if tags else "", count, sorting, 0)
        
        if data := await e621_api.e621_get_next_post_data(genderbend_sessions[ctx.channel.id]):
            embeds = [
                e621_api.e621_formatted_embed(post, genderbend_sessions[ctx.channel.id])
                for post in data["posts"]]
            
            next_button = Button(style=ButtonStyles.GREY, label="Next", emoji="🔽", custom_id="e621_next")
            await ctx.send(embeds=embeds, components=[next_button])
        else:
            await ctx.send("No posts were found.")
        

def setup(bot):
    NSFW(bot)
    bot.add_component_callback(
        ComponentCommand(
            name="ComponentCallback::hentai_next",
            callback = hentai_button_next,
            listeners=["hentai_next"]
        )
    )
    bot.add_component_callback(
        ComponentCommand(
            name="ComponentCallback::gb_next",
            callback = gb_button_next,
            listeners=["gb_next"]
        )
    )
    bot.add_component_callback(
        ComponentCommand(
            name="ComponentCallback::e621_next",
            callback = e621_button_next,
            listeners=["e621_next"]
        )
    )
    log.info("Module nsfw.py loaded.")
