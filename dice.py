"""
dice.py

Dice objects for tgames.

Die: A single die. (object)
"""

import random


class Die(object):
    """
    A single die. (object)

    While typically integers, the sides of the die can be any object.

    Attributes:
    sides: The sides of the die. (list)
    value: The current value of the die. (object)

    Methods:
    roll: Roll the die. (object)

    Overridden Methods:
    __init__
    __repr__
    __str__
    """

    def __init__(self, sides = 6):
        """
        Set up the die.

        Parameters:
        sides: The number of sides or a list of the sides of the die. (int or list)
        """
        # Set up the list of sides, 1 to n for integer input.
        if isinstance(sides, int):
            self.sides = list(range(1, sides + 1))
        else:
            self.sides = sides
        # Get an initial value for the die.
        self.roll()

    def __repr__(self):
        """Debugging text representation. (str)"""
        return '<Die {}>'.format(self.value)

    def __str__(self):
        """Human readable text representation. (str)"""
        return str(self.value)

    def roll(self):
        """
        Roll the die. (object)

        The return value depends on the sides attribute.
        """
        self.value = random.choice(self.sides)
        return self.value


class Pool(object):
    """
    A set of dice. (object)

    Attributes:
    dice: The dice in the pool. (list of Die)
    values: The current values of the dice in the pool. (list)

    Overridden Methods:
    __init__
    __repr__
    __str__
    """

    def __init__(self, dice = [6, 6]):
        """
        Set up the dice in the pool. (None)

        The dice parameter can be Die instances, or values that can be used to create
        Die instances.

        Parameters:
        dice: A list of dice specifications. (list)
        """
        self.dice = []
        for die in dice:
            if isinstance(die, Die):
                self.dice.append(die)
            else:
                self.dice.append(Die(die))

    def __repr__(self):
        """Debugging text representation. (str)"""
        return '<Pool {}>'.format(self)

    def __str__(self):
        """Human readable text representation. (str)"""
        text = ', '.join(self.values[:-1])
        text = '{} and {}'.format(text, self.values[-1])
        return text

    def roll(self):
        """Roll the dice in the pool. (list)"""
        self.values = []
        for die in self.dice:
            self.values.append(die.roll())
        return self.values