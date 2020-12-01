import curses
import sys

import trio

from tetris import Window
from tetris.core import COLORS, GRID_HEIGHT, GRID_WIDTH


SCREEN_WIDTH: int = GRID_WIDTH * 2
SCREEN_HEIGHT: int = GRID_HEIGHT


class UserInterface:
    def __init__(self, screen: Window):
        self.screen = screen
        self.renderer = Renderer(screen)
        self.make_color_pairs()

    @staticmethod
    def ensure_terminal_size() -> bool:
        """
        Helper method to ensure correct terminal size
        """
        if curses.LINES >= 24 and curses.COLS >= 80:
            return True
        return False

    @staticmethod
    def make_color_pairs() -> None:
        """
        Helper method to make curses color pairs
        """
        curses.init_color(curses.COLOR_YELLOW, 1000, 1000, 0)
        for color in COLORS.values():
            curses.init_pair(color, color, color)

    def display_score(self, screen, score):
        """
        Displays current score at the lower left-hand side of the screen.
        """
        y_coord = (curses.LINES - SCREEN_HEIGHT) // 2 + SCREEN_HEIGHT + 1
        x_coord = (curses.COLS - SCREEN_WIDTH) // 2 - 1
        screen.addstr(y_coord, x_coord, f" SCORE: {score} ", curses.A_BOLD)

    def display_next_block(self, screen, block):
        """
        Displays incoming block at the right-hand side of the play field.
        """
        y_coord = (curses.LINES - SCREEN_HEIGHT) // 2
        x_coord = (curses.COLS - SCREEN_WIDTH) // 2

        screen.addstr(y_coord, x_coord + SCREEN_WIDTH + 3, "NEXT", curses.A_BOLD)

        for rowidx, row in enumerate(block.shape):
            for colidx, _ in enumerate(row):
                if block.shape[rowidx][colidx] != 0:
                    screen.addstr(
                        rowidx + y_coord + 2,
                        (colidx * 2) + x_coord + SCREEN_WIDTH + 3,
                        "██",
                        block.color,
                    )

    async def display_game_over_screen(self, game):
        """
        Displays game over screen and waits for user input.
        If the input are keys "q" or "r", it quits or restarts the game, respectively.
        """
        self.screen.erase()
        self.screen.addstr(SCREEN_HEIGHT // 2 - 1, SCREEN_WIDTH // 2 - 4, "GAME OVER")
        self.screen.addstr(SCREEN_HEIGHT // 2, SCREEN_WIDTH // 2 - 4, f"SCORE: {game.score}")
        self.screen.addstr(SCREEN_HEIGHT // 2 + 2, SCREEN_WIDTH // 2 - 8, "[r]estart [q]uit")
        self.screen.refresh()
        while True:
            try:
                user_input = self.screen.getch()
            except curses.error:
                await trio.sleep(0.1)
                continue
            if ord("q") == user_input:
                sys.exit()
            if ord("r") == user_input:
                game.restart()
                break


class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def _addstr(self, y_coord, x_coord, text, color_info_stuff):
        """
        Works around curses' limitation of drawing at bottom right corner
        of the screen, as seen on https://stackoverflow.com/q/36387625
        """
        screen_height, screen_width = self.screen.getmaxyx()
        if x_coord + len(text) == screen_width and y_coord == screen_height - 1:
            try:
                self.screen.addstr(y_coord, x_coord, text, color_info_stuff)
            except curses.error:
                pass
        else:
            self.screen.addstr(y_coord, x_coord, text, color_info_stuff)

    def render_landed_blocks(self, grid):
        """
        Renders all the landed tetrominos.
        """
        for rowidx, row in enumerate(grid):
            for colidx, col in enumerate(row):
                if grid[rowidx][colidx][0] != 0:
                    self._addstr(rowidx, colidx * 2, "██", col[1])

    def render_current_block(self, block):
        """
        Renders a current tetromino.
        """
        for rowidx, row in enumerate(block.shape):
            for colidx, _ in enumerate(row):
                if block.shape[rowidx][colidx] != 0:
                    y_coord, x_coord = block.topleft
                    self._addstr(
                        rowidx + y_coord, (colidx + x_coord) * 2, "██", block.color
                    )
