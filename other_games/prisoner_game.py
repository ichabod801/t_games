"""
prisoners_game.py

An implementation of the Iterated Prisoner's Dilemma.

Constants:
CREDITS: The credits for Priosoner's Dilemma.
RULES: The rules for Prisoner's Dilemma.

Classes:
PrisonersDilemma: A game of the Interated Prisoner's Dilemma. (game.Game)
"""

from .. import game

CREDITS = """
Game Design: Merrill Flood and Melvin Dresher
Game Programming: Craig "Ichabod" O'Brien
Bot Design: Anatol Rapoport
"""

RULES = """
Each turn, you and your opponent make the choice to cooperate or defect. If
both players cooperate, they both score the punishment. If they both defect,
they both score the reward. If one defects and the other cooperates, the
cooperator scores the sucker bet, while the defecter wins the temptation. The
standard scores are:

    Temptation: 3
    Reward: 2
    Punishment: 1
    Sucker Bet: 0

The game is played over multiple turns. Each round you know who you are playing
against, but you don't know their move until the result is calculated.

The idea of the game is that the rational move is always to defect: that will
get you the best score no matter what your opponent does. However, mutual
cooperation is a better outcome (the total score is highest).

Options:
punishment= (p=): The punishment score. It must be higher than the sucker bet.
reward= (r=): The reward score. It must be higher than the punishment score.
sucker= (s=): The sucker bet score. It must be lower than the punishment score.
temptation= (t=): The temptation score. It must be higher than the reward
    score.
"""

class PrisonersDilemma(game.Game):
    """
    A game of the Interated Prisoner's Dilemma. (game.Game)
    """

    credits = CREDITS
    num_options = 4
    rules = RULES

    def handle_options(self):
        """Handle the game options from the user. (None)"""
        self.points = {}
        super(PrisonersDilemma, self).handle_options(self)

    def set_options(self):
        """Set the possible game options. (None)"""
        self.option_set.add_option('sucker', ['s'], int, default = 0)
