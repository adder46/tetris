import random
import curses
import collections

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
        self.topleft = [0, 6]
        self.colour = curses.color_pair(COLOURS[self.letter])

    def land(self, grid):
        if self.topleft[0] <= 0:
            raise GameOverError

        for rowidx, row in enumerate(self.shape):
            for colidx, col in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    grid[rowidx + self.topleft[0]][colidx + self.topleft[1] // 2][0] = self.shape[rowidx][colidx]
                    grid[rowidx + self.topleft[0]][colidx + self.topleft[1] // 2][1] = self.colour

    def move_left(self, grid):
        if self.is_vertical_I_tetromino():
            boundary = -3 
        else:
            boundary = 1

        if self.topleft[1] <= boundary:
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
        if self.is_horizontal_I_tetromino():
            boundary = 17
        else:
            boundary = 16

        if self.topleft[0] >= boundary - len(self.shape):
            raise OutOfBoundsError

        for rowidx, row in enumerate(self.shape):
            for colidx, col in enumerate(row):
                if self.shape[rowidx][colidx] != 0:
                    if grid[rowidx + self.topleft[0] + 1][colidx + self.topleft[1] // 2][0] != 0:
                        raise CollisionError

        self.topleft[0] += 1

    def rotate_right(self, grid):
        current_rotation = BLOCKS[self.letter].index(self.shape)
        next_rotation = current_rotation + 1

        if self.is_horizontal_I_tetromino() or self.is_vertical_I_tetromino():
            boundary = 16
        else:
            boundary = 17

        try:
            potential_shape = BLOCKS[self.letter][next_rotation]
        except IndexError:
            next_rotation = 0
            potential_shape = BLOCKS[self.letter][next_rotation]
   
        for rowidx, row in enumerate(potential_shape):
            for colidx, col in enumerate(row):
                if potential_shape[rowidx][colidx] != 0:
                    try:
                        next_step_right = grid[rowidx + self.topleft[0]][colidx + (self.topleft[1] // 2) + 1][0]
                    except IndexError:
                        next_step_right = grid[rowidx + self.topleft[0]][colidx + (self.topleft[1] // 2)][0]
                    if next_step_right != 0:
                        return
                    next_step_left = colidx + (self.topleft[1] // 2) - 1
                    if next_step_left == -1: 
                        next_step_left = 0
                    if grid[rowidx + self.topleft[0]][next_step_left][0] != 0:
                        return
                    if grid[rowidx + self.topleft[0] + 1][colidx + (self.topleft[1] // 2)][0] != 0:
                        return
                    if grid[rowidx + self.topleft[0] - 1][colidx + (self.topleft[1] // 2)][0] != 0:
                        return
                    if colidx + self.topleft[1] >= boundary:
                        return
                    if colidx + self.topleft[1] <= -1:
                        return

        self.shape = BLOCKS[self.letter][next_rotation]

    def rotate_left(self, grid):
        current_rotation = BLOCKS[self.letter].index(self.shape)
        next_rotation = current_rotation - 1

        if next_rotation <= -1:
            next_rotation = len(BLOCKS[self.letter]) - 1

        if self.is_horizontal_I_tetromino() or self.is_vertical_I_tetromino():
            boundary = 16
        else:
            boundary = 17

        potential_shape = BLOCKS[self.letter][next_rotation]

        for rowidx, row in enumerate(potential_shape):
            for colidx, col in enumerate(row):
                if potential_shape[rowidx][colidx] != 0:
                    try:
                        next_step_right = grid[rowidx + self.topleft[0]][colidx + (self.topleft[1] // 2) + 1][0]
                    except IndexError:
                        next_step_right = grid[rowidx + self.topleft[0]][colidx + (self.topleft[1] // 2)][0]
                    if next_step_right != 0:
                        return
                    next_step_left = colidx + (self.topleft[1] // 2) - 1
                    if next_step_left == -1: 
                        next_step_left = 0
                    if grid[rowidx + self.topleft[0]][next_step_left][0] != 0:
                        return
                    if grid[rowidx + self.topleft[0] + 1][colidx + (self.topleft[1] // 2)][0] != 0:
                        return
                    if grid[rowidx + self.topleft[0] - 1][colidx + (self.topleft[1] // 2)][0] != 0:
                        return
                    if colidx + self.topleft[1] >= boundary:
                        return
                    if colidx + self.topleft[1] <= -1:
                        return

        self.shape = BLOCKS[self.letter][next_rotation]

    def move_all_the_way_down(self, grid):
        while True:
            try:
                self.move_down(grid)
            except (OutOfBoundsError, CollisionError):
                break

    def is_vertical_I_tetromino(self):
        return len(self.shape) == 4 and all(x[2] == 1 for x in self.shape)

    def is_horizontal_I_tetromino(self):
        return len(self.shape) == 4 and all(x == 1 for x in self.shape[2])


class Game:

    def __init__(self, screen, user_interface):
        self.screen = screen
        self.user_interface = user_interface
        self.block = Block()
        self.grid = collections.deque([[[0, None] for i in range(10)] for j in range(16)], maxlen=16)
        # self.grid = collections.deque([[[0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [1, None], [0, None], [0, None], [1, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [1, None], [0, None], [0, None], [1, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [1, None], [0, None], [0, None], [1, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [1, None], [0, None], [0, None], [1, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [1, None], [0, None], [0, None], [1, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [1, None], [0, None], [0, None], [1, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [1, None], [0, None], [0, None], [1, None], [0, None], [0, None], [0, None]],
        # [[0, None], [0, None], [0, None], [1, None], [0, None], [0, None], [1, None], [0, None], [0, None], [0, None]]])
        self.counter = 0
        self.score = 0


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

    def clear_rows(self):
        for rowidx, row in enumerate(self.grid.copy()):
            if all(x[0] == 1 for x in row):
                self.grid.remove(row)
                self.grid.insert(0, [[0, None] for i in range(10)])
                self.score += 10

class OutOfBoundsError(Exception):
    pass

class CollisionError(Exception):
    pass

class GameOverError(Exception):
    pass