"""
gin_rummy_test.py

Unit testing of gin_rummy_game.py

Classes:
"""


import unittest

from t_games import cards
from t_games.card_games import gin_rummy_game as gin
from t_games.t_tests import unitility


class ParseMeldsTest(unittest.TestCase):
    """Test parsing melds by input by a player. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = gin.GinRummy(self.human, 'none')

    def testBasicRun(self):
        """Test parsing a basic run."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KC', 'AC', '6D', '6H', 'JS', '3S')]
        self.assertEqual(['as', '2s', '3s'], self.game.parse_meld('as 2s 3s', hand))

    def testBasicSet(self):
        """Test parsing a basic set."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KC', 'AC', '6D', '6H', 'JS', '6S')]
        self.assertEqual(['6d', '6h', '6s'], self.game.parse_meld('6D 6H 6S'))

    def testInvalidMeld(self):
        """Test parsing a basic set."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KC', 'AC', '6D', '6H', 'JS', '6S')]
        self.assertEqual(['6d', '6h', '7h'], self.game.parse_meld('6D 6H 7h'))

    def testShortRun(self):
        """Test parsing a shorthand run."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', 'JS', 'QS')]
        self.assertEqual(['js', 'qs', 'ks'], self.game.parse_meld('js-k'))

    def testShortRunDoubleSuit(self):
        """Test parsing a shorthand run with suit specified at start and end."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', '4H', '5H')]
        self.assertEqual(['4h', '6h', '7h'], self.game.parse_meld('4h-6h'))

    def testShortRunEndSuit(self):
        """Test parsing a shorthand run with the suit at the end."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', '7D', '8D')]
        self.assertEqual(['6d', '7d', '8d'], self.game.parse_meld('6-8D'))

    def testShortRunNumAlpha(self):
        """Test parsing a shorthand run crossing the 9/T line."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'TS', 'AC', '6D', '6H', 'JS', '9S')]
        self.assertEqual(['9s', 'ts', 'js'], self.game.parse_meld('9s-t'))

    def testShortRunSpaceAfter(self):
        """Test parsing a shorthand run with a space after the dash."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', 'JS', 'QS')]
        self.assertEqual(['js', 'qs', 'ks'], self.game.parse_meld('js- k'))

    def testShortRunSpaceBefore(self):
        """Test parsing a shorthand run with a space before the dash."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', 'JS', 'QS')]
        self.assertEqual(['js', 'qs', 'ks'], self.game.parse_meld('js -k'))

    def testShortRunSpaceBoth(self):
        """Test parsing a shorthand run with a space before and after the dash."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', 'JS', 'QS')]
        self.assertEqual(['js', 'qs', 'ks'], self.game.parse_meld('js - k'))

    def testShortSet(self):
        """Test parsing a shorthand set."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', 'AH', 'JS', 'QS')]
        self.assertEqual(['as', 'ac', 'ah'], self.game.parse_meld('a'))

    def testShortSetNumber(self):
        """Test parsing a shorthand set using a number rank."""
        hand = [cards.Card(*text) for text in ('AS', '2S', 'KS', 'AC', '6D', '6H', '6S', 'QS')]
        self.assertEqual(['6d', '6h', '6s'], self.game.parse_meld('6'))


if __name__ == '__main__':
    unittest.main()