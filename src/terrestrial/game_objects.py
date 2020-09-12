import numpy as np

'''
y,x  coordinate system
'''

MAP_SIZE = (20, 50)

RENDER_SIZE = (9, 9)

CAMERA_TETHER = 1 # distance at which camera frame will start moving

directions = delta = {"LEFT":[0, -1], "RIGHT":[0, 1], "UP":[-1, 0], "DOWN":[1, 0]}
BLOCKS = {0:"🟦", 1:"🟩", 2:"🟫", 3:"🌳", 4:"🏠", 5:"💎", 6:"🔥", 7:"⬛", 98:"😳", 99:"⛏"}


def numround(LIMIT, position):
    for i in range(len(position)):
        if position[i] < 0: position[i] = 0
        elif position[i] >= LIMIT[i]: position[i] = LIMIT[i] - 1

def TL2BL(position):
    # converts to bottom-left coordinates (np array)
    return np.array([MAP_SIZE[0]-position[0], position[1]])

class Game():
    def __init__(self, seed=0):
        self.player_pos = np.array((5, 25))
        self.camera_pos = self.player_pos - (np.array(RENDER_SIZE)/2).astype(int)
        # Camera is centered around player

        self.state = 0 #😳

        self.seed = seed
        # terrain generation seed

        self.map = np.zeros(MAP_SIZE)

        self.generate_terrain()

        self.moveplayer("UP", 0) # initialize player to valid position

        

    # coordinates of bounding points for the renderer
    @property
    def LEFT(self): return self.camera_pos[1]
    @property
    def RIGHT(self): return self.camera_pos[1] + RENDER_SIZE[1] - 1
    @property
    def TOP(self): return self.camera_pos[0]
    @property
    def BOTTOM(self): return self.camera_pos[0] + RENDER_SIZE[0] - 1

    @property
    def frame(self):
        '''
        return a np array as the frame [FOR rendering]
        '''
        retmap = np.copy(self.map[self.TOP:self.BOTTOM+1, self.LEFT:self.RIGHT+1])
        retmap[self.player_pos[0]-self.TOP, self.player_pos[1]-self.LEFT] = 98 + self.state # render the player
        
        return retmap

    @property
    def describe(self):
        '''
        Add flavour text
        '''
        return f"\nx = {self.position[1]}, y = {self.position[0]}\nStanding On: {BLOCKS[self.tile_at_player]}" # player position update
    
    @property
    def rendered(self): return "\n".join(["".join([BLOCKS[sq] for sq in row]) for row in self.frame])

    @property
    def position(self): return TL2BL(self.player_pos)

    def action(self):
        '''
        Performs an action
        '''
        self.state = 1-self.state
    @property
    def tile_at_player(self):
        return self.map[self.player_pos[0], self.player_pos[1]]
    
    def generate_terrain(self):
        '''
        Generates terrain for the map
        '''
        # random.seed(self.seed) # seed random

        rng = np.random.default_rng(self.seed)

        LOWEST_TERRAIN = 11
        HIGHEST_TERRAIN = 13

        heightmap = ((HIGHEST_TERRAIN - LOWEST_TERRAIN) * rng.random((MAP_SIZE[1],)) + LOWEST_TERRAIN + 1).astype(int)

        NUM_TREES = int(MAP_SIZE[1]/3)

        tree_locations = (MAP_SIZE[1] * rng.random((NUM_TREES,)) + 1).astype(int)

        for i in range(MAP_SIZE[1]):
            self.map[MAP_SIZE[0]-heightmap[i]:, i].fill(2)# fill dirt
            self.map[MAP_SIZE[0]-heightmap[i]: MAP_SIZE[0]-heightmap[i] + 2, i].fill(1) # fill grass
            if i in tree_locations: self.map[MAP_SIZE[0]-heightmap[i]-1][i] = 3

    def frameshift(self, direction, num_steps = 1):
        '''
        Shifts the frame a number of squares in the direction specified
        '''
        self.camera_pos += num_steps * np.array(directions[direction])
        numround(MAP_SIZE, self.camera_pos)

    def moveplayer(self, direction, num_steps = 1):
        '''
        Moves the player
        '''
        self.player_pos += num_steps * np.array(directions[direction])
        numround(MAP_SIZE, self.player_pos)

        # camera pushing
        if self.RIGHT - self.player_pos[1] < CAMERA_TETHER: self.frameshift("RIGHT", num_steps)
        elif self.player_pos[1] - self.LEFT < CAMERA_TETHER: self.frameshift("LEFT", num_steps)
        elif self.BOTTOM - self.player_pos[0] < CAMERA_TETHER: self.frameshift("DOWN", num_steps)
        elif self.player_pos[0] - self.TOP < CAMERA_TETHER: self.frameshift("UP", num_steps)

        # position checking
        if self.tile_at_player == 0: self.moveplayer("DOWN")
        elif self.tile_at_player == 2 and self.state == 0: self.moveplayer(direction, -1)

        # mining
        if self.state == 1: self.map[self.player_pos[0], self.player_pos[1]] = 7