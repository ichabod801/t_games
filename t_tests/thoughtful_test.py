"""
thoughtful_test.py

Test of thoughtful_game.py (Thoughtful Solitaire).

Classes:
TurnTest: Test of the turn command. (unittest.TestCase)
"""


import unittest

from t_games.card_games.solitaire_games import thoughtful_game as thoughtful
from t_games.t_tests import unitility


class TurnTest(unittest.TestCase):
    """Test of the turn command. (unittest.TestCase)"""

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = thoughtful.Thoughtful(self.human, 'none')
        self.game.scores = {}
        self.game.set_up()
        self.check = [pile[:] for pile in self.game.reserve]

    def shift_reserve(self, reserve):
        """
        Shift the cards over in the way a turn should.

        Parameters:
        reserve: The reserve to shift. (list of list of TrackingCard)
        """
        # Flatten the list.
        reserve = sum(reserve, [])
        # Group the list into piles of three.
        start = 0
        piles = []
        while start < len(reserve):
            piles.append(reserve[start:(start + 3)])
            start += 3
        # Fill out with empty lists
        while len(piles) < self.game.options['num-reserve']:
            piles.append([])
        return piles

    def testBlankEnd(self):
        """Test turning with an empty pile at the end."""
        # Set the expected result.
        self.check[-1] = []
        # Move the cards and turn.
        self.game.transfer(self.game.reserve[-1][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[-1][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[-1][-1:], self.game.tableau[0])
        self.game.do_turn('')
        # Run the test.
        self.assertEqual(self.check, self.game.reserve)

    def testBlankMiddle(self):
        """Test turning with an empty pile in the middle."""
        # Set the expected result.
        self.check[3] = []
        self.check = self.shift_reserve(self.check)
        # Move the cards and turn.
        self.game.transfer(self.game.reserve[3][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[3][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[3][-1:], self.game.tableau[0])
        self.game.do_turn('')
        # Run the test.
        self.assertEqual(self.check, self.game.reserve)

    def testBlankStart(self):
        """Test turning with an empty pile at the start."""
        # Set the expected result.
        self.check[0] = []
        self.check = self.shift_reserve(self.check)
        # Move the cards and turn.
        self.game.transfer(self.game.reserve[0][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[0][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[0][-1:], self.game.tableau[0])
        self.game.do_turn('')
        # Run the test.
        self.assertEqual(self.check, self.game.reserve)

    def testEmpty(self):
        """Test turning with an empty reserve."""
        # Set the expected result.
        check = [[] for pile in range(self.game.options['num-reserve'])]
        # Move the cards and turn.
        for pile_index, pile in enumerate(self.game.reserve):
            while pile:
                self.game.transfer(pile[-1:], self.game.tableau[pile_index % len(self.game.tableau)])
        self.game.do_turn('')
        # Run the test.
        self.assertEqual(check, self.game.reserve)

    def testFull(self):
        """Test turning with a full reserve."""
        self.game.do_turn('')
        self.assertEqual(self.check, self.game.reserve)

    def testOneEnd(self):
        """Test turning with one card missing at the end."""
        # Set the expected result.
        self.check[-1].pop()
        # Move the cards and turn.
        self.game.transfer(self.game.reserve[-1][-1:], self.game.tableau[0])
        self.game.do_turn('')
        # Run the test.
        self.assertEqual(self.check, self.game.reserve)

    def testOneMiddle(self):
        """Test turning with one card missing in the middle."""
        # Set the expected result.
        self.check[3].pop()
        self.check = self.shift_reserve(self.check)
        # Move the cards and turn.
        self.game.transfer(self.game.reserve[3][-1:], self.game.tableau[0])
        self.game.do_turn('')
        # Run the test.
        self.assertEqual(self.check, self.game.reserve)

    def testOneStart(self):
        """Test turning with one card missing at the start."""
        # Set the expected result.
        self.check[0].pop()
        self.check = self.shift_reserve(self.check)
        # Move the cards and turn.
        self.game.transfer(self.game.reserve[0][-1:], self.game.tableau[0])
        self.game.do_turn('')
        # Run the test.
        self.assertEqual(self.check, self.game.reserve)

    def testTwoEnd(self):
        """Test turning with two cards missing at the end."""
        # Set the expected result.
        self.check[-1] = self.check[-1][:1]
        # Move the cards and turn.
        self.game.transfer(self.game.reserve[-1][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[-1][-1:], self.game.tableau[0])
        self.game.do_turn('')
        # Run the test.
        self.assertEqual(self.check, self.game.reserve)

    def testTwoMiddle(self):
        """Test turning with two cards missing in the middle."""
        # Set the expected result.
        self.check[3] = self.check[3][:1]
        self.check = self.shift_reserve(self.check)
        # Move the cards and turn.
        self.game.transfer(self.game.reserve[3][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[3][-1:], self.game.tableau[0])
        self.game.do_turn('')
        # Run the test.
        self.assertEqual(self.check, self.game.reserve)

    def testTwoStart(self):
        """Test turning with two cards missing at the start."""
        # Set the expected result.
        self.check[0] = self.check[0][:1]
        self.check = self.shift_reserve(self.check)
        # Move the cards and turn.
        self.game.transfer(self.game.reserve[0][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[0][-1:], self.game.tableau[0])
        self.game.do_turn('')
        # Run the test.
        self.assertEqual(self.check, self.game.reserve)


if __name__ == '__main__':
    unittest.main()