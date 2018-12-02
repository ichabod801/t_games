"""
connect_four_test.py

Automated testing for connect_four_game.py.

Classes:
ABFindShortsTest: Tests of finding two or three pieces in a row. (TestCase)
"""


import unittest

import t_games.board as board
import t_games.board_games.connect_four_game as connect_four
import t_tests.unitility as unitility


class ABFindShortsTest(unittest.TestCase):
    """Tests of finding two or three pieces in a row. (unittest.TestCase)"""

    def setUp(self):
        self.bot = connect_four.C4BotAlphaBeta()
        pieces = [(2, 0), (3, 0), (4, 0), (3, 1), (2, 2), (3, 2), (5, 2), (4, 3), (6, 3), (3, 4), (5, 4)]
        pieces.append((3, 5))
        self.shorts = self.bot.find_shorts([board.Coordinate(piece) for piece in pieces])

    def testTwoHorizontal(self):
        """Test detecting a horizontal two length short."""
        self.assertIn(((2, 2), (3, 2)), self.shorts[0])

    def testTwoNegative(self):
        """Test detecting a negative slope two length short."""
        self.assertIn(((5, 4), (6, 3)), self.shorts[0])

    def testTwoPositive(self):
        """Test detecting a positive slope two length short."""
        self.assertIn(((5, 2), (6, 3)), self.shorts[0])

    def testTwoVertical(self):
        """Test detecting a vertical two length short."""
        self.assertIn(((3, 4), (3, 5)), self.shorts[0])

    def testThreeHorizontal(self):
        """Test detecting a horizontal three length short."""
        self.assertIn(((2, 0), (3, 0), (4, 0)), self.shorts[1])

    def testThreeNegative(self):
        """Test detecting a negative slope three length short."""
        self.assertIn(((3, 4), (4, 3), (5, 2)), self.shorts[1])

    def testThreePositive(self):
        """Test detecting a positive slope three length short."""
        self.assertIn(((3, 2), (4, 3), (5, 4)), self.shorts[1])

    def testThreeVertical(self):
        """Test detecting a vertical three length short."""
        self.assertIn(((3, 0), (3, 1), (3, 2)), self.shorts[1])


if __name__ == '__main__':
    unittest.main()