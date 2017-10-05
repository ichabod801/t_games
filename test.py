"""
test.py

Testing tgames.

Functions:
test: Test some text games. (None)
"""

from __future__ import print_function

import tgames.interface as interface
import tgames.player as player

def test(held_inputs = []):
    """Test some text games. (None)"""
    human = player.Tester()
    human.held_inputs = held_inputs
    menu = interface.Interface(human)
    menu.menu()

if __name__ == '__main__':
    #test()
    test(['crazy eights / draw=2 reshuffle'])