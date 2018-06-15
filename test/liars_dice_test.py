"""
liars_dice_test.py

Unit testing for dice_games/liars_dice_game.py

Classes:
OneSixAdjustTest: Test adjusting counts for ones counting as sixes.
OneWildAdjustTest: Test adjusting counts for ones wild.
OneSixeScoreTest: Test of calling poker hands with ones counting as sixes.
PokerScoreTest: Tests of calling poker hands on dice.
PokerTextTest: Tests of converting poker hands to text.

Function:
by_count: Crate a counts dictionary for testing. (collections.defaultdict)
"""


import collections
import unittest

import _test_utility
import t_games.dice_games.liars_dice_game as liar
import t_games.player as player


class OneSixAdjustTest(unittest.TestCase):
    """Test adjusting counts for ones counting as sixes. (TestCase)"""

    def setUp(self):
        """Set up the tests."""
        self.game = liar.LiarsDice(player.Tester(), 'one-six')

    def testBothUnique(self):
        """Test one-six adjustemnt with unique ones count and sixes count."""
        values = [1, 6, 1, 1, 6]
        adjusted = self.game.one_six_adjust(by_count(values), values)
        check = by_count([6, 6, 6, 6, 6])
        self.assertEqual(check, adjusted)

    def testNeighterUnique(self):
        """Test one-six adjustemnt with no unique counts."""
        values = [1, 6, 2, 3, 4]
        adjusted = self.game.one_six_adjust(by_count(values), values)
        check = by_count([6, 6, 2, 3, 4])
        self.assertEqual(check, adjusted)

    def testNoOnesNoSixes(self):
        """Test one-six adjustemnt with no ones or sixes."""
        values = [2, 2, 4, 3, 5]
        adjusted = self.game.one_six_adjust(by_count(values), values)
        check = by_count([2, 2, 4, 3, 5])
        self.assertEqual(check, adjusted)

    def testOnesUnique(self):
        """Test one-six adjustemnt with unique ones count."""
        values = [1, 1, 2, 3, 6]
        adjusted = self.game.one_six_adjust(by_count(values), values)
        check = by_count([2, 3, 6, 6, 6])
        self.assertEqual(check, adjusted)

    def testOnesUniqueNoSixes(self):
        """Test one-six adjustemnt with unique ones count and no sixes."""
        values = [1, 1, 2, 3, 5]
        adjusted = self.game.one_six_adjust(by_count(values), values)
        check = by_count([2, 3, 5, 6, 6])
        self.assertEqual(check, adjusted)

    def testSixesUnique(self):
        """Test one-six adjustemnt with unique sixes count."""
        values = [1, 6, 2, 3, 6]
        adjusted = self.game.one_six_adjust(by_count(values), values)
        check = by_count([2, 3, 6, 6, 6])
        self.assertEqual(check, adjusted)

    def testSixesUniqueNoOnes(self):
        """Test one-six adjustemnt with unique sixes count."""
        values = [5, 6, 2, 3, 6]
        adjusted = self.game.one_six_adjust(by_count(values), values)
        check = by_count([2, 3, 5, 6, 6])
        self.assertEqual(check, adjusted)


class OneWildAdjustTest(unittest.TestCase):
    """Test adjusting counts for ones wild. (TestCase)"""

    def setUp(self):
        """Set up the tests."""
        self.game = liar.LiarsDice(player.Tester(), 'one-wild')

    def testFiveKind(self):
        """Test one-wild adjustment with five of a kind."""
        values = [1, 2, 1, 1, 2]
        adj_counts, adj_values = self.game.one_wild_adjust(by_count(values), values)
        check = by_count([2, 2, 2, 2, 2])
        self.assertEqual(check, adj_counts)
        self.assertEqual(values, adj_values)

    def testFiveSixes(self):
        """Test one-wild adjustment with five of a ones."""
        values = [1, 1, 1, 1, 1]
        adj_counts, adj_values = self.game.one_wild_adjust(by_count(values), values)
        check = by_count([6, 6, 6, 6, 6])
        self.assertEqual(check, adj_counts)
        self.assertEqual([6, 6, 6, 6, 6], adj_values)

    def testFourKind(self):
        """Test one-wild adjustment with four of a kind."""
        values = [4, 5, 1, 1, 1]
        adj_counts, adj_values = self.game.one_wild_adjust(by_count(values), values)
        check = by_count([5, 5, 5, 4, 5])
        self.assertEqual(check, adj_counts)
        self.assertEqual(values, adj_values)

    def testFourKindLow(self):
        """Test one-wild adjustment with four of a kind forced low."""
        values = [4, 5, 1, 4, 1]
        adj_counts, adj_values = self.game.one_wild_adjust(by_count(values), values)
        check = by_count([4, 4, 5, 4, 4])
        self.assertEqual(check, adj_counts)
        self.assertEqual(values, adj_values)

    def testFullHouse(self):
        """Test one-wild adjustment with a full house."""
        values = [2, 3, 3, 2, 1]
        adj_counts, adj_values = self.game.one_wild_adjust(by_count(values), values)
        check = by_count([2, 3, 2, 3, 3])
        self.assertEqual(check, adj_counts)
        self.assertEqual(values, adj_values)

    def testOnesUnique(self):
        """Test one-wild adjustment with a unique count of ones."""
        values = [1, 2, 2, 3, 3]
        adj_counts, adj_values = self.game.one_wild_adjust(by_count(values), values)
        check = by_count([3, 2, 2, 3, 3])
        self.assertEqual(check, adj_counts)
        self.assertEqual(values, adj_values)

    def testStraight(self):
        """Test one-wild adjustment with a straight."""
        values = [1, 2, 3, 6, 5]
        adj_counts, adj_values = self.game.one_wild_adjust(by_count(values), values)
        check = by_count([2, 3, 4, 5, 6])
        self.assertEqual(check, adj_counts)
        self.assertEqual([2, 3, 4, 5, 6], adj_values)

    def testStraightTwo(self):
        """Test one-wild adjustment with a straight and two ones."""
        values = [1, 2, 1, 6, 5]
        adj_counts, adj_values = self.game.one_wild_adjust(by_count(values), values)
        check = by_count([2, 3, 4, 5, 6])
        self.assertEqual(check, adj_counts)
        self.assertEqual([2, 3, 4, 5, 6], adj_values)

    def testTrips(self):
        """Test one-wild adjustment with a three of a kind."""
        values = [4, 5, 6, 5, 1]
        adj_counts, adj_values = self.game.one_wild_adjust(by_count(values), values)
        check = by_count([5, 5, 4, 5, 6])
        self.assertEqual(check, adj_counts)
        self.assertEqual(values, adj_values)


class OneSixScoreTest(unittest.TestCase):
    """Test of calling poker hands with ones counting as sixes. (TestCase)"""

    def setUp(self):
        """Set up the tests."""
        self.game = liar.LiarsDice(player.Tester(), 'one-six')

    def testFiveKind(self):
        """Test scoring five of a kind with ones as sixes."""
        score = self.game.poker_score((6, 6, 1, 6, 1))
        check = [7, 6, 6, 6, 6, 6]
        self.assertEqual(check, score)

    def testFourKind(self):
        """Test scoring five of a kind with ones as sixes."""
        score = self.game.poker_score((6, 3, 1, 6, 1))
        check = [6, 6, 6, 6, 6, 3]
        self.assertEqual(check, score)

    def testFullHouse(self):
        """Test scoring a full house with ones as sixes."""
        score = self.game.poker_score((6, 2, 1, 6, 2))
        check = [5, 6, 6, 6, 2, 2]
        self.assertEqual(check, score)

    def testStraight(self):
        """Test scoring a straight with ones as sixes."""
        score = self.game.poker_score((3, 2, 5, 1, 4))
        check = [4, 6, 5, 4, 3, 2]
        self.assertEqual(check, score)

    def testTrips(self):
        """Test scoring three of a kind with ones as sixes."""
        score = self.game.poker_score((6, 1, 4, 6, 5))
        check = [3, 6, 6, 6, 5, 4]
        self.assertEqual(check, score)

    def testTripsNoSixes(self):
        """Test scoring three of a kind with ones as sixes and no sixes."""
        score = self.game.poker_score((1, 1, 4, 1, 5))
        check = [3, 6, 6, 6, 5, 4]
        self.assertEqual(check, score)

    def testTwoPair(self):
        """Test scoring two pair with ones as sixes."""
        score = self.game.poker_score((2, 1, 3, 6, 2))
        check = [2, 6, 6, 2, 2, 3]
        self.assertEqual(check, score)

    def testPair(self):
        """Test scoring a pair with ones as sixes."""
        score = self.game.poker_score((6, 1, 4, 5, 2))
        check = [1, 6, 6, 5, 4, 2]
        self.assertEqual(check, score)


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


class ValidateClaimTest(unittest.TestCase):
    """Test validating that the new claim is better than the old."""

    def setUp(self):
        self.player = _test_utility.Mute()
        self.game = liar.LiarsDice(self.player, 'none')
        self.game.reset()

    def testFiveFive(self):
        """Test comparing five of a kind to a different five of a kind."""
        # Test the higher against the lower.
        claim = [6, 6, 6, 6, 6]
        self.game.claim = [5, 5, 5, 5, 5]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player)) 

    def testFiveFour(self):
        """Test comparing five of a kind to four of a kind."""
        # Test the higher against the lower.
        claim = [1, 1, 1, 1, 1]
        self.game.claim = [1, 1, 1, 1, 2]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testFourFour(self):
        """Test comparing four of a kind to a different four of a kind."""
        # Test the higher against the lower.
        claim = [3, 3, 3, 3, 2]
        self.game.claim = [2, 2, 2, 2, 3]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testFourFull(self):
        """Test comparing five of a kind to four of a kind."""
        # Test the higher against the lower.
        claim = [2, 2, 2, 2, 1]
        self.game.claim = [3, 3, 3, 4, 4]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testFullFull(self):
        """Test comparing a full house to a different full house."""
        # Test the higher against the lower.
        claim = [4, 4, 4, 1, 1]
        self.game.claim = [1, 1, 1, 4, 4]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testFullStraight(self):
        """Test comparing a full house to a straight"""
        # Test the higher against the lower.
        claim = [3, 5, 3, 5, 3]
        self.game.claim = [6, 3, 2, 4, 5]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testHighCardDummy(self):
        """Test comparing a high card to a dummy hand."""
        # Test the higher against the lower.
        claim = [1, 2, 4, 5, 6]
        self.game.claim = [0, 0, 0, 0, 0]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testHighCardHighCard(self):
        """Test comparing a high card to a different high card."""
        # Test the higher against the lower.
        claim = [1, 3, 4, 5, 6]
        self.game.claim = [1, 2, 3, 4, 6]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testPairHighCard(self):
        """Test comparing a pair to a high card."""
        # Test the higher against the lower.
        claim = [4, 3, 4, 2, 5]
        self.game.claim = [6, 1, 2, 3, 5]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testPairPair(self):
        """Test comparing a pair to a different pair."""
        # Test the higher against the lower.
        claim = [6, 6, 5, 4, 3]
        self.game.claim = [1, 1, 4, 3, 2]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testStraightStraight(self):
        """Test comparing a high straight to a low straight."""
        # Test the higher against the lower.
        claim = [2, 3, 4, 5, 6]
        self.game.claim = [5, 4, 1, 2, 3]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testStraightTrip(self):
        """Test comparing a straight to three of a kind."""
        # Test the higher against the lower.
        claim = [1, 2, 3, 4, 5]
        self.game.claim = [6, 1, 6, 6, 2]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testTwoPairPair(self):
        """Test comparing two pair to a pair."""
        # Test the higher against the lower.
        claim = [3, 1, 2, 1, 2]
        self.game.claim = [2, 2, 6, 5, 4]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testTwoPairTwoPair(self):
        """Test comparing two pair to a different two pair."""
        # Test the higher against the lower.
        claim = [4, 5, 4, 6, 5]
        self.game.claim = [5, 5, 4, 4, 2]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testTripTrip(self):
        """Test comparing a trip to a different trip."""
        # Test the higher against the lower.
        claim = [4, 5, 2, 5, 5]
        self.game.claim = [5, 3, 5, 5, 2]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))

    def testTripTwoPair(self):
        """Test comparing a trip to two pair."""
        # Test the higher against the lower.
        claim = [6, 6, 1, 6, 3]
        self.game.claim = [1, 1, 6, 3, 6]
        self.assertTrue(self.game.validate_claim(claim, self.player))
        # Test the higher against itself.
        self.assertFalse(self.game.validate_claim(self.game.claim, self.player))
        # Test the lower the higher.
        claim = self.game.history[0]
        self.assertFalse(self.game.validate_claim(claim, self.player))
        # Test the lower against itself.
        self.game.claim = claim
        self.assertFalse(self.game.validate_claim(claim, self.player))


def by_count(values):
    """
    Create a counts dictionary for testing. (collections.defaultdict)

    Parameters:
    values: The values to create as a count.
    """
    counts = collections.defaultdict(list)
    for value in set(values):
        counts[values.count(value)].append(value)
    return counts


if __name__ == '__main__':
    unittest.main()