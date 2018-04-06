"""
__init__.py

Package initializer for tgames.

Functions:
play: Play some text games. (None)
"""

from __future__ import print_function

import tgames.dice as dice
import tgames.game as game
import tgames.interface as interface
import tgames.player as player
from tgames.test import test

def play():
    """Play some text games. (None)"""
    human = player.Human()
    menu = interface.Interface(human)
    menu.menu()

if __name__ == '__main__':
    play()