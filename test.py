"""
test.py

Testing t_games.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
Test: An object for saving state when testing. (object)

Functions:
test: Test some text games. (None)
"""


from __future__ import print_function

try:
    # Standard imports.
    from . import interface
    from . import player
except (ValueError, ImportError):
    try:
        # Imports for running play.py independently.
        from t_games import interface
        from t_games import player
    except ImportError:
        # Imports for running play.py from the t_games folder in 2.7.
        import os
        import sys
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, here)
        from t_games import interface
        from t_games import player


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
        """Set up the saved state attributes. (None)"""
        self.human = player.Tester()
        self.menu = interface.Interface(self.human)

    def __call__(self, held_inputs = []):
        """
        Test t_games when called. (list of lists)

        The return value is a list of results from the games played.

        Parameters:
        held_inputs: The commands for the player to start with. (list of str)
        """
        self.human.held_inputs = held_inputs
        self.menu.menu()
        return self.human.results[self.human.session_index:]


# Test some text games. (None)
test = Test()


if __name__ == '__main__':
    test()
