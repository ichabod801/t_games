"""
Utility functions for tgames.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
LOC: tgames location. (str)
MAX_INT: The largest allowed integer. (int)
NINETEEN: English words for 1-19. (list of str)
ORDINALS: Conversion of cardinal numbers to ordinal numbers. (dict of str: str)
TENS: English words for multiples of 10. (list of str)
THOUSAND_UP: English words for powers of one thousand. (list of str)
YES: Synonyms for 'yes'. (set of str)

Functions:
choose: Combinations [n choose r]. (int)
flip: Returns a random bit. (int)
hundred_word: Give the word form of a number less than 100. (str)
median: Calculate the median of a list of values. (float)
mean: Calculate the mean of a list of values. (float)
number_word: Give the word form of a number. (str)
permutations: The number of permutations of n out r objects. (int)
streaks: Calculates longest streaks for a sequence. (dict of float: int)
thousand_word: Give the word form of a number less than 100. (str)
"""


import collections
import math
import os
import sys


LOC = os.path.dirname(os.path.abspath(__file__))

try:
    MAX_INT = sys.maxint
except AttributeError:
    MAX_INT = sys.maxsize

NINETEEN = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen',
    'nineteen']

ORDINALS = {'zero': 'zeroth', 'one': 'first', 'two': 'second', 'three': 'third', 'four': 'fourth',
    'five': 'fifth', 'six': 'sixth', 'seven': 'seventh', 'eight': 'eighth', 'nine': 'ninth', 'ten': 'tenth',
    'eleven': 'eleventh', 'twelve': 'twelfth', 'thirteen': 'thirteenth', 'fourteen': 'fourteenth',
    'fifteen': 'fifteenth', 'sixteen': 'sixteenth', 'seventeen': 'seventeenth', 'eighteen': 'eighteenth',
    'nineteen': 'nineteenth', 'twenty': 'twentieth', 'thirty': 'thirtieth', 'forty': 'fortieth',
    'fifty': 'fiftieth', 'sixty': 'sixtieth', 'seventy': 'seventieth', 'eighty': 'eightieth',
    'ninety': 'ninetieth', 'hundred': 'hundredth', 'thousand': 'thousandth', 'million': 'millionth',
    'billion': 'billionth', 'trillion': 'trillionth', 'quadrillion': 'quadrillionth',
    'quintillion': 'quintillionth', 'sextillion': 'sextillionth', 'septillion': 'septillionth',
    'octillion': 'octillionth', 'nonillion': 'nonillionth', 'decillion': 'decillionth',
    'undecillion': 'undecillionth', 'duodecillion': 'duodecillionth', 'tredecillion': 'tredecillionth',
    'quatturodecillion': 'quatturodecillionth', 'quindecillion': 'quindecillionth',
    'sexdecillion': 'sexdecillionth', 'octodecillion': 'octodecillionth', 'novemdecillion':
    'novemdecillionth', 'vigintillion': 'vigintillionth'}

TENS = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']

THOUSAND_UP = ['', 'thousand', 'million', 'billion', 'trillion', 'quadrillion', 'quintillion',
    'sextillion', 'septillion', 'octillion', 'nonillion', 'decillion', 'undecillion', 'duodecillion',
    'tredecillion', 'quatturodecillion', 'quindecillion', 'sexdecillion', 'octodecillion',
    'novemdecillion', 'vigintillion']

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
    # Don't use zero for compound words.
    if not n:
        return ''
    # Numbers under nineteen are predefined.
    elif n < 20:
        return NINETEEN[n]
    # Number over nineteen must be combined with tens place numbers.
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


def number_word(n, ordinal = False):
    """
    Give the word form of a number. (str)

    Parameter:
    n: A number to give the word form of. (int)
    ordinal: A flag for returning an ordinal number. (bool)
    """
    # Handle zero.
    if not n:
        word = NINETEEN[n]
    else:
        # Loop thruogh powers of one thousand.
        word = ''
        level = 0
        while n:
            # Add the thousand word with the word for the power of one thousand.
            word = '{} {} {}'.format(thousand_word(n), THOUSAND_UP[level], word).strip()
            n //= 1000
            level += 1
    # Convert to an ordinal number if requested.
    if ordinal:
        words = word.split()
        if '-' in words[-1]:
            parts = words[-1].split('-')
            parts[-1] = ORDINALS[parts[-1]]
            words[-1] = '-'.join(parts)
        else:
            words[-1] = ORDINALS[words[-1]]
        word = ' '.join(words)
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
    Give the word form of a number less than 1000. (str)

    Parameter:
    n: A number to give the word form of. (int)
    """
    # Force the word to be less than one thousand.
    n %= 1000
    # Handle less than one hunded.
    if n < 100:
        return hundred_word(n)
    # Handle above and below one hundred.
    elif n % 100:
        return '{} hundred {}'.format(NINETEEN[n // 100], hundred_word(n))
    # Handle no hundred words.
    else:
        return '{} hundred'.format(NINETEEN[n // 100])


if __name__ == '__main__':
    test = [1, 0, 1, 1, 1, 0, 1, 1, 0, 0]
    print(test)
    print(streaks(test))
    print(number_word(1023405600070890))
