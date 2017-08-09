"""
__init__.py

Package initializer for tgames.

todo:
write some real games
expand the interface
write more real games

Functions:
play: Play some text games. (None)
"""

from __future__ import print_function

import interface
import player

def play():
    """Play some text games. (None)"""
    human = player.Human()
    menu = interface.Interface(human)
    menu.menu()

if __name__ == '__main__':
    play()