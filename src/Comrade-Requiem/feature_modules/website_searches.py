from dis_snek.models.scale import Scale
from dis_snek.models.application_commands import (slash_command, OptionTypes,
                                                  slash_option)
from dis_snek.models.context import InteractionContext
from dis_snek.models.discord_objects.embed import Embed
from dis_snek.models.paginators import Paginator
from dis_snek.models.color import FlatUIColours

import aiohttp
from bs4 import BeautifulSoup

from logger import log


class WebSearches(Scale):
    @slash_command(name="define",
                   description="Defines a term from Urban Dictionary",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="term", opt_type=OptionTypes.STRING,
                  description="the term to define", required=True)
    async def define_urban(self, ctx: InteractionContext, term: str):

        # Defer the interaction to give processing time
        await ctx.defer()

        # Process term into URL encoded string
        term = term.replace(" ", "%20")

        # Generate request to urban dictionary
        url = f"https://www.urbandictionary.com/define.php?term={term}"

        # Make request
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()

        # If response failed, return error
        if response.status != 200:
            await ctx.send(f"No results found. (Error: {response.status})")
            return

        # Otherwise, Parse response
        soup = BeautifulSoup(html, "html.parser")

        # Find divs with class "definition"
        definitions = soup.find_all("div", class_="definition")

        embeds = []  # embeds to store the definitions

        # In each div, find divs with classes "meaning" and "example"
        for i in range(len(definitions)):
            meaning = definitions[i].find("div", class_="meaning")
            example = definitions[i].find("div", class_="example")

            # If either of these are not found, skip
            if not meaning or not example:
                continue

            # Otherwise, send the definition
            embed = Embed(title=term, url=url, color=FlatUIColours.MIDNIGHTBLUE)
            embed.add_field(name="Definition", value=meaning.text)
            embed.add_field(name="Example", value=example.text)
            embed.set_footer(text="Powered by Urban Dictionary | "
                             f"({i + 1}/{len(definitions)})")
            embeds.append(embed)

        paginator = Paginator.create_from_embeds(ctx.bot, *embeds, timeout=120)
        paginator.show_callback_button = False
        await paginator.send(ctx)


def setup(bot):
    WebSearches(bot)
    log.info("Module website_searches.py loaded.")
