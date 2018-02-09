"""
yacht_game.py

Games similar to Yacht.

Classes:
Yacht: The game of Yacht and it's cousins. (game.Game)

Functions:
four_kind: Score the four of a kind category. (int)
full_house: Score the full house category. (int)
score_n: Creating a scoring function for a number category. (callable)
straight: Score a straight category. (int)
"""


import tgames.dice as dice
import tgames.game as game


class Yacht(game.Game):
    """
    The game of Yacht and it's cousins. (game.Game)

    Class Attributes:
    categories: The scoring functions for each category. (dict of str: callable)

    Attributes:
    dice: The pool of dice for the game. (dice.Pool)

    Overridden Methods:
    set_up
    """

    categories = {'ones': score_n(1), }

    def set_up(self):
        """Set up the game. (None)"""
        self.dice = dice.Pool([6] * 5)


def four_kind(dice):
    """
    Score the four of a kind category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    if values[0] == values[3] or values[2] == values[4]:
        return 4 * values[2]
    else:
        return 0

def full_house(dice):
    """
    Score the full house category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    if values[0] == values[1] and values[2] == values[4] and values[1] != values[2]:
        return sum(values)
    else:
        return 0

def score_n(number):
    """
    Creating a scoring function for a number category. (callable)

    Parameters:
    number: The number of the category. (int)
    """
    def score_num(dice):
        return number * dice.count(number)

def straight(dice):
    """
    Score a straight category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    for value_index, value in enumerate(values):
        if value - values[value_index - 1] != 1:
            break
    else:
        return 30
    return 0
