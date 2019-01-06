"""
pig_test.py

Automated test of pig_game.py.

Constants:
TEST_BOTS: The bot classes for Pig.

Classes:
PigBotBaseTest: Test the Pig bots w/ no options. (unittest.TestCase)
PigBotEvenTest: Test the Pig bots w/ the even-turns option. (unittest.TestCase)
"""


import unittest

from t_games.dice_games import pig_game as pig
from t_games.t_tests import unitility


TEST_BOTS = [pig.PigBotBasePaceRace, pig.PigBotPaceRace, pig.PigBotRolls, pig.PigBotScoringTurns,
    pig.PigBotValue]


PigBotBaseTest = unitility.bot_test(pig.Pig, TEST_BOTS, 10, [3, 4])


PigBotEvenTest = unitility.bot_test(pig.Pig, TEST_BOTS, 10, [3, 4], 'even-turns')


if __name__ == '__main__':
    unittest.main()