"""
test.py

Testing tgames.

Functions:
test: Test some text games. (None)
"""

from __future__ import print_function

import tgames.interface as interface
import tgames.player as player

def test():
    """Test some text games. (None)"""
    human = player.Tester()
    menu = interface.Interface(human)
    menu.menu()

if __name__ == '__main__':
    test()