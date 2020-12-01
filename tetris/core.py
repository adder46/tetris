import curses
import random
from typing import Dict, List, Optional

import trio

from tetris import Window
from tetris.blocks import BLOCKS
from tetris.exceptions import CollisionError, GameOverError, OutOfBoundsError


COLORS: Dict[str, int] = {
    "I": curses.COLOR_YELLOW,
    "O": curses.COLOR_BLUE,
    "T": curses.COLOR_GREEN,
    "L": curses.COLOR_RED,
    "J": curses.COLOR_MAGENTA,
    "S": curses.COLOR_CYAN,
    "Z": curses.COLOR_WHITE,
}

DIRECTIONS: Dict[str, int] = {"right": 1, "left": -1}

GRID_WIDTH: int = 10
GRID_HEIGHT: int = 16


class Game:
    def __init__(self, screen: Window, user_interface):
        self.screen = screen
        self.user_interface = user_interface
        self.grid = [[[0, None] for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.block = Block(self.grid)
        self.next_block = Block(self.grid)
        self.counter = 0
        self.score = 0

    def clear_rows(self) -> None:
        """
        Clears all the filled rows and prepends the grid with an empty row.
        """
        for row in self.grid.copy():
            if all(x[0] == 1 for x in row):
                self.grid.remove(row)
                self.grid.insert(0, [[0, None] for _ in range(GRID_WIDTH)])
                self.score += GRID_WIDTH

    async def handle_falling(self) -> None:
        """
        Handles automatic tetromino falling (every 0.5 seconds), as well as
        landing in case the tetromino touches the ground or another tetromino.

        Besides that, it displays game over screen in case the GameOverError is raised.

        Score is updated appropriately, too.
        """
        self.counter += 1
        if self.counter == 5:
            try:
                self.block.move_down()
            except (CollisionError, OutOfBoundsError):
                try:
                    self.block.land()
                except GameOverError:
                    await self.user_interface.display_game_over_screen(self)
                else:
                    self.block = self.next_block
                    self.next_block = Block(self.grid)
            finally:
                self.counter = 0

    def restart(self) -> None:
        """
        Restarts the game by putting all vital game parameters to initial state.
        """
        self.grid = [[[0, None] for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.block = Block(self.grid)
        self.next_block = Block(self.grid)
        self.counter = 0
        self.score = 0

    async def pause(self) -> None:
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


class Block:
    def __init__(self, grid: List[List[List[Optional[int]]]]):
        self.grid = grid
        self.letter = random.choice(list(BLOCKS.keys()))
        self.shape = random.choice(BLOCKS[self.letter])
        self.topleft = [0, GRID_WIDTH // 2 - 1]
        self.color = curses.color_pair(COLORS[self.letter])

    def land(self):
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
                    self.grid[rowidx + y_coord][colidx + x_coord][0] = self.shape[rowidx][
                        colidx
                    ]
                    self.grid[rowidx + y_coord][colidx + x_coord][1] = self.color

    def move_sideways(self, direction):
        """
        Moves a tetromino one step left or right if another tetromino is not in
        its way, whilst making sure it does not go out of bounds at the same time.
        """
        for rowidx, row in enumerate(self.shape):
            for colidx, _ in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    y_coord, x_coord = self.topleft
                    if colidx + x_coord + DIRECTIONS[direction] not in range(GRID_WIDTH):
                        raise OutOfBoundsError
                    if (
                        self.grid[rowidx + y_coord][
                            colidx + x_coord + DIRECTIONS[direction]
                        ][0]
                        != 0
                    ):
                        raise CollisionError

        self.topleft[1] += DIRECTIONS[direction]

    def move_down(self):
        """
        Moves a tetromino one step down if another tetromino is not in its way,
        whilst making sure it does not go out of bounds at the same time.
        """
        for rowidx, row in enumerate(self.shape):
            for colidx, _ in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    y_coord, x_coord = self.topleft
                    if rowidx + y_coord + 1 >= GRID_HEIGHT:
                        raise OutOfBoundsError
                    elif self.grid[rowidx + y_coord + 1][colidx + x_coord][0] != 0:
                        raise CollisionError

        self.topleft[0] += 1

    def move_all_the_way_down(self):
        """
        Moves a tetromino all the way down until it either goes
        out of bounds, or until another tetromino is encountered.
        """
        while True:
            try:
                self.move_down()
            except (OutOfBoundsError, CollisionError):
                break

    def rotate(self, direction):
        """
        Rotates a tetromino either left or right if another tetromino is
        not in its way, whilst making sure it does not go out of bounds.
        """
        current_rotation = BLOCKS[self.letter].index(self.shape)
        next_rotation = current_rotation + DIRECTIONS[direction]

        potential_shape = BLOCKS[self.letter][next_rotation % len(BLOCKS[self.letter])]

        for rowidx, row in enumerate(potential_shape):
            for colidx, _ in enumerate(row):
                if potential_shape[rowidx][colidx] != 0:
                    y_coord, x_coord = self.topleft
                    if colidx + x_coord not in range(GRID_WIDTH):
                        raise OutOfBoundsError
                    if rowidx + y_coord >= GRID_HEIGHT:
                        raise OutOfBoundsError
                    if self.grid[rowidx + y_coord][colidx + x_coord][0] != 0:
                        raise CollisionError

        self.shape = potential_shape
