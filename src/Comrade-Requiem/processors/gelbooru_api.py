# API for Gelbooru

import aiohttp
from dataclasses import dataclass
import orjson
from dis_snek.models.discord import Embed

URL_BASE = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1"
# Base URL for Gelbooru API

@dataclass
class GelbooruSession:
    # User inputs
    tags: str
    count: int  # Number of posts per msg
    sorting: str
    # Internal data store and tracker
    pid: int  # which page to fetch
    post_data: dict = None


async def get_next_post_data(session: GelbooruSession) -> dict:
    # Gets the next post from a session and post attibutes
    
    # Assemble url to query gelbooru API
    url_ext = f"&tags={session.tags}+sort:{session.sorting}&limit={session.count}&pid={session.pid}"
    
    # Advance page by 1
    session.pid += 1
    
    # Make request to gelbooru API
    async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
        async with session.get(URL_BASE+url_ext) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                raise Exception(f"Error: {resp.status}")


def formatted_embed(post: dict, attrs: dict, session: GelbooruSession) -> Embed:
    # Formats a post into an embed
    embed = Embed(title=session.tags + " (Click for source)",
                  url = f"https://gelbooru.com/index.php?page=post&s=view&id={post['id']}",
                  color=0xfecbed,
                  image=post["file_url"])
    embed.set_footer(text=post["tags"])
    embed.set_author(name=f"Gelbooru Post ({session.pid})",
                        icon_url="https://gelbooru.com/favicon.ico")
    embed.add_field(name="id", value=post["id"], inline=True)
    embed.add_field(name="Score", value=post["score"], inline=True)
    embed.add_field(name="Rating", value=post["rating"], inline=True)
    embed.add_field(name="Hit Count", value=attrs["count"], inline=True)
    
    return embed
