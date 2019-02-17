import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'tetris',
    version = '0.0.1',
    author = 'adder46',
    author_email = 'dedmauz69@gmail.com',
    description = ('classic game implementation: tetris'),
    license = 'MIT',
    keywords = 'classic game implementation tetris terminal curses',
    url = 'https://github.com/adder46/tetris',
    packages=['tetris'],
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Games/Entertainment',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points = {
        'console_scripts': [
            'tetris = tetris.app:sync_main'
        ],
    },
    install_requires=[
          'trio'
      ],
)
