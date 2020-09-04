from utils.core_dependencies.utilities import *
import numpy as np
from numpy import log, log10, log1p, log2, logaddexp, logaddexp2, exp, exp2, sqrt, power, e, pi, sin, cos,tan,arcsin,arccos,arctan,arcsinh,arccosh,arctan2,radians,rad2deg,deg2rad,radians,sinc,sinh,tanh,angle

import matplotlib.pyplot as plt
import parser
import io


class Graphing(commands.Cog):
    '''
    Graphing Calcualtor Module
    '''
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def graph(self, ctx: commands.Context, function: str, xstart: int = -10, xend: int = 10):
        '''
        Graphs a single variable algebraic function in some domain.
        '''
        async with ctx.channel.typing():
            if "." in function:
                await ctx.send("Function rejected for invalid syntax.")
            else:
                function = re.sub(r"([0-9])([a-z])", r"\1*\2", function)
                function = function.replace("^", "**") # exponentiation

                stepsize = 500
                try:
                    D = xend-xstart
                    x = np.arange(xstart, xend, D/stepsize)

                    fnc = parser.expr(function).compile()
                    
                    arr = eval(fnc)

                    plt.plot(x, arr, label=function)

                    plt.title("Plot Requested by {}".format(ctx.author.name))
                    plt.ylabel("y")
                    plt.xlabel("x")
                    plt.legend()
                    plt.axhline(y=0, color='k')
                    plt.axvline(x=0, color='k')
                    plt.grid()
                    f = io.BytesIO()
                    plt.savefig(f, format="png")
                    f.seek(0)
                    plt.clf()

                    await ctx.send(file=discord.File(f, "graph.png"))

                except:
                    await ctx.send("Something went wrong with parsing. Try again.")