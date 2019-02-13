import random
import curses

import q

BLOCKS = {
#   ([0,1,1],
#    [1,1,0]),

#   ([1,1,0],
#    [0,1,1]),

#"T": [
#        ([1,1,1],
#         [0,1,0]),

#        ([0,1],
#         [1,1],
#         [0,1]),

#        ([0,1,0],
#         [1,1,1]),

#        ([1,0],
#         [1,1],
#         [1,0])
#     ],

#    ([0,1],
#     [0,1],
#     [1,1]),

#"L": [
#        ([1,0],
#         [1,0],
#         [1,1]),

#        ([1,1,1],
#         [1,0,0]),

#        ([1,1],
#         [0,1],
#         [0,1]),

#        ([0,0,1],
#         [1,1,1])
#     ]

"I": [
        ([1],
         [1],
         [1],
         [1]),

        ([[1,1,1,1]])
      ]

}

COLOURS = [
    curses.COLOR_RED,
    curses.COLOR_BLUE,
    curses.COLOR_GREEN,
    curses.COLOR_YELLOW
]

class Block:

    def __init__(self):
        self.shape = BLOCKS[random.choice(list(BLOCKS))][random.randint(0,1)]
        self.topleft = [1, 4]
        self.colour_num = random.choice([1,2,3,4])
        self.colour = curses.color_pair(self.colour_num)

    def land(self, grid):
        for rowidx, row in enumerate(self.shape):
            for colidx, col in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    grid[rowidx + self.topleft[0]][colidx + self.topleft[1] // 2][0] = self.shape[rowidx][colidx]
                    grid[rowidx + self.topleft[0]][colidx + self.topleft[1] // 2][1] = self.colour

    def move_left(self, grid):
        if self.topleft[1] <= 1:
            raise OutOfBoundsError

        for rowidx, row in enumerate(self.shape):
            for colidx, col in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    if grid[rowidx + self.topleft[0]][colidx + (self.topleft[1] // 2) - 1][0] != 0:
                        raise CollisionError

        self.topleft[1] -= 2

    def move_right(self, grid):
        if len(self.shape[0]) == 4 and all(x == 1 for x in self.shape[0]):
            boundary = 15
        elif len(self.shape) == 4 and all(x[0] == 1 for x in self.shape):
            boundary = 18 
        else:
            boundary = 16

        if self.topleft[1] + len(self.shape[0]) - 1 >= boundary:
            raise OutOfBoundsError

        for row in range(len(self.shape)):
            for col in range(len(self.shape[row])):
                if self.shape[row][col] != 0:
                    if grid[row + self.topleft[0]][col + (self.topleft[1] // 2) + 1][0] != 0:
                        raise CollisionError

        self.topleft[1] += 2

    def move_down(self, grid):
        if self.topleft[0] >= 16 - len(self.shape):
            raise OutOfBoundsError

        for row in range(len(self.shape)):
            for col in range(len(self.shape[row])):
                if self.shape[row][col] != 0:
                    if grid[row + self.topleft[0] + 1][col + self.topleft[1] // 2][0] != 0:
                        raise CollisionError

        self.topleft[0] += 1

class Game:

    def __init__(self, screen):
        self.screen = screen
        self.block = Block()
        self.grid = [[[0, None] for i in range(10)] for j in range(16)]
        self.counter = 0

    def pause(self):
        pass

class OutOfBoundsError(Exception):
    pass

class CollisionError(Exception):
    pass

