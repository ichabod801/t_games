"""
Utility functions for tgames.

Constants:
LOC: tgames location. (str)
YES: Synonyms for 'yes'. (set of str)

Functions:
choose: Combinations [n choose r]. (int)
median: Calculate the median of a list of values. (float)
mean: Calculate the mean of a list of values. (float)
percentile: Calculate the percentile of a value in a list. (int)
permutations: The number of permutations of n out r objects. (int)
streaks: Calculates longest streaks for a sequence. (dict of float: int)
"""


import collections
import math
import os
import sys


# tgames location.
LOC = os.path.dirname(os.path.abspath(__file__))

# maximum integer.
try:
    MAX_INT = sys.maxint
except AttributeError:
    MAX_INT = sys.maxsize


# Yes
YES = set(['yes', 'y', '1', 'yup', 'sure', 'affirmative', 'yeah', 'indubitably', 'yep', 'aye', 'ok'])
YES.update(['okay', 'darn tootin', 'roger'])


def choose(n, r):
    """
    Combinations [n choose r]. (int)

    Parameters:
    n: The number of items to choose from. (int)
    r: The number of items to choose. (int)
    """
    return math.factorial(n) / (math.factorial(r) * math.factorial(n - r))

def flip():
    """Return a random bit. (int)"""
    return random.choice([1, 0])

def median(values):
    """
    Calculate the median of a list. (float)

    Parameters:
    values: The list of values. (seq of float)
    """
    return sorted(values)[len(values) // 2]

def mean(values):
    """
    Calculate the mean of a list. (float)

    Parameters:
    values: The list of values. (seq of float)
    """
    return sum(values) / float(len(values))

def permutations(n, r):
    """
    The number of permutations of r out of n objects. (int)

    Parameters:
    n: The number of objects to choose from. (int)
    r: The number of objects to permute. (int)
    """
    return math.factorial(n) / math.factorial(n - r)

def streaks(values):
    """
    Calculates longest streaks for a sequence. (dict of float: int)

    Parameters:
    values: The list of values. (seq of float)
    """
    # Prep the loop.
    previous = values[0]
    lengths = collections.defaultdict(int)
    length = 0
    # Calculate streaks
    for value in values:
        if value == previous:
            length += 1
        else:
            lengths[previous] = max(length, lengths[previous])
            length = 1
            previous = value
    # Record the last streak.
    lengths[value] = max(length, lengths[value])
    # Get notable streaks.
    max_winning = max(max(lengths), 0)
    max_losing = min(min(lengths), 0)
    return length, value, lengths


if __name__ == '__main__':
    test = [1, 0, 1, 1, 1, 0, 1, 1, 0, 0]
    print(test)
    print(streaks(test))