"""
backgammon_test.py

Unit testing for backgammon_game.py.

Classes:
MoveTest: Test movement on a BackgammonBoard. (TestCase)
PlayTest: Test play generation. (TestCase)

Functions:
make_play: Make a BackgammonPlay from a list as tuples. (BackgammonPlay)
"""


import io
import unittest
import sys

import t_games.board_games.backgammon_game as backgammon
import t_games.player as player


BAR = -1

OUT = -2

PRINT_START = '\n'.join(['  1 1 1 1 1 1   1 2 2 2 2 2  ', '  3 4 5 6 7 8   9 0 1 2 3 4  ',
    '+-------------+-------------+', '| X : . : O : | O : . : . X |', '| X : . : O : | O : . : . X |',
    '| X : . : O : | O : . : . : |', '| X : . : . : | O : . : . : |', '| X : . : . : | O : . : . : |',
    '|             |             |', '| O . : . : . | X . : . : . |', '| O . : . : . | X . : . : . |',
    '| O . : . X . | X . : . : . |', '| O . : . X . | X . : . : O |', '| O . : . X . | X . : . : O |',
    '+-------------+-------------+', '  1 1 1                      ', '  2 1 0 9 8 7   6 5 4 3 2 1  '])


class MoveTest(unittest.TestCase):
    """Test movement on a BackgammonBoard. (TestCase)"""
    # Most of this should be covered by board_test.LineBoardTest.

    def setUp(self):
        """Set up with a standard board. (None)"""
        self.board = backgammon.BackgammonBoard()

    def testBasic(self):
        """Test a basic move."""
        self.board.move(13, 7)
        self.assertEqual(['X'], self.board.cells[7].contents)
        self.assertEqual(['X', 'X', 'X', 'X'], self.board.cells[13].contents)

    def testBasicClear(self):
        """That that basic moves go away with a new board."""
        self.assertEqual([], self.board.cells[7].contents)

    def testBear(self):
        """Test bearing off the board."""
        self.board.move(19, OUT)
        self.assertEqual(['O'], self.board.cells[OUT].contents)
        self.assertEqual(['O', 'O', 'O', 'O'], self.board.cells[19].contents)

    def testBearNoCapture(self):
        """Test bearing off the board."""
        self.board.move(19, OUT)
        self.board.move(6, OUT)
        self.assertEqual(['O', 'X'], self.board.cells[OUT].contents)
        self.assertEqual([], self.board.cells[BAR].contents)

    def testCapture(self):
        """Test capture."""
        self.board.move(13, 7)
        self.board.move(1, 7)
        self.assertEqual(['O'], self.board.cells[7].contents)
        self.assertEqual(['X'], self.board.cells[BAR].contents)


class PlayTest(unittest.TestCase):
    """Test play generation. (TestCase)"""

    def setBoard(self, layout = ((6, 5), (8, 3), (13, 5), (24, 2)), moves = [], piece = 'O',
        rolls = [6, 5], bar = []):
        """Set up the board for a test. (None)"""
        self.board = backgammon.BackgammonBoard(layout = layout)
        for captured in bar:
            self.board.cells[BAR].add_piece(captured)
        for start, end in moves:
            self.board.move(start, end)
        raw_moves = self.board.get_plays(piece, rolls)
        self.legal_moves = set(tuple(move) for move in raw_moves)

    def testBasicRepr(self):
        """Test debugging text representation of a standard move."""
        play = backgammon.BackgammonPlay(13, 7, 6)
        self.assertEqual('<BackgammonPlay [(13, 7, 6)]>', repr(play))

    def testBear(self):
        """Test bearing off moves."""
        self.setBoard(layout = ((6, 2), (5, 2)))
        check = [((20, OUT), (19, OUT)), ((19, 24), (19, OUT))]
        self.assertEqual(set(check), self.legal_moves)

    def testBearOver(self):
        """Test bearing off with over rolls."""
        self.setBoard(layout = ((4, 1), (3, 2)))
        check = [((21, OUT), (22, OUT))]
        self.assertEqual(set(check), self.legal_moves)

    def testBearPartial(self):
        """Test bearing off with empty point rolled."""
        self.setBoard(layout = ((6, 2), (4, 2)))
        check = [((19, 24), (19, OUT))]
        self.assertEqual(set(check), self.legal_moves)

    def testBearRepr(self):
        """Test debugging text representation of a bearing off move."""
        play = backgammon.BackgammonPlay(21, OUT, 5)
        self.assertEqual('<BackgammonPlay [(21, -2, 5)]>', repr(play))

    def testDoubles(self):
        """Test moves with doubles."""
        self.setBoard(layout = ((24, 1), (23, 1), (22, 1)), rolls = [1, 1, 1, 1])
        check = [((1, 2), (2, 3), (2, 3), (3, 4)),
            ((1, 2), (2, 3), (3, 4), (3, 4)),
            ((1, 2), (2, 3), (3, 4), (4, 5)),
            ((1, 2), (3, 4), (4, 5), (5, 6)),
            ((2, 3), (3, 4), (3, 4), (4, 5)),
            ((2, 3), (3, 4), (4, 5), (5, 6)),
            ((3, 4), (4, 5), (5, 6), (6, 7))]
        self.legal_moves = set([tuple(sorted(move)) for move in self.legal_moves])
        check = set(check)
        self.assertEqual(check, self.legal_moves)

    def testEnter(self):
        """Test moves from the bar."""
        self.setBoard(layout = ((7, 2),), bar = ['X', 'O'], rolls = [2, 3])
        check = [((BAR, 2), (2, 5)), ((BAR, 2), (18, 21)),
            ((BAR, 3), (3, 5)), ((BAR, 3), (18, 20))]
        self.assertEqual(set(check), self.legal_moves)

    def testEnterBlock(self):
        """Test moves from the bar with some moves blocked."""
        self.setBoard(layout = ((3, 2), (7, 2)), bar = ['X', 'O'], rolls = [2, 3])
        check = [((BAR, 2), (2, 5)), ((BAR, 2), (18, 21))]
        self.assertEqual(set(check), self.legal_moves)

    def testEnterNone(self):
        """Test moves from the bar when none are legal."""
        self.setBoard(layout = ((18, 2), (6, 2), (5, 2), (4, 2), (3, 2), (2, 2), (1, 2)), rolls = [6, 6],
            bar = ['X', 'O'])
        self.assertEqual(set(), self.legal_moves)

    def testEnterRepr(self):
        """Test debugging text representation of an entering move."""
        play = backgammon.BackgammonPlay(BAR, 2, 2)
        self.assertEqual('<BackgammonPlay [(-1, 2, 2)]>', repr(play))

    def testNone(self):
        """Test a situation with no legal moves."""
        self.setBoard(layout = ((7, 2), (6, 2), (5, 2), (4, 2), (3, 2), (2, 2), (24, 2)), rolls = [6, 6])
        self.assertEqual(set(), self.legal_moves)

    def testPartial(self):
        """Test moves where only part of the move is legal."""
        self.setBoard(layout = ((24, 1), (23, 1), (3, 2)), moves = [(24, 23)], rolls = [1, 1])
        check = [((1, 2),)]
        self.assertEqual(set(check), self.legal_moves)

    def testStart(self):
        """Test the moves at the start of the game."""
        self.setBoard()
        check = [((12, 17), (1, 7)), ((12, 17), (12, 18)),
            ((12, 17), (17, 23)), ((17, 22), (1, 7)),
            ((17, 22), (12, 18)), ((17, 22), (17, 23)),
            ((1, 7), (7, 12)), ((12, 18), (18, 23))]
        check = set(check)
        self.assertEqual(check, self.legal_moves)

    def testStartBlock(self):
        """Test the starting moves with a simple block."""
        self.setBoard(moves = [(13, 7), (8, 7)])
        check = [((12, 17), (12, 18)), ((12, 17), (17, 23)),
            ((17, 22), (12, 18)), ((17, 22), (17, 23)),
            ((12, 18), (18, 23))]
        check = set(check)
        self.assertEqual(check, self.legal_moves)

    def testUseBothDice(self):
        """Test being required to use both dice."""
        layout = ((2, 2), (4, 2), (8, 2), (20, 1), (24, 2))
        self.setBoard(layout = layout, moves = [(8, OUT), (8, OUT)])
        self.assertNotIn(((BAR, 2),), self.legal_moves)

    def testUseLargerDie(self):
        """Test being required to use the larger die."""
        self.setBoard(layout = ((5, 2),), moves = [(20, 24), (20, 24)], rolls = [3, 2], bar = ['X', 'O'])
        check = [((BAR, 3),)]
        self.assertEqual(set(check), self.legal_moves)


class PrintTest(unittest.TestCase):
    """Test printing of the board on the screen. (TestCase)"""

    def setUp(self):
        """Set up the test case. (None)"""
        self.board = backgammon.BackgammonBoard()

    def testStart(self):
        """Test printing the starting board."""
        self.assertEqual(PRINT_START, self.board.get_text('X'))

    def testBar(self):
        """Test printing with a piece on the bar."""
        self.board.cells[BAR].contents = ['X']
        check = PRINT_START + '\n\nBar: X'
        self.assertEqual(check, self.board.get_text('X'))


def make_play(moves):
    """
    Make a BackgammonPlay from a list of moves as tuples. (BackgammonPlay)

    Parameters:
    moves: A list of Backgammon moves as tuples. (tu)
    """
    play = backgammon.BackgammonPlay()
    for move in moves:
        play.add_move(*move)
    return play


if __name__ == '__main__':
    unittest.main()