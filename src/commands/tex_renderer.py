import discord
from discord.ext import commands
import io

from matplotlib import pyplot as plt
import matplotlib as mpl

class TexRender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tex(self, ctx:commands.Context, *, text):
        '''
        Renders a LaTeX equation.
        '''
        await ctx.trigger_typing()

        fig, ax = plt.subplots()

        plt.axis('off')

        mpl.rcParams['mathtext.fontset'] = "cm"

        L = len(text) if len(text) >= 4 else 4
        S = int(630/L)-12
        if S < 20: S = 20

        ax.text(0.5, 0.5, f"${text}$", size=S, ha='center', va='center')

        f = io.BytesIO()
        plt.savefig(f, format="png")
        f.seek(0)
        plt.clf()

        await ctx.send(file=discord.File(f, "renderedtex.png"))