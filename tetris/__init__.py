from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from _curses import _CursesWindow  # pylint: disable=no-name-in-module

    Window = _CursesWindow
else:
    Window = Any
