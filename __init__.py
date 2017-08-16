"""
__init__.py

Package initializer for tgames.

todo:
expand the interface
    store results (with flags)
    statistics
    defensive programming on games
    bot tournaments
write more real games (trac ticket #69)

Functions:
play: Play some text games. (None)
"""

from __future__ import print_function

import tgames.interface as interface
import tgames.player as player

def play():
    """Play some text games. (None)"""
    human = player.Human()
    menu = interface.Interface(human)
    menu.menu()

if __name__ == '__main__':
    play()