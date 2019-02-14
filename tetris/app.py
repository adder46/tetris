import curses
import sys

import trio
import q
import more_itertools
from pprint import pprint as pp

from tetris.core import Block, Game, OutOfBoundsError, CollisionError
from tetris.user_interface import UserInterface, MIN_HEIGHT, MIN_WIDTH

def sync_main():
    curses.wrapper(lambda outer_screen: trio.run(main, outer_screen))

async def main(outer_screen):
    outer_screen.clear()
    outer_screen.nodelay(True)
    curses.curs_set(False)

    if UserInterface.ensure_terminal_size():
        inner_screen = curses.newwin(
            MIN_HEIGHT, MIN_WIDTH + 3,
            curses.LINES // 2 - (MIN_HEIGHT // 2),
            (curses.COLS // 2 - (MIN_WIDTH // 2)) + 1
        )
        border_screen = curses.newwin(
            MIN_HEIGHT + 2, MIN_WIDTH + 4,
            (curses.LINES // 2 - (MIN_HEIGHT // 2)) - 1,
            (curses.COLS // 2 - (MIN_WIDTH // 2)) - 1
        )
    else:
        sys.exit(f"fatal: minimum terminal size needed [{MIN_HEIGHT}x{MIN_WIDTH}]")

    inner_screen.nodelay(True)
    inner_screen.keypad(True)

    user_interface = UserInterface(inner_screen)
    game = Game(inner_screen)

    bindings = {
        "ctrl": {
            ord("p"): game.pause,
            ord("q"): sys.exit,
        },
        "dir": {
            curses.KEY_DOWN: lambda grid: game.block.move_down(grid),
            curses.KEY_LEFT: lambda grid: game.block.move_left(grid),
            curses.KEY_RIGHT: lambda grid: game.block.move_right(grid),
        },
        "tetromino": {
            ord("a"): lambda block: game.block.rotate_left(),
            ord("d"): lambda block: game.block.rotate_right()
        }
    }

    while True:
        game.counter += 1
        outer_screen.erase()
        inner_screen.erase()
        border_screen.erase()
        border_screen.box(0, 0)

        outer_screen.refresh()
        inner_screen.refresh()
        border_screen.refresh()

        user_interface.renderer.render_landed_blocks(game.grid)      
        user_interface.renderer.render_current_block(game.block)        
       
        if game.counter == 5:
            try:
                game.block.move_down(game.grid)
            except (OutOfBoundsError, CollisionError):
                game.block.land(game.grid)
                game.block = Block()
                continue
            finally:
                game.counter = 0

        game.clear_row()

        while True:
            user_input = inner_screen.getch()
            if user_input == -1:
                break
            if user_input in bindings["dir"]:
                try:
                    bindings["dir"][user_input](game.grid)
                except (OutOfBoundsError, CollisionError):
                    break
            if user_input in bindings["ctrl"]:
                bindings["ctrl"][user_input]()
            if user_input in bindings["tetromino"]:
                bindings["tetromino"][user_input](game.block)
        
        await trio.sleep(.1)

