"""
dice.py

Dice objects for t_games.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Die: A single die. (object)
ShuffleDie: A die that samples from the range without replacement. (Die)
Pool: A set of dice. (object)
DominoPool: A set of dice based on dominos. (Pool)
"""


import collections
import functools
import itertools
import random

from . import utility


@functools.total_ordering
class Die(object):
    """
    A single die. (object)

    While typically integers, the sides of the die can be any object. Dice can be
    used with most mathematical operators, but there is no support for bit based
    operators like <<. Math with dice is always done by the value attribute (the
    result of the last roll), and never results in a Die object. Use of in-place
    operators is not advised. If die is a Die with value = 3, 'die += 1' will
    assign 4 to die, and die will no longer be an instance of Die.

    Attributes:
    held: A flag for holding the die aside and not rolling it. (bool)
    sides: The sides of the die. (list)
    value: The current value of the die. (object)

    Methods:
    roll: Roll the die. (object)

    Overridden Methods:
    __init__
    __abs__
    __add__
    __complex__
    __divmod__
    __eq__
    __float__
    __floordiv__
    __int__
    __invert__
    __lt__
    __mod__
    __mul__
    __neg__
    __pos__
    __pow__
    __radd__
    __rdivmod__
    __repr__
    __rmod__
    __rmul__
    __rpow__
    __rsub__
    __rtruediv__
    __str__
    __sub__
    __truediv__
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

    def __abs__(self):
        """Absolute value. (object)"""
        return abs(self.value)

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

    def __complex__(self):
        """Convert to a complex number. (complex)"""
        return complex(self.value)

    def __divmod__(self, other):
        """
        Integer division with remainder.

        Parameters:
        other: The item to divide by. (object)
        """
        return (self // other, self % other)

    def __eq__(self, other):
        """
        Equality testing. (bool)

        Parameters:
        other: The item to check for equality. (object)
        """
        # Test by value.
        if isinstance(other, Die):
            return self.value == other.value
        else:
            return self.value == other

    def __float__(self):
        """Convert to a floating point number. (float)"""
        return float(self.value)

    def __floordiv__(self, other):
        """
        Integer division. (object)

        Parameters:
        other: The item to divide by. (object)
        """
        # dice divide by sides.
        if isinstance(other, Die):
            return self.value // other.value
        # Divide value by other objects.
        else:
            return self.value // other

    def __index__(self):
        """Convert to an integer for slicing and other conversions. (int)"""
        return int(self.value)

    def __int__(self):
        """Convert to an integer. (int)"""
        return int(self.value)

    def __invert__(self):
        """Inversion. (object)"""
        return ~self.value

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

    def __mod__(self, other):
        """
        Modulus. (object)

        Parameters:
        other: The item to modulate by. (object)
        """
        # dice modulate by sides.
        if isinstance(other, Die):
            return self.value % other.value
        # Modulate value to other objects.
        else:
            return self.value % other

    def __mul__(self, other):
        """
        Multiplication. (object)

        Parameters:
        other: The item to multiply by. (object)
        """
        # dice multiply by sides.
        if isinstance(other, Die):
            return self.value * other.value
        # Multiply value to other objects.
        else:
            return self.value * other

    def __neg__(self):
        """Negation. (object)"""
        return -self.value

    def __round__(self, ndigits = None):
        """
        Rounding. (float)

        Parameters:
        ndigits: The number of digits to round. (int)
        """
        return round(self.value, ndigits)

    def __pos__(self):
        """Positive value. (object)"""
        return +self.value

    def __pow__(self, other, mod = None):
        """
        Exponentiation. (object)

        Parameters:
        other: The exponent. (object)
        mod: The modulus for ternary pow() calls. (object)
        """
        # Dice exponentiate by sides.
        if isinstance(other, Die):
            power = self.value ** other.value
        # Exponentioate value for other objects.
        else:
            power = self.value ** other
        # Check for modulation.
        if mod is None:
            return power
        else:
            return power % mod

    def __radd__(self, other):
        """
        Right-side addition.

        Parameters:
        other: The item to add to. (object)
        """
        return self + other

    def __rdivmod__(self, other):
        """
        Right hand integer division with remainder.

        Parameters:
        other: The item to divide. (object)
        """
        return (other // self, other % self)

    def __repr__(self):
        """Generate a debugging text representation. (str)"""
        return '<{} {}>'.format(self.__class__.__name__, self.value)

    def __rmod__(self, other):
        """
        Right hand modulus. (object)

        Parameters:
        other: The item to modulate. (object)
        """
        # dice modulate by sides.
        if isinstance(other, Die):
            return other.value % self.value
        # Modulate value to other objects.
        else:
            return other % self.value

    def __rmul__(self, other):
        """
        Right-side multiplication.

        Parameters:
        other: The item to multiply by. (object)
        """
        return self * other

    def __rpow__(self, other, mod = None):
        """
        Right hand exponentiation. (object)

        Parameters:
        other: The item to exponentiate. (object)
        mod: The modulus for ternary pow() calls. (object)
        """
        # Dice exponentiate by sides.
        if isinstance(other, Die):
            power = other.value ** self.value
        # Exponentioate value for other objects.
        else:
            power = other ** self.value
        # Check for modulation.
        if mod is None:
            return power
        else:
            return power % mod

    def __rsub__(self, other):
        """
        Right hand subtraction. (object)

        Parameters:
        other: The item to subtract from. (object)
        """
        # dice subtract by sides.
        if isinstance(other, Die):
            return other.value - self.value
        # Subtract value to other objects.
        else:
            return other - self.value

    def __rtruediv__(self, other):
        """
        Right hand division. (object)

        Parameters:
        other: The item to divide. (object)
        """
        # dice divide by sides.
        if isinstance(other, Die):
            return other.value / self.value
        # Divide value by other objects.
        else:
            return other / self.value

    def __str__(self):
        """Generate a human readable text representation. (str)"""
        if self.held:
            return '{}*'.format(self.value)
        else:
            return str(self.value)

    def __sub__(self, other):
        """
        Subtraction. (object)

        Parameters:
        other: The item to subtract. (object)
        """
        # dice subtract by sides.
        if isinstance(other, Die):
            return self.value - other.value
        # Subtract value to other objects.
        else:
            return self.value - other

    def __truediv__(self, other):
        """
        Division. (object)

        Parameters:
        other: The item to divide by. (object)
        """
        # dice divide by sides.
        if isinstance(other, Die):
            return self.value / other.value
        # Divide value by other objects.
        else:
            return self.value / other

    def copy(self):
        """Create an independent copy of the Die. (Die)"""
        clone = Die(self.sides)
        clone.value = self.value
        return clone

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

    Manipulating the dice attribute directly is dangerous, as it can make the
    values attribute not map to the dice attribute directly. Use the provided list
    like methods instead, which update values as well as dice.

    Attributes:
    dice: The dice in the pool. (list of Die)
    values: The current values of the dice in the pool. (list)

    Methods:
    count: Count the number of times a particular rolls has been made. (int)
    counts: Return counts of the values in the pool. (list of int)
    describe: Returns a dictionary describing the rolls in the pool. (dict)
    extend: Add multiple dice to the end of the Pool. (None)
    hold: Hold some of the dice from further rolling. (None)
    index: Return the index of the die with the specified value. (int)
    insert: Insert a new die into the pool. (None)
    release: Make all held dice available for rolling. (None)
    remove: Remove the first die with the specified value. (None)
    reverse: Reverse the order of the dice in the pool. (None)
    roll: Roll the dice in the pool. (list)
    sort: Sort the dice in the pool in place. (list)

    Overridden Methods:
    __init__
    __contains__
    __delitem__
    __eq__
    __getitem__
    __iadd__
    __iter__
    __len__
    __repr__
    __reversed__
    __setitem__
    __str__
    """

    def __init__(self, dice = [6, 6], roll = True):
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
        if roll:
            self.roll()
        else:
            self.values = [die.value for die in self.dice]

    def __contains__(self, value):
        """
        Checking if the specified value has been rolled. (bool)

        Parameters:
        value: The value to check for. (object)
        """
        return value in self.dice

    def __delitem__(self, key):
        """
        Remove one or more dice. (None)

        Parameters:
        key: The die or dice to remove. (int or slice)
        """
        del self.dice[key]
        del self.values[key]

    def __eq__(self, other):
        """
        Equality check. (bool)

        Parameters:
        other: The item to check equality with. (object)
        """
        if isinstance(other, Pool):
            return self.dice == other.dice
        else:
            return self.values == other

    def __getitem__(self, key):
        """
        Get one or more of the dice. (Die or list)

        Parameters:
        key: The die or dice to get. (int or slice)
        """
        if isinstance(key, slice):
            return Pool(self.dice[key], roll = False)
        else:
            return self.dice[key]

    def __iadd__(self, dice):
        """
        Add multiple dice to the end of the Pool. (None)

        Parameters:
        dice: The dice to add. (sequence of Die)
        """
        self.extend(dice)

    def __iter__(self):
        """Iterate over the dice. (iterator)"""
        return iter(self.dice)

    def __len__(self):
        """Return the number of dice. (int)"""
        return len(self.dice)

    def __repr__(self):
        """Generate debugging text representation. (str)"""
        return '<{} {}>'.format(self.__class__.__name__, self)

    def __reversed__(self):
        """Return a reversed version of the Pool. (Pool)"""
        return Pool(reversed(self.dice), roll = False)

    def __setitem__(self, key, value):
        """
        Modify the pool by index or slice. (None)

        Parameters:
        key: The dice to modify. (int or slice)
        value: The new dice to use. (object)
        """
        self.dice[key] = value
        self.values = [die.value for die in self.dice]

    def __str__(self):
        """Generate human readable text representation. (str)"""
        return utility.oxford(self.dice)

    def append(self, die):
        """
        Add a new die to the end of the Pool. (None)

        Parameter:
        die: The new die to add. (Die)
        """
        self.dice.append(die)
        self.values.append(die.value)

    def copy(self):
        """Create an independent deep copy of the Pool. (Pool)"""
        return Pool([die.copy() for die in self.dice], roll = False)

    def count(self, object):
        """
        Count the number of times a particular rolls has been made. (int)

        Parameters:
        object: The roll to count. (object)
        """
        return self.dice.count(object)

    def counts(self):
        """
        Return counts of the values in the pool. (list of int)

        Returns a list counts such that counts[value] is the number of times value was
        rolled. Will raise an error for non-integer dice, and may be sparse depending
        on the value of self.sides.
        """
        counts = [0] * (max(self.dice[0].sides)  + 1)
        for value in self.values:
            counts[value] += 1
        return counts

    def describe(self):
        """
        Returns a dictionary describing the rolls in the pool. (dict)

        The keys in the dictionary 'min', 'max', 'counts' (counts[value] = # of rolls),
        and 'by_counts' (by_counts[# of rolls] = list of values).
        """
        info = {'counts': [0] * (self.sides[-1]  + 1), 'max': 0, 'min': self.sides[-1] + 1}
        for value in self.values:
            info['counts'][value] += 1
            if value < info['min']:
                info['min'] = value
            if value > info['max']:
                info['max'] = value
        info['by_counts'] = collections.defaultdict(list)
        for value, count in enumerate(info['counts']):
            if count + value:
                info['by_counts'][count].append(value)
        return info

    def extend(self, dice):
        """
        Add multiple dice to the end of the Pool. (None)

        Parameters:
        dice: The dice to add. (sequence of Die)
        """
        self.dice.extend(dice)
        self.values.extend([die.value for die in dice])

    def get_free(self):
        """Return a sub-pool of the un-held dice. (Pool)"""
        return Pool([die for die in self.dice if not die.held], roll = False)

    def get_held(self):
        """Return a sub-pool of the held dice. (Pool)"""
        return Pool([die for die in self.dice if die.held], roll = False)

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
            del unheld[spot]

    def index(self, value, start = 0, end = None):
        """
        Return the index of the die with the specified value. (int)

        Parameters:
        value: The value to search for. (object)
        start: The index to start searching from. (int)
        end: The index to stop searching on. (int)
        """
        if end is None:
            end = len(self)
        while True:
            if start >= end:
                raise ValueError('No die currently has the value {!r}.'.format(value))
            if self.dice[start] == value:
                return start
            start += 1

    def insert(self, index, die):
        """
        Insert a new die into the pool. (None)

        Parameters:
        index: Where to insert the die. (int)
        die: The die to instert. (Die)
        """
        self.dice.insert(index, die)
        self.values.insert(index, die.value)

    def pop(self, index = -1):
        """
        Remove and return a die. (Die)

        Parameters:
        index: The die to remove and return. (int)
        """
        self.values.pop(index)
        return self.dice.pop(index)

    def release(self):
        """Make all held dice available for rolling. (None)"""
        for die in self.dice:
            die.held = False
        self.held = 0

    def remove(self, value):
        """Remove the first die with the specified value. (None)"""
        index = self.dice.index(value)
        del self.dice[index]
        del self.values[index]

    def reverse(self):
        """Reverse the order of the dice in the pool. (None)"""
        self.dice.reverse()
        self.values.reverse()

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