# API for e621.net or genderbender.me

import aiohttp
from dataclasses import dataclass
import orjson
from dis_snek.models.discord_objects.embed import Embed

GB_BASE = "https://genderbend.me/posts.json?"
E621_BASE = "https://e621.net/posts.json?"

@dataclass
class GBSession:
    # User inputs
    tags: str
    count: int  # Number of posts per msg
    sorting: str
    # Internal data store and tracker
    pid: int  # which page to fetch
    post_data: dict = None
    
    
async def gb_get_next_post_data(session: GBSession) -> dict:
    # Gets the next post from a session and post attibutes
    
    # Assemble url to query genderbender API
    url_ext = f"&tags={session.tags}+order:{session.sorting}&limit={session.count}&page={session.pid}"
    
    print(GB_BASE + url_ext)
    
    # Advance page by 1
    session.pid += 1
    
    # Make request to gelbooru API
    async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
        async with session.get(GB_BASE+url_ext) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                raise Exception(f"Error: {resp.status}")
            
async def e621_get_next_post_data(session: GBSession) -> dict:
    # Gets the next post from a session and post attibutes
    
    # Assemble url to query genderbender API
    url_ext = f"&tags={session.tags}+order:{session.sorting}&limit={session.count}&page={session.pid}"
    
    print(E621_BASE + url_ext)
    
    # Advance page by 1
    session.pid += 1
    
    # Make request to gelbooru API
    async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
        async with session.get(GB_BASE+url_ext) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                raise Exception(f"Error: {resp.status}")
            
def e621_formatted_embed(post: dict, session: GBSession) -> Embed:
    # Formats a post into an embed
    embed = Embed(title=session.tags + " (Click for source)",
                  url = f"https://e621.net/posts/{post['id']}",
                  color=0xfecbed,
                  image=post["file"]["url"])
    embed.set_author(name=f"Genderbender Post ({session.pid})",
                        icon_url="https://e621.net/favicon.ico")
    embed.add_field(name="id", value=post["id"], inline=True)
    embed.add_field(name="Score", value=post["score"]["total"], inline=True)
    
    return embed           
            
def gb_formatted_embed(post: dict, session: GBSession) -> Embed:
    # Formats a post into an embed
    embed = Embed(title=session.tags + " (Click for source)",
                  url = f"https://genderbend.me/posts/{post['id']}",
                  color=0xfecbed,
                  image=post["file"]["url"])
    embed.set_author(name=f"Genderbender Post ({session.pid})",
                        icon_url="https://genderbend.me/favicon.ico")
    embed.add_field(name="id", value=post["id"], inline=True)
    embed.add_field(name="Score", value=post["score"]["total"], inline=True)
    
    return embed