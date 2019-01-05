"""
crazy_eights_test.py

Automated tests of crazy_eights_game.py.

CrazyEightsBotTest: Tests of the CrazyEights bots. (unittest.TestCase)
"""


import unittest

from ..card_games import crazy_eights_game as c8
from . import unitility


TEST_BOTS = [c8.Crazy8Bot, c8.CrazySmartBot, c8.Crazy8Bot, c8.CrazySmartBot, c8.Crazy8Bot, c8.CrazySmartBot]


CrazyEightsBotTest = unitility.bot_test(c8.CrazyEights, TEST_BOTS, 4, [3, 4, 5])


CrazyOptionsBotTest = unitility.bot_test(c8.CrazyEights, TEST_BOTS, 4, [3, 4, 5], 'draw-one multi-score')
