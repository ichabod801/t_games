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

    def cardText(self, text):
        """
        Create a list of cards from a string. (list of cards.Card)

        Parameters:
        text: A space delimited list of cards. (str)
        """
        return [cards.Card(*card_text.upper()) for card_text in text.split()]

    def setHand(self, text):
        """
        Set up a hand of cards for a test. (None)

        Parameters:
        text: A space delimited list of cards. (str)
        """
        self.game.hands[self.human.name].cards = self.cardText(text)

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = gin.GinRummy(self.human, 'none')
        self.game.set_up()

    def testBadMeld(self):
        """Test spreading with a bad meld specification."""
        self.setHand('qh qs qc ad 2d 3d 4h 4s 4c 5d')
        self.human.replies = ['q', 'a-3', 'ad-3', '4', '']
        spreads = [self.cardText(spread) for spread in ('qh qs qc', 'ad 2d 3d', '4h 4s 4c')]
        deadwood = [cards.Card(*'5D')]
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))
        self.assertEqual(["\nInvalid meld specification: 'a-3'.\n"], self.human.errors)

    def testBasic(self):
        """Test spreading some basic runs and sets."""
        self.setHand('ac 2c 3c 4d 4h 4s 5c 6c 7c 8d')
        self.human.replies = ['ac 2c 3c', '4d 4h 4s', '5c 6c 7c', '']
        spreads = [self.cardText(spread) for spread in self.human.replies[:-1]]
        deadwood = [cards.Card(*'8D')]
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))

    def testCancel(self):
        """Test resetting during spreading."""
        self.setHand('qh qs qc kd ah 2s 3c 4d 5h 6s')
        self.human.replies = ['q', 'cancel']
        self.game.player_index = 0
        self.assertEqual(([], self.cardText('qh qs qc kd ah 2s 3c 4d 5h 6s')), self.game.spread(self.human))

    def testCancelFail(self):
        """Test resetting during spreading."""
        self.setHand('7c 8c 9c td jh qs kc ad 2h 3s')
        self.human.replies = ['7c-9', 'cancel', '']
        self.game.player_index = 1
        self.game.players.append(unitility.AutoBot())
        self.game.players[-1].name = 'Not {}'.format(self.human.name)
        spreads = [self.cardText('7c 8c 9c')]
        deadwood = self.cardText('td jh qs kc ad 2h 3s')
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))
        self.assertEqual(['\nThe defending player may not cancel.\n'], self.human.errors)

    def testGin(self):
        """Test spreading a basic gin hand."""
        self.setHand('9h 9s 9c 9d th jh qh ks kc kd')
        self.human.replies = ['9h 9s 9c 9d', 'th jh qh', 'ks kc kd', '']
        spreads = [self.cardText(spread) for spread in self.human.replies[:-1]]
        deadwood = []
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))

    def testMultiDead(self):
        """Test spreading with multiple dead cards."""
        self.setHand('4c 4d 4h 5s 6s 7s 8h 9s tc jd')
        self.human.replies = ['4', '5s-7s', '']
        spreads = [self.cardText(spread) for spread in ('4c 4d 4h', '5s 6s 7s')]
        deadwood = self.cardText('8h 9s tc jd')
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))

    def testNoCards(self):
        """Test spreading without the cards in hand."""
        self.setHand('6h 7h 8h ks kd kh 9c tc jc qd')
        self.human.replies = ['6h-7', 'k', '9h-j', '9c-j', '']
        spreads = [self.cardText(spread) for spread in ('6h 7h 8h', 'ks kd kh', '9c tc jc')]
        deadwood = [cards.Card(*'QD')]
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))
        self.assertEqual(["You do not have all of those cards.\n"], self.human.errors)

    def testReset(self):
        """Test resetting during spreading."""
        self.setHand('7h 7s 7c 7d 8d 9d th ts tc jd')
        self.human.replies = ['7', 'reset', '7h 7s 7c', '7d 8d 9d', 'th ts tc', '']
        spreads = [self.cardText(spread) for spread in self.human.replies[2:-1]]
        deadwood = [cards.Card(*'JD')]
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))

    def testShorthand(self):
        """Test spreading using shorthand."""
        self.setHand('ah as ac 2d 3d 4d 5h 5s 5c 6d')
        self.human.replies = ['a', '2d-4', '5', '']
        spreads = [self.cardText(spread) for spread in ('ah as ac', '2d 3d 4d', '5h 5s 5c')]
        deadwood = [cards.Card(*'6D')]
        self.assertEqual((spreads, deadwood), self.game.spread(self.human))


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