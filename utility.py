"""
Utility functions for tgames.

Functions:
choose: Combinations [n choose r]. (int)
median: Calculate the median of a list of values. (float)
mean: Calculate the mean of a list of values. (float)
percentile: Calculate the percentile of a value in a list. (int)
permutations: The number of permutations of n out r objects. (int)
streaks: Calculates longest streaks for a sequence. (dict of float: int)
"""

import csv
import math
import os
import sys
import textwrap

# English interface text for options. (dict of str: dict)
# text for interface options.
LOCAL_TEXT = {'options': {}}


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
    pass

def mean(values):
    """
    Calculate the mean of a list. (float)

    Parameters:
    values: The list of values. (seq of float)
    """
    pass

def percentile(value, population):
    """
    Calculate the percentile of a value within a population. (int)

    Parameters:
    value: The value to get a percentile for. (float)
    population: The population of values. (seq of float)
    """
    pass

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
    pass