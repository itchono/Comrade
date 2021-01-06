'''
This module generates text using a Markov chain algorithm.
Text generation is based off of what each user has said in
a given text channel.
Models are cached using a LRU (Least-recently-used) system,
which makes it so that previously generated models can be
used again
'''
import discord
from discord.ext import commands
from collections import Counter, defaultdict  # markov
from async_lru import alru_cache
import random
import typing
import time
from config import cfg
from client import client as bot
from utils.echo import echo

MODEL_LEN = 3  # Length of text generation model


async def member_msgs(channel_id: int, member_id: int, depth: int):
    '''
    Iterator yielding a certain number of messages in a channel for a user
    This is different from discord.py's implementation, which only allows you
    to set a limit for total messages scanned
    '''
    num_msgs = 0

    # Define iterator to fetch messages
    baseline_iter = (bot.get_channel(channel_id).history(
        limit=None)).filter(lambda m: m.author.id == member_id)

    while num_msgs < depth:
        try:
            yield await baseline_iter.next()
        except discord.NoMoreItems:
            break
        num_msgs += 1
    # try/except used to catch if the iterator runs out of items
    # For example, your channel only has 10 messages, and depth = 100


@alru_cache(maxsize=int(cfg["Performance"]["text-model-limit"]))
async def text_model(channel_id: int, member_id: int):
    '''
    Returns text model for a given user in a given channel.
    Sped up using a LRU cache.
    '''
    msgs = [m.content async for m in member_msgs(
        channel_id, member_id, 100)]

    text = " ".join(msgs)

    # calls a counter object in the event that an index doesn't exist
    model = defaultdict(Counter)

    for i in range(len(text) - MODEL_LEN):
        model[text[i:(i + MODEL_LEN)]][text[i + MODEL_LEN]] += 1

    return model


def generate_text(model, num_chars):
    '''
    Generates num_chars characters of text given a character model
    '''
    if len(model) == 0:
        return None
    selector = random.choice(list(model.keys()))  # select a starting character

    output = selector

    for i in range(num_chars):
        if len(model[selector]) == 0:
            break
        # generate next character
        output += random.choices(list(model[selector]),
                                 model[selector].values())[0]
        selector = output[-MODEL_LEN:]

    return output


class Textgen(commands.Cog):
    '''
    Text generator, based off of what each user has said in
    a given text channel.
    '''

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.guild_only()
    async def gen(self, ctx: commands.Context,
                  channel: typing.Optional[discord.TextChannel],
                  *, member: discord.Member = None):
        '''
        Generates text from model of a user and outputs it.
        Text is based on the user's 100 most recent messages in
        the specified channel.

        Please note that the first runthrough takes a bit longer,
        as it must cache all of the messages sent by the user.
        '''
        if not member:
            member = ctx.author
        if not channel:
            channel = ctx.channel

        m = None
        # We want to check if our model is cached
        if not [channel.id, member.id] in list(text_model._cache.keys()):
            t_start = time.perf_counter()
            m = await ctx.send(
                f"Building model for {member.display_name}..."
                "\n(This may take a while, but the "
                "model will be cached after.)")
            await ctx.trigger_typing()

        model: dict = await text_model(channel.id, member.id)

        if m:
            t_ = time.perf_counter() - t_start
            await m.delete()
            await ctx.send(
                content=(f"Model for {member.display_name} "
                         f"built in {round(t_)} s"),
                delete_after=5)

        text = generate_text(model, 200)

        if text:
            await echo(ctx, member, text)
        else:
            await ctx.send(f"{member.display_name} has not posted any "
                           "messages in this channel,"
                           " and so I cannot generate any text for them.")

    @commands.command()
    @commands.guild_only()
    async def buildmodel(self, ctx: commands.Context,
                         channel: typing.Optional[discord.TextChannel],
                         *, member: discord.Member = None):
        '''
        Builds the text generation model for a given user ahead of time,
        so that you don't need to wait as long when you run the gen command
        '''
        if not member:
            member = ctx.author
        if not channel:
            channel = ctx.channel

        t_start = time.perf_counter()
        await ctx.trigger_typing()
        await text_model(channel.id, member.id)
        t_ = time.perf_counter() - t_start
        await ctx.send(
            content=f"Model for {member.display_name} built in {round(t_)} s",
            delete_after=5)

    @commands.command()
    @commands.guild_only()
    async def cachestatus(self, ctx: commands.Context):
        '''
        Shows status of LRU cache
        '''
        await ctx.send(text_model.cache_info())

# TODO: Background generation of models?
