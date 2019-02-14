import random
import curses

import q

from tetris.blocks import BLOCKS


COLOURS = {
    "I": 1,
    "O": 3,
    "T": 4,
    "L": 5,
    "J": 7,
    "S": 2,
    "Z": 6
}


class Block:

    def __init__(self):
        self.letter = random.choice(list(BLOCKS.keys()))
        self.shape = BLOCKS[self.letter][random.randint(0, len(BLOCKS[self.letter]) - 1)]
        self.topleft = [1, 4]
        self.colour = curses.color_pair(COLOURS[self.letter])

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
        if self.is_horizontal_I_tetromino():
            boundary = 15
        elif self.is_vertical_I_tetromino():
            boundary = 18 
        else:
            boundary = 16

        if self.topleft[1] + len(self.shape[0]) - 1 >= boundary:
            raise OutOfBoundsError

        for rowidx, row in enumerate(self.shape):
            for colidx, col in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    if grid[rowidx + self.topleft[0]][colidx + (self.topleft[1] // 2) + 1][0] != 0:
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

    def rotate_right(self):
        current_rotation = BLOCKS[self.letter].index(self.shape)
        next_rotation = current_rotation + 1
        try:
            BLOCKS[self.letter][next_rotation]
        except IndexError:
            next_rotation = 0
        finally:
            self.shape = BLOCKS[self.letter][next_rotation]

    def rotate_left(self):
        current_rotation = BLOCKS[self.letter].index(self.shape)
        next_rotation = current_rotation - 1
        if next_rotation <= -1:
            next_rotation = len(BLOCKS[self.letter]) - 1
        self.shape = BLOCKS[self.letter][next_rotation]

    def is_vertical_I_tetromino(self):
        return len(self.shape) == 4 and all(x[0] == 1 for x in self.shape)

    def is_horizontal_I_tetromino(self):
        return len(self.shape[0]) == 4 and all(x == 1 for x in self.shape[0])


class Game:

    def __init__(self, screen):
        self.screen = screen
        self.block = Block()
        self.grid = [[[0, None] for i in range(10)] for j in range(16)]
        self.counter = 0

    async def pause(self):
        """
        Pauses the gameplay and waits for user input. If the input is key "p",
        it quits waiting and goes back to main game loop.
        """
        while True:
            try:
                user_input = self.screen.getch()
            except curses.error:
                await trio.sleep(0.1)
                continue
            if ord("p") == user_input:
                break



class OutOfBoundsError(Exception):
    pass

class CollisionError(Exception):
    pass

