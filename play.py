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

import getopt
import sys

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
    An object for saving state when playing. (object)

    Attributes:
    human: The player. (player.Human)
    menu: The t_games interface object. (interface.Interface)

    Methods:
    reset: Set the player and the interface. (None)

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
        if self.human is None or self.menu is None:
            self.reset()
        # Play the requested game.
        self.human.held_inputs = held_inputs
        self.menu.menu()
        # Handle the results
        results = self.human.results[self.human.session_index:]
        self.human.session_index = len(self.human.results)
        return results

    def reset(self):
        """Set the player and the interface. (None)"""
        print()
        self.human = player.Human()
        self.menu = interface.Interface(self.human)


# Play some text games.
play = Play()


class Test(Play):
    """
    An object for saving state when playing. (object)

    Overridden Methods:
    reset
    """

    def reset(self):
        """Set the player and the interface. (None)"""
        self.human = player.Tester()
        self.menu = interface.Interface(self.human)


# Test some games
test = Test()


if __name__ == '__main__':
    # Get any options.
    try:
        opts, args = getopt.getopt(sys.argv[1:], 't')
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    # Check for testing.
    if ('-t', '') in opts:
        play_function = test
    else:
        play_function = play
    play_function(args)
