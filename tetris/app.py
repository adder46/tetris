import curses
import sys

import trio

from tetris.core import Game, OutOfBoundsError, CollisionError
from tetris.user_interface import UserInterface, INNER_SCREEN_HEIGHT, INNER_SCREEN_WIDTH

def sync_main():
    curses.wrapper(lambda outer_screen: trio.run(main, outer_screen))

async def main(outer_screen):
    curses.curs_set(False)

    if UserInterface.ensure_terminal_size():
        inner_screen = curses.newwin(
            INNER_SCREEN_HEIGHT, INNER_SCREEN_WIDTH,
            curses.LINES // 2 - (INNER_SCREEN_HEIGHT // 2),
            (curses.COLS // 2 - (INNER_SCREEN_WIDTH // 2))
        )
        border_screen = curses.newwin(
            1 + INNER_SCREEN_HEIGHT + 1, 1 + INNER_SCREEN_WIDTH + 1,
            (curses.LINES // 2 - (INNER_SCREEN_HEIGHT // 2)) - 1,
            (curses.COLS // 2 - (INNER_SCREEN_WIDTH // 2)) - 1
        )
    else:
        sys.exit(f"fatal: minimum terminal size needed [{INNER_SCREEN_HEIGHT}x{INNER_SCREEN_WIDTH}]")

    inner_screen.timeout(100)
    inner_screen.keypad(True)

    user_interface = UserInterface(inner_screen)
    game = Game(inner_screen, user_interface)

    bindings = {
        "controls": {
            ord("p"): game.pause,
            ord("q"): sys.exit,
        },
        "movements": {
            curses.KEY_LEFT: lambda grid: game.block.move_left(grid),
            curses.KEY_RIGHT: lambda grid: game.block.move_right(grid),
            curses.KEY_DOWN: lambda grid: game.block.move_down(grid),
            ord("s"): lambda grid: game.block.move_all_the_way_down(grid)
        },
        "rotations": {
            ord("a"): lambda grid: game.block.rotate_left(grid),
            ord("d"): lambda grid: game.block.rotate_right(grid),
        }
    }

    while True:
        inner_screen.erase()

        border_screen.box(0, 0)

        user_interface.renderer.render_landed_blocks(game.grid)      
        user_interface.renderer.render_current_block(game.block)        
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
                bindings["movements"][user_input](game.grid)
            except (CollisionError, OutOfBoundsError):
                continue
        if user_input in bindings["rotations"]:
            bindings["rotations"][user_input](game.grid)
