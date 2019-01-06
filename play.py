"""
play.py

Playing t_games.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
Play: An object for saving state when playing. (object)

Functions:
play: Play t_games. (list of lists)
test: Play t_games with a default player. (list of lists)
"""


from __future__ import print_function

import unittest

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


class Play(object):
    """
    An object for saving state when testing. (object)

    Attributes:
    human: The player. (player.Human)
    menu: The t_games interface object. (interface.Interface)

    Overridden Methods:
    __init__
    __call__
    """

    def __init__(self):
        """Set up the saved state attributes. (None)"""
        self.human = None
        self.menu = None

    def __call__(self, held_inputs = [], action = 'play'):
        """
        Play t_games. (list of lists)

        The action can be 'play' (play t_games), 'test' (play t_games with a default
        player), or 'auto' (run the automatic testing). For the 'auto' action,
        held_inputs can specify the test files to run.

        The return value is a list of results from the games played.

        Parameters:
        held_inputs: The commands for the player to start with. (list of str)
        action: The action to take. (str)
        """
        # Handle the action type.
        if action.lower() in ('a', 'auto'):
            return self.auto_test(held_inputs)
        if action in ('t', 'test') and not isinstance(self.human, player.Tester):
            self.human = player.Tester()
            self.menu = interface.Interface(self.human)
        elif action in ('p', 'play') and not isinstance(self.human, player.Human):
            print()
            self.human = player.Human()
            self.menu = interface.Interface(self.human)
        # Play the requested game.
        self.human.held_inputs = held_inputs
        self.menu.menu()
        return self.human.results[self.human.session_index:]


# Test some text games. (None)
play = Play()

def auto_test(test_files = []):
    """
    Run automated testing on the t_games system. (None)

    If not test files are specified, all test files are run.

    Parameters:
    test_files: The names of the test files to run. (list of str)
    """
    play.auto_test(test_files)

def test(held_inputs = []):
    """
    Play t_games with a default player. (list of lists)

    The return value is a list of results from the games played.

    Parameters:
    held_inputs: The commands for the player to start with. (list of str)
    """
    return play(held_inputs, action = 'test')


if __name__ == '__main__':
    play()
