# tetris

Classic tetris game implementation written in Python using curses.

## Playing

You will need [poetry](https://github.com/python-poetry/poetry), preferably with these options in config:

```toml
virtualenvs.create = true
virtualenvs.in-project = true
```

Then clone the repo, cd into it, make a venv, activate it, and install the project:

```sh
git clone https://github.com/adder46/tetris
cd tetris
poetry env use python3
. .venv/bin/activate
poetry install
```

## Licensing

Licensed under the [MIT License](https://opensource.org/licenses/MIT). For details, see [LICENSE](https://github.com/adder46/pysnake/blob/master/LICENSE)
