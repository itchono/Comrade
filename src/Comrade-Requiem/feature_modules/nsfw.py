from dis_snek.models.scale import Scale
from dis_snek.models.application_commands import (slash_command,
                                                  OptionTypes, slash_option,
                                                  SlashCommandChoice,
                                                  ComponentCommand)
from dis_snek.models.context import InteractionContext, ComponentContext, Context
from dis_snek.models.discord_objects.embed import Embed
from dis_snek.models.discord_objects.components import Button
from dis_snek.models.enums import ButtonStyles
from logger import log
import aiohttp
from dataclasses import dataclass


@dataclass
class HentaiSession:
    tags: str
    count: int
    sorting: str
    page: int


hentai_sessions = {}

URL_BASE = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1"
# Base URL for Gelbooru API


async def get_post_embeds(ctx: Context, tags: str, count: int, sorting: str, page: int = 0) -> list[Embed]:
    embeds = []
    
    # Assemble url to query gelbooru API
    url_ext = f"&tags={tags}+sort:{sorting}&limit={count}&pid={page}" if tags \
        else f"&tags=sort:{sorting}&limit={count}&pid={page}"
    
    print(URL_BASE+url_ext)
    
    # Make request to gelbooru API
    async with aiohttp.ClientSession() as session:
        async with session.get(URL_BASE+url_ext) as resp:
            if resp.status == 200:
                data = await resp.json()
                if not data:
                    await ctx.send("No results found")
            else:
                await ctx.send(f"Error: {resp.status}")
    
    # Get each post, a dict which contains the attributes of the post
    attrs = data["@attributes"]
    for post in data["post"]:
        # Construct the embed
        embed = Embed(title=tags if tags else "*",
                      url = f"https://gelbooru.com/index.php?page=post&s=view&id={post['id']}",
                      color=0xfecbed,
                      image=post["file_url"])
        embed.set_footer(text=post["tags"])
        embed.set_author(name=f"Hentai ({page+1})",
                         icon_url=ctx.author.avatar.url)
        embed.add_field(name="id", value=post["id"], inline=True)
        embed.add_field(name="Score", value=post["score"], inline=True)
        embed.add_field(name="Hit Count", value=attrs["count"], inline=True)
        
        embeds.append(embed)
    return embeds


async def hentai_button_next(ctx: ComponentContext):
    # Disable the previous button
    await ctx.edit_origin(components=[])
    
    if ctx.channel.id not in hentai_sessions:
        await ctx.channel.send(
            "Sorry, the session attached to this button has expired.",
            reply_to = ctx.message)
    
    # Update the page number in the session
    hentai_sessions[ctx.channel.id].page += 1
    session = hentai_sessions[ctx.channel.id]
    
    embeds = await get_post_embeds(ctx, session.tags, session.count,
                                   session.sorting, session.page)
    
    next_button = Button(style=ButtonStyles.GREY, label="Next", emoji="🔽", custom_id="hentai_next")
    await ctx.channel.send(embeds=embeds, components=[next_button])
 

class NSFW(Scale):
    @slash_command(name="hentai",
                   description="nice",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="tags", description="tags to search for",
                  opt_type=OptionTypes.STRING, required=False)
    @slash_option(name="count", description="Number of posts to return, default 1",
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
        if embeds := await get_post_embeds(ctx, tags, count, sorting):
            next_button = Button(style=ButtonStyles.GREY, label="Next", emoji="🔽", custom_id="hentai_next")
            await ctx.send(embeds=embeds, components=[next_button])
            
            # Save Session
            hentai_sessions[ctx.channel.id] = HentaiSession(tags, count, sorting, 0)
        

def setup(bot):
    NSFW(bot)
    bot.add_component_callback(
        ComponentCommand(
            name="ComponentCallback::hentai_next",
            callback = hentai_button_next,
            listeners=["hentai_next"]
        )
    )
    log.info("Module nsfw.py loaded.")
