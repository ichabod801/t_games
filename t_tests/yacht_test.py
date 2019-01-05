"""
yacht_test.py

Unit testing of t_games/dice_games/yacht_game.py.

Constants:
TEST_BOTS: The bots (bachts) for test Yacht. (list of type)

Classes:
BachtBaseTest: Tests of Yacht bots with no options. (unittest.TestCase)
BachtCheerioTest: Tests of Yacht bots with the cheerio option. (TestCase)
BachtGeneralTest: Tests of Yacht bots with the general option. (TestCase)
BachtHindenbergTest: Tests of Yacht bots with the hindenberg option. (TestCase)
BachtYahtzeeTest: Tests of Yacht bots with the yahtzee option. (TestCase)
BachtYamTest: Tests of Yacht bots with the yam option. (unittest.TestCase)
ScoreCategoryTest: Tests of score categories. (unittest.TestCase)
ScoreFunctionsTest: Tests of scoring functions. (unittest.TestCase)
"""


import unittest

from . import unitility
from ..dice_games import yacht_game as yacht


TEST_BOTS = [yacht.Bacht, yacht.Bachter] * 2


BachtBaseTest = unitility.bot_test(yacht.Yacht, TEST_BOTS, 5, [3, 4])


BachtCheerioTest = unitility.bot_test(yacht.Yacht, TEST_BOTS, 5, [3, 4], 'cheerio')


BachtGeneralTest = unitility.bot_test(yacht.Yacht, TEST_BOTS, 5, [3, 4], 'general')


BachtHindenbergTest = unitility.bot_test(yacht.Yacht, TEST_BOTS, 5, [3, 4], 'hindenberg')


BachtYahtzeeTest = unitility.bot_test(yacht.Yacht, TEST_BOTS, 5, [3, 4], 'yahtzee')


BachtYamTest = unitility.bot_test(yacht.Yacht, TEST_BOTS, 5, [3, 4], 'yam')


class ScoreCategoryTest(unittest.TestCase):
    """Tests of score categories. (unittest.TestCase)"""

    def testReprFirst(self):
        """Test a simple points score category repr."""
        category = yacht.ScoreCategory('Broken Straight', 'Nothing', self.zero, '30', 42)
        self.assertEqual('<ScoreCategory Broken Straight (30/42)>', repr(category))

    def testReprNumber(self):
        """Test a simple points score category repr."""
        category = yacht.ScoreCategory('Straight', 'Ascending Ranks', self.zero, '30')
        self.assertEqual('<ScoreCategory Straight (30)>', repr(category))

    def testReprSubTotal(self):
        """Test the default sub-total category repr."""
        category = yacht.ScoreCategory('Eights', 'Eights', self.zero)
        self.assertEqual('<ScoreCategory Eights (Sub-total)>', repr(category))

    def testReprTotal(self):
        """Test a total scoring category repr."""
        category = yacht.ScoreCategory('Second Chance', 'Whatev', self.zero, 'total')
        self.assertEqual('<ScoreCategory Second Chance (Total)>', repr(category))

    def testReprTotalBonus(self):
        """Test a total scoring (with a bonus) category repr."""
        category = yacht.ScoreCategory('Third Chance', 'Whatever', self.zero, 'total+33')
        self.assertEqual('<ScoreCategory Third Chance (Total + 33)>', repr(category))

    def zero(self):
        """Dummy score function for testing score categories."""
        return 0


class ScoreFunctionsTest(unittest.TestCase):
    """Tests of scoring functions. (unittest.TestCase)"""

    def scoreTest(self, values, function, check):
        self.dice.values = values
        self.assertEqual(check, function(self.dice))

    def setUp(self):
        self.dice = yacht.dice.Pool([6] * 5)

    def testFiveKindValid(self):
        """Test a valid five of a kind."""
        self.scoreTest([5, 5, 5, 5, 5], yacht.five_kind, 25)

    def testFiveKindZero(self):
        """Test an invalid five of kind."""
        self.scoreTest([5, 5, 4, 5, 5], yacht.five_kind, 0)

    def testFourKindFive(self):
        """Test five of a kind as four of a kind."""
        self.scoreTest([6, 6, 6, 6, 6], yacht.four_kind, 24)

    def testFourKindValid(self):
        """Test a valid four of a kind."""
        self.scoreTest([6, 6, 6, 3, 6], yacht.four_kind, 24)

    def testFourKindZero(self):
        """Test an invalid four of a kind."""
        self.scoreTest([6, 2, 6, 3, 6], yacht.four_kind, 0)

    def testFullHouseFive(self):
        """Test five of a kind as a full house."""
        self.scoreTest([6, 6, 6, 6, 6], yacht.full_house, 30)

    def testFullHouseHigh(self):
        """Test a full house high die over low."""
        self.scoreTest([5, 5, 5, 4, 4], yacht.full_house, 23)

    def testFullHouseLow(self):
        """Test a full house low die over high."""
        self.scoreTest([2, 3, 2, 3, 2], yacht.full_house, 12)

    def testFullHouseZero(self):
        """Test an invalid full house."""
        self.scoreTest([6, 6, 1, 1, 5], yacht.full_house, 0)

    def testHighStraightBroken(self):
        """Test a high straight with a broken straight."""
        self.scoreTest([1, 2, 6, 5, 4], yacht.straight_high, 0)

    def testHighStraightHigh(self):
        """Test a high straight with a high straight."""
        self.scoreTest([6, 2, 5, 4, 3], yacht.straight_high, 20)

    def testHighStraightLow(self):
        """Test a high straight with a low straight."""
        self.scoreTest([1, 2, 5, 3, 4], yacht.straight_high, 0)

    def testLowStraightBroken(self):
        """Test a low straight with a broken straight."""
        self.scoreTest([1, 2, 6, 5, 4], yacht.straight_low, 0)

    def testLowStraightHigh(self):
        """Test a low straight with a high straight."""
        self.scoreTest([6, 2, 5, 4, 3], yacht.straight_low, 0)

    def testLowStraightLow(self):
        """Test a low straight with a low straight."""
        self.scoreTest([1, 2, 5, 3, 4], yacht.straight_low, 15)

    def testScoreNumberFive(self):
        """Test a score number function with five values."""
        self.scoreTest([4, 4, 4, 4, 4], yacht.score_number(4), 20)

    def testScoreNumberMultiple(self):
        """Test a score number function with more than one value."""
        self.scoreTest([6, 6, 1, 2, 3], yacht.score_number(6), 12)

    def testScoreNumberOne(self):
        """Test a score number function with one value."""
        self.scoreTest([1, 2, 3, 4, 5], yacht.score_number(1), 1)

    def testScoreNumberZero(self):
        """Test a score number function with no values."""
        self.scoreTest([5, 6, 1, 2, 3], yacht.score_number(4), 0)

    def testStraightBroken(self):
        """Test a straight with a broken straight."""
        self.scoreTest([1, 2, 6, 5, 4], yacht.straight, 0)

    def testStraightHigh(self):
        """Test a straight with a high straight."""
        self.scoreTest([6, 2, 5, 4, 3], yacht.straight, 20)

    def testStraightLow(self):
        """Test a straight with a low straight."""
        self.scoreTest([1, 2, 5, 3, 4], yacht.straight, 15)

    def testStrictFourKindFive(self):
        """Test five of a kind as strict four of a kind."""
        self.scoreTest([1, 1, 1, 1, 1], yacht.four_kind_strict, 0)

    def testStrictFourKindValid(self):
        """Test a valid strict four of a kind."""
        self.scoreTest([2, 3, 2, 2, 2], yacht.four_kind_strict, 8)

    def testStrictFourKindZero(self):
        """Test an invalid strict four of a kind."""
        self.scoreTest([4, 5, 3, 3, 3], yacht.four_kind_strict, 0)

    def testStrictFullHouseFive(self):
        """Test five of a kind as a strict full house."""
        self.scoreTest([6, 6, 6, 6, 6], yacht.full_house_strict, 0)

    def testStrictFullHouseHigh(self):
        """Test a strict full house high die over low."""
        self.scoreTest([5, 5, 5, 4, 4], yacht.full_house_strict, 23)

    def testStrictFullHouseLow(self):
        """Test a strict full house low die over high."""
        self.scoreTest([2, 3, 2, 3, 2], yacht.full_house_strict, 12)

    def testStrictFullHouseZero(self):
        """Test an invalid strict full house."""
        self.scoreTest([6, 6, 1, 1, 5], yacht.full_house_strict, 0)

    def testThreeKindFour(self):
        """Test four of a kind as three of a kind."""
        self.scoreTest([1, 1, 2, 1, 1], yacht.three_kind, 3)

    def testThreeKindValid(self):
        """Test a valid three of a kind."""
        self.scoreTest([3, 4, 3, 5, 3], yacht.three_kind, 9)

    def testThreeKindZero(self):
        """Test an invalid three of a kind."""
        self.scoreTest([6, 1, 6, 1, 2], yacht.three_kind, 0)

    def testWildStraightBroken(self):
        """Test a wild straight with a broken straight."""
        self.scoreTest([1, 2, 6, 5, 4], yacht.straight, 0)

    def testWildStraightHigh(self):
        """Test a wild straight with a high straight."""
        self.scoreTest([6, 2, 5, 4, 3], yacht.straight, 20)

    def testWildStraightLow(self):
        """Test a wild straight with a low straight."""
        self.scoreTest([1, 2, 5, 3, 4], yacht.straight, 15)

    def testWildStraightWildBroken(self):
        """Test a wild straight with a wild broken straight."""
        self.scoreTest([1, 2, 6, 5, 4], yacht.straight_wild, 0)

    def testWildStraightWildHigh(self):
        """Test a wild straight with a wild high straight."""
        self.scoreTest([1, 6, 5, 4, 3], yacht.straight_wild, 20)

    def testWildStraightWildLow(self):
        """Test a wild straight with a wild low straight."""
        self.scoreTest([1, 1, 5, 3, 4], yacht.straight_wild, 15)
