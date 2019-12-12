"""
Utility functions for tgames.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
FIBONACCI: Fibonacci numbers under 200. (list of int)
LOC: tgames location. (str)
MAX_INT: The largest allowed integer. (int)
NINETEEN: English words for 1-19. (list of str)
ORDINALS: Conversion of cardinal numbers to ordinal numbers. (dict of str: str)
PRIMES: All primes under 200. (list of int)
TENS: English words for multiples of 10. (list of str)
THOUSAND_UP: English words for powers of one thousand. (list of str)
YES: Synonyms for 'yes'. (set of str)

Functions:
choose: Combinations [n choose r]. (int)
flip: Returns a random bit. (int)
hundred_word: Give the word form of a number less than 100. (str)
mean: Calculate the mean of a list of values. (float)
median: Calculate the median of a list of values. (float)
number_plural: Convert a number and word to two words with the plural. (str)
number_word: Give the word form of a number. (str)
oxford: Convert a sequence to a word list with an Oxford comma. (str)
permutations: The number of permutations of n out r objects. (int)
plural: Match the plural/singular form of the word to the number. (str)
pow: Expnonentiation. (number)
streaks: Calculates longest streaks for a sequence. (dict of float: int)
thousand_word: Give the word form of a number less than 100. (str)
"""


import collections
import math
import os
import random
import sys


FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

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

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
    101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197,
    199]

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


def levenshtein(text_a, text_b):
    """
    Determine the Levenshtein distance between two strings. (int)

    Parameters:
    text_a: The first string. (str)
    text_b: The second string. (str)
    """
    # Initialize the matrix.
    matrix = [[0] * (len(text_a) + 1) for row in range(len(text_b) + 1)]
    matrix[0] = list(range(len(text_a) + 1))
    for y in range(len(text_b) + 1):
        matrix[y][0] = y
    # Fill the matrix of edits.
    for x in range(1, len(text_b) + 1):
        for y in range(1, len(text_a) + 1):
            base = [matrix[x - 1][y] + 1, matrix[x][y - 1] + 1]
            if text_b[x - 1] == text_a[y - 1]:
                base.append(matrix[x - 1][y - 1])
            else:
                base.append(matrix[x - 1][y - 1] + 1)
            matrix[x][y] = min(base)
    # Return the final value.
    return matrix[-1][-1]


def mean(values):
    """
    Calculate the mean of a list. (float)

    Parameters:
    values: The list of values. (seq of float)
    """
    return sum(values) / float(len(values))


def median(values):
    """
    Calculate the median of a list. (float)

    Parameters:
    values: The list of values. (seq of float)
    """
    if len(values) % 2:
        return sorted(values)[len(values) // 2]
    else:
        mid_point = len(values) // 2
        values = sorted(values)
        return sum(values[(mid_point - 1):(mid_point + 1)]) / 2.0


def number_plural(number, singular, many = ''):
    """
    Convert the number to a word and get the right form of the word counted. (str)

    Parameters:
    number: The number determining plural or singular. (int)
    single: The singular form of the word. (str)
    many: The plural form of the word, if not a simple + 's'. (str)
    """
    return '{} {}'.format(number_word(number), plural(number, singular, many))


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


def oxford(sequence, conjunction = 'and', word_format = '{}'):
    """
    Convert a sequence to a word list with an Oxford comma. (str)

    Parameters:
    sequence: The items to convert to words. (list)
    conjunction: The conjunction at the end of the list. (str)
    word_format: The format string syntax for each item. (str)
    """
    words = [word_format.format(item) for item in sequence]
    if not words:
        return ''
    elif len(words) == 1:
        return words[0]
    elif len(words) == 2:
        return '{1} {0} {2}'.format(conjunction, *words)
    else:
        return '{}, {} {}'.format(', '.join(words[:-1]), conjunction, words[-1])


def permutations(n, r):
    """
    The number of permutations of r out of n objects. (int)

    Parameters:
    n: The number of objects to choose from. (int)
    r: The number of objects to permute. (int)
    """
    return int(math.factorial(n) / math.factorial(n - r))


def plural(number, singular, many = ''):
    """
    Match the plural/singular form of the word to the number. (str)

    Parameters:
    number: The number determining plural or singular. (int)
    single: The singular form of the word. (str)
    many: The plural form of the word, if not a simple + 's'. (str)
    """
    if number == 1:
        return singular
    elif many:
        return many
    else:
        return '{}s'.format(singular)


def pow(x, y):
    """
    Expnonentiation. (number)

    This  assumes x and y are literal numbers, and preserves order of operations.

    Parameters:
    x: The base. (number)
    y: The exponent. (number)
    """
    result = x ** y
    if x < 0:
        return -abs(result)
    else:
        return result


def streaks(values):
    """
    Calculates longest streaks for a sequence. (dict of float: int)

    Parameters:
    values: The list of values. (seq of float)
    """
    if not values:
        return 0, 0, [0, 0, 0]
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
    # Run the unit testing.
    from t_tests.utility_test import *
    unittest.main()
