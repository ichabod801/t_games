"""
_test_utility.py

Classes and functions of general use to unit testing in the t_games project.

Classes:
Mute: A player who doesn't say anything.
"""


import t_games.player as player


class Mute(player.Player):
    """
    A player who doesn't say anything. (player.Player)

    Overrideen Methods:
    error
    tell
    """

    def __init__(self):
        """Set the mute's name. (None)"""
        super(Mute, self).__init__(name = 'Hellen')

    def error(self, *args, **kwargs):
        """
        Warn the player about an invalid play. (None)

        Parameters:
        The parameters are as teh built-in print function.
        """
        pass

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        pass