"""
backgammon_test.py

Unit testing for backgammon_game.py.

Classes:
MoveTest: Test movement on a BackgammonBoard. (TestCase)
PlayTest: Test play generation. (TestCase)
"""


import io
import unittest
import sys

from tgames.board_games import backgammon_game as bg
from tgames import player as player


PRINT_START = """  1 1 1 1 1 1   1 2 2 2 2 2  
  3 4 5 6 7 8   9 0 1 2 3 4  
+-------------+-------------+
| X : . : O : | O : . : . X |
| X : . : O : | O : . : . X |
| X : . : O : | O : . : . : |
| X : . : . : | O : . : . : |
| X : . : . : | O : . : . : |
|             |             |
| O . : . : . | X . : . : . |
| O . : . : . | X . : . : . |
| O . : . X . | X . : . : . |
| O . : . X . | X . : . : O |
| O . : . X . | X . : . : O |
+-------------+-------------+
  1 1 1                      
  2 1 0 9 8 7   6 5 4 3 2 1  """


class MoveTest(unittest.TestCase):
    """Test movement on a BackgammonBoard. (TestCase)"""

    def setUp(self):
        """Set up with a standard board. (None)"""
        self.board = bg.BackgammonBoard()

    def testBasic(self):
        """Test a basic move."""
        self.board.move(13, 7)
        self.assertEqual(['X'], self.board.cells[7].contents)
        self.assertEqual(['X', 'X', 'X', 'X'], self.board.cells[13].contents)

    def testBasicClear(self):
        """That that basic moves go away with a new board."""
        self.assertEqual([], self.board.cells[7].contents)

    def testCapture(self):
        """Test capture."""
        self.board.move(13, 7)
        self.board.move(1, 7)
        self.assertEqual(['O'], self.board.cells[7].contents)
        self.assertEqual(['X'], self.board.cells['bar'].contents)


@unittest.skip('Pending more basic testing.')
class PlayTest(unittest.TestCase):
    """Test play generation. (TestCase)"""

    def setBoard(self, layout = ((6, 5), (8, 3), (13, 5), (24, 2)), moves = [], piece = 'O', 
        rolls = [6, 5], bar = None):
        """Set up the board for a test. (None)"""
        self.board = bg.BackgammonBoard(layout = layout)
        if bar:
            self.board.cells['bar'].add_piece(bar)
        for start, end in moves:
            self.board.move(start, end)
        raw_moves = self.board.get_plays(piece, rolls)
        self.legal_moves = set(tuple(move) for move in raw_moves)

    def testBear(self):
        """Test bearing off moves."""
        self.setBoard(layout = ((6, 2), (5, 2)))
        check = [((19, 'out'), (18, 'out')), ((18, 23), (18, 'out'))]
        self.assertEqual(set(check), self.legal_moves)

    def testBearOver(self):
        """Test bearing off with over rolls."""
        self.setBoard(layout = ((4, 1), (3, 2)))
        check = [((20, 'out'), (21, 'out'))]
        self.assertEqual(set(check), self.legal_moves)

    def testBearPartial(self):
        """Test bearing off with empty point rolled."""
        self.setBoard(layout = ((6, 2), (4, 2)))
        check = [((18, 23), (18, 'out'))]
        self.assertEqual(set(check), self.legal_moves)

    def testDoubles(self):
        """Test moves with doubles."""
        self.setBoard(layout = ((24, 1), (23, 1), (22, 1)), rolls = [1, 1, 1, 1])
        check = [((0, 1), (1, 2), (1, 2), (2, 3)), 
            ((0, 1), (1, 2), (2, 3), (2, 3)), 
            ((0, 1), (1, 2), (2, 3), (3, 4)), 
            ((0, 1), (2, 3), (3, 4), (4, 5)), 
            ((1, 2), (2, 3), (2, 3), (3, 4)), 
            ((1, 2), (2, 3), (3, 4), (4, 5)), 
            ((2, 3), (3, 4), (4, 5), (5, 6))]
        self.legal_moves = set([tuple(sorted(move)) for move in self.legal_moves])
        check = set(check)
        self.assertEqual(check, self.legal_moves)

    def testEnter(self):
        """Test moves from the bar."""
        # !! test for X, it has the home board off by one
        self.setBoard(layout = ((7, 2),), bar = ['X', 'O'], rolls = [2, 3])
        check = [((-1, 1), (1, 4)), ((-1, 1), (17, 20)),
            ((-1, 2), (2, 4)), ((-1, 2), (17, 19))]
        self.assertEqual(set(check), self.legal_moves)

    def testEnterBlock(self):
        """Test moves from the bar with some moves blocked."""
        self.setBoard(layout = ((3, 2), (7, 2)), bar = ['X', 'O'], rolls = [2, 3])
        check = [((-1, 1), (1, 4)), ((-1, 1), (17, 20))]
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
        self.setBoard(layout = ((24, 1), (23, 1), (3, 2)), moves = [(24, 23)], rolls = [1, 1])
        check = [((0, 1),)]
        self.assertEqual(set(check), self.legal_moves)

    def testStart(self):
        """Test the moves at the start of the game."""
        self.setBoard()
        check = [((11, 16), (0, 6)), ((11, 16), (11, 17)), 
            ((11, 16), (16, 22)), ((16, 21), (0, 6)), 
            ((16, 21), (11, 17)), ((16, 21), (16, 22)), 
            ((0, 6), (6, 11)), ((11, 17), (17, 22))]
        check = set(check)
        self.assertEqual(check, self.legal_moves)

    def testStartBlock(self):
        """Test the starting moves with a simple block."""
        self.setBoard(moves = [(13, 7), (8, 7)])
        check = [((11, 16), (11, 17)), ((11, 16), (16, 22)), 
            ((16, 21), (11, 17)), ((16, 21), (16, 22)), 
            ((11, 17), (17, 22))]
        check = set(check)
        self.assertEqual(check, self.legal_moves)

    def testUseBothDice(self):
        """Test being required to use both dice."""
        layout = ((2, 2), (4, 2), (8, 2), (20, 1), (24, 2))
        self.setBoard(layout = layout, moves = [(8, 'out'), (8, 'out')])
        self.assertNotIn(((-1, 1),), self.legal_moves)


class PrintTest(unittest.TestCase):
    """Test printing of the board on the screen. (TestCase)"""

    def setUp(self):
        """Set up the test case. (None)"""
        self.board = bg.BackgammonBoard()

    def testStart(self):
        """Test printing the starting board."""
        self.assertEqual(PRINT_START, self.board.get_text('X'))

    def testBar(self):
        """Test printing with a piece on the bar."""
        self.board.cells['bar'].contents = ['X']
        check = PRINT_START + '\n\nBar: X'
        self.assertEqual(check, self.board.get_text('X'))

if __name__ == '__main__':
    unittest.main()