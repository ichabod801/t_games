"""
mate_test.py

Tests of mate_game.py

Constants:
TEST_BOTS: The various bots for Mate. (list of type)

Classes:
MateBotTest: Test Mate using the bots. (unittest.TestCase)
"""


import unittest

from ..dice_games import mate_game as mate
from . import unitility


TEST_BOTS = [mate.MateBot, mate.MateAttackBot, mate.MateDefendBot]


MateBotTest = unitility.bot_test(mate.Mate, TEST_BOTS, 18, [2])
