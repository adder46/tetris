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

GRID_WIDTH = 10
GRID_HEIGHT = 16


class Block:

    def __init__(self):
        self.letter = random.choice(list(BLOCKS.keys()))
        self.shape = random.choice(BLOCKS[self.letter])
        self.topleft = [0, 4]
        self.colour = curses.color_pair(COLOURS[self.letter])

    def land(self, grid):
        """
        Lands a tetromino. If top left corner of the tetromino
        is beyond upper boundary, raises GameOverError.
        """
        if self.topleft[0] <= 0:
            raise GameOverError

        for rowidx, row in enumerate(self.shape):
            for colidx, _ in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    y_coord, x_coord = self.topleft
                    grid[rowidx + y_coord][colidx + x_coord][0] = self.shape[rowidx][colidx]
                    grid[rowidx + y_coord][colidx + x_coord][1] = self.colour

    def move_sideways(self, grid, direction):
        """
        Moves a tetromino one step left or right whilst making sure
        it does not go out of bounds or collide with another tetromino.
        """
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
        """
        Moves a tetromino one step down whilst making sure it does
        not go out of bounds or collide with another tetromino.
        """
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
        """
        Moves a tetromino all the way down until it either goes
        out of bounds, or until another tetromino is encountered.
        """
        while True:
            try:
                self.move_down(grid)
            except (OutOfBoundsError, CollisionError):
                break

    def rotate(self, grid, direction):
        """
        Rotates a tetromino either left or right whilst making sure
        it does not go out of bounds, or collide with another tetromino.
        """
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
            [[0, None] for i in range(GRID_WIDTH)] for j in range(GRID_HEIGHT)
        ]
        self.counter = 0
        self.score = 0

    def clear_rows(self):
        """
        Clears all the filled rows and prepends the grid with an empty row.
        """
        for row in self.grid.copy():
            if all(x[0] == 1 for x in row):
                self.grid.remove(row)
                self.grid.insert(0, [[0, None] for i in range(GRID_WIDTH)])
                self.score += 10

    async def handle_falling(self):
        """
        Handles automatic tetromino falling (every 0.5 seconds), as well as
        landing in case the tetromino touches the ground or another tetromino.

        Besides that, it displays game over screen in case the GameOverError is raised.

        Score is updated appropriately, too.
        """
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
        """
        Restarts the game by putting all vital game parameters to initial state.
        """
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
