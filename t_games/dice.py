"""
dice.py

Dice objects for tgames.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Die: A single die. (object)
ShuffleDie: A die that samples from the range without replacement. (Die)
Pool: A set of dice. (object)
DominoPool: A set of dice based on dominos. (Pool)
"""


import functools
import itertools
import random

import t_games.utility as utility


@functools.total_ordering
class Die(object):
    """
    A single die. (object)

    While typically integers, the sides of the die can be any object.

    Attributes:
    held: A flag for holding the die aside and not rolling it. (bool)
    sides: The sides of the die. (list)
    value: The current value of the die. (object)

    Methods:
    roll: Roll the die. (object)

    Overridden Methods:
    __init__
    __add__
    __eq__
    __hash__
    __lt__
    __radd__
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
        # Set the default attribute.
        self.held = False
        # Get an initial value for the die.
        self.roll()

    def __add__(self, other):
        """
        Addition. (object)

        Parameters:
        other: The item to add to. (object)
        """
        # dice add by sides.
        if isinstance(other, Die):
            return self.value + other.value
        # add value to other objects.
        else:
            return self.value + other

    def __eq__(self, other):
        """
        Equality testing. (bool)

        Parameters:
        other: The item to check for equality. (object)
        """
        # Test by value.
        if isinstance(other, Die):
            return self.value == other.value
        elif isinstance(other, (int, float)):
            return self.value == other
        else:
            return NotImplemented

    def __hash__(self):
        """Hash value. (int)"""
        return hash(self.value)

    def __lt__(self, other):
        """
        Ordering (less than) testing. (bool)

        Parameters:
        other: The item to check for less than. (object)
        """
        # Testing is by value.
        if isinstance(other, Die):
            return self.value < other.value
        elif isinstance(other, (int, float)):
            return self.value < other
        else:
            return NotImplemented

    def __radd__(self, other):
        """
        Right-side addition.

        Parameters:
        other: The item to add to. (object)
        """
        return self + other

    def __repr__(self):
        """Generate a debugging text representation. (str)"""
        return '<{} {}>'.format(self.__class__.__name__, self.value)

    def __str__(self):
        """Generate a human readable text representation. (str)"""
        if self.held:
            return '{}*'.format(self.value)
        else:
            return str(self.value)

    def roll(self):
        """
        Roll the die. (object)

        The return value depends on the sides attribute.
        """
        if self.held:
            # Raise error if the die is held.
            raise ValueError('Attempt to roll a held die.')
        else:
            # Get the new value and return it.
            self.value = random.choice(self.sides)
            return self.value


class ShuffleDie(Die):
    """
    A die that samples from the range without replacement. (Die)

    Attributes:
    population: The set of future rolls. (list)
    repeats: The number of times the sides are repeated. (int)

    Methods:
    reset: Reset the population of future rolls. (None)

    Overridden Methods:
    __init__
    __repr__
    roll
    """

    def __init__(self, sides = 6, repeats = 1):
        """
        Set up the die. (None)

        Parameters:
        sides: The number of sides or a list of the sides of the die. (int or list)
        repeats: The number of times the sides are repeated. (int)
        """
        # Set up the list of sides, 1 to n for integer input.
        self.population = [0, 0]  # for roll in Die.__init__
        super(ShuffleDie, self).__init__(sides)
        # Set up the population to sample from.
        self.repeats = repeats
        self.reset()
        # Get an initial value for the die.
        self.roll()

    def reset(self):
        """Reset the population of future rolls. (None)"""
        self.population = self.sides * self.repeats
        random.shuffle(self.population)

    def roll(self):
        """
        Roll the die. (object)

        The return value depends on the population attribute.
        """
        # Check for no values to pull.
        if not self.population:
            self.reset()
        # Pull a value as the "roll".
        self.value = self.population.pop()
        return self.value


class Pool(object):
    """
    A set of dice. (object)

    Attributes:
    dice: The dice in the pool. (list of Die)
    held: The number of dice currently being held. (int)
    values: The current values of the dice in the pool. (list)

    Methods:
    count: Count the number of times a particular rolls has been made. (int)
    hold: Hold some of the dice from further rolling. (None)
    release: Make all held dice available for rolling. (None)
    roll: Roll the dice in the pool. (list)
    sort: Sort the dice in the pool in place. (list)

    Overridden Methods:
    __init__
    __iter__
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
        # Set up the dice.
        self.dice = []
        for die in dice:
            if isinstance(die, Die):
                self.dice.append(die)
            else:
                self.dice.append(Die(die))
        # Get an initial value.
        self.roll()
        self.held = 0

    def __iter__(self):
        """Iterate over the dice. (iterator)"""
        return iter(self.dice)

    def __repr__(self):
        """Generate debugging text representation. (str)"""
        return '<{} {}>'.format(self.__class__.__name__, self)

    def __str__(self):
        """Generate human readable text representation. (str)"""
        return utility.oxford(self.dice)

    def count(self, object):
        """
        Count the number of times a particular rolls has been made. (int)

        Parameters:
        object: The roll to count. (object)
        """
        return self.dice.count(object)

    def hold(self, values):
        """
        Hold some of the dice from further rolling. (None)

        Parameters:
        values: The values of the dice to hold. (int or list of int)
        """
        # Check for single value.
        if not isinstance(values, (list, tuple, set)):
            values = [values]
        # Loop through the values.
        unheld = [die for die in self.dice if not die.held]
        for value in values:
            # Find a die with that value and hold it.
            spot = unheld.index(value)
            unheld[spot].held = True
            self.held += 1
            del unheld[spot]

    def release(self):
        """Make all held dice available for rolling. (None)"""
        for die in self.dice:
            die.held = False
        self.held = 0

    def roll(self, index = None):
        """
        Roll the dice in the pool. (list)

        Parameters:
        index: The specific die to roll, if any. (int or None)
        """
        if index is not None:
            # Roll a single die.
            self.values[index] = self.dice[index].roll()
        else:
            # Roll all of the unheld dice.
            self.values = []
            for die in self.dice:
                if not die.held:
                    die.roll()
                self.values.append(die.value)
        return self.values

    def sort(self, key = None, reverse = False):
        """
        Sort the dice in the pool in place. (None)

        This sorts the values, not the actual dice objeects. But the sort is based on
        the dice objects, so it can use any of their attributes.

        Parameters:
        key: A function returning the value to sort an item by. (callable)
        reverse: A flag for reversing the sort order. (bool)
        """
        self.dice.sort(key = key, reverse = reverse)
        self.values = [die.value for die in self.dice]


class DominoPool(Pool):
    """
    A set of dice based on dominoes. (Pool)

    A domino pool uses dominoes instead of dice. If one of the values on the
    domino is blank, a normal die is used to replace the blank value. This gives
    a shallower but more staggered distribution of rolls, with more certainty in
    the distribution.

    Attributes:
    filler: The die used to replace blanks. (Die)
    population: The set of future values for the pool. (list of tuple of int)
    possible: The possible values for the pool. (list of tuple of int)

    Methods:
    replace: Replace a blank with a value from the filler die. (int)
    reset: Reset the population of dice rolls. (None)

    Overridden Methods:
    __init__
    replace
    roll
    sort
    """

    def __init__(self, dice = [6, 6], filler = Die(6)):
        """
        Set up the distribution of the roll results. (None)

        Parameters:
        dice: A list of dice specifications. (list of int)
        filler: The die to use to fill blanks. (Die)
        """
        ranges = [range(x + 1) for x in sorted(dice)]
        self.possible = [prod for prod in itertools.product(*ranges) if sorted(prod) == list(prod)]
        self.filler = filler
        self.reset()
        self.roll()

    def __str__(self):
        """Generate a human readable text representation. (str)"""
        return utility.oxford(self.values)

    def replace(self, value):
        """
        Replace a blank with a value from the filler die. (int)

        Parameters:
        value: The value to check for a blank to replace. (int)
        """
        if value:
            return value
        else:
            return self.filler.roll()

    def reset(self):
        """Reset the population of dice rolls. (None)"""
        self.population = self.possible[:]
        random.shuffle(self.population)

    def roll(self):
        """Roll the pool. (list)"""
        self.values = [self.replace(x) for x in self.population.pop()]
        if not self.population:
            self.reset()
        self.values.sort()
        return self.values

    def sort(self, key = None, reverse = False):
        """Sort the dice in the pool. (list)"""
        self.values.sort(key = key, reverse = reverse)


if __name__ == '__main__':
    # Run the unit testing.
    from t_tests.dice_test import *
    unittest.main()