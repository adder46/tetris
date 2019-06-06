import curses
import sys

import trio

from tetris.core import Game
from tetris.exceptions import CollisionError, OutOfBoundsError
from tetris.user_interface import (
    INNER_SCREEN_HEIGHT,
    INNER_SCREEN_WIDTH,
    UserInterface
)

bindings = {
    "controls": {
        ord("p"): lambda: game.pause(),
        ord("q"): sys.exit,
    },
    "movements": {
        curses.KEY_LEFT: lambda game, grid: game.block.move_sideways(grid, "left"),
        curses.KEY_RIGHT: lambda game, grid: game.block.move_sideways(grid, "right"),
        curses.KEY_DOWN: lambda game, grid: game.block.move_down(grid),
        ord("s"): lambda game, grid: game.block.move_all_the_way_down(grid),
        ord("a"): lambda game, grid: game.block.rotate(grid, "left"),
        ord("d"): lambda game, grid: game.block.rotate(grid, "right"),
    }
}

def create_screens(outer_screen):
    if UserInterface.ensure_terminal_size():
        border_screen = outer_screen.subwin(
            1 + INNER_SCREEN_HEIGHT + 1, 1 + INNER_SCREEN_WIDTH + 1,
            (curses.LINES // 2 - (INNER_SCREEN_HEIGHT // 2)) - 1,
            (curses.COLS // 2 - (INNER_SCREEN_WIDTH // 2)) - 1
        )
        inner_screen = border_screen.subwin(
            INNER_SCREEN_HEIGHT, INNER_SCREEN_WIDTH,
            curses.LINES // 2 - (INNER_SCREEN_HEIGHT // 2),
            (curses.COLS // 2 - (INNER_SCREEN_WIDTH // 2))
        )
    else:
        sys.exit("fatal: minimum terminal size needed [24x80]")

    return border_screen, inner_screen

def sync_main():
    curses.wrapper(lambda outer_screen: trio.run(main, outer_screen))

async def main(outer_screen):
    curses.curs_set(False)

    border_screen, inner_screen = create_screens(outer_screen)

    inner_screen.timeout(100)
    inner_screen.keypad(True)

    user_interface = UserInterface(inner_screen)
    game = Game(inner_screen, user_interface)
  
    while True:
        for screen in (inner_screen, border_screen, outer_screen):
            screen.erase()

        border_screen.box(0, 0)

        user_interface.renderer.render_landed_blocks(game.grid)
        user_interface.renderer.render_current_block(game.block)
        user_interface.display_next_block(outer_screen, game.next_block)
        user_interface.display_score(outer_screen, game.score)

        for screen in (outer_screen, border_screen, inner_screen):
            screen.refresh()

        await game.handle_falling()
        game.clear_rows()

        try:
            user_input = inner_screen.getch()
        except curses.error:
            continue

        if user_input in bindings["controls"]:
            await bindings["controls"][user_input]()

        if user_input in bindings["movements"]:
            try:
                bindings["movements"][user_input](game, game.grid)
            except (CollisionError, OutOfBoundsError):
                continue
