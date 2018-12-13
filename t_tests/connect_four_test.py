"""
connect_four_test.py

Automated testing for connect_four_game.py.

Constants:
C4Bots: The bot classes used in testing. (list of player.Bot)

Classes:
ABFindShortsTest: Tests of finding two or three pieces in a row. (TestCase)
BoardCheckWinTest: Tests of C4Board.check_win. (unittest.TestCase)
C4BotTest: Tests of the ConnectFour bots. (unittest.TestCase)
"""


import random
import unittest

import t_games.board as board
import t_games.board_games.connect_four_game as connect_four
import t_tests.unitility as unitility


C4Bots = [connect_four.C4BotAlphaBeta, connect_four.C4BotGamma, connect_four.C4BotGamma]


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


class BoardCheckWinTest(unittest.TestCase):
    """Tests of C4Board.check_win. (unittest.TestCase)"""

    def setUp(self):
        self.board = connect_four.C4Board(pieces = ['X', 'O'])

    def testHorizontalLeft(self):
        """Test detecting a horizontal win touching the left edge."""
        row = random.randint(1, 6)
        for col in range(1, 5):
            self.board.place((col, row), 'X')
        self.assertEqual('X', self.board.check_win())

    def testHorizontalMiddle(self):
        """Test detecting a horizontal win not touching an edge."""
        row = random.randint(1, 6)
        start = random.randint(2, 3)
        for col in range(start, start + 4):
            self.board.place((col, row), 'O')
        self.assertEqual('O', self.board.check_win())

    def testHorizontalRight(self):
        """Test detecting a horizontal win touching the right edge."""
        row = random.randint(1, 6)
        for col in range(4, 8):
            self.board.place((col, row), 'X')
        self.assertEqual('X', self.board.check_win())

    def testNegativeHigh(self):
        """Test a negative slope win touching the top edge."""
        col = random.randint(2, 3)
        row = 6
        for delta in range(4):
            self.board.place((col + delta, row - delta), 'O')
        self.assertEqual('O', self.board.check_win())

    def testNegativeHighRight(self):
        """Test a negative slope win touching the top right corner."""
        col = 4
        row = 6
        for delta in range(4):
            self.board.place((col + delta, row - delta), 'X')
        self.assertEqual('X', self.board.check_win())

    def testNegativeLeft(self):
        """Test a negative slope win touching the left edge."""
        col = 1
        row = 5
        for delta in range(4):
            self.board.place((col + delta, row - delta), 'O')
        self.assertEqual('O', self.board.check_win())

    def testNegativeLeftHigh(self):
        """Test a negative slope win touching the top left corner."""
        col = 1
        row = 6
        for delta in range(4):
            self.board.place((col + delta, row - delta), 'X')
        self.assertEqual('X', self.board.check_win())

    def testNegativeLow(self):
        """Test a negative slope win touching the bottom edge."""
        col = random.randint(2, 3)
        row = 4
        for delta in range(4):
            self.board.place((col + delta, row - delta), 'O')
        self.assertEqual('O', self.board.check_win())

    def testNegativeLowLeft(self):
        """Test a negative slope win touching the bottom left corner."""
        col = 1
        row = 4
        for delta in range(4):
            self.board.place((col + delta, row - delta), 'X')
        self.assertEqual('X', self.board.check_win())

    def testNegativeMiddle(self):
        """Test a negative slope win touching not touching an edge."""
        col = random.randint(2, 3)
        row = 5
        for delta in range(4):
            self.board.place((col + delta, row - delta), 'O')
        self.assertEqual('O', self.board.check_win())

    def testNegativeRight(self):
        """Test a negative slope win touching the right edge."""
        col = 4
        row = 5
        for delta in range(4):
            self.board.place((col + delta, row - delta), 'X')
        self.assertEqual('X', self.board.check_win())

    def testNegativeRightLow(self):
        """Test a negative slope win touching the bottom right corner."""
        col = 4
        row = 4
        for delta in range(4):
            self.board.place((col + delta, row - delta), 'O')
        self.assertEqual('O', self.board.check_win())

    def testPositiveHigh(self):
        """Test a positive slope win touching the top edge."""
        col = random.randint(2, 3)
        row = 3
        for delta in range(4):
            self.board.place((col + delta, row + delta), 'X')
        self.assertEqual('X', self.board.check_win())

    def testPositiveHighRight(self):
        """Test a positive slope win touching the top right corner."""
        col = 4
        row = 3
        for delta in range(4):
            self.board.place((col + delta, row + delta), 'O')
        self.assertEqual('O', self.board.check_win())

    def testPositiveLeft(self):
        """Test a positive slope win touching the left edge."""
        col = 1
        row = 2
        for delta in range(4):
            self.board.place((col + delta, row + delta), 'X')
        self.assertEqual('X', self.board.check_win())

    def testPositiveLeftHigh(self):
        """Test a positive slope win touching the top left corner."""
        col = 1
        row = 3
        for delta in range(4):
            self.board.place((col + delta, row + delta), 'O')
        self.assertEqual('O', self.board.check_win())

    def testPositiveLow(self):
        """Test a positive slope win touching the bottom edge."""
        col = random.randint(2, 3)
        row = 1
        for delta in range(4):
            self.board.place((col + delta, row + delta), 'X')
        self.assertEqual('X', self.board.check_win())

    def testPositiveLowLeft(self):
        """Test a positive slope win touching the bottom left corner."""
        col = 1
        row = 1
        for delta in range(4):
            self.board.place((col + delta, row + delta), 'O')
        self.assertEqual('O', self.board.check_win())

    def testPositiveMiddle(self):
        """Test a positive slope win touching not touching an edge."""
        col = random.randint(2, 3)
        row = 2
        for delta in range(4):
            self.board.place((col + delta, row + delta), 'X')
        self.assertEqual('X', self.board.check_win())

    def testPositiveRight(self):
        """Test a positive slope win touching the right edge."""
        col = 4
        row = 2
        for delta in range(4):
            self.board.place((col + delta, row + delta), 'O')
        self.assertEqual('O', self.board.check_win())

    def testPositiveRightLow(self):
        """Test a positive slope win touching the bottom right corner."""
        col = 4
        row = 1
        for delta in range(4):
            self.board.place((col + delta, row + delta), 'X')
        self.assertEqual('X', self.board.check_win())

    def testVerticalHigh(self):
        """Test detecting a vertical win touching the top edge."""
        col = random.randint(1, 7)
        for row in range(3, 7):
            self.board.place((col, row), 'O')
        self.assertEqual('O', self.board.check_win())

    def testVerticalLow(self):
        """Test detecting a vertical win touching the bottom edge."""
        col = random.randint(1, 7)
        for row in range(1, 5):
            self.board.place((col, row), 'X')
        self.assertEqual('X', self.board.check_win())

    def testVerticalMiddle(self):
        """Test detecting a vertical win not touching an edge."""
        col = random.randint(1, 7)
        for row in range(2, 6):
            self.board.place((col, row), 'O')
        self.assertEqual('O', self.board.check_win())


C4BotTest = unitility.bot_test(connect_four.ConnectFour, C4Bots, 4, [2], bot_params = [(), (), (8,)])


if __name__ == '__main__':
    unittest.main()