"""
cards_test.py

Unit testing of cards.py

Classes:
CardTest: Tests of the standard Card class. (unittest.TestCase)
CRandTest: Test of the implementation of C's rand function.
DeckTest: Test of the standard Deck class. (unittest.TestCase)
HandTest: Test of the Hand (of cards) class. (unittest.TestCase)
TrackingCardTest: Tests of the TrackingCard class. (unittest.TestCase)
TrackingDeckTest: Tests of the TrackingDeck class. (unittest.TestCase)
"""


import unittest

import t_games.cards as cards


class CardTest(unittest.TestCase):
    """Tests of the standard Card class. (unittest.TestCase)"""

    def setUp(self):
        self.ace = cards.Card('A', 'S')
        self.jack = cards.Card('J', 'H')
        self.joker = cards.Card('X', 'D')

    def testAboveBelow(self):
        """Test Card.above when below."""
        self.assertFalse(self.jack.above(cards.Card('Q', 'H')))

    def testAboveOne(self):
        """Test Card.above when above."""
        self.assertTrue(self.jack.above(cards.Card('T', 'C')))

    def testAboveTwoNo(self):
        """Test Card.above when too far above."""
        self.assertFalse(self.jack.above(cards.Card('9', 'D')))

    def testAboveTwoYes(self):
        """Test Card.above with multi-rank distance."""
        self.assertTrue(self.jack.above(cards.Card('9', 'D'), n = 2))

    def testAboveWrapNo(self):
        """Test Card.above with wrapped ranks."""
        self.assertFalse(self.ace.above(cards.Card('K', 'S')))

    def testAboveWrapYes(self):
        """Test Card.above with wrapped ranks."""
        self.assertTrue(self.ace.above(cards.Card('K', 'S'), wrap_ranks = True))

    def testBelowAbove(self):
        """Test Card.below when below."""
        self.assertFalse(self.jack.below(cards.Card('T', 'H')))

    def testBelowOne(self):
        """Test Card.below when below."""
        self.assertTrue(self.jack.below(cards.Card('Q', 'C')))

    def testBelowTwoNo(self):
        """Test Card.below when too far below."""
        self.assertFalse(self.jack.below(cards.Card('K', 'D')))

    def testBelowTwoYes(self):
        """Test Card.below with multi-rank distance."""
        self.assertTrue(self.jack.below(cards.Card('K', 'D'), n = 2))

    def testBelowWrapNo(self):
        """Test Card.below with wrapped ranks."""
        self.assertFalse(cards.Card('K', 'S').below(self.ace))

    def testBelowWrapYes(self):
        """Test Card.below with wrapped ranks."""
        self.assertTrue(cards.Card('K', 'S').below(self.ace, wrap_ranks = True))

    def testEqualCard(self):
        """Test equality of card and card."""
        self.assertEqual(cards.Card('A', 'S'), self.ace)

    def testEqualCardLower(self):
        """Test equality of card and lower case string."""
        self.assertEqual('jh', self.jack)

    def testEqualCardUpper(self):
        """Test equality of card and upper case string."""
        self.assertEqual('XD', self.joker)

    def testNotEqualCard(self):
        """Test inequality of card and card."""
        self.assertNotEqual(cards.Card('A', 'C'), self.ace)

    def testNotEqualCardLower(self):
        """Test inequality of card and lower case string."""
        self.assertNotEqual('js', self.jack)

    def testNotEqualCardUpper(self):
        """Test inequality of card and upper case string."""
        self.assertNotEqual('2D', self.joker)

    def testNotEqualNotImplemented(self):
        """Test inequality of card and integer."""
        self.assertNotEqual(108, self.ace)

    def testLessThanEqal(self):
        """Test a less than comparison of equalcards."""
        self.assertFalse(self.jack < self.jack)

    def testLessThanNo(self):
        """Test an incorrect less than comparison of cards."""
        self.assertFalse(self.jack < self.ace)

    def testLessThanYes(self):
        """Test a correct less than comparison of cards."""
        self.assertTrue(self.ace < self.jack)

    def testRepr(self):
        """Test the computer readable text representation."""
        self.assertEqual("Card('A', 'S')", repr(self.ace))

    def testReprEqual(self):
        """Test equality of the computer read text representation."""
        Card = cards.Card
        self.assertEqual(eval(repr(self.jack)), self.jack)


class CRandTest(unittest.TestCase):
    """Test of the implementation of C's rand function."""

    def setUp(self):
        self.rand = cards.CRand(801)

    def testRepr(self):
        """Test the computer readable text representation."""
        self.assertEqual('CRand(801)', repr(self.rand))

    def testReprSimilar(self):
        """Test similarity of the computer read text representation."""
        for test in range(18):
            value = self.rand()
        CRand = cards.CRand
        similar = eval(repr(self.rand))
        for test in range(18):
            value = self.rand()
            value = similar()
        self.assertEqual(similar.state, self.rand.state)

    def testReprUsed(self):
        """Test the computer readable text representation after some use."""
        for test in range(18):
            value = self.rand()
        self.assertEqual('CRand({})'.format(self.rand.state), repr(self.rand))


class DeckTest(unittest.TestCase):
    """Test of the standard Deck class. (unittest.TestCase)"""

    def setUp(self):
        self.deck = cards.Deck()

    def testRepr(self):
        """Test the repr of a fresh deck."""
        self.assertEqual('<Deck with 52 cards remaining>', repr(self.deck))

    def testReprDeal(self):
        """Test the repr of a deck after dealing some cards."""
        for deal in range(18):
            card = self.deck.deal()
        self.assertEqual('<Deck with 34 cards remaining>', repr(self.deck))


class HandTest(unittest.TestCase):
    """Test of the Hand (of cards) class. (unittest.TestCase)"""

    def setUp(self):
        self.deck = cards.Deck()
        self.hand = cards.Hand(self.deck)

    def testRepr(self):
        """Test the repr of a hand of cards."""
        for card in range(5):
            self.hand.draw()
        self.assertEqual('<Hand: KS, KH, KD, KC, QS>', repr(self.hand))

    def testReprDiscard(self):
        """Test the repr of a hand of cards after some discards."""
        for card in range(5):
            self.hand.draw()
        self.hand.discard('KH')
        self.hand.discard('KC')
        self.assertEqual('<Hand: KS, KD, QS>', repr(self.hand))

    def testReprEmpty(self):
        """Test the repr of an empty hand of cards."""
        self.assertEqual('<Hand: (empty)>', repr(self.hand))


class MultiTrackingDeckTest(unittest.TestCase):
    """Tests of the MultiTrackingDeck class. (unittest.TestCase)"""

    def setUp(self):
        self.deck = cards.MultiTrackingDeck('dummy game')

    def testRepr(self):
        """Test the debugging text representation."""
        self.assertEqual("<MultiTrackingDeck of TrackingCards for 'dummy game'>", repr(self.deck))


class TrackingCardTest(unittest.TestCase):
    """Tests of the location aware TrackingCard class. (unittest.TestCase)"""

    def setUp(self):
        self.deck = cards.TrackingDeck('dummy game')
        self.ace = self.deck.force('AS', self.deck.cards)
        self.jack = self.deck.force('JH', self.deck.cards)

    def testRepr(self):
        """Test the debugging text representation."""
        self.assertEqual('<TrackingCard AS>', repr(self.ace))


class TrackingDeckTest(unittest.TestCase):
    """Tests of the TrackingDeck class. (unittest.TestCase)"""

    def setUp(self):
        self.deck = cards.TrackingDeck('dummy game')

    def testRepr(self):
        """Test the debugging text representation."""
        self.assertEqual("<TrackingDeck of TrackingCards for 'dummy game'>", repr(self.deck))


if __name__ == '__main__':
    unittest.main()
