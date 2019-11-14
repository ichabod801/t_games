"""
gin_rummy_test.py

Unit testing of gin_rummy_game.py

Classes:
ParseMeldTest: Test parsing melds by input by a player. (unittest.TestCase)
SpreadTest: Tests of spreading cards at the end of a hand. (unittest.TestCase)
ValidateMeldTest: Test of validating melds. (unittest.TestCase)
"""


import unittest

from t_games import cards
from t_games.card_games import gin_rummy_game as gin
from t_games.t_tests import unitility


class ParseMeldTest(unittest.TestCase):
    """Test parsing melds by input by a player. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = gin.GinRummy(self.human, 'none')
        self.game.set_up()

    def testBasicRun(self):
        """Test parsing a basic run."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KC', 'AC', '6D', '6H', 'JS', '3S')]
        self.assertEqual(['as', '2s', '3s'], self.game.parse_meld('as 2s 3s', hand))

    def testBasicSet(self):
        """Test parsing a basic set."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KC', 'AC', '6D', '6H', 'JS', '6S')]
        self.assertEqual(['6d', '6h', '6s'], self.game.parse_meld('6D 6H 6S', hand))

    def testInvalidMeld(self):
        """Test parsing a basic set."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KC', 'AC', '6D', '6H', 'JS', '6S')]
        self.assertEqual(['6d', '6h', '7h'], self.game.parse_meld('6D 6H 7h', hand))

    def testShortRun(self):
        """Test parsing a shorthand run."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', 'JS', 'QS')]
        self.assertEqual(['JS', 'QS', 'KS'], self.game.parse_meld('js-k', hand))

    def testShortRunDoubleSuit(self):
        """Test parsing a shorthand run with suit specified at start and end."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', '4H', '5H')]
        self.assertEqual(['4H', '5H', '6H'], self.game.parse_meld('4h-6h', hand))

    def testShortRunEndSuit(self):
        """Test parsing a shorthand run with the suit at the end."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', '7D', '8D')]
        self.assertEqual(['6D', '7D', '8D'], self.game.parse_meld('6-8D', hand))

    def testShortRunErrorRank(self):
        """Test parsing a shorthand run with a band rank."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', '7D', '8D')]
        self.assertEqual(['error'], self.game.parse_meld('6-FD', hand))

    def testShortRunErrorSuitless(self):
        """Test parsing a shorthand run with a bad suit."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', '7D', '8D')]
        self.assertEqual(['error'], self.game.parse_meld('6-8', hand))

    def testShortRunNumAlpha(self):
        """Test parsing a shorthand run crossing the 9/T line."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'TS', 'AC', '6D', '6H', 'JS', '9S')]
        self.assertEqual(['9S', 'TS', 'JS'], self.game.parse_meld('9s-j', hand))

    def testShortRunSpaceAfter(self):
        """Test parsing a shorthand run with a space after the dash."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', 'JS', 'QS')]
        self.assertEqual(['JS', 'QS', 'KS'], self.game.parse_meld('js- k', hand))

    def testShortRunSpaceBefore(self):
        """Test parsing a shorthand run with a space before the dash."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', 'JS', 'QS')]
        self.assertEqual(['JS', 'QS', 'KS'], self.game.parse_meld('js -k', hand))

    def testShortRunSpaceBoth(self):
        """Test parsing a shorthand run with a space before and after the dash."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', 'JS', 'QS')]
        self.assertEqual(['JS', 'QS', 'KS'], self.game.parse_meld('js - k', hand))

    def testShortSet(self):
        """Test parsing a shorthand set."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', 'AH', 'JS', 'QS')]
        self.assertEqual(['AS', 'AC', 'AH'], self.game.parse_meld('a', hand))

    def testShortSetErrorBad(self):
        """Test parsing a shorthand set with a bad rank."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', 'AH', 'JS', 'QS')]
        self.assertEqual(['error'], self.game.parse_meld('i', hand))

    def testShortSetErrorMissing(self):
        """Test parsing a shorthand set with a rank not in hand."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', 'AH', 'JS', 'QS')]
        self.assertEqual([], self.game.parse_meld('8', hand))

    def testShortSetNumber(self):
        """Test parsing a shorthand set using a number rank."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', '6S', 'QS')]
        self.assertEqual(['6D', '6H', '6S'], self.game.parse_meld('6', hand))

class SpreadTest(unittest.TestCase):
    """Tests of spreading cards at the end of a hand. (unittest.TestCase)"""
    pass


class ValidateMeldTest(unittest.TestCase):
    """Test of validating melds entered by players. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = gin.GinRummy(self.human, 'none')
        self.game.set_up()

    def testAceKingFail(self):
        """Test an ace-king run without the high-low option."""
        self.assertFalse(self.game.validate_meld(['qs', 'ks', 'as']))

    def testAceKingPass(self):
        """Test an ace-king run without the high-low option."""
        self.game = gin.GinRummy(self.human, 'high-low')
        self.game.set_up()
        self.assertTrue(self.game.validate_meld(['QC', 'KC', 'AC']))

    def testBadRank(self):
        """Test a rank that isn't in the deck."""
        self.assertFalse(self.game.validate_meld(['2d', '3d', 'fd']))

    def testBasicRun(self):
        """Test a basic run."""
        self.assertTrue(self.game.validate_meld(['2s', '3s', '4s']))

    def testBasicRunAlpha(self):
        """Test a basic run with alphabetical ranks."""
        self.assertTrue(self.game.validate_meld(['js', 'qs', 'ks']))

    def testBasicRunNumAlpha(self):
        """Test a basic run crossing the 9/T ranks."""
        self.assertTrue(self.game.validate_meld(['8C', '9C', 'TC']))

    def testBasicSet(self):
        """Test a basic run."""
        self.assertTrue(self.game.validate_meld(['5C', '5D', '5H']))

    def testBrokenRun(self):
        """Test a broken run."""
        self.assertFalse(self.game.validate_meld(['3H', '5H', '6H']))

    def testEightRun(self):
        """Test a four card run."""
        self.assertTrue(self.game.validate_meld(['ah', '2h', '3h', '4h', '5h', '6h', '7h', '8h']))

    def testFourRun(self):
        """Test a four card run."""
        self.assertTrue(self.game.validate_meld(['6d', '7d', '8d', '9d']))

    def testFourSet(self):
        """Test a four card set."""
        self.assertTrue(self.game.validate_meld(['AC', 'AD', 'AS', 'AH']))

    def testHinge(self):
        """Test three cards making a partial set and a partial run."""
        self.assertFalse(self.game.validate_meld(['ac', 'ad', '2d']))

    def testShortRun(self):
        """Test a two card run."""
        self.assertTrue(self.game.validate_meld(['9C', 'TC']))

    def testShortSet(self):
        """Test a two card set."""
        self.assertTrue(self.game.validate_meld(['jd', 'jh']))

    def testSingleton(self):
        """Test one card."""
        self.assertTrue(self.game.validate_meld(['QS']))


if __name__ == '__main__':
    unittest.main()