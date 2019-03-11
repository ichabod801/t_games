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

    #@unittest.skip('Isolating infinite loop.')
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