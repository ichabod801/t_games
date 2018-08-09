"""
cards_test.py

Unit testing of cards.py

Classes:
CardTest: Tests of the standard Card class. (unittest.TestCase)
CRandTest: Test of the implementation of C's rand function.
DeckTest: Test of the standard Deck class. (unittest.TestCase)
"""


import unittest

import t_games.cards as cards


class CardTest(unittest.TestCase):
    """Tests of the standard Card class. (unittest.TestCase)"""

    def setUp(self):
        self.ace = cards.Card('A', 'S')
        self.jack = cards.Card('J', 'H')
        self.joker = cards.Card('X', 'D')

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


if __name__ == '__main__':
    unittest.main()
