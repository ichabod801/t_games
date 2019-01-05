"""
ninety_nine_test.py

Automated testing of ninety_nine_game.py.

Constants:
TEST_BOTS: The list of bots for bot testing. (list of Bot99)

Classes:
Bot99ChicagoTest: Tests of Ninety Nine / Chicago. (unitest.TestCase)
Bot99JokerTest: Tests of Ninety Nine / joker-rules. (unitest.TestCase)
Bot99Test: Tests of Ninety Nine with no options. (unitest.TestCase)
"""


import unittest

from ..card_games import ninety_nine_game as ninety9
from . import unitility


TEST_BOTS = [ninety9.Bot99, ninety9.Bot99Medium] * 3


Bot99ChicagoTest = unitility.bot_test(ninety9.NinetyNine, TEST_BOTS, 4, [3, 4, 5, 6], 'chicago')


Bot99JokerTest = unitility.bot_test(ninety9.NinetyNine, TEST_BOTS, 4, [3, 4, 5, 6], 'joker-rules')


Bot99Test = unitility.bot_test(ninety9.NinetyNine, TEST_BOTS, 4, [3, 4, 5, 6])
