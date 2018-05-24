"""
test.py

Testing t_games.

Classes:
Test: An object for saving state when testing. (object)

Functions:
test: Test some text games. (None)
"""

from __future__ import print_function

import t_games.interface as interface
import t_games.player as player


class Test(object):
    """
    An object for saving state when testing. (object)

    Attributes:
    human: The test player. (player.Tester)
    menu: The t_games interface object. (interface.Interface)

    Overridden Methods:
    __init__
    __call__
    """

    def __init__(self):
        """Test some text games. (None)"""
        self.human = player.Tester()
        self.menu = interface.Interface(self.human)

    def __call__(self, held_inputs = []):
        """
        Play the game when called. (None)

        Parameters:
        held_inputs: The commands for the player to start with. (list of str)
        """
        self.human.held_inputs = held_inputs
        self.menu.menu()


test = Test()


if __name__ == '__main__':
    test()
    #test(['roulette / none'])