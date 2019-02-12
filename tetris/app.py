import curses

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

        while True:
            try:
                user_input = inner_screen.getkey()
            except curses.error:
                break

            if user_input == 'a':
                try:
                    game.block.move_left(game.grid)
                except (OutOfBoundsError, CollisionError):
                    break
            if user_input == 'd':
                try:
                    game.block.move_right(game.grid)
                except (OutOfBoundsError, CollisionError):
                    break

        await trio.sleep(.1)
