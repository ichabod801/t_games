"""
__init__.py

Package initializer for t_games.

Functions:
play: Play some text games. (None)
"""

from __future__ import print_function

import t_games.dice as dice
import t_games.game as game
import t_games.interface as interface
import t_games.player as player
from t_games.test import test

def play():
    """Play some text games. (None)"""
    human = player.Human()
    menu = interface.Interface(human)
    menu.menu()

if __name__ == '__main__':
    play()