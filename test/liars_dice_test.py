"""
liars_dice_test.py

Unit testing for dice_games/liars_dice_game.py

Classes:
PokerScoreTest: Tests of calling poker hands on dice. (unittest.TestCase)
PokerTextTest: Tests of converting poker hands to text. (unittest.TestCase)
"""


import unittest

import t_games.dice_games.liars_dice_game as liar
import t_games.player as player


class PokerScoreTest(unittest.TestCase):
    """Tests of calling poker hands on dice. (unittest.TestCase)"""

    def setUp(self):
        """Set up the tests."""
        self.game = liar.LiarsDice(player.Tester(), 'none')

    def testFiveKind(self):
        """Test scoring five of a kind."""
        score = self.game.poker_score((5, 5, 5, 5, 5))
        check = [7, 5, 5, 5, 5, 5]
        self.assertEqual(check, score)

    def testFourKindHigh(self):
        """Test scoring four of a kind with a high kicker."""
        score = self.game.poker_score((5, 5, 6, 5, 5))
        check = [6, 5, 5, 5, 5, 6]
        self.assertEqual(check, score)

    def testFourKindLow(self):
        """Test scoring four of a kind with a low kicker."""
        score = self.game.poker_score((3, 2, 3, 3, 3))
        check = [6, 3, 3, 3, 3, 2]
        self.assertEqual(check, score)

    def testFullHouseHigh(self):
        """Test scoring a full house with a high trip."""
        score = self.game.poker_score((4, 2, 4, 2, 4))
        check = [5, 4, 4, 4, 2, 2]
        self.assertEqual(check, score)

    def testFullHouseLow(self):
        """Test scoring a full house with a low trip."""
        score = self.game.poker_score((1, 1, 1, 6, 6))
        check = [5, 1, 1, 1, 6, 6]
        self.assertEqual(check, score)

    def testHighCardNoFive(self):
        """Test scoring a high card hand with no five."""
        score = self.game.poker_score((1, 2, 3, 4, 6))
        check = [0, 6, 4, 3, 2, 1]
        self.assertEqual(check, score)

    def testHighCardNoTwo(self):
        """Test scoring a high card hand with no two."""
        score = self.game.poker_score((1, 3, 4, 5, 6))
        check = [0, 6, 5, 4, 3, 1]
        self.assertEqual(check, score)

    def testPairHigh(self):
        """Test scoring a pair with high kickers."""
        score = self.game.poker_score((2, 3, 6, 1, 1))
        check = [1, 1, 1, 6, 3, 2]
        self.assertEqual(check, score)

    def testPairLow(self):
        """Test scoring a pair with low kickers."""
        score = self.game.poker_score((5, 2, 5, 1, 3))
        check = [1, 5, 5, 3, 2, 1]
        self.assertEqual(check, score)

    def testPairMixed(self):
        """Test scoring a pair with high and low kickers."""
        score = self.game.poker_score((3, 3, 6, 4, 1))
        check = [1, 3, 3, 6, 4, 1]
        self.assertEqual(check, score)

    def testStraightHigh(self):
        """Test scoring a high straight."""
        score = self.game.poker_score((4, 5, 3, 6, 2))
        check = [4, 6, 5, 4, 3, 2]
        self.assertEqual(check, score)

    def testStraightLow(self):
        """Test scoring a low straight."""
        score = self.game.poker_score((1, 2, 3, 4, 5))
        check = [4, 5, 4, 3, 2, 1]
        self.assertEqual(check, score)

    def testTripHigh(self):
        """Test scoring trips with high kickers."""
        score = self.game.poker_score((1, 2, 4, 1, 1))
        check = [3, 1, 1, 1, 4, 2]
        self.assertEqual(check, score)

    def testTripLow(self):
        """Test scoring trips with low kickers."""
        score = self.game.poker_score((1, 2, 6, 6, 6))
        check = [3, 6, 6, 6, 2, 1]
        self.assertEqual(check, score)

    def testTripMixed(self):
        """Test scoring trips with high and low kickers."""
        score = self.game.poker_score((4, 4, 3, 4, 6))
        check = [3, 4, 4, 4, 6, 3]
        self.assertEqual(check, score)

    def testTwoPairHigh(self):
        """Test scoring two pair with a high kicker."""
        score = self.game.poker_score((2, 3, 3, 2, 6))
        check = [2, 3, 3, 2, 2, 6]
        self.assertEqual(check, score)

    def testTwoPairLow(self):
        """Test scoring two pair with a low kicker."""
        score = self.game.poker_score((6, 4, 6, 4, 1))
        check = [2, 6, 6, 4, 4, 1]
        self.assertEqual(check, score)

    def testTwoPairMiddle(self):
        """Test scoring two pair with a kicker between the pairs."""
        score = self.game.poker_score((4, 2, 3, 4, 2))
        check = [2, 4, 4, 2, 2, 3]
        self.assertEqual(check, score)


class PokerTextTest(unittest.TestCase):
    """Tests of converting poker hands to text. (unittest.TestCase)"""

    def setUp(self):
        """Set up the tests."""
        self.game = liar.LiarsDice(player.Tester(), 'none')

    def testFiveKind(self):
        """Test text generation for five of a kind."""
        text = self.game.poker_text([7, 5, 5, 5, 5, 5])
        check = 'five fives'
        self.assertEqual(check, text)

    def testFourKindHigh(self):
        """Test text generation for four of a kind with a high kicker."""
        text = self.game.poker_text([6, 5, 5, 5, 5, 6])
        check = 'four fives and a six'
        self.assertEqual(check, text)

    def testFourKindLow(self):
        """Test text generation for four of a kind with a low kicker."""
        text = self.game.poker_text([6, 3, 3, 3, 3, 2])
        check = 'four threes and a two'
        self.assertEqual(check, text)

    def testFullHouseHigh(self):
        """Test text generation for a full house with a high trip."""
        text = self.game.poker_text([5, 4, 4, 4, 2, 2])
        check = 'full house fours over twos'
        self.assertEqual(check, text)

    def testFullHouseLow(self):
        """Test text generation for a full house with a low trip."""
        text = self.game.poker_text([5, 1, 1, 1, 6, 6])
        check = 'full house ones over sixes'
        self.assertEqual(check, text)

    def testHighCardNoFive(self):
        """Test text generation for a high card hand with no five."""
        text = self.game.poker_text([0, 6, 4, 3, 2, 1])
        check = 'six high missing five'
        self.assertEqual(check, text)

    def testHighCardNoTwo(self):
        """Test text generation for a high card hand with no two."""
        text = self.game.poker_text([0, 6, 5, 4, 3, 1])
        check = 'six high missing two'
        self.assertEqual(check, text)

    def testPairHigh(self):
        """Test text generation for a pair with high kickers."""
        text = self.game.poker_text([1, 1, 1, 6, 3, 2])
        check = 'a pair of ones with six, three, two'
        self.assertEqual(check, text)

    def testPairLow(self):
        """Test text generation for a pair with low kickers."""
        text = self.game.poker_text([1, 5, 5, 3, 2, 1])
        check = 'a pair of fives with three, two, one'
        self.assertEqual(check, text)

    def testPairMixed(self):
        """Test text generation for a pair with high and low kickers."""
        text = self.game.poker_text([1, 3, 3, 6, 4, 1])
        check = 'a pair of threes with six, four, one'
        self.assertEqual(check, text)

    def testStraightHigh(self):
        """Test text generation for a high straight."""
        text = self.game.poker_text([4, 6, 5, 4, 3, 2])
        check = 'a six-high straight'
        self.assertEqual(check, text)

    def testStraightLow(self):
        """Test text generation for a low straight."""
        text = self.game.poker_text([4, 5, 4, 3, 2, 1])
        check = 'a five-high straight'
        self.assertEqual(check, text)

    def testTripHigh(self):
        """Test text generation for trips with high kickers."""
        text = self.game.poker_text([3, 1, 1, 1, 4, 2])
        check = 'three ones with four and two'
        self.assertEqual(check, text)

    def testTripLow(self):
        """Test text generation for trips with low kickers."""
        text = self.game.poker_text([3, 6, 6, 6, 2, 1])
        check = 'three sixes with two and one'
        self.assertEqual(check, text)

    def testTripMixed(self):
        """Test text generation for trips with high and low kickers."""
        text = self.game.poker_text([3, 4, 4, 4, 6, 3])
        check = 'three fours with six and three'
        self.assertEqual(check, text)

    def testTwoPairHigh(self):
        """Test text generation for two pair with a high kicker."""
        text = self.game.poker_text([2, 3, 3, 2, 2, 6])
        check = 'two pair threes over twos with a six'
        self.assertEqual(check, text)

    def testTwoPairLow(self):
        """Test text generation for two pair with a low kicker."""
        text = self.game.poker_text([2, 6, 6, 4, 4, 1])
        check = 'two pair sixes over fours with a one'
        self.assertEqual(check, text)

    def testTwoPairMiddle(self):
        """Test text generation for two pair with a kicker between the pairs."""
        text = self.game.poker_text([2, 4, 4, 2, 2, 3])
        check = 'two pair fours over twos with a three'
        self.assertEqual(check, text)


if __name__ == '__main__':
    unittest.main()