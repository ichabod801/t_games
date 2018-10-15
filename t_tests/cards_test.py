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


import collections
import random
import unittest

import t_games.cards as cards
import t_games.card_games.solitaire_games.solitaire_game as solitaire
from t_tests import unitility


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

    def testLessThanEqual(self):
        """Test a less than comparison of equalcards."""
        self.assertFalse(self.jack < self.jack)

    def testLessThanNo(self):
        """Test an incorrect less than comparison of cards."""
        self.assertFalse(self.jack < self.ace)

    def testLessThanYes(self):
        """Test a correct less than comparison of cards."""
        self.assertTrue(self.ace < self.jack)

    def testRegExBackwards(self):
        """Test the card regular expression on backwards card text."""
        self.assertIsNone(self.ace.card_re.match('dk'))

    def testRegExLower(self):
        """Test the card regular expression on lower case card text."""
        self.assertIsNotNone(self.ace.card_re.match('kd'))

    def testRegExMixed(self):
        """Test the card regular expression on mexed case card text."""
        self.assertIsNotNone(self.ace.card_re.match('aC'))

    def testRegExValid(self):
        """Test the card regular expression on valid card text."""
        self.assertIsNotNone(self.ace.card_re.match('9C'))

    def testRegExWord(self):
        """Test the card regular expression on an English word."""
        self.assertIsNone(self.ace.card_re.match('feline'))

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

    def testCut(self):
        """Test cutting a deck of cards."""
        self.deck.shuffle()
        check = self.deck.cards[:]
        for card in range(18):
            check.append(check.pop(0))
        self.deck.cut(18)
        self.assertEqual(check, self.deck.cards)

    def testCutDeal(self):
        """Test cutting a deck of cards after some have been dealt."""
        self.deck.shuffle()
        for deal in range(18):
            card = self.deck.deal()
        check = self.deck.cards[:]
        for card in range(18):
            check.append(check.pop(0))
        self.deck.cut(18)
        self.assertEqual(check, self.deck.cards)

    def testCutMod(self):
        """Test cutting a deck of cards with a large cut number."""
        self.deck.shuffle()
        check = self.deck.cards[:]
        for card in range(4):
            check.append(check.pop(0))
        self.deck.cut(108)
        self.assertEqual(check, self.deck.cards)

    def testCutNot(self):
        """Test not really cutting a deck of cards."""
        self.deck.shuffle()
        check = self.deck.cards[:]
        self.deck.cut(0)
        self.assertEqual(check, self.deck.cards)

    def testDealCard(self):
        """Test that Deck.deal returns a valid card."""
        self.deck.shuffle()
        card = self.deck.deal()
        valid_rank = card.rank in self.deck.ranks
        valid_suit = card.suit in self.deck.suits
        self.assertTrue(isinstance(card, cards.Card) and valid_rank and valid_suit)

    def testDealDown(self):
        """Test that Deck.deal returns a down card."""
        self.deck.shuffle()
        card = self.deck.deal()
        self.assertFalse(card.up)

    def testDealEmpty(self):
        """Test deck.deal with an empty deck."""
        self.deck.shuffle()
        self.deck.cards, self.deck.discards = self.deck.discards, self.deck.cards
        card = self.deck.deal()
        self.assertEqual(51, len(self.deck.cards))

    def testDealGone(self):
        """Test that Deck.deal removes the card from the deck."""
        self.deck.shuffle()
        card = self.deck.deal()
        self.assertFalse(card in self.deck.cards)

    def testDealTop(self):
        """Test that Deck.deal deals the top card of the deck."""
        self.deck.shuffle()
        check = self.deck.cards[-1]
        card = self.deck.deal()
        self.assertEqual(check, card)

    def testDealUp(self):
        """Test that Deck.deal can return a up card."""
        self.deck.shuffle()
        card = self.deck.deal(up = True)
        self.assertTrue(card.up)

    def testDiscard(self):
        """Test discarding a card."""
        self.deck.shuffle()
        card = self.deck.deal()
        self.deck.discard(card)
        self.assertEqual([card], self.deck.discards)

    def testDiscardDeal(self):
        """Test discarding a card after dealing some cards."""
        self.deck.shuffle()
        for deal in range(9):
            card = self.deck.deal()
        check = self.deck.deal()
        for deal in range(9):
            card = self.deck.deal()
        self.deck.discard(check)
        self.assertEqual([check], self.deck.discards)

    def testDiscardDown(self):
        """Test discarding a card face down."""
        self.deck.shuffle()
        card = self.deck.deal(up = True)
        self.deck.discard(card)
        self.assertFalse(card.up)

    def testDiscardMultiple(self):
        """Test discarding multiple cards."""
        self.deck.shuffle()
        check = []
        for deal in range(9):
            card = self.deck.deal()
            self.deck.discard(card)
            check.append(card)
        self.assertEqual(check, self.deck.discards)

    def testDiscardUp(self):
        """Test discarding a card face down."""
        self.deck.shuffle()
        card = self.deck.deal()
        self.deck.discard(card, up = True)
        self.assertTrue(card.up)

    def testForceCard(self):
        """Test that Deck.force returns a card."""
        self.deck.shuffle()
        card = self.deck.force('9S')
        self.assertTrue(isinstance(card, cards.Card))

    def testForceDown(self):
        """Test that Deck.force can return a down card."""
        self.deck.shuffle()
        card = self.deck.force('QH', up = False)
        self.assertFalse(card.up)

    def testForcePlain(self):
        """Test that forced cards are no longer in the deck."""
        self.deck.shuffle()
        card = self.deck.force('AC')
        self.assertNotIn(card, self.deck.cards)

    def testForceLower(self):
        """Test forcing a card from the deck with lower case text."""
        self.deck.shuffle()
        card = self.deck.force('tc')
        check = cards.Card('T', 'C')
        self.assertEqual(check, card)

    def testForceMixed(self):
        """Test forcing a card from the deck with mixed case text."""
        self.deck.shuffle()
        card = self.deck.force('Jd')
        check = cards.Card('J', 'D')
        self.assertEqual(check, card)

    def testForcePlain(self):
        """Test forcing a card from the deck."""
        self.deck.shuffle()
        card = self.deck.force('8H')
        check = cards.Card('8', 'H')
        self.assertEqual(check, card)

    def testForceUp(self):
        """Test that Deck.force returns an up card."""
        self.deck.shuffle()
        card = self.deck.force('KS')
        self.assertTrue(card.up)

    def testPickCard(self):
        """Test that Deck.pick gets the right card."""
        self.deck.shuffle()
        check = self.deck.cards[18]
        self.assertEqual(check, self.deck.pick(18))

    def testPickUp(self):
        """Test that Deck.pick can get a face down card."""
        self.deck.shuffle()
        card = self.deck.pick(18, up = False)
        self.assertFalse(card.up)

    def testPickGone(self):
        """Test that Deck.pick removes the card."""
        self.deck.shuffle()
        check = self.deck.pick(18)
        self.assertNotIn(check, self.deck.cards)

    def testPickLarge(self):
        """Test that Deck.pick gets the right card with a large number."""
        self.deck.shuffle()
        check = self.deck.cards[8]
        self.assertEqual(check, self.deck.pick(123456))

    def testPickUp(self):
        """Test that Deck.pick gets a face up card."""
        self.deck.shuffle()
        card = self.deck.pick(18)
        self.assertTrue(card.up)

    def testRepr(self):
        """Test the repr of a fresh deck."""
        self.assertEqual('<Deck with 52 cards remaining>', repr(self.deck))

    def testReprDeal(self):
        """Test the repr of a deck after dealing some cards."""
        for deal in range(18):
            card = self.deck.deal()
        self.assertEqual('<Deck with 34 cards remaining>', repr(self.deck))

    def testShuffleDiscards(self):
        """Test that shuffling the deck gets back the discards."""
        self.deck.shuffle()
        for deal in range(18):
            card = self.deck.deal()
            self.deck.discard(card)
        self.deck.shuffle()
        self.assertEqual(52, len(self.deck.cards))

    def testShuffleInPlayCount(self):
        """Test that shuffling does not gets back cards in play (by count)."""
        self.deck.shuffle()
        for deal in range(18):
            card = self.deck.deal()
            card = self.deck.deal()
            self.deck.discard(card)
        self.deck.shuffle()
        self.assertEqual(34, len(self.deck.cards))

    def testShuffleInPlayGone(self):
        """Test that shuffling does not gets back cards in play (by contains)."""
        self.deck.shuffle()
        for deal in range(18):
            in_play = self.deck.deal()
            card = self.deck.deal()
            self.deck.discard(card)
        self.deck.shuffle()
        self.assertNotIn(in_play, self.deck.cards)

    def testShuffleNumbered(self):
        """Test shuffling a deck with a deal number."""
        self.deck.shuffle(801)
        # Deal list from http://fc-solve.shlomifish.org/js-fc-solve/find-deal/
        check = 'ah ac 6s 4c qd 2d 8h 7h 5h 3s 4h 8c jd 5c 4s tc 3d jh as 2h 7s qs qc 9c th 2c js ks kh 2s '
        check += 'td 6h 7d qh 6c kd 3h 3c 9h 5s ts 9s jc 4d 9d ad 6d 8s kc 8d 5d 7c'
        check = [cards.Card(*text.upper()) for text in check.split()]
        check.reverse()
        self.assertEqual(check, self.deck.cards)

    def testShuffleOrder(self):
        """Test that shuffling the deck changes the order."""
        check = self.deck.cards[:]
        self.deck.shuffle()
        self.assertNotEqual(check, self.deck.cards)


class HandTest(unittest.TestCase):
    """Test of the Hand (of cards) class. (unittest.TestCase)"""

    def setUp(self):
        self.deck = cards.Deck()
        self.hand = cards.Hand(self.deck)

    def testBoolFalse(self):
        """Test the bool of an empty hand."""
        self.assertFalse(self.hand)

    def testBoolTrue(self):
        """Test the bool of a hand with cards in it."""
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        self.assertTrue(self.hand)

    def testBoolTrueFalse(self):
        """Test the bool of a hand that discard all of its cards."""
        for deal in range(5):
            self.hand.draw()
        self.hand.discard()
        self.assertFalse(self.hand)

    def testContainsGone(self):
        """Test contains for a card that used to be in the hand."""
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        check = self.hand.cards[2]
        self.hand.discard()
        self.assertNotIn(check, self.hand)

    def testContainsNo(self):
        """Test contains for a card not in the hand."""
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        check = self.deck.cards[2]
        self.assertNotIn(check, self.hand)

    def testContainsYes(self):
        """Test contains for a card in the hand."""
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        check = self.hand.cards[2]
        self.assertIn(check, self.hand)

    def testDrawCard(self):
        """Test drawing a card from the deck."""
        self.deck.shuffle()
        check = self.deck.cards[-1]
        self.hand.draw()
        self.assertEqual([check], self.hand.cards)

    def testDrawDown(self):
        """Test drawing a down card from the deck."""
        self.deck.shuffle()
        self.hand.draw(up = False)
        self.assertFalse(self.hand.cards[0].up)

    def testDrawUp(self):
        """Test drawing a down card from the deck."""
        self.deck.shuffle()
        self.hand.draw()
        self.assertTrue(self.hand.cards[0].up)

    def testDiscardAll(self):
        """Test that discarding a whole hand sends it to the discard pile."""
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        discards = self.hand.cards[:]
        self.hand.discard()
        self.assertEqual(discards, self.deck.discards)

    def testDiscardCard(self):
        """Test discarding a specific card puts it in the discard pile."""
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        discard = random.choice(self.hand.cards)
        self.hand.discard(discard)
        self.assertEqual([discard], self.deck.discards)

    def testDiscardEmpty(self):
        """Test that discarding a whole hand leaves the hand empty."""
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        self.hand.discard()
        self.assertEqual([], self.hand.cards)

    def testDiscardGone(self):
        """Test discarding a specific card removes it from the hand.."""
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        discard = random.choice(self.hand.cards)
        self.hand.discard(discard)
        self.assertNotIn(discard, self.hand.cards)

    def testIter(self):
        """Test the iterator for a hand."""
        self.assertEqual(list(self.hand), self.hand.cards)

    def testLenEmpty(self):
        """Test the len of a hand."""
        self.assertEqual(0, len(self.hand))

    def testLenFull(self):
        """Test the length of a hand with cards."""
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        self.assertEqual(5, len(self.hand))

    def testLenGone(self):
        """Test the length of a hand that has discarded cards."""
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        self.hand.discard(self.hand.cards[0])
        self.hand.discard(self.hand.cards[-1])
        self.assertEqual(3, len(self.hand))

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

    def testShiftGone(self):
        """Test that a shifted card is not in the old hand."""
        other = cards.Hand(self.deck)
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        card = random.choice(self.hand.cards)
        self.hand.shift(card, other)
        self.assertNotIn(card, self.hand.cards)

    def testShiftIn(self):
        """Test that a shifted card is in the new hand."""
        other = cards.Hand(self.deck)
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        card = random.choice(self.hand.cards)
        self.hand.shift(card, other)
        self.assertIn(card, other.cards)

    def testShowPlayerDown(self):
        """Test show player when the cards are down."""
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        check = str(self.hand)
        for card in self.hand:
            card.down = False
        self.assertEqual(check, self.hand.show_player())

    def testShowPlayerUp(self):
        """Test show player when the cards are up."""
        self.deck.shuffle()
        for card in range(5):
            self.hand.draw()
        check = str(self.hand)
        self.assertEqual(check, self.hand.show_player())

    def testStrEmpty(self):
        """Test the string version of an empty hand."""
        self.assertEqual('', str(self.hand))

    def testStrFull(self):
        """Test the string version of a hand with cards in it."""
        self.deck.shuffle()
        check = ''
        for card in range(5):
            self.hand.draw()
            check = '{}, {}'.format(check, self.hand.cards[-1])
        check = check[2:]
        self.assertEqual(check, str(self.hand))

    def testStrOne(self):
        """Test the string version of a hand with one card in it."""
        self.deck.shuffle()
        check = self.deck.cards[-1].rank + self.deck.cards[-1].suit
        self.hand.draw()
        self.assertEqual(check, str(self.hand))

class MultiTrackingDeckTest(unittest.TestCase):
    """Tests of the MultiTrackingDeck class. (unittest.TestCase)"""

    def setUp(self):
        self.game = unitility.ProtoObject(reserve = [[], [], []], cells = [], waste = [],
            tableau = [[], [], []])
        self.deck = cards.MultiTrackingDeck(self.game)

    def testFindBlank(self):
        """Find a card with no location indicator."""
        self.deck.shuffle()
        card = self.deck.deal(self.game.cells)
        self.assertIn(card, self.deck.find(str(card)))

    def testFindMultiple(self):
        """Find a card with a full location indicator."""
        self.deck.shuffle()
        card = self.deck.deal(self.game.reserve[1])
        self.assertEqual([card], self.deck.find(str(card) + '-R2'))

    def testFindSingle(self):
        """Find a card with just a alphabetic location indicator."""
        self.deck.shuffle()
        card = self.deck.deal(self.game.waste)
        self.assertEqual([card], self.deck.find(str(card) + '-W'))

    def testFindTableau(self):
        """Find a card with just a numeric location indicator."""
        self.deck.shuffle()
        card = self.deck.deal(self.game.tableau[2])
        self.assertEqual([card], self.deck.find(str(card) + '-3'))

    def testRepr(self):
        """Test the debugging text representation."""
        check = '<MultiTrackingDeck of TrackingCards for {!r}>'.format(self.game)
        self.assertEqual(check, repr(self.deck))


class TrackingCardTest(unittest.TestCase):
    """Tests of the location aware TrackingCard class. (unittest.TestCase)"""

    game_tuple = collections.namedtuple('game_tuple', 'wrap_ranks')

    def setUp(self):
        self.game = self.game_tuple(wrap_ranks = False)
        self.deck = cards.TrackingDeck(self.game)
        self.ace = self.deck.force('AS', self.deck.cards)
        self.jack = self.deck.force('JH', self.deck.cards)

    def testAboveBelow(self):
        """Test TrackingCard.above when below."""
        self.assertFalse(self.jack.above(cards.TrackingCard('Q', 'H', self.deck)))

    def testAboveOne(self):
        """Test TrackingCard.above when above."""
        self.assertTrue(self.jack.above(cards.TrackingCard('T', 'C', self.deck)))

    def testAboveTwoNo(self):
        """Test TrackingCard.above when too far above."""
        self.assertFalse(self.jack.above(cards.TrackingCard('9', 'D', self.deck)))

    def testAboveTwoYes(self):
        """Test TrackingCard.above with multi-rank distance."""
        self.assertTrue(self.jack.above(cards.TrackingCard('9', 'D', self.deck), card_index = 2))

    def testAboveWrapNo(self):
        """Test TrackingCard.above with wrapped ranks."""
        self.assertFalse(self.ace.above(cards.TrackingCard('K', 'S', self.deck)))

    def testAboveWrapYes(self):
        """Test TrackingCard.above with wrapped ranks."""
        self.deck.game = self.game_tuple(wrap_ranks = True)
        self.assertTrue(self.ace.above(cards.TrackingCard('K', 'S', self.deck)))

    def testBelowAbove(self):
        """Test TrackingCard.below when below."""
        self.assertFalse(self.jack.below(cards.TrackingCard('T', 'H', self.deck)))

    def testBelowOne(self):
        """Test TrackingCard.below when below."""
        self.assertTrue(self.jack.below(cards.TrackingCard('Q', 'C', self.deck)))

    def testBelowTwoNo(self):
        """Test TrackingCard.below when too far below."""
        self.assertFalse(self.jack.below(cards.TrackingCard('K', 'D', self.deck)))

    def testBelowTwoYes(self):
        """Test TrackingCard.below with multi-rank distance."""
        self.assertTrue(self.jack.below(cards.TrackingCard('K', 'D', self.deck), card_index = 2))

    def testBelowWrapNo(self):
        """Test TrackingCard.below with wrapped ranks."""
        self.assertFalse(cards.TrackingCard('K', 'S', self.deck).below(self.ace))

    def testBelowWrapYes(self):
        """Test TrackingCard.below with wrapped ranks."""
        self.deck.game = self.game_tuple(wrap_ranks = True)
        self.assertTrue(cards.TrackingCard('K', 'S', self.deck).below(self.ace))

    def testEqualSelf(self):
        """Test that a TrackingCard is equal to iteslf."""
        self.assertEqual(self.ace, self.ace)

    def testEqualSimilar(self):
        """Test that TrackingCard is not equal to one of the same rank and suit."""
        check = cards.TrackingCard('A', 'S', self.deck)
        self.assertNotEqual(check, self.ace)

    def testEqualStringNo(self):
        """Test that TrackingCard is not equal to a different string."""
        self.assertNotEqual('AC', self.ace)

    def testEqualStringYes(self):
        """Test that Tracking card is equal to a similar string."""
        self.assertEqual('AS', self.ace)

    def testEqualUntrackedNo(self):
        """Test that a TrackingCard is not equal to a different untracked card."""
        check = cards.Card('2', 'C')
        self.assertNotEqual(check, self.jack)

    def testEqualUntrackedYes(self):
        """Test that a TrackingCard is equal to a similar untracked card."""
        check = cards.Card('J', 'H')
        self.assertEqual(check, self.jack)

    def testRepr(self):
        """Test the debugging text representation."""
        self.assertEqual('<TrackingCard AS>', repr(self.ace))


class TrackingDeckTest(unittest.TestCase):
    """Tests of the TrackingDeck class. (unittest.TestCase)"""

    def setUp(self):
        self.game = solitaire.Solitaire(unitility.AutoBot(), 'none')
        self.deck = cards.TrackingDeck(self.game)
        self.game.deck = self.deck

    def testDealCard(self):
        """Test that Deck.deal returns a valid card."""
        self.deck.shuffle()
        card = self.deck.deal([])
        valid_rank = card.rank in self.deck.ranks
        valid_suit = card.suit in self.deck.suits
        self.assertTrue(isinstance(card, cards.Card) and valid_rank and valid_suit)

    def testDealDown(self):
        """Test that Deck.deal returns a down card."""
        self.deck.shuffle()
        card = self.deck.deal([], face_up = False)
        self.assertFalse(card.up)

    def testDealInPlayDeck(self):
        """Test that Deck.deal puts the card in play per deck."""
        self.deck.shuffle()
        dummy_location = []
        card = self.deck.deal(dummy_location)
        self.assertEqaul(dummy_location, card.game_location)

    def testDealGone(self):
        """Test that Deck.deal removes the card from the deck."""
        self.deck.shuffle()
        card = self.deck.deal([])
        self.assertNotIn(card, self.deck.cards)

    def testDealInPlayDeck(self):
        """Test that Deck.deal puts the card in play per deck."""
        self.deck.shuffle()
        card = self.deck.deal([])
        self.assertIn(card, self.deck.in_play)

    def testDealInPlayCard(self):
        """Test that Deck.deal puts the card in play per card."""
        self.deck.shuffle()
        card = self.deck.deal([])
        self.assertIn(card, card.deck_location)

    def testDealTop(self):
        """Test that Deck.deal deals the top card of the deck."""
        self.deck.shuffle()
        check = self.deck.cards[-1]
        card = self.deck.deal([])
        self.assertEqual(check, card)

    def testDealUp(self):
        """Test that Deck.deal can return a up card."""
        self.deck.shuffle()
        card = self.deck.deal([])
        self.assertTrue(card.up)

    def testDiscard(self):
        """Test discarding a card."""
        self.deck.shuffle()
        card = self.deck.deal([])
        self.deck.discard(card)
        self.assertEqual([card], self.deck.discards)

    def testDiscardDeal(self):
        """Test discarding a card after dealing some cards."""
        self.deck.shuffle()
        for deal in range(9):
            card = self.deck.deal([])
        check = self.deck.deal([])
        for deal in range(9):
            card = self.deck.deal([])
        self.deck.discard(check)
        self.assertEqual([check], self.deck.discards)

    def testDiscardDeckDiscard(self):
        """Test that a discarded card's deck location is the discard pile."""
        pile = []
        self.deck.shuffle()
        card = self.deck.deal(pile)
        self.deck.discard(card)
        self.assertEqual(card.deck_location, self.deck.discards)

    def testDiscardInPlay(self):
        """Test that a discarded card is removed from play."""
        self.deck.shuffle()
        card = self.deck.deal([])
        self.deck.discard(card)
        self.assertNotIn(card, self.deck.in_play)

    def testDiscardGameDiscard(self):
        """Test that a discarded card's game location is the discard pile."""
        pile = []
        self.deck.shuffle()
        card = self.deck.deal(pile)
        self.deck.discard(card)
        self.assertEqual(card.game_location, self.deck.discards)

    def testDiscardGameGone(self):
        """Test that a discarded card is removed from it's game location."""
        pile = []
        self.deck.shuffle()
        card = self.deck.deal(pile)
        self.deck.discard(card)
        self.assertNotIn(card, pile)

    def testDiscardMultiple(self):
        """Test discarding multiple cards."""
        self.deck.shuffle()
        check = []
        for deal in range(9):
            card = self.deck.deal([])
            self.deck.discard(card)
            check.append(card)
        self.assertEqual(check, self.deck.discards)

    def testShuffleDeckLocation(self):
        """Test shuffle on discard's deck location."""
        self.deck.shuffle()
        card = self.deck.deal([])
        self.deck.discard(card)
        self.deck.shuffle()
        self.assertEqual(card.deck_location, self.deck.cards)

    def testShuffleGameLocation(self):
        """Test shuffle on discard's game location."""
        self.deck.shuffle()
        card = self.deck.deal([])
        self.deck.discard(card)
        self.deck.shuffle()
        self.assertEqual(card.game_location, self.deck.cards)

    def testRepr(self):
        """Test the debugging text representation."""
        check = "<TrackingDeck of TrackingCards for <Game of Solitaire Base with 1 player>>"
        self.assertEqual(check, repr(self.deck))

    def testStrAllNumbers(self):
        """Test the human readable text representation with discarded and in-play cards."""
        for deal in range(18):
            card = self.deck.deal([])
            card = self.deck.deal([])
            self.deck.discard(card)
        check = 'Deck of cards with 16 cards, plus 18 cards in play and 18 cards discarded'
        self.assertEqual(check, str(self.deck))

    def testStrDiscards(self):
        """Test the human readable text representation with discarded cards."""
        for deal in range(18):
            card = self.deck.deal([])
            self.deck.discard(card)
        check = 'Deck of cards with 34 cards, plus 0 cards in play and 18 cards discarded'
        self.assertEqual(check, str(self.deck))

    def testStrInPlay(self):
        """Test the human readable text representation with cards in play."""
        for deal in range(18):
            card = self.deck.deal([])
        check = 'Deck of cards with 34 cards, plus 18 cards in play and 0 cards discarded'
        self.assertEqual(check, str(self.deck))

    def testStrStart(self):
        """Test the human readable text representation at the start."""
        check = 'Deck of cards with 52 cards, plus 0 cards in play and 0 cards discarded'
        self.assertEqual(check, str(self.deck))


if __name__ == '__main__':
    unittest.main()
