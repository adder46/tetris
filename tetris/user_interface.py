import curses
import sys

import trio

MIN_WIDTH = 20
MIN_HEIGHT = 16

class UserInterface:

    def __init__(self, screen):
        self.screen = screen
        self.renderer = Renderer(screen)
        self.lines, self.cols = screen.getmaxyx()
        self.make_colour_pairs()

    @staticmethod
    def ensure_terminal_size():
        """
        Helper method to ensure correct terminal size
        """
        if curses.LINES >= MIN_HEIGHT and curses.COLS >= MIN_WIDTH:
            return True
        return False

    @staticmethod
    def make_colour_pairs():
        """
        Helper method to make curses colour pairs
        """
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLUE)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_CYAN)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_WHITE)


class Renderer:

    def __init__(self, screen):
        self.screen = screen

    def render_landed_blocks(self, grid):
        for rowidx, row in enumerate(grid):
            for colidx, col in enumerate(row):
                if grid[rowidx][colidx][0] != 0:
                    self.screen.addstr(rowidx, colidx * 2, "██", col[1] if col[1] is not None else curses.COLOR_BLACK)

    def render_current_block(self, block):
        for rowidx, row in enumerate(block.shape):
            for colidx, col in enumerate(row):
                if block.shape[rowidx][colidx] != 0:
                    self.screen.addstr(rowidx + block.topleft[0], (colidx * 2) + block.topleft[1], "██", block.colour)
