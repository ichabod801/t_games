"""
test.py

Testing tgames.

Functions:
test: Test some text games. (None)
"""

from __future__ import print_function

import tgames.interface as interface
import tgames.player as player

class Test(object):

    def __init__(self):
        """Test some text games. (None)"""
        self.human = player.Tester()
        self.menu = interface.Interface(self.human)

    def __call__(self, held_inputs = []):
        self.human.held_inputs = held_inputs
        self.menu.menu()

if __name__ == '__main__':
    test = Test()
    test()
    #test(['roulette / none'])