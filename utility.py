"""
Utility functions for tgames.

Constants:
LOC: tgames location. (str)
MAX_INT: The largest allowed integer. (int)
NINETEEN: English words for 1-19. (list of str)
TENS: English words for multiples of 10. (list of str)
THOUSAND_UP: English words for powers of one thousand. (list of str)
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

# The first twenty number words.
NINETEEN = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 
    'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen',
    'nineteen']

# The words for the tens place.
TENS = ['', '', 'twenty', 'thirty', 'fourty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']

# Words for one thousand and higher.
THOUSAND_UP = ['', 'thousand', 'million', 'billion', 'trillion', 'quadrillion', 'quintillion',
    'sextillion', 'septillion', 'octillion', 'nonillion', 'decillion', 'undecillion', 'duodecillion',
    'tredecillion', 'quatturodecillion', 'quindecillion', 'sexdecillion', 'octodecillion',
    'novemdecillion', 'vigintillion']

# Synonyms for 'yes'. 
YES = set(['yes', 'y', '1', 'yup', 'sure', 'affirmative', 'yeah', 'indubitably', 'yep', 'aye', 'ok'])
YES.update(['okay', 'darn tootin', 'roger', 'da', 'si'])


def choose(n, r):
    """
    Combinations [n choose r]. (int)

    Parameters:
    n: The number of items to choose from. (int)
    r: The number of items to choose. (int)
    """
    return int(math.factorial(n) / (math.factorial(r) * math.factorial(n - r)))

def flip():
    """Return a random bit. (int)"""
    return random.choice([1, 0])

def hundred_word(n):
    """
    Give the word form of a number less than 100. (str)

    Parameter:
    n: A number to give the word form of. (int)
    """
    n %= 100
    if n < 20:
        return NINETEEN[n]
    else:
        word = TENS[n // 10]
        if n % 10:
            word = '{}-{}'.format(word, NINETEEN[n % 10])
        return word

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

def number_word(n):
    """
    Give the word form of a number. (str)

    Parameter:
    n: A number to give the word form of. (int)
    """
    word = ''
    level = 0
    while n:
        word = '{} {} {}'.format(thousand_word(n), THOUSAND_UP[level], word).strip()
        n //= 1000
        level += 1
    return word

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

def thousand_word(n):
    """
    Give the word form of a number less than 100. (str)

    Parameter:
    n: A number to give the word form of. (int)
    """
    n %= 1000
    if n < 100:
        return hundred_word(n)
    elif n % 100:
        return '{} hundred {}'.format(NINETEEN[n // 100], hundred_word(n))
    else:
        return '{} hundred'.format(NINETEEN[n // 100])


if __name__ == '__main__':
    test = [1, 0, 1, 1, 1, 0, 1, 1, 0, 0]
    print(test)
    print(streaks(test))
    print(number_word(1023405600070890))