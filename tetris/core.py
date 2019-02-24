import curses
import random

import trio

from tetris.blocks import BLOCKS


COLOURS = {
    "I": curses.COLOR_YELLOW,
    "O": curses.COLOR_BLUE,
    "T": curses.COLOR_GREEN,
    "L": curses.COLOR_RED,
    "J": curses.COLOR_MAGENTA,
    "S": curses.COLOR_CYAN,
    "Z": curses.COLOR_WHITE
}

DIRECTIONS = {
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
            for colidx, _ in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    y_coord, x_coord = self.topleft
                    grid[rowidx + y_coord][colidx + x_coord][0] = self.shape[rowidx][colidx]
                    grid[rowidx + y_coord][colidx + x_coord][1] = self.colour

    def move_sideways(self, grid, direction):
        for rowidx, row in enumerate(self.shape):
            for colidx, _ in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    y_coord, x_coord = self.topleft
                    if colidx + x_coord + DIRECTIONS[direction] not in range(len(grid[0])):
                        raise OutOfBoundsError
                    if grid[rowidx + y_coord][colidx + x_coord + DIRECTIONS[direction]][0] != 0:
                        raise CollisionError

        self.topleft[1] += DIRECTIONS[direction]

    def move_down(self, grid):
        for rowidx, row in enumerate(self.shape):
            for colidx, _ in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    y_coord, x_coord = self.topleft
                    if rowidx + y_coord + 1 >= len(grid):
                        raise OutOfBoundsError
                    elif grid[rowidx + y_coord + 1][colidx + x_coord][0] != 0:
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
        next_rotation = current_rotation + DIRECTIONS[direction]

        potential_shape = BLOCKS[self.letter][next_rotation % len(BLOCKS[self.letter])]

        for rowidx, row in enumerate(potential_shape):
            for colidx, _ in enumerate(row):
                if potential_shape[rowidx][colidx] != 0:
                    y_coord, x_coord = self.topleft
                    if colidx + x_coord not in range(len(grid[0])):
                        raise OutOfBoundsError
                    if rowidx + y_coord >= len(grid):
                        raise OutOfBoundsError
                    if grid[rowidx + y_coord][colidx + x_coord][0] != 0:
                        raise CollisionError

        self.shape = potential_shape


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
        for row in self.grid.copy():
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
