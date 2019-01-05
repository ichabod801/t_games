"""
play.py

Playing t_games.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
Play: An object for saving state when playing. (object)

Functions:
play: Play some text games. (None)
"""


from __future__ import print_function

try:
    from . import interface
    from . import player
except (ValueError, ImportError):
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

    def __call__(self, held_inputs = []):
        """
        Test t_games when called. (list of lists)

        The return value is a list of results from the games played.

        Parameters:
        held_inputs: The commands for the player to start with. (list of str)
        """
        if self.human is None or self.menu is None:
            print()
            self.human = player.Human()
            self.menu = interface.Interface(self.human)
        self.human.held_inputs = held_inputs
        self.menu.menu()
        return self.human.results[self.human.session_index:]


# Test some text games. (None)
play = Play()


if __name__ == '__main__':
    play()
