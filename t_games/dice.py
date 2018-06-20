"""
dice.py

Dice objects for tgames.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Die: A single die. (object)
"""


import functools
import random


@functools.total_ordering
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
    __add__
    __eq__
    __hash__
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

    def __add__(self, other):
        """
        Addition.

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


class ShuffleDie(Die):
    """
    A die that samples from the range without replacement. (Die)

    Attributes:
    population: The set of future rolls. (list)

    Methods:
    reset: Reset the population of future rolls. (None)

    Overridden Methods:
    __init__
    __repr__
    roll
    """

    def __init__(self, sides = 6, repeats = 1):
        """
        Set up the die.

        Parameters:
        sides: The number of sides or a list of the sides of the die. (int or list)
        repeats: The number of times the sides are repeated. (int)
        """
        # Set up the list of sides, 1 to n for integer input.
        self.population = [0, 0] # for roll in Die.__init__
        super(ShuffleDie, self).__init__(sides)
        # Set up the population to sample from.
        self.repeats = repeats
        self.reset()
        # Get an initial value for the die.
        self.roll()

    def __repr__(self):
        """Debugging text representation. (str)"""
        return '<ShuffleDie {}>'.format(self.value)

    def reset(self):
        """Reset the population of future rolls. (None)"""
        self.population = self.sides * self.repeats
        random.shuffle(self.population)

    def roll(self):
        """
        Roll the die. (object)

        The return value depends on the population attribute.
        """
        self.value = self.population.pop()
        if not self.population:
            self.reset()
        return self.value


class Pool(object):
    """
    A set of dice. (object)

    Attributes:
    dice: The dice in the pool. (list of Die)
    held: Dice put asside and not rolled. (list of Die)
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
        self.dice = []
        self.held = []
        for die in dice:
            if isinstance(die, Die):
                self.dice.append(die)
            else:
                self.dice.append(Die(die))
        self.roll()

    def __iter__(self):
        """Iterate over the dice. (iterator)"""
        return iter(self.held + self.dice)

    def __repr__(self):
        """Debugging text representation. (str)"""
        return '<Pool {}>'.format(self)

    def __str__(self):
        """Human readable text representation. (str)"""
        dice_text = [str(die.value) + '*' for die in self.held] + [str(die.value) for die in self.dice]
        text = '{}, and {}'.format(', '.join(dice_text[:-1]), dice_text[-1])
        return text

    def count(self, object):
        """
        Count the number of times a particular rolls has been made. (int)

        Parameters:
        object: The roll to count. (object)
        """
        return self.dice.count(object) + self.held.count(object)

    def hold(self, *values):
        """
        Hold some of the dice from further rolling. (None)

        Parameters:
        *values: The values of the dice to hold.
        """
        for value in values:
            spot = self.dice.index(value)
            self.held.append(self.dice[spot])
            del self.dice[spot]
        self.held.sort()

    def release(self):
        """Make all held dice available for rolling. (None)"""
        self.dice.extend(self.held)
        self.held = []

    def roll(self, index = None):
        """
        Roll the dice in the pool. (list)
        
        Parameters:
        index: The specific die to roll, if any. (int or None)
        """
        if index is not None:
            self.values[index] = self.dice[index].roll()
        else:
            self.values = []
            for die in self.held:
                self.values.append(die.value)
            for die in self.dice:
                self.values.append(die.roll())
        return self.values

    def sort(self, key = None, reverse = False):
        """
        Sort the dice in the pool in place. (None)

        Parameters:
        key: A function returning the value to sort an item by. (callable)
        reverse: A flag for reversing the sort order. (bool)
        """
        all_dice = self.held + self.dice
        all_dice.sort(key = key, reverse = reverse)
        self.values = [die.value for die in all_dice]


class DominoPool(Pool):
    """
    A set of dice based on dominoes. (Pool)

    A domino pool uses dominoes instead of dice. If one of the values on the 
    domino is blank, a normal die is used to replace the blank value. This gives
    a shallower but more staggered distribution of rolls, with more certainty in
    the distribution.

    Attributes:
    population: The set of future values for the pool. (list of tuple of int)
    possible: The possible values for the pool. (list of tuple of int)

    Methods:
    replace: Replace a blank with a value from the filler die. (int)

    Overridden Methods:
    __init__
    __repr__
    replace
    roll
    sort
    """

    def __init__(self, dice = [6, 6], filler = Die(6)):
        """
        Set up the dice in the pool. (None)

        Parameters:
        dice: A list of dice specifications. (list of int)
        filler: The die to use to fill blanks. (Die)
        """
        ranges = [range(x + 1) for x in sorted(dice)]
        self.possible = [prod for prod in itertools.product(*ranges) if sorted(prod) == prod]
        self.population = self.possible[:]
        self.roll()

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

    def roll(self):
        """Roll the pool. (list)"""
        self.values = [self.replace(x) for x in self.population.pop()]
        if not self.population:
            self.population = self.possible[:]
        self.values.sort()

    def sort(self, key = None, reverse = False):
        """Sort the dice in the pool. (list)"""
        pass


if __name__ == '__main__':
    die = Die('die')
    rolls = [die.roll() for roll in range(3)]
    while rolls[-3:] != ['d', 'i', 'e']:
        rolls.append(die.roll())
    print(rolls)