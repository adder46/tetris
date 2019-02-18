import random
import curses
import collections

from tetris.blocks import BLOCKS


COLOURS = {
    "I": 1,
    "O": 2,
    "T": 3,
    "L": 4,
    "J": 5,
    "S": 6,
    "Z": 7
}

DIRECTIONS = {
    "right": ((0,1), 1),
    "left": ((0,-1), -1)
}

ROTATIONS = {
    "right": 1,
    "left": -1
}


class Block:

    def __init__(self):
        self.letter = random.choice(list(BLOCKS.keys()))
        self.shape = random.choice(BLOCKS[self.letter])
        self.topleft = [0, 6]
        self.colour = curses.color_pair(COLOURS[self.letter])

    def land(self, grid):
        if self.topleft[0] <= 0:
            raise GameOverError

        for rowidx, row in enumerate(self.shape):
            for colidx, col in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    grid[rowidx + self.topleft[0]][colidx + self.topleft[1] ][0] = self.shape[rowidx][colidx]
                    grid[rowidx + self.topleft[0]][colidx + self.topleft[1] ][1] = self.colour

    def move_sideways(self, grid, direction):
        for rowidx, row in enumerate(self.shape):
            for colidx, col in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    if colidx + (self.topleft[1] ) + DIRECTIONS[direction][0][1] not in range(len(grid[0])):
                        raise OutOfBoundsError         
                    if grid[rowidx + self.topleft[0]][colidx + (self.topleft[1] ) + DIRECTIONS[direction][0][1]][0] != 0:
                        raise CollisionError

        self.topleft[1] += DIRECTIONS[direction][1]

    def move_down(self, grid):
        for rowidx, row in enumerate(self.shape):
            for colidx, col in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    if rowidx + self.topleft[0] + 1 >= len(grid):
                        raise OutOfBoundsError
                    elif grid[rowidx + self.topleft[0] + 1][colidx + (self.topleft[1] )][0] != 0:
                        raise CollisionError

        self.topleft[0] += 1

    def move_all_the_way_down(self, grid):
        while True:
            try:
                self.move_down(grid)
            except (OutOfBoundsError, CollisionError):
                break

    def rotate(self, grid, direction):
        current_rotation = BLOCKS[self.letter].index(self.shape)
        next_rotation = current_rotation + ROTATIONS[direction]

        if direction == "right":
            try:
                potential_shape = BLOCKS[self.letter][next_rotation]
            except IndexError:
                next_rotation = 0
                potential_shape = BLOCKS[self.letter][next_rotation]        
        elif direction == "left":
            if next_rotation <= -1:
                next_rotation = len(BLOCKS[self.letter]) - 1
            potential_shape = BLOCKS[self.letter][next_rotation]

        for rowidx, row in enumerate(potential_shape):
            for colidx, col in enumerate(row):
                if potential_shape[rowidx][colidx] != 0:
                    if colidx + (self.topleft[1] ) not in range(len(grid[0])):
                        raise OutOfBoundsError
                    if rowidx + self.topleft[0] >= len(grid):
                        raise OutOfBoundsError
                    if grid[rowidx + self.topleft[0]][colidx + (self.topleft[1] )][0] != 0:
                        raise CollisionError

        self.shape = BLOCKS[self.letter][next_rotation]


class Game:

    def __init__(self, screen, user_interface):
        self.screen = screen
        self.user_interface = user_interface
        self.block = Block()
        self.grid = [
            [[0, None] for i in range(10)] for j in range(16)
        ]         
        self.counter = 0
        self.score = 0

    def clear_rows(self):
        for rowidx, row in enumerate(self.grid.copy()):
            if all(x[0] == 1 for x in row):
                self.grid.remove(row)
                self.grid.insert(0, [[0, None] for i in range(10)])
                self.score += 10

    async def handle_falling(self):
        self.counter += 1
        if self.counter == 5:
            try:
                self.block.move_down(self.grid)
            except (CollisionError, OutOfBoundsError):
                try:
                    self.block.land(self.grid)
                except GameOverError:
                    await self.user_interface.display_game_over_screen(self)
                else:
                    self.block = Block()
                    return
            finally:
                self.counter = 0

    def restart(self):
        self.__init__(self.screen, self.user_interface)

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

class GameOverError(Exception):
    pass