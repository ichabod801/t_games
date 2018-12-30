"""
mate_test.py

Tests of mate_game.py

Constants:
TEST_BOTS: The various bots for Mate. (list of type)

Classes:
MateBotTest: Test Mate using the bots. (unittest.TestCase)
"""


import unittest

import t_games.dice_games.mate_game as mate
import t_tests.unitility as unitility


TEST_BOTS = [mate.MateBot, mate.MateAttackBot, mate.MateDefendBot]


MateBotTest = unitility.bot_test(mate.Mate, TEST_BOTS, 18, [2])


if __name__ == '__main__':
	unittest.main()
