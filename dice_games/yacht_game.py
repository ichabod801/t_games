"""
yacht_game.py

Games similar to Yacht.

Classes:
ScoreCategory: A category for a category dice game. (object)
Yacht: The game of Yacht and it's cousins. (game.Game)

Functions:
four_kind: Score the four of a kind category. (int)
full_house: Score the full house category. (int)
score_n: Creating a scoring function for a number category. (callable)
straight: Score a straight category. (int)
"""


import tgames.dice as dice
import tgames.game as game


class ScoreCategory(object):
    """
    A category for a category dice game. (object)

    !! I will want to move this to dice.py.

    Attributes:
    description: A description of the category. (str)
    first: The bonus for getting the roll on the first roll. (int)
    name: The name of the category. (str)
    validator: A function to check validity and get the sub-total. (callable)
    score_type: How the category is scored. (str)

    Methods:
    score: Score a roll based on this category. (int)

    Overridden Methods:
    __init__
    """

    def __init__(self, name, description, validator, score_type = 'total', first = 0):
        """
        Set up the category. (None)

        Parameters:
        description: A description of the category. (str)
        name: The name of the category. (str)
        validator: A function to check validity and get the sub-total. (callable)
        score_type: How the category is scored. (str)
        first: The bonus for getting the roll on the first roll. (int)
        """
        # Set basic attributes.
        self.name = name
        self.description = description
        self.validator = validator
        self.first = first
        # Parse the score type.
        if score_type.isdigit():
            self.score_type = int(score_type)
        else:
            self.score_type = score_type.lower()
        # Check for a bonus.
        if self.score_type.startswith('total+'):
            self.bonus = int(score_type.split('+')[1])
            self.score_type = 'total'
        else:
            self.bonus = 0

    def score(self, dice, roll_count):
        """
        Score a roll based on this category. (int)

        Parameters:
        dice: The roll to score. (dice.Pool)
        roll_count: How many rolls it took to get the roll. (int)
        """
        sub_total = self.validator(dice)
        # Score a valid roll
        if sub_total:
            # Score by type of category.
            if isinstance(self.score_type, int):
                score = self.score_type
            elif self.score_type == 'sub-total':
                score = sub_total
            else:
                score = sum(dice)
            # Add bonuses.
            score += self.bonus
            if roll_count == 1:
                score += self.first
        else:
            # Invalid rolls score 0.
            score = 0
        return score


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
