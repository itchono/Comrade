'''
Just an idea.
'''

import numpy as np

## Not implemented yet

BLOCKS = {0: "🟦", 1: "🟩", 2: "🟫", 3: "🌳", 4: "🏠",
          5: "💎", 6: "🔥", 7: "⬛", 98: "😳", 99: "⛏"}


class SnakeandLaddersGame():
    def __init__(self):
        self.map = np.zeros((10, 10))

    @property
    def rendered(self):
        return "\n".join(
            ["".join([BLOCKS[sq] for sq in row]) for row in self.frame])

    def start_game(self, num_players):
        pass
