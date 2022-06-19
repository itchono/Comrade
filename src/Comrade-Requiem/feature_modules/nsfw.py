from dis_snek.models.snek import (Scale, slash_command,
                                  OptionTypes, slash_option,
                                  SlashCommandChoice,
                                  ComponentCommand, InteractionContext,
                                  ComponentContext)
from dis_snek.models.discord import Button, ButtonStyles
from logger import log

from processors import gelbooru_api, e621_api, nhentai_processor


gelbooru_sessions = {}
genderbend_sessions = {}
nhentai_sessions = {}
nsearch_sessions = {}


async def e621_button_next(ctx: ComponentContext):
    # Disable the previous button
    await ctx.edit_origin(components=[])

    if ctx.channel.id not in genderbend_sessions:
        await ctx.channel.send(
            "Sorry, the session attached to this button has expired.",
            reply_to=ctx.message)

    session = genderbend_sessions[ctx.channel.id]

    if data := await e621_api.e621_get_next_post_data(session):
        embeds = [e621_api.e621_formatted_embed(post, session)
                  for post in data["posts"]]

        next_button = Button(style=ButtonStyles.GREY,
                             label="Next", emoji="🔽", custom_id="e621_next")
        await ctx.channel.send(embeds=embeds, components=[next_button])
    else:
        await ctx.send("No more posts.")


async def gb_button_next(ctx: ComponentContext):
    # Disable the previous button
    await ctx.edit_origin(components=[])

    if ctx.channel.id not in genderbend_sessions:
        await ctx.channel.send(
            "Sorry, the session attached to this button has expired.",
            reply_to=ctx.message)

    session = genderbend_sessions[ctx.channel.id]

    if data := await e621_api.gb_get_next_post_data(session):
        embeds = [e621_api.gb_formatted_embed(post, session)
                  for post in data["posts"]]

        next_button = Button(style=ButtonStyles.GREY,
                             label="Next", emoji="🔽", custom_id="gb_next")
        await ctx.channel.send(embeds=embeds, components=[next_button])
    else:
        await ctx.send("No more posts.")


async def hentai_button_next(ctx: ComponentContext):
    # Disable the previous button
    await ctx.edit_origin(components=[])

    if ctx.channel.id not in gelbooru_sessions:
        await ctx.channel.send(
            "Sorry, the session attached to this button has expired.",
            reply_to=ctx.message)

    session = gelbooru_sessions[ctx.channel.id]

    if data := await gelbooru_api.get_next_post_data(session):
        attrs = data["@attributes"]
        embeds = [gelbooru_api.formatted_embed(post, attrs, session)
                  for post in data["post"]]

        next_button = Button(style=ButtonStyles.GREY,
                             label="Next", emoji="🔽", custom_id="hentai_next")
        await ctx.channel.send(embeds=embeds, components=[next_button])
    else:
        await ctx.send("No more posts.")


async def nhentai_button_next(ctx: ComponentContext):
    # Disable the previous button
    await ctx.edit_origin(components=[])

    if ctx.channel.id not in nhentai_sessions:
        await ctx.channel.send(
            "Sorry, the session attached to this button has expired.",
            reply_to=ctx.message)

    nhentai_sessions[ctx.channel.id].current_page_number += 1
    session = nhentai_sessions[ctx.channel.id]

    if session.current_page_number > session.length:
        await ctx.send("No more pages.")
        return

    next_button = Button(style=ButtonStyles.GREY,
                         label="Next", emoji="🔽", custom_id="nhentai_next")

    # Simply get the URL of the image for the next message
    await ctx.channel.send(session.pages[session.current_page_number].direct_url,
                           components=[next_button])


async def nsearch_button_next(ctx: ComponentContext):
    if ctx.channel.id not in nsearch_sessions:
        await ctx.channel.send(
            "Sorry, the session attached to this button has expired.",
            reply_to=ctx.message)

    session = nsearch_sessions[ctx.channel.id]

    # Advance cursor by one position
    current_pg_num_results = len(session.cached_pages[session.page_cursor])

    if session.page_subcursor + 1 >= current_pg_num_results:
        session.page_cursor += 1
        session.page_subcursor = 0

        if session.page_cursor >= session.num_pages:
            await ctx.send("No more pages.")
            return
    else:
        session.page_subcursor += 1

    # Get first page result
    nhentai_session = nhentai_processor.nhentai_search_cursor(session)
    embed = nhentai_processor.cover_page_embed(nhentai_session)

    page_len = len(session.cached_pages[session.page_cursor])
    position_indicator = f"Results Page: {session.page_cursor+1}/{session.num_pages}; Result: {session.page_subcursor+1}/{page_len}"

    await ctx.edit_origin(content=position_indicator, embeds=[embed])

    # update session
    nsearch_sessions[ctx.channel.id] = session


async def nsearch_button_prev(ctx: ComponentContext):
    if ctx.channel.id not in nsearch_sessions:
        await ctx.channel.send(
            "Sorry, the session attached to this button has expired.",
            reply_to=ctx.message)

    session = nsearch_sessions[ctx.channel.id]

    # Advance cursor by one position
    current_pg_num_results = len(session.cached_pages[session.page_cursor])

    if session.page_subcursor == 0:
        if session.page_cursor == 0:
            await ctx.send("This is the first page!.")
            return

        session.page_cursor -= 1

        pg_num_results = len(session.cached_pages[session.page_cursor])
        session.page_subcursor = pg_num_results - 1
    else:
        session.page_subcursor -= 1

    # Get first page result
    nhentai_session = nhentai_processor.nhentai_search_cursor(session)
    embed = nhentai_processor.cover_page_embed(nhentai_session)

    page_len = len(session.cached_pages[session.page_cursor])
    position_indicator = f"Results Page: {session.page_cursor+1}/{session.num_pages}; Result: {session.page_subcursor+1}/{page_len}"

    await ctx.edit_origin(content=position_indicator, embeds=[embed])

    # update session
    nsearch_sessions[ctx.channel.id] = session


async def nsearch_button_exec(ctx: ComponentContext):
    if ctx.channel.id not in nsearch_sessions:
        await ctx.channel.send(
            "Sorry, the session attached to this button has expired.",
            reply_to=ctx.message)

    search_session = nsearch_sessions[ctx.channel.id]
    session = nhentai_processor.nhentai_search_cursor(search_session)
    nhentai_sessions[ctx.channel.id] = session

    next_button = Button(style=ButtonStyles.GREY,
                         label="Next", emoji="🔽", custom_id="nhentai_next")
    embed = nhentai_processor.cover_page_embed(session)

    await ctx.send(
        embeds=[embed], components=[next_button])


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
                  opt_type=OptionTypes.STRING, choices=[
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
                gelbooru_api.formatted_embed(
                    post, attrs, gelbooru_sessions[ctx.channel.id])
                for post in data["post"]]

            video_urls = [
                post["file_url"] for post in data["post"]
                if ("webm" in post["file_url"] or "mp4" in post["file_url"])]

            next_button = Button(
                style=ButtonStyles.GREY, label="Next", emoji="🔽", custom_id="hentai_next")
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
                  opt_type=OptionTypes.STRING, choices=[
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
                e621_api.gb_formatted_embed(
                    post, genderbend_sessions[ctx.channel.id])
                for post in data["posts"]]

            next_button = Button(style=ButtonStyles.GREY,
                                 label="Next", emoji="🔽", custom_id="gb_next")
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
                  opt_type=OptionTypes.STRING, choices=[
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
                e621_api.e621_formatted_embed(
                    post, genderbend_sessions[ctx.channel.id])
                for post in data["posts"]]

            next_button = Button(style=ButtonStyles.GREY,
                                 label="Next", emoji="🔽", custom_id="e621_next")
            await ctx.send(embeds=embeds, components=[next_button])
        else:
            await ctx.send("No posts were found.")

    @slash_command(name="nhentai",
                   description="Retrieves a gallery from NHentai.",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="gallery_id", description="ID of the gallery.",
                  opt_type=OptionTypes.INTEGER, required=True)
    async def nhentai(self, ctx: InteractionContext, gallery_id: int):
        await ctx.defer()

        # Save Session
        session = nhentai_processor.initialize_session(gallery_id)
        nhentai_sessions[ctx.channel.id] = session

        if not session.exists:
            await ctx.send(f"No result could be returned. Error: {session.error}")
            return

        next_button = Button(style=ButtonStyles.GREY,
                             label="Next", emoji="🔽", custom_id="nhentai_next")
        embed = nhentai_processor.cover_page_embed(session)

        await ctx.send(
            embeds=[embed], components=[next_button])

    @slash_command(name="nsearch",
                   description="Searches NHentai for a given query.",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="query", description="tags to search for",
                  opt_type=OptionTypes.STRING, required=False)
    @slash_option(name="sorting", description="Sorting method, default popular",
                  opt_type=OptionTypes.STRING, choices=[
                      SlashCommandChoice(name="recent", value="recent"),
                      SlashCommandChoice(name="popular", value="popular")
                  ], required=False)
    async def nsearch(self, ctx: InteractionContext, query: str = None, sorting: str = "popular"):
        await ctx.defer()

        # Save Session
        session = nhentai_processor.nhentai_search(query, sorting)
        nsearch_sessions[ctx.channel.id] = session

        if session.num_results == 0:
            await ctx.send(f"No result could be returned. Error: {session.error}")
            return

        prev_button = Button(style=ButtonStyles.GREY,
                             label="Prev Result", emoji="◀", custom_id="nsearch_prev")
        exec_button = Button(style=ButtonStyles.GREY,
                             label="View Gallery", emoji="🔽", custom_id="nsearch_exec")
        next_button = Button(style=ButtonStyles.GREY,
                             label="Next Result", emoji="▶", custom_id="nsearch_next")

        # Get first page result
        nhentai_session = nhentai_processor.nhentai_search_cursor(session)
        embed = nhentai_processor.cover_page_embed(nhentai_session)

        page_len = len(session.cached_pages[session.page_cursor])
        position_indicator = f"Results Page: 1/{session.num_pages}; Result: 1/{page_len}"

        await ctx.send(position_indicator,
                       embeds=[embed], components=[prev_button, exec_button, next_button])


def setup(bot):
    NSFW(bot)
    bot.add_component_callback(
        ComponentCommand(
            name="ComponentCallback::hentai_next",
            callback=hentai_button_next,
            listeners=["hentai_next"]
        )
    )
    bot.add_component_callback(
        ComponentCommand(
            name="ComponentCallback::gb_next",
            callback=gb_button_next,
            listeners=["gb_next"]
        )
    )
    bot.add_component_callback(
        ComponentCommand(
            name="ComponentCallback::e621_next",
            callback=e621_button_next,
            listeners=["e621_next"]
        )
    )
    bot.add_component_callback(
        ComponentCommand(
            name="ComponentCallback::nhentai_next",
            callback=nhentai_button_next,
            listeners=["nhentai_next"]
        )
    )
    bot.add_component_callback(
        ComponentCommand(
            name="ComponentCallback::nsearch_next",
            callback=nsearch_button_next,
            listeners=["nsearch_next"]
        )
    )
    bot.add_component_callback(
        ComponentCommand(
            name="ComponentCallback::nsearch_prev",
            callback=nsearch_button_prev,
            listeners=["nsearch_prev"]
        )
    )
    bot.add_component_callback(
        ComponentCommand(
            name="ComponentCallback::nsearch_exec",
            callback=nsearch_button_exec,
            listeners=["nsearch_exec"]
        )
    )
    log.info("Module nsfw.py loaded.")
