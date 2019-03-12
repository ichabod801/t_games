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

    def shift_reserve(self, reserve):
        """
        Shift the cards over in the way a turn should.

        Parameters:
        reserve: The reserve to shift. (list of list of TrackingCard)
        """
        reserve = sum(reserve, [])
        start = 0
        piles = []
        while start < len(reserve):
            piles.append(reserve[start:(start + 3)])
            start += 3
        while len(piles) < self.game.options['num-reserve']:
            piles.append([])
        return piles

    def testBlankEnd(self):
        """Test turning with an empty pile at the end."""
        check = self.game.reserve[-2][:]
        self.game.transfer(self.game.reserve[-1][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[-1][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[-1][-1:], self.game.tableau[0])
        self.game.do_turn('')
        self.assertEqual(check, self.game.reserve[-2])

    def testBlankMiddle(self):
        """Test turning with an empty pile in the middle."""
        self.game.transfer(self.game.reserve[3][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[3][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[3][-1:], self.game.tableau[0])
        check = self.game.reserve[-1][:]
        self.game.do_turn('')
        self.assertEqual(check, self.game.reserve[-2])

    def testBlankStart(self):
        """Test turning with an empty pile at the start."""
        self.game.transfer(self.game.reserve[0][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[0][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[0][-1:], self.game.tableau[0])
        check = self.game.reserve[-1][:]
        self.game.do_turn('')
        self.assertEqual(check, self.game.reserve[-2])

    def testEmpty(self):
        """Test turning with an empty reserve."""
        for pile_index, pile in enumerate(self.game.reserve):
            while pile:
                self.game.transfer(pile[-1:], self.game.tableau[pile_index % len(self.game.tableau)])
        check = [[] for pile in range(self.game.options['num-reserve'])]
        self.game.do_turn('')
        self.assertEqual(check, self.game.reserve)

    def testFull(self):
        """Test turning with a full reserve."""
        check = [pile[:] for pile in self.game.reserve]
        self.game.do_turn('')
        self.assertEqual(check, self.game.reserve)

    def testOneEnd(self):
        """Test turning with one card missing at the end."""
        check = self.game.reserve[-1][:2]
        self.game.transfer(self.game.reserve[-1][-1:], self.game.tableau[0])
        self.game.do_turn('')
        self.assertEqual(check, self.game.reserve[-1])

    def testOneMiddle(self):
        """Test turning with one card missing in the middle."""
        self.game.transfer(self.game.reserve[3][-1:], self.game.tableau[0])
        check = self.game.reserve[-1][1:]
        self.game.do_turn('')
        self.assertEqual(check, self.game.reserve[-1])

    def testOneStart(self):
        """Test turning with one card missing at the start."""
        self.game.transfer(self.game.reserve[0][-1:], self.game.tableau[0])
        check = self.game.reserve[-1][1:]
        self.game.do_turn('')
        self.assertEqual(check, self.game.reserve[-1])

    def testTwoEnd(self):
        """Test turning with two cards missing at the end."""
        check = self.game.reserve[-1][:1]
        self.game.transfer(self.game.reserve[-1][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[-1][-1:], self.game.tableau[0])
        self.game.do_turn('')
        self.assertEqual(check, self.game.reserve[-1])

    def testTwoMiddle(self):
        """Test turning with two cards missing in the middle."""
        self.game.transfer(self.game.reserve[3][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[3][-1:], self.game.tableau[0])
        check = self.game.reserve[-1][2:]
        self.game.do_turn('')
        self.assertEqual(check, self.game.reserve[-1])

    def testTwoStart(self):
        """Test turning with two cards missing at the start."""
        self.game.transfer(self.game.reserve[0][-1:], self.game.tableau[0])
        self.game.transfer(self.game.reserve[0][-1:], self.game.tableau[0])
        check = self.game.reserve[-1][2:]
        self.game.do_turn('')
        self.assertEqual(check, self.game.reserve[-1])


if __name__ == '__main__':
    unittest.main()