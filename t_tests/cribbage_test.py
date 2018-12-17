"""
cribbage_test.py

Automated testing of cribbage_game.py.

Classes:
ScoreHandTest: Test scoring cribbage hands. (unittest.TestCase)
"""


import unittest

import t_games.card_games.cribbage_game as crib
import t_tests.unitility as unitility


class ScoreHandTest(unittest.TestCase):
    """Test scoring cribbage hands. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = crib.Cribbage(self.human, 'none')

    def testFifteenDouble(self):
        """Test scoring 15s with a card working double."""
        hand = [crib.CribCard(*card) for card in ('5S', '4S', '6D', '3H', 'KC')]
        self.assertEqual(2, self.game.score_fifteens(hand))

    def testFifteenFive(self):
        """Test scoring 15 with five cards."""
        hand = [crib.CribCard(*card) for card in ('AS', '4S', '2D', '3H', '5C')]
        self.assertEqual(1, self.game.score_fifteens(hand))

    def testFifteenMax(self):
        """Test scoring four 15s."""
        hand = [crib.CribCard(*card) for card in ('5S', 'TS', 'QD', 'JH', 'KC')]
        self.assertEqual(4, self.game.score_fifteens(hand))

    def testFifteenPair(self):
        """Test scoring 15 with two cards."""
        hand = [crib.CribCard(*card) for card in ('AS', '3S', '5S', '8S', 'JS')]
        self.assertEqual(1, self.game.score_fifteens(hand))

    def testFifteenQuad(self):
        """Test scoring 15 with four cards."""
        hand = [crib.CribCard(*card) for card in ('AS', '4S', '2D', '3H', '7C')]
        self.assertEqual(1, self.game.score_fifteens(hand))

    def testFifteenTen(self):
        """Test scoring 15 with a face card and a five."""
        hand = [crib.CribCard(*card) for card in ('2S', '5S', '2D', '7H', 'QC')]
        self.assertEqual(1, self.game.score_fifteens(hand))

    def testFifteenTrip(self):
        """Test scoring 15 with three cards."""
        hand = [crib.CribCard(*card) for card in ('AS', '4S', '5S', '6H', '7C')]
        self.assertEqual(1, self.game.score_fifteens(hand))

    def testFifteenTwice(self):
        """Test scoring 15s with two sets of cards."""
        hand = [crib.CribCard(*card) for card in ('5S', '4S', '8H', '3H', 'KC')]
        self.assertEqual(2, self.game.score_fifteens(hand))

    def testFlushFive(self):
        """Test a five card flush in a hand."""
        hand = [crib.CribCard(*card) for card in ('AS', '3S', '5S', '8S')]
        self.game.starter = crib.CribCard(*'JS')
        self.game.hands = {'The Crib': []}
        self.assertEqual(5, self.game.score_flush(hand))

    def testFlushFiveCrib(self):
        """Test scoring a five card flush in the crib."""
        hand = [crib.CribCard(*card) for card in ('AS', '3S', '5S', '8S')]
        self.game.starter = crib.CribCard(*'JS')
        self.game.hands = {'The Crib': hand}
        self.assertEqual(5, self.game.score_flush(hand))

    def testFlushFour(self):
        """Test a four card flush in a hand."""
        hand = [crib.CribCard(*card) for card in ('AS', '3S', '5S', '8S')]
        self.game.starter = crib.CribCard(*'JC')
        self.game.hands = {'The Crib': []}
        self.assertEqual(4, self.game.score_flush(hand))

    def testFlushFourCrib(self):
        """Test not scoring a four card flush in the crib."""
        hand = [crib.CribCard(*card) for card in ('AS', '3S', '5S', '8S')]
        self.game.starter = crib.CribCard(*'JC')
        self.game.hands = {'The Crib': hand}
        self.assertEqual(0, self.game.score_flush(hand))

    def testFlushFourNot(self):
        """Test not scoring a four card flush made with the starter card."""
        hand = [crib.CribCard(*card) for card in ('AS', '3C', '5S', '8S')]
        self.game.starter = crib.CribCard(*'JS')
        self.game.hands = {'The Crib': []}
        self.assertEqual(0, self.game.score_flush(hand))

    def testPairDouble(self):
        """Test scoring three of a kind with doubled pairs."""
        hand = [crib.CribCard(*card) for card in ('AD', '3C', '8H', '8S', '8C')]
        self.game.double_pairs = True
        self.assertEqual([('8', 3, 12)], self.game.score_pairs(hand))

    def testPairFour(self):
        """Test scoring four of a kind."""
        hand = [crib.CribCard(*card) for card in ('8D', '3C', '8H', '8S', '8C')]
        self.game.double_pairs = False
        self.assertEqual([('8', 4, 12)], self.game.score_pairs(hand))

    def testPairFull(self):
        """Test scoring a full house."""
        hand = [crib.CribCard(*card) for card in ('3D', '3C', '8H', '8S', '8C')]
        self.game.double_pairs = False
        self.assertEqual(set([('8', 3, 6), ('3', 2, 2)]), set(self.game.score_pairs(hand)))

    def testPairNot(self):
        """Test scoring no pairs."""
        hand = [crib.CribCard(*card) for card in ('AD', '3C', '5H', 'JS', '8C')]
        self.game.double_pairs = False
        self.assertEqual([], self.game.score_pairs(hand))

    def testPairOne(self):
        """Test scoring one pair."""
        hand = [crib.CribCard(*card) for card in ('AD', '3C', '5H', '8S', '8C')]
        self.game.double_pairs = False
        self.assertEqual([('8', 2, 2)], self.game.score_pairs(hand))

    def testPairThree(self):
        """Test scoring three of a kind."""
        hand = [crib.CribCard(*card) for card in ('AD', '3C', '8H', '8S', '8C')]
        self.game.double_pairs = False
        self.assertEqual([('8', 3, 6)], self.game.score_pairs(hand))

    def testPairTwo(self):
        """Test scoring two distinct pairs."""
        hand = [crib.CribCard(*card) for card in ('AD', '5C', '5H', '8S', '8C')]
        self.game.double_pairs = False
        self.assertEqual(set([('5', 2, 2), ('8', 2, 2)]), set(self.game.score_pairs(hand)))

    def testRunFive(self):
        """Test scoring a five card run."""
        hand = [crib.CribCard(*card) for card in ('8D', '5C', '6H', '7S', '9C')]
        self.assertEqual([(5, 1)], self.game.score_runs(hand))

    def testRunFour(self):
        """Test scoring a four card run."""
        hand = [crib.CribCard(*card) for card in ('8D', '6C', '5H', '7S', 'JC')]
        self.assertEqual([(4, 1)], self.game.score_runs(hand))

    def testRunFourTwice(self):
        """Test scoring a four card run twice."""
        hand = [crib.CribCard(*card) for card in ('8D', '6C', '5H', '7S', '5C')]
        self.assertEqual([(4, 2)], self.game.score_runs(hand))

    def testRunThree(self):
        """Test scoring a three card run."""
        hand = [crib.CribCard(*card) for card in ('5C', 'AD', '6H', '9C', '7S')]
        self.assertEqual([(3, 1)], self.game.score_runs(hand))

    def testRunThreeFour(self):
        """Test scoring a three card run four times."""
        hand = [crib.CribCard(*card) for card in ('5C', '7D', '6H', '6C', '7S')]
        self.assertEqual([(3, 4)], self.game.score_runs(hand))


if __name__ == '__main__':
    unittest.main()
