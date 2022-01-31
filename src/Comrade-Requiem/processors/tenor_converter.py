# Converts tenor links to gifs
import aiohttp
import bs4
import asyncio

async def get_tenor_gif(tenor_link: str) -> str:
    '''
    Take in a tenor link formatted like the example:
    https://tenor.com/view/kotori-kotori-itsuka-itsuka-kotori-gif-23001734

    And return a link to the HD GIF
    '''
    if not tenor_link.startswith("https://tenor.com/view/"):
        raise ValueError("Invalid tenor link")

    async with aiohttp.ClientSession() as session:
        async with session.get(tenor_link) as resp:
            html = await resp.text()

    soup = bs4.BeautifulSoup(html, "html.parser")

    # Find all <img> tags with links ending in .gif
    img_tags = soup.find_all("img", src=lambda x: x and x.endswith(".gif"))

    # Get src of the first one
    return img_tags[0]["src"]

if __name__ == "__main__":
    url = input("Enter a tenor link: ")
    print(asyncio.run(get_tenor_gif(url)))
