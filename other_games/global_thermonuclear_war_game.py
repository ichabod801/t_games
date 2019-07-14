"""
global_thermonuclear_war_game.py

A game inspired by Global Thermonuclear War in the movie War Games.

Classes:
GlobalThermonuclearWar: A game of thermonuclear armageddon. (game.Game)
"""


from .. import game
from .. import utility


def GlobalThermonuclearWar(game.Game):
    """
    A game of thermonuclear armageddon. (game.Game)

    Overridden Methods:
    set_options
    set_up
    """

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Check for Chess win.
        if self.force_end:
            return False

    def set_options(self):
        """Define the options for the game. (None)"""
        self.option_set.add_option('united-states', ['us'])
        self.option_set.add_option('russia', ['r'])

    def set_up(self):
        """Set up the game. (None)"""
        if self.human.ask("WOULDN'T YOU PREFER A NICE GAME OF CHESS?") in utility.YES:
            results = self.interface.games['chess'].play('')
            self.win_loss_draw = [1, 0, 0]
            self.force_end = 'chess'
