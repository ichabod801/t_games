"""
player.py

Base player classes for tgames.

Classes:
Player: The base player class. (object)
"""

from __future__ import print_function

import sys


if sys.version_info[0] == 2:
    input = raw_input
    

class Player(object):
    """
    The base player class. (object)

    Attributes:
    name: The name of the player. (str)

    Methods:
    ask: Get information from the player. (str)
    tell: Give information to the player. (None)

    Overridden Methods:
    __init__
    """

    def __init__(self, name):
        """
        Save the player's name. (None)

        Parameters:
        name: The name of the player. (str)
        """
        self.name = name

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        return input(prompt)

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        print(*args, **kwargs)