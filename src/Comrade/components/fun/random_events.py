import discord
from discord.ext import commands

from collections import Counter

import random


class RandomEvents(commands.Cog):
    '''
    Random event
    '''
    probabilities: dict = {"nameswap": 1, "rickroll": 1, "nothing": 998}

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.lastroll = []

    # random.choices from these elements

    @classmethod
    def roll():
        choice = random.choices(*zip(*RandomEvents.probabilities.items()))[0]
