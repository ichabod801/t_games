"""
cribbage_test.py

Automated testing of cribbage_game.py.

Classes:
CribBotsFourTest: Bot test of the partnership game. (unittest.TestCase)
CribBotsFiveTest: Bot test of the five-card game. (unittest.TestCase)
CribBotsSevenTest: Bot test of the seven-card game. (unittest.TestCase)
CribBotsThreeTest: Bot test of the three player game. (unittest.TestCase)
CribBotsTest: Bot test of the basic game. (unittest.TestCase)
ScoreHandTest: Test scoring cribbage hands. (unittest.TestCase)
ScorePeggingTest: Test scoring cribbage plays. (unittest.TestCase)
"""


import unittest

from t_games.card_games import cribbage_game as crib
from t_games.t_tests import unitility


CribBotsFourTest = unitility.bot_test(crib.Cribbage, [crib.CribBot] * 4, 2, [4], 'four-partners')


CribBotsFiveTest = unitility.bot_test(crib.Cribbage, [crib.CribBot, crib.CribBot], 4, [2], 'five-card')


CribBotsSevenTest = unitility.bot_test(crib.Cribbage, [crib.CribBot, crib.CribBot], 4, [2], 'seven-card')


CribBotsTest = unitility.bot_test(crib.Cribbage, [crib.CribBot, crib.CribBot], 4, [2])


CribBotsThreeTest = unitility.bot_test(crib.Cribbage, [crib.CribBot] * 3, 3, [3], 'three-solo')


class ScoreHandTest(unittest.TestCase):
    """Test scoring cribbage hands. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot(['n'])
        self.game = crib.Cribbage(self.human, 'no-cut no-pick')
        self.game.set_up()

    def testFifteenDouble(self):
        """Test scoring 15s with a card working double."""
        hand = self.game.deck.parse_text('5S 4S 6D 3H KC')
        self.assertEqual(2, self.game.score_fifteens(hand))

    def testFifteenFive(self):
        """Test scoring 15 with five cards."""
        hand = self.game.deck.parse_text('AS 4S 2D 3H 5C')
        self.assertEqual(1, self.game.score_fifteens(hand))

    def testFifteenMax(self):
        """Test scoring four 15s."""
        hand = self.game.deck.parse_text('5S TS QD JH KC')
        self.assertEqual(4, self.game.score_fifteens(hand))

    def testFifteenPair(self):
        """Test scoring 15 with two cards."""
        hand = self.game.deck.parse_text('AS 3S 5S 8S JS')
        self.assertEqual(1, self.game.score_fifteens(hand))

    def testFifteenQuad(self):
        """Test scoring 15 with four cards."""
        hand = self.game.deck.parse_text('AS 4S 2D 3H 7C')
        self.assertEqual(1, self.game.score_fifteens(hand))

    def testFifteenTen(self):
        """Test scoring 15 with a face card and a five."""
        hand = self.game.deck.parse_text('2S 5S 2D 7H QC')
        self.assertEqual(1, self.game.score_fifteens(hand))

    def testFifteenTrip(self):
        """Test scoring 15 with three cards."""
        hand = self.game.deck.parse_text('AS 4S 5S 6H 7C')
        self.assertEqual(1, self.game.score_fifteens(hand))

    def testFifteenTwice(self):
        """Test scoring 15s with two sets of cards."""
        hand = self.game.deck.parse_text('5S 4S 8H 3H KC')
        self.assertEqual(2, self.game.score_fifteens(hand))

    def testFlushFive(self):
        """Test a five card flush in a hand."""
        hand = self.game.deck.parse_text('AS 3S 5S 8S')
        self.game.starter = self.game.deck.parse_text('JS')
        self.game.hands = {'The Crib': []}
        self.assertEqual(5, self.game.score_flush(hand))

    def testFlushFiveCrib(self):
        """Test scoring a five card flush in the crib."""
        hand = self.game.deck.parse_text('AS 3S 5S 8S')
        self.game.starter = self.game.deck.parse_text('JS')
        self.game.hands = {'The Crib': hand}
        self.assertEqual(5, self.game.score_flush(hand))

    def testFlushFour(self):
        """Test a four card flush in a hand."""
        hand = self.game.deck.parse_text('AS 3S 5S 8S')
        self.game.starter = self.game.deck.parse_text('JC')
        self.game.hands = {'The Crib': []}
        self.assertEqual(4, self.game.score_flush(hand))

    def testFlushFourCrib(self):
        """Test not scoring a four card flush in the crib."""
        hand = self.game.deck.parse_text('AS 3S 5S 8S')
        self.game.starter = self.game.deck.parse_text('JC')
        self.game.hands = {'The Crib': hand}
        self.assertEqual(0, self.game.score_flush(hand))

    def testFlushFourNot(self):
        """Test not scoring a four card flush made with the starter card."""
        hand = self.game.deck.parse_text('AS 3C 5S 8S')
        self.game.starter = self.game.deck.parse_text('JS')
        self.game.hands = {'The Crib': []}
        self.assertEqual(0, self.game.score_flush(hand))

    def testMaximum(self):
        """Test scoring the best possible hand)."""
        hand = self.game.deck.parse_text('5D 5C 5H JS')
        self.game.starter = self.game.deck.parse_text('5S')
        self.game.double_pairs = False
        self.assertEqual(29, self.game.score_one_hand(hand, 'Bob'))

    def testNob(self):
        """Test scoring his nob (jack of the starter suit)."""
        hand = self.game.deck.parse_text('AS 3C 7S JS')
        self.game.starter = self.game.deck.parse_text('9S')
        self.game.double_pairs = False
        self.assertEqual(1, self.game.score_one_hand(hand, 'Bob'))

    def testNothing(self):
        """Test scoring a worthless hand."""
        hand = self.game.deck.parse_text('4S 7C 9S QS')
        self.game.starter = self.game.deck.parse_text('TS')
        self.game.double_pairs = False
        self.assertEqual(0, self.game.score_one_hand(hand, 'Bob'))

    def testPairDouble(self):
        """Test scoring three of a kind with doubled pairs."""
        hand = self.game.deck.parse_text('AD 3C 8H 8S 8C')
        self.game.double_pairs = True
        self.assertEqual([('8', 3, 12)], self.game.score_pairs(hand))

    def testPairFour(self):
        """Test scoring four of a kind."""
        hand = self.game.deck.parse_text('8D 3C 8H 8S 8C')
        self.game.double_pairs = False
        self.assertEqual([('8', 4, 12)], self.game.score_pairs(hand))

    def testPairFull(self):
        """Test scoring a full house."""
        hand = self.game.deck.parse_text('3D 3C 8H 8S 8C')
        self.game.double_pairs = False
        self.assertEqual(set([('8', 3, 6), ('3', 2, 2)]), set(self.game.score_pairs(hand)))

    def testPairNot(self):
        """Test scoring no pairs."""
        hand = self.game.deck.parse_text('AD 3C 5H JS 8C')
        self.game.double_pairs = False
        self.assertEqual([], self.game.score_pairs(hand))

    def testPairOne(self):
        """Test scoring one pair."""
        hand = self.game.deck.parse_text('AD 3C 5H 8S 8C')
        self.game.double_pairs = False
        self.assertEqual([('8', 2, 2)], self.game.score_pairs(hand))

    def testPairThree(self):
        """Test scoring three of a kind."""
        hand = self.game.deck.parse_text('AD 5C 8H 8S 8C')
        self.game.double_pairs = False
        self.assertEqual([('8', 3, 6)], self.game.score_pairs(hand))

    def testPairTwo(self):
        """Test scoring two distinct pairs."""
        hand = self.game.deck.parse_text('AD 5C 5H 8S 8C')
        self.game.double_pairs = False
        self.assertEqual(set([('5', 2, 2), ('8', 2, 2)]), set(self.game.score_pairs(hand)))

    def testRunFive(self):
        """Test scoring a five card run."""
        hand = self.game.deck.parse_text('8D 5C 6H 7S 9C')
        self.assertEqual([(5, 1)], self.game.score_runs(hand))

    def testRunFour(self):
        """Test scoring a four card run."""
        hand = self.game.deck.parse_text('8D 6C 5H 7S JC')
        self.assertEqual([(4, 1)], self.game.score_runs(hand))

    def testRunFourTwo(self):
        """Test scoring a four card run twice."""
        hand = self.game.deck.parse_text('8D 6C 5H 7S 5C')
        self.assertEqual([(4, 2)], self.game.score_runs(hand))

    def testRunFourFour(self):
        """Test scoring a four card run four times."""
        hand = self.game.deck.parse_text('8D 6C 5H 7S 5C 8S')
        self.assertEqual([(4, 4)], self.game.score_runs(hand))

    def testRunThree(self):
        """Test scoring a three card run."""
        hand = self.game.deck.parse_text('5C AD 6H 9C 7S')
        self.assertEqual([(3, 1)], self.game.score_runs(hand))

    def testRunThreeEight(self):
        """Test scoring a three card run eight times."""
        hand = self.game.deck.parse_text('5C 7D 6H 6C 7S 5D')
        self.assertEqual([(3, 8)], self.game.score_runs(hand))

    def testRunThreeFour(self):
        """Test scoring a three card run four times."""
        hand = self.game.deck.parse_text('7H 5C 7D 6H 7C 7S')
        self.assertEqual([(3, 4)], self.game.score_runs(hand))

    def testRunThreeSix(self):
        """Test scoring a three card run six times."""
        hand = self.game.deck.parse_text('5C 7D 6H 6C 7S 7H')
        self.assertEqual([(3, 6)], self.game.score_runs(hand))

    def testRunThreeTwice(self):
        """Test scoring two three card runs."""
        hand = self.game.deck.parse_text('5C 7D TH 6C QS JH')
        self.assertEqual([(3, 1), (3, 1)], self.game.score_runs(hand))

    def testRunTwo(self):
        """Test not scoring a two card run."""
        hand = self.game.deck.parse_text('5C 2D TH 6C QS 8H')
        self.assertEqual([], self.game.score_runs(hand))

    def testRunTwoTwoHigh(self):
        """Test not scoring a two card run two times on the high side."""
        hand = self.game.deck.parse_text('5C 2D TH 6C 6S 8H')
        self.assertEqual([], self.game.score_runs(hand))

    def testRunTwoTwoLow(self):
        """Test not scoring a two card run two times on the low side."""
        hand = self.game.deck.parse_text('5C 2D TH 6C QS 5H')
        self.assertEqual([], self.game.score_runs(hand))

    def testRunTwoTwice(self):
        """Test not scoring two two card run."""
        hand = self.game.deck.parse_text('5C 2D TH 6C QS 9H')
        self.assertEqual([], self.game.score_runs(hand))


class ScorePeggingTest(unittest.TestCase):
    """Test scoring cribbage plays. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot([5, 23, 108, 801])
        self.game = crib.Cribbage(self.human, 'none')
        self.game.set_up()

    def testFifteen(self):
        """Test pegging to 15."""
        self.game.in_play['Play Sequence'].cards = [self.game.deck.parse_text('5C')]
        play = self.game.deck.parse_text('JS')
        self.game.card_total = 5
        message = '{} scores 2 points for reaching 15.'.format(self.human.name)
        self.assertEqual((2, message), self.game.score_sequence(self.human, play))

    def testFourKind(self):
        """Test pegging four of a kind."""
        self.game.in_play['Play Sequence'].cards = self.game.deck.parse_text('6C 6D 6H')
        play = self.game.deck.parse_text('6S')
        message = '{} scores 12 points for getting four cards of the same rank.'.format(self.human.name)
        self.assertEqual((12, message), self.game.score_sequence(self.human, play))

    def testNothing(self):
        """Test pegging nothing."""
        self.game.in_play['Play Sequence'].cards = self.game.deck.parse_text('4H 2C 3D')
        play = self.game.deck.parse_text('7S')
        self.game.card_total = 9
        self.assertEqual((0, ''), self.game.score_sequence(self.human, play))

    def testPair(self):
        """Test pegging a pair."""
        self.game.in_play['Play Sequence'].cards = self.game.deck.parse_text('5H 6C')
        play = self.game.deck.parse_text('6S')
        message = '{} scores 2 points for getting two cards of the same rank.'.format(self.human.name)
        self.assertEqual((2, message), self.game.score_sequence(self.human, play))

    def testStraightFive(self):
        """Test pegging a five card straight."""
        self.game.in_play['Play Sequence'].cards = self.game.deck.parse_text('4H 2C 5S 3D')
        play = self.game.deck.parse_text('6C')
        message = '{} scores 5 points for getting a five-card straight.'.format(self.human.name)
        self.assertEqual((5, message), self.game.score_sequence(self.human, play))

    def testStraightFour(self):
        """Test pegging a four card straight."""
        self.game.in_play['Play Sequence'].cards = self.game.deck.parse_text('4H 2C 3D')
        play = self.game.deck.parse_text('5S')
        message = '{} scores 4 points for getting a four-card straight.'.format(self.human.name)
        self.assertEqual((4, message), self.game.score_sequence(self.human, play))

    def testStraightThree(self):
        """Test pegging a four card straight."""
        self.game.in_play['Play Sequence'].cards = self.game.deck.parse_text('2C 3D')
        play = self.game.deck.parse_text('4H')
        message = '{} scores 3 points for getting a three-card straight.'.format(self.human.name)
        self.assertEqual((3, message), self.game.score_sequence(self.human, play))

    def testThirtyOne(self):
        """Test pegging to 31."""
        self.game.in_play['Play Sequence'].cards = self.game.deck.parse_text('4H 2C 5S 3D QC')
        play = self.game.deck.parse_text('7C')
        self.game.card_total = 24
        message = '\nThe count has reached 31.\n{} scores 2 points for reaching 31.'
        message = message.format(self.human.name)
        self.assertEqual((2, message), self.game.score_sequence(self.human, play))

    def testTrip(self):
        """Test pegging three of a kind."""
        self.game.in_play['Play Sequence'].cards = self.game.deck.parse_text('6C 6D')
        play = self.game.deck.parse_text('6S')
        message = '{} scores 6 points for getting three cards of the same rank.'.format(self.human.name)
        self.assertEqual((6, message), self.game.score_sequence(self.human, play))


if __name__ == '__main__':
    unittest.main()
