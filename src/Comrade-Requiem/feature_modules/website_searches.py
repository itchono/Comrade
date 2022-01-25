from dis_snek.models.snek import (Scale, slash_command, OptionTypes,
                                  InteractionContext, slash_option)
from dis_snek.models.discord import Embed, FlatUIColours
from dis_snek.ext.paginators import Paginator

import aiohttp
from bs4 import BeautifulSoup

import orjson

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
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
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
        
    # @slash_command(name="lyrics",
    #                description="Gets the lyrics of a song from Genius",
    #                scopes=[419214713252216848, 709954286376976425])
    # @slash_option(name="song", opt_type=OptionTypes.STRING,
    #               description="Name of the song", required=True)
    async def lyrics(self, ctx: InteractionContext, song: str):
        '''
        This function gets the lyrics of the song specified by (song)
        by scraping Genius
        '''
        await ctx.defer(ephemeral=True)
        
        song = song.replace(" ", "%20")
        
        query_url = f"https://genius.com/search?q={song}"
        
        print(query_url)
        
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            async with session.get(query_url) as response:
                html = await response.text()
        # If response failed, return error
        if response.status != 200:
            await ctx.send(f"No results found. (Error: {response.status})")
            return     
        
        # Otherwise, Parse response
        soup = BeautifulSoup(html, "html.parser")
        
        # Export the html to a file
        with open("lyrics.html", "w") as f:
            f.write(html)

        # Find div with property ng-if = $ctrl.section.hits.length > 0
        top_result = soup.find("div", attrs={"ng-if": "$ctrl.section.hits.length > 0"})
        # Find ahref with class "mini_card"
        ahref = top_result.find("a", class_="mini_card")
        song_page_url = ahref["href"]
        
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            async with session.get(song_page_url) as response:
                html = await response.text()
        # If response failed, return error
        if response.status != 200:
            await ctx.send(f"Could not retrieve song (Error: {response.status} for URL {song_page_url})")
            return
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Find all divs with property data-lyrics-container="true"
        lyric_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})
        # Extract and merge text
        lyrics = "".join([div.text for div in lyric_divs])
        
        paginator = Paginator.create_from_text(ctx.bot, lyrics, timeout=120)
        
        await paginator.send(ctx)
            

def setup(bot):
    WebSearches(bot)
    log.info("Module website_searches.py loaded.")
