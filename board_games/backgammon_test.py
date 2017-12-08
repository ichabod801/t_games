"""
backgammon_test.py

Unit testing for backgammon_game.py.

Classes:
EndPointTest: Test moves made just providing an end point. (TestCase)
PlayTest: Test play generation. (TestCase)
"""


import io
import unittest
import sys

from tgames.board_games import backgammon_game as bg
from tgames import player as player


class EndPointTest(unittest.TestCase):
    """Test moves made just providing an end point. (TestCase)"""

    def setUp(self):
        """Set up the test case. (None)"""
        self.game = bg.Backgammon(player.Tester())
        if not isinstance(self.game.players[0], player.Tester):
            self.game.players.reverse()
        self.stdin_hold = sys.stdin

    def tearDown(self):
        """Clean up after the test case. (None)"""
        sys.stdin = self.stdin_hold

    def testValid(self):
        """Test a valid end point move."""
        self.game.board.rolls = [2, 1]
        sys.stdin = io.StringIO('7\n')
        self.assertEqual(['X'], self.game.board.cells[(6,)].piece)


class PlayTest(unittest.TestCase):
    """Test play generation. (TestCase)"""

    def setBoard(self, layout = ((6, 5), (8, 3), (13, 5), (24, 2)), moves = [], piece = 'O', 
        rolls = [6, 5], bar = None):
        """Set up the board for a test. (None)"""
        self.board = bg.BackgammonBoard(layout = layout)
        if bar:
            self.board.bar.piece = bar
        for start, end in moves:
            self.board.move(start, end)
        raw_moves = self.board.get_plays(piece, rolls)
        self.legal_moves = set(tuple(move) for move in raw_moves)

    def testBear(self):
        """Test bearing off moves."""
        self.setBoard(layout = ((6, 2), (5, 2)))
        check = [(((19,), (-3,)), ((18,), (-3,))), (((18,), (23,)), ((18,), (-3,)))]
        self.assertEqual(set(check), self.legal_moves)

    def testBearOver(self):
        """Test bearing off with over rolls."""
        self.setBoard(layout = ((4, 1), (3, 2)))
        check = [(((20,), (-3,)), ((21,), (-3,)))]
        self.assertEqual(set(check), self.legal_moves)

    def testBearPartial(self):
        """Test bearing off with empty point rolled."""
        self.setBoard(layout = ((6, 2), (4, 2)))
        check = [(((18,), (23,)), ((18,), (-3,)))]
        self.assertEqual(set(check), self.legal_moves)

    def testDoubles(self):
        """Test moves with doubles."""
        self.setBoard(layout = ((24, 1), (23, 1), (22, 1)), rolls = [1, 1, 1, 1])
        check = [(((0,), (1,)), ((1,), (2,)), ((1,), (2,)), ((2,), (3,))), 
            (((0,), (1,)), ((1,), (2,)), ((2,), (3,)), ((2,), (3,))), 
            (((0,), (1,)), ((1,), (2,)), ((2,), (3,)), ((3,), (4,))), 
            (((0,), (1,)), ((2,), (3,)), ((3,), (4,)), ((4,), (5,))), 
            (((1,), (2,)), ((2,), (3,)), ((2,), (3,)), ((3,), (4,))), 
            (((1,), (2,)), ((2,), (3,)), ((3,), (4,)), ((4,), (5,))), 
            (((2,), (3,)), ((3,), (4,)), ((4,), (5,)), ((5,), (6,)))]
        self.legal_moves = set([tuple(sorted(move)) for move in self.legal_moves])
        check = set(check)
        self.assertEqual(check, self.legal_moves)

    def testEnter(self):
        """Test moves from the bar."""
        # !! test for X, it has the home board off by one
        self.setBoard(layout = ((7, 2),), bar = ['X', 'O'], rolls = [2, 3])
        check = [(((-1,), (1,)), ((1,), (4,))), (((-1,), (1,)), ((17,), (20,))),
            (((-1,), (2,)), ((2,), (4,))), (((-1,), (2,)), ((17,), (19,)))]
        self.assertEqual(set(check), self.legal_moves)

    def testEnterBlock(self):
        """Test moves from the bar with some moves blocked."""
        self.setBoard(layout = ((3, 2), (7, 2)), bar = ['X', 'O'], rolls = [2, 3])
        check = [(((-1,), (1,)), ((1,), (4,))), (((-1,), (1,)), ((17,), (20,)))]
        self.assertEqual(set(check), self.legal_moves)

    def testEnterNone(self):
        """Test moves from the bar when none are legal."""
        self.setBoard(layout = ((18, 2), (6, 2), (5, 2), (4, 2), (3, 2), (2, 2), (1, 2)), rolls = [6, 6], 
            bar = ['X', 'O'])
        self.assertEqual(set(), self.legal_moves)

    def testNone(self):
        """Test a situation with no legal moves."""
        self.setBoard(layout = ((7, 2), (6, 2), (5, 2), (4, 2), (3, 2), (2, 2), (24, 2)), rolls = [6, 6])
        self.assertEqual(set(), self.legal_moves)

    def testPartial(self):
        """Test moves where only part of the move is legal."""
        self.setBoard(layout = ((24, 1), (23, 1), (3, 2)), moves = [((23,), (22,))], rolls = [1, 1])
        check = [(((0,), (1,)),)]
        self.assertEqual(set(check), self.legal_moves)

    def testStart(self):
        """Test the moves at the start of the game."""
        self.setBoard()
        check = [(((11,), (16,)), ((0,), (6,))), (((11,), (16,)), ((11,), (17,))), 
            (((11,), (16,)), ((16,), (22,))), (((16,), (21,)), ((0,), (6,))), 
            (((16,), (21,)), ((11,), (17,))), (((16,), (21,)), ((16,), (22,))), 
            (((0,), (6,)), ((6,), (11,))), (((11,), (17,)), ((17,), (22,)))]
        check = set(check)
        self.assertEqual(check, self.legal_moves)

    def testStartBlock(self):
        """Test the starting moves with a simple block."""
        self.setBoard(moves = [((12,), (6,)), ((7,), (6,))])
        check = [(((11,), (16,)), ((11,), (17,))), (((11,), (16,)), ((16,), (22,))), 
            (((16,), (21,)), ((11,), (17,))), (((16,), (21,)), ((16,), (22,))), 
            (((11,), (17,)), ((17,), (22,)))]
        check = set(check)
        self.assertEqual(check, self.legal_moves)


if __name__ == '__main__':
    unittest.main()