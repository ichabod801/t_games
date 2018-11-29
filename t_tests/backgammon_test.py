"""
backgammon_test.py

Unit testing for backgammon_game.py.

Constants:
BAR: The index of the bar in BackgammonBoard.cells. (int)
OUT: The index of the removed pieces in BackgammonBoard.cells. (int)
START_TEXT_O: The starting text from the 'O' player's perspective. (str)
START_TEXT_X: The starting text from the 'X' player's perspective. (str)

Classes:
BackAutoBearTest: Tests of Backgammon.auto_bear. (unittest.TestCase)
BackBoardSetTest: A test case that can set up a board. (unittest.TestCase)
BackCheckWinTest: Tests of Backgammon.check_win. (BackBoardSetTest)
BackDefaultTest: Tests of Backgammon.default repeating move. (TestCase)
BackDoBearOTest: Tests of the bear command for O pieces. (unittest.TestCase)
BackDoBearOTest: Tests of the bear command for X pieces. (unittest.TestCase)
BackDoEnterTestO: Tests of the enter command for O pieces. (unittest.TestCase)
BackDoEnterTestX: Tests of the enter command for X pieces. (unittest.TestCase)
BackDoubleTest: Test handling of doubling requests. (unittest.TestCase)
BackGameOverTest: Test checking for Backgammon game end/final score. (TestCase)
BackGetRollsTest: Test getting the rolls from the dice. (unittest.TestCase)
BackGetStartTest: Tests of getting the start of a move. (unittest.TestCase)
BackGetTotalsTest: Test totalling dice in Backgammon. (unittest.TestCase)
BackMoveTest: Test movement on a BackgammonBoard. (unittest.TestCase)
BackPipCountTest: Tests of BackgammonBoard.get_pip_count. (BackBoardSetTest)
BackPlayTest: Test backgammon play generation. (BackBoardSetTest)
BackPrintTest: Test printing a backgammon board. (unittest.TestCase)
BackSetUpTest: Tests of setting up the board. (unittest.TestCase)
BackValidateMoveTest: Test validating moves in Backgammon. (unittest.TestCase)

Functions:
make_play: Make a BackgammonPlay from a list as tuples. (BackgammonPlay)
"""


import io
import unittest
import sys

import t_games.board_games.backgammon_game as backgammon
import t_games.player as player
import t_tests.unitility as unitility


BAR = -1

OUT = -2

START_TEXT_O = '\n'.join(['', '                      1 1 1  ', '  1 2 3 4 5 6   7 8 9 0 1 2  ',
    '+-------------+-------------+', '| O : . : . X | . X . : . O |', '| O : . : . X | . X . : . O |',
    '| . : . : . X | . X . : . O |', '| . : . : . X | . : . : . O |', '| . : . : . X | . : . : . O |',
    '|             |             |', '| : . : . : O | : . : . : X |', '| : . : . : O | : . : . : X |',
    '| : . : . : O | : O : . : X |', '| X . : . : O | : O : . : X |', '| X . : . : O | : O : . : X |',
    '+-------------+-------------+', '  2 2 2 2 2 1   1 1 1 1 1 1  ', '  4 3 2 1 0 9   8 7 6 5 4 3  '])

START_TEXT_X = '\n'.join(['', '  1 1 1 1 1 1   1 2 2 2 2 2  ', '  3 4 5 6 7 8   9 0 1 2 3 4  ',
    '+-------------+-------------+', '| X : . : O : | O : . : . X |', '| X : . : O : | O : . : . X |',
    '| X : . : O : | O : . : . : |', '| X : . : . : | O : . : . : |', '| X : . : . : | O : . : . : |',
    '|             |             |', '| O . : . : . | X . : . : . |', '| O . : . : . | X . : . : . |',
    '| O . : . X . | X . : . : . |', '| O . : . X . | X . : . : O |', '| O . : . X . | X . : . : O |',
    '+-------------+-------------+', '  1 1 1                      ', '  2 1 0 9 8 7   6 5 4 3 2 1  '])


class BackAutoBearTest(unittest.TestCase):
    """Tests of Backgammon.auto_bear. (unittest.TestCase)"""

    def getHome(self):
        """Get the state of X's home."""
        return [self.game.board.cells[point].contents for point in range(6, 0, -1)]

    def setUp(self):
        self.human = unitility.AutoBot()
        self.game = backgammon.Backgammon(self.human, 'none')
        self.game.board = backgammon.BackgammonBoard(layout = ((4, 1), (2, 1), (1, 2)))

    def testInside(self):
        """Test bearing two pieces below the max piece."""
        self.game.rolls = [2, 1]
        self.game.auto_bear(self.human, 'X')
        self.assertEqual([[], [], ['X'], [], [], ['X']], self.getHome())

    def testNoneHome(self):
        """Test a case where no bearing is possible."""
        self.game.rolls = [3, 3]
        self.game.auto_bear(self.human, 'X')
        self.assertEqual([[], [], ['X'], [], ['X'], ['X', 'X']], self.getHome())

    def testNoneWarning(self):
        """Test the warning from a case where no bearing is possible."""
        self.game.rolls = [3, 3]
        self.game.auto_bear(self.human, 'X')
        self.assertEqual('There are no pieces that can be auto-built.\n', self.human.errors[0])

    def testOnPoint(self):
        """Test bearing two pieces with exact rolls."""
        self.game.rolls = [4, 2]
        self.game.auto_bear(self.human, 'X')
        self.assertEqual([[], [], [], [], [], ['X', 'X']], self.getHome())

    def testOver(self):
        """Test bearing two pieces with over-rolls."""
        self.game.rolls = [6, 5]
        self.game.auto_bear(self.human, 'X')
        self.assertEqual([[], [], [], [], [], ['X', 'X']], self.getHome())

    def testPartialHome(self):
        """Test a case where only one roll can bear."""
        self.game.rolls = [3, 2]
        self.game.auto_bear(self.human, 'X')
        self.assertEqual([[], [], ['X'], [], [], ['X', 'X']], self.getHome())

    def testPartialHomeRoll(self):
        """Test thre remaining roll after a case where only one roll can bear."""
        self.game.rolls = [3, 2]
        self.game.auto_bear(self.human, 'X')
        self.assertEqual([3], self.game.rolls)


class BackBoardSetTest(unittest.TestCase):
    """A test case that can set up a board. (unittest.TestCase)"""

    def setBoard(self, layout = ((6, 5), (8, 3), (13, 5), (24, 2)), moves = [], piece = 'O',
        rolls = [6, 5], bar = []):
        """Set up the board for a test. (None)"""
        self.board = backgammon.BackgammonBoard(layout = layout)
        for captured in bar:
            self.board.cells[BAR].add_piece(captured)
        for start, end in moves:
            self.board.move(start, end)


class BackCheckWinTest(BackBoardSetTest):
    """Tests of Backgammon.check_win. (unittest.TestCase)"""

    def setBoard(self, layout = ((6, 5), (8, 3), (13, 5), (24, 2)), moves = [], piece = 'O',
        rolls = [6, 5], bar = []):
        """Set up the board for a test. (None)"""
        super(BackCheckWinTest, self).setBoard(layout, moves, piece, rolls, bar)
        self.human = unitility.AutoBot()
        self.game = backgammon.Backgammon(self.human, 'none')
        self.game.set_up()
        self.game.board = self.board
        self.game.board.cells[OUT].contents = [piece] * 15

    def testMatchWinBackgammonHome(self):
        """Test a match backgammon win due to a piece in the enemy's home."""
        self.setBoard(layout = ((1, 1),), piece = 'X')
        self.board.cells[1].contents = ['O']
        self.game.doubling_die = 2
        self.assertEqual(6, self.game.check_win('X'))

    def testMatchWinBackgammonBar(self):
        """Test a match backgammon win due to a piece on the bar."""
        self.setBoard(layout = ((1, 1),), piece = 'O')
        self.board.cells[1].contents = []
        self.board.cells[BAR].contents = ['X']
        self.game.doubling_die = 4
        self.assertEqual(12, self.game.check_win('O'))

    def testMatchWinBasic(self):
        """Test a match win."""
        self.setBoard(layout = ((1, 1),), piece = 'X')
        self.board.cells[1].contents = []
        self.board.cells[OUT].contents.append('O')
        self.game.doubling_die = 8
        self.assertEqual(8, self.game.check_win('X'))

    def testMatchWinGammon(self):
        """Test a match win with a gammon."""
        self.setBoard(layout = ((1, 1),), piece = 'O')
        self.board.cells[24].contents = []
        self.game.doubling_die = 16
        self.assertEqual(32, self.game.check_win('O'))

    def testWinBackgammonHome(self):
        """Test a backgammon win due to a piece in the enemy's home."""
        self.setBoard(layout = ((1, 1),), piece = 'X')
        self.board.cells[1].contents = ['O']
        self.assertEqual(3, self.game.check_win('X'))

    def testWinBackgammonBar(self):
        """Test a backgammon win due to a piece on the bar."""
        self.setBoard(layout = ((1, 1),), piece = 'O')
        self.board.cells[1].contents = []
        self.board.cells[BAR].contents = ['X']
        self.assertEqual(3, self.game.check_win('O'))

    def testWinBasic(self):
        """Test a basic win."""
        self.setBoard(layout = ((1, 1),), piece = 'X')
        self.board.cells[1].contents = []
        self.board.cells[OUT].contents.append('O')
        self.assertEqual(1, self.game.check_win('X'))

    def testWinGammon(self):
        """Test a win with a gammon."""
        self.setBoard(layout = ((1, 1),), piece = 'O')
        self.board.cells[24].contents = []
        self.assertEqual(2, self.game.check_win('O'))


class BackDefaultTest(unittest.TestCase):
    """Tests of Backgammon.default repeating move. (TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.game = backgammon.Backgammon(self.bot, 'none')
        self.game.player_index = 0

    def testAsterisk(self):
        """Test repeating a command with an asterisk."""
        self.game.default('13 7 * 2')
        self.assertEqual(['13 7', '13 7'], self.bot.held_inputs)

    def testError(self):
        """Test getting an error without any repeat syntax."""
        self.game.default('Sit!')
        self.assertEqual(['I do not understand that move.\n'], self.bot.errors)

    def testNoOpenError(self):
        """Test getting an error with no open parenthesis."""
        self.game.default('13 7 4)')
        self.assertEqual(['I do not understand that move.\n'], self.bot.errors)

    def testNoOpenHeld(self):
        """Test not holding anything with no open parenthesis."""
        self.game.default('13 7 4)')
        self.assertEqual([], self.bot.held_inputs)

    def testParentheses(self):
        """Test repeating a command with parentheses."""
        self.game.default('spam (4)')
        self.assertEqual(['spam', 'spam', 'spam', 'spam'], self.bot.held_inputs)

    def testSaveHeld(self):
        """Test keeping the player's current held inputs."""
        self.bot.held_inputs = ['eggs']
        self.game.default('spam * 3')
        self.assertEqual(['spam', 'spam', 'spam', 'eggs'], self.bot.held_inputs)


class BackDoBearOTest(unittest.TestCase):
    """Tests of the bear command with the O pieces in Backgammon. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.game = backgammon.Backgammon(self.bot, 'none')
        self.game.layout = ((4, 2), (2, 2), (1, 2))
        self.game.players[1] = unitility.AutoBot()
        self.game.players[1].name = 'Evil {}'.format(self.bot.name)
        self.game.set_up()
        self.game.player_index = self.game.players.index(self.game.bot)

    def testBarredBearError(self):
        """Test of error from bearing off an O with an O still on the bar."""
        self.game.rolls = [4, 2]
        self.game.board.cells[BAR].contents = ['O']
        self.game.do_bear('2')
        self.assertEqual(['You still have a piece on the bar.\n'], self.game.bot.errors)

    def testBarredBearPieces(self):
        """Test of pieces after bearing off an O with an O still on the bar."""
        self.game.rolls = [4, 2]
        self.game.board.cells[BAR].contents = ['O']
        self.game.do_bear('2')
        check = [2, 2, 0, 2, 0, 0]
        self.assertEqual(check, [len(self.game.board.cells[point]) for point in range(24, 18, -1)])

    def testBasicBear(self):
        """Test bearing off two O's with exact rolls."""
        self.game.rolls = [4, 2]
        self.game.do_bear('4 2')
        check = (['O'], ['O'])
        self.assertEqual(check, (self.game.board.cells[21].contents, self.game.board.cells[21].contents))

    def testBasicBearRolls(self):
        """Test the rolls after bearing off two O's with exact rolls."""
        self.game.rolls = [4, 2]
        self.game.do_bear('4 2')
        self.assertEqual([], self.game.rolls)

    def testHomelessBearError(self):
        """Test the error from trying to bear an O with pieces outside O's home."""
        self.game.rolls = [4, 2]
        self.game.board.cells[15].contents = ['O']
        self.game.do_bear('2')
        self.assertEqual(['You do not have all of your pieces in your home yet.\n'], self.game.bot.errors)

    def testHomelessBearPieces(self):
        """Test the pieces after trying to bear an O with pieces outside O's home."""
        self.game.rolls = [4, 2]
        self.game.board.cells[15].contents = ['O']
        self.game.do_bear('2')
        check = [2, 2, 0, 2, 0, 0]
        self.assertEqual(check, [len(self.game.board.cells[point]) for point in range(24, 18, -1)])

    def testNothingBearError(self):
        """Test the error from trying to bear an O from an empty space."""
        self.game.rolls = [3, 2]
        self.game.do_bear('3')
        self.assertEqual(['You do not have a piece on the 3 point.\n'], self.game.bot.errors)

    def testNothingBearPieces(self):
        """Test the the pieces after trying to bear an O from an empty space."""
        self.game.rolls = [3, 2]
        self.game.do_bear('3')
        check = [2, 2, 0, 2, 0, 0]
        self.assertEqual(check, [len(self.game.board.cells[point]) for point in range(24, 18, -1)])

    def testOverBear(self):
        """Test bearing with higher numbers than needed."""
        self.game.rolls = [6, 5]
        self.game.do_bear('4 4')
        self.assertEqual([], self.game.board.cells[21].contents)

    def testOverBearRolls(self):
        """Test the rolls after bearing with higher numbers than needed."""
        self.game.rolls = [6, 5]
        self.game.do_bear('4 4')
        self.assertEqual([], self.game.rolls)

    def testPartialBear(self):
        """Test bearing valid point before an invalid point."""
        self.game.rolls = [4, 3]
        self.game.do_bear('4 2')
        check = [2, 2, 0, 1, 0, 0]
        self.assertEqual(check, [len(self.game.board.cells[point]) for point in range(24, 18, -1)])

    def testPartialBearRolls(self):
        """Test the rolls afer bearing valid point before an invalid point."""
        self.game.rolls = [4, 3]
        self.game.do_bear('4 2')
        self.assertEqual([3], self.game.rolls)

    def testSingleBear(self):
        """Test bearing off one piece."""
        self.game.rolls = [4, 1]
        self.game.do_bear('1')
        self.assertEqual(['O'], self.game.board.cells[24].contents)

    def testSingleBearRolls(self):
        """Test the rolls after bearing off one piece."""
        self.game.rolls = [4, 1]
        self.game.do_bear('1')
        self.assertEqual([4], self.game.rolls)

    def testUnderBearError(self):
        """Test the error from bearing with higher number and higher pieces."""
        self.game.rolls = [6, 5]
        self.game.do_bear('2 2')
        self.assertEqual(['You must clear the pieces above the 2 point first.\n'], self.game.bot.errors)

    def testUnderBearPieces(self):
        """Test the error from bearing with higher number and higher pieces."""
        self.game.rolls = [6, 5]
        self.game.do_bear('2 2')
        check = [2, 2, 0, 2, 0, 0]
        self.assertEqual(check, [len(self.game.board.cells[point]) for point in range(24, 18, -1)])

    def testUnderRollError(self):
        """Test the error from bearing with higher number and higher pieces."""
        self.game.rolls = [3, 2]
        self.game.do_bear('4 4')
        self.assertEqual(['You need a higher roll to bear from the 4 point.\n'], self.game.bot.errors)

    def testUnderRollPieces(self):
        """Test the error from bearing with higher number and higher pieces."""
        self.game.rolls = [3, 2]
        self.game.do_bear('4 4')
        check = [2, 2, 0, 2, 0, 0]
        self.assertEqual(check, [len(self.game.board.cells[point]) for point in range(24, 18, -1)])


class BackDoBearXTest(unittest.TestCase):
    """Tests of the bear command with the X pieces in Backgammon. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.game = backgammon.Backgammon(self.bot, 'none')
        self.game.layout = ((4, 2), (2, 2), (1, 2))
        self.game.set_up()
        self.game.player_index = self.game.players.index(self.bot)

    def testAutoBear(self):
        """Test that auto_bear is called after do_bear with no arguments."""
        self.game.auto_bear = unitility.ProtoObject()
        self.game.rolls = [4, 2]
        self.game.do_bear('')
        self.assertEqual((self.bot, 'X'), self.game.auto_bear.args)

    def testBarredBearError(self):
        """Test of error from bearing off an X with an X still on the bar."""
        self.game.rolls = [4, 2]
        self.game.board.cells[BAR].contents = ['X']
        self.game.do_bear('2')
        self.assertEqual(['You still have a piece on the bar.\n'], self.bot.errors)

    def testBarredBearPieces(self):
        """Test of pieces after bearing off an X with an X still on the bar."""
        self.game.rolls = [4, 2]
        self.game.board.cells[BAR].contents = ['X']
        self.game.do_bear('2')
        self.assertEqual([2, 2, 0, 2, 0, 0], [len(self.game.board.cells[point]) for point in range(1, 7)])

    def testBasicBear(self):
        """Test bearing off two X's with exact rolls."""
        self.game.rolls = [4, 2]
        self.game.do_bear('4 2')
        check = (['X'], ['X'])
        self.assertEqual(check, (self.game.board.cells[4].contents, self.game.board.cells[4].contents))

    def testBasicBearRolls(self):
        """Test the rolls after bearing off two O's with exact rolls."""
        self.game.rolls = [4, 2]
        self.game.do_bear('4 2')
        self.assertEqual([], self.game.rolls)

    def testBearOff(self):
        """Test bearing with the off word."""
        self.game.rolls = [4, 2]
        self.game.do_bear('off 2')
        self.assertEqual(['X'], self.game.board.cells[2].contents)

    def testHomelessBearError(self):
        """Test the error from trying to bear an X with pieces outside X's home."""
        self.game.rolls = [4, 2]
        self.game.board.cells[15].contents = ['X']
        self.game.do_bear('2')
        self.assertEqual(['You do not have all of your pieces in your home yet.\n'], self.bot.errors)

    def testHomelessBearPieces(self):
        """Test the pieces trying to bear an X with pieces outside X's home."""
        self.game.rolls = [4, 2]
        self.game.board.cells[15].contents = ['X']
        self.game.do_bear('2')
        self.assertEqual([2, 2, 0, 2, 0, 0], [len(self.game.board.cells[point]) for point in range(1, 7)])

    def testNothingBearError(self):
        """Test the error from trying to bear an X from an empty space."""
        self.game.rolls = [3, 2]
        self.game.do_bear('3')
        self.assertEqual(['You do not have a piece on the 3 point.\n'], self.bot.errors)

    def testNothingBearPieces(self):
        """Test the the pieces after trying to bear an X from an empty space."""
        self.game.rolls = [3, 2]
        self.game.do_bear('3')
        self.assertEqual([2, 2, 0, 2, 0, 0], [len(self.game.board.cells[point]) for point in range(1, 7)])

    def testOverBear(self):
        """Test bearing with higher numbers than needed."""
        self.game.rolls = [6, 5]
        self.game.do_bear('4 4')
        self.assertEqual([], self.game.board.cells[4].contents)

    def testOverBearRolls(self):
        """Test the rolls after bearing with higher numbers than needed."""
        self.game.rolls = [6, 5]
        self.game.do_bear('4 4')
        self.assertEqual([], self.game.rolls)

    def testPartialBear(self):
        """Test bearing valid point before an invalid point."""
        self.game.rolls = [4, 3]
        self.game.do_bear('4 2')
        self.assertEqual([2, 2, 0, 1, 0, 0], [len(self.game.board.cells[point]) for point in range(1, 7)])

    def testPartialBearRolls(self):
        """Test the rolls afer bearing valid point before an invalid point."""
        self.game.rolls = [4, 3]
        self.game.do_bear('4 2')
        self.assertEqual([3], self.game.rolls)

    def testSingleBear(self):
        """Test bearing off one piece."""
        self.game.rolls = [4, 1]
        self.game.do_bear('1')
        self.assertEqual(['X'], self.game.board.cells[1].contents)

    def testSingleBearRolls(self):
        """Test the rolls after bearing off one piece."""
        self.game.rolls = [4, 1]
        self.game.do_bear('1')
        self.assertEqual([4], self.game.rolls)

    def testUnderBearError(self):
        """Test the error from bearing with higher number and higher pieces."""
        self.game.rolls = [6, 5]
        self.game.do_bear('2 2')
        self.assertEqual(['You must clear the pieces above the 2 point first.\n'], self.bot.errors)

    def testUnderBearPieces(self):
        """Test the error from bearing with higher number and higher pieces."""
        self.game.rolls = [6, 5]
        self.game.do_bear('2 2')
        self.assertEqual([2, 2, 0, 2, 0, 0], [len(self.game.board.cells[point]) for point in range(1, 7)])

    def testUnderRollError(self):
        """Test the error from bearing with higher number and higher pieces."""
        self.game.rolls = [3, 2]
        self.game.do_bear('4 4')
        self.assertEqual(['You need a higher roll to bear from the 4 point.\n'], self.bot.errors)

    def testUnderRollPieces(self):
        """Test the error from bearing with higher number and higher pieces."""
        self.game.rolls = [3, 2]
        self.game.do_bear('4 4')
        self.assertEqual([2, 2, 0, 2, 0, 0], [len(self.game.board.cells[point]) for point in range(1, 7)])

    def testWordBearError(self):
        """Test the error from bearing off with a word instead of a number."""
        self.game.rolls = [4, 1]
        self.game.do_bear('one')
        self.assertEqual(['Invalid argument to the bear command: one.\n'], self.bot.errors)

    def testWordBearPieces(self):
        """Test the pieces after bearing off with a word instead of a number."""
        self.game.rolls = [4, 1]
        self.game.do_bear('one')
        self.assertEqual([2, 2, 0, 2, 0, 0], [len(self.game.board.cells[point]) for point in range(1, 7)])


class BackDoEnterTestO(unittest.TestCase):
    """Tests of the enter command for O pieces in Backgammon."""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.game = backgammon.Backgammon(self.bot, 'none')
        self.game.layout = ((1, 2), (2, 1), (4, 2), (20, 1))
        self.game.players[1] = unitility.AutoBot()
        self.game.players[1].name = 'Evil {}'.format(self.bot.name)
        self.game.set_up()
        self.game.player_index = self.game.players.index(self.game.bot)
        self.game.board.cells[BAR].contents = ['O']

    def testEnterBlockedBar(self):
        """Test the bar after trying to enter a blocked point."""
        self.game.rolls = [4, 1]
        self.game.do_enter('4')
        self.assertEqual(['O'], self.game.board.cells[BAR].contents)

    def testEnterBlockedError(self):
        """Test the error from trying to enter a blocked point."""
        self.game.rolls = [4, 1]
        self.game.do_enter('4')
        self.assertEqual(['That point is blocked.\n'], self.game.bot.errors)

    def testEnterCaptureBar(self):
        """Test removing an O piece from the bar when entering a point with an X."""
        self.game.rolls = [2, 1]
        self.game.do_enter('2')
        self.assertEqual(['X'], self.game.board.cells[BAR].contents)

    def testEnterCaptureHome(self):
        """Test putting an O piece on the board when entering a point with an X."""
        self.game.rolls = [2, 1]
        self.game.do_enter('2')
        self.assertEqual(['O'], self.game.board.cells[5].contents)

    def testEnterCaptureRolls(self):
        """Test the rolls after entering an O piece on a point with an X."""
        self.game.rolls = [2, 1]
        self.game.do_enter('2')
        self.assertEqual([1], self.game.rolls)

    def testEnterEmptyBar(self):
        """Test removing an O piece from the bar when entering an empty space."""
        self.game.rolls = [6, 1]
        self.game.do_enter('6')
        self.assertEqual([], self.game.board.cells[BAR].contents)

    def testEnterEmptyHome(self):
        """Test putting an O piece on the board when entering an empty space."""
        self.game.rolls = [6, 1]
        self.game.do_enter('6')
        self.assertEqual(['O'], self.game.board.cells[6].contents)

    def testEnterEmptyRolls(self):
        """Test the rolls after entering an O piece to an empty space."""
        self.game.rolls = [6, 1]
        self.game.do_enter('6')
        self.assertEqual([1], self.game.rolls)

    def testEnterMineBar(self):
        """Test removing an O piece from the bar when entering a point with an O."""
        self.game.rolls = [6, 5]
        self.game.do_enter('5')
        self.assertEqual([], self.game.board.cells[BAR].contents)

    def testEnterMineHome(self):
        """Test putting an O piece on the board when entering a point with an O."""
        self.game.rolls = [6, 5]
        self.game.do_enter('5')
        self.assertEqual(['O', 'O'], self.game.board.cells[5].contents)

    def testEnterMineRolls(self):
        """Test the rolls after entering an O piece on a point with an O."""
        self.game.rolls = [6, 5]
        self.game.do_enter('5')
        self.assertEqual([6], self.game.rolls)

    def testEnterNoCaptureError(self):
        """Test the error from trying to enter without a piece on the bar."""
        self.game.rolls = [6, 1]
        self.game.board.cells[BAR].contents = []
        self.game.do_enter('6')
        self.assertEqual(['You do not have a piece on the bar.\n'], self.game.bot.errors)

    def testEnterNoRollBar(self):
        """Test the bar after trying to enter without the required roll."""
        self.game.rolls = [4, 1]
        self.game.do_enter('6')
        self.assertEqual(['O'], self.game.board.cells[BAR].contents)

    def testEnterNoRollError(self):
        """Test the error from trying to enter without the required roll."""
        self.game.rolls = [4, 1]
        self.game.do_enter('6')
        self.assertEqual(['You need to roll a 6 to enter on that point.\n'], self.game.bot.errors)

    def testEnterWordBar(self):
        """Test the bar after trying to enter with invalid input."""
        self.game.rolls = [5, 6]
        self.game.do_enter('six')
        self.assertEqual(['O'], self.game.board.cells[BAR].contents)

    def testEnterWordError(self):
        """Test the error from trying to enter with invalid input."""
        self.game.rolls = [5, 6]
        self.game.do_enter('six')
        self.assertEqual(["Invalid argument to the enter command: 'six'.\n"], self.game.bot.errors)


class BackDoEnterTestX(unittest.TestCase):
    """Tests of the enter command for X pieces in Backgammon."""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.game = backgammon.Backgammon(self.bot, 'none')
        self.game.layout = ((1, 2), (2, 1), (4, 2), (20, 1))
        self.game.set_up()
        self.game.player_index = self.game.players.index(self.bot)
        self.game.board.cells[BAR].contents = ['X']

    def testEnterBlockedBar(self):
        """Test the bar after trying to enter a blocked point."""
        self.game.rolls = [4, 1]
        self.game.do_enter('4')
        self.assertEqual(['X'], self.game.board.cells[BAR].contents)

    def testEnterBlockedError(self):
        """Test the error from trying to enter a blocked point."""
        self.game.rolls = [4, 1]
        self.game.do_enter('4')
        self.assertEqual(['That point is blocked.\n'], self.bot.errors)

    def testEnterCaptureBar(self):
        """Test removing an X piece from the bar when entering a point with an O."""
        self.game.rolls = [2, 1]
        self.game.do_enter('2')
        self.assertEqual(['O'], self.game.board.cells[BAR].contents)

    def testEnterCaptureHome(self):
        """Test putting an X piece on the board when entering a point with an O."""
        self.game.rolls = [2, 1]
        self.game.do_enter('2')
        self.assertEqual(['X'], self.game.board.cells[20].contents)

    def testEnterCaptureRolls(self):
        """Test the rolls after entering an O piece on a point with an X."""
        self.game.rolls = [2, 1]
        self.game.do_enter('2')
        self.assertEqual([1], self.game.rolls)

    def testEnterEmptyBar(self):
        """Test removing an X piece from the bar when entering an empty space."""
        self.game.rolls = [6, 1]
        self.game.do_enter('6')
        self.assertEqual([], self.game.board.cells[BAR].contents)

    def testEnterEmptyHome(self):
        """Test putting an X piece on the board when entering an empty space."""
        self.game.rolls = [6, 1]
        self.game.do_enter('6')
        self.assertEqual(['X'], self.game.board.cells[19].contents)

    def testEnterEmptyRolls(self):
        """Test the rolls after entering an X piece to an empty space."""
        self.game.rolls = [6, 1]
        self.game.do_enter('6')
        self.assertEqual([1], self.game.rolls)

    def testEnterMineBar(self):
        """Test removing an X piece from the bar when entering a point with an X."""
        self.game.rolls = [6, 5]
        self.game.do_enter('5')
        self.assertEqual([], self.game.board.cells[BAR].contents)

    def testEnterMineHome(self):
        """Test putting an X piece on the board when entering a point with an X."""
        self.game.rolls = [6, 5]
        self.game.do_enter('5')
        self.assertEqual(['X', 'X'], self.game.board.cells[20].contents)

    def testEnterMineRolls(self):
        """Test the rolls after entering an X piece on a point with an X."""
        self.game.rolls = [6, 5]
        self.game.do_enter('5')
        self.assertEqual([6], self.game.rolls)


class BackDoubleTest(unittest.TestCase):
    """Test handling of doubling requests in Backgammon. (unittest.TestCase)"""

    def setUp(self):
        self.bot_x = unitility.AutoBot()
        self.game = backgammon.Backgammon(self.bot_x, 'none')
        self.bot_o = unitility.AutoBot()
        if self.bot_x.name == self.bot_o.name:
            self.bot_o.name = 'Evil {}'.format(self.bot_x.name)
        self.game.players[1] = self.bot_o
        self.game.set_up()
        self.game.player_index = self.game.players.index(self.bot_x)

    def testDontAsk(self):
        """Test not asking a player for doubling."""
        self.game.doubling_status = 'O'
        self.assertTrue(self.game.double(self.bot_x, 'X'))

    def testDoubleDouble(self):
        """Test doubling the die."""
        self.bot_x.replies = ['Yes']
        self.bot_o.replies = ['1']
        self.game.double(self.bot_x, 'X')
        self.assertEqual(2, self.game.doubling_die)

    def testDoubleEightDouble(self):
        """Test doubling an already doubled die."""
        self.bot_x.replies = ['Yes']
        self.bot_o.replies = ['1']
        self.game.doubling_die = 8
        self.game.double(self.bot_x, 'X')
        self.assertEqual(16, self.game.doubling_die)

    def testDoubleMessage(self):
        """Test the message from doubling the die."""
        self.bot_x.replies = ['Yes']
        self.bot_o.replies = ['1']
        self.game.double(self.bot_x, 'X')
        check = '\n{} accepts the double, the doubling die is now at 2.\n'.format(self.bot_o.name)
        self.assertEqual(check, self.bot_x.info[1])

    def testDoubleReturn(self):
        """Test return value from doubling the die."""
        self.bot_x.replies = ['Yes']
        self.bot_o.replies = ['1']
        self.assertTrue(self.game.double(self.bot_x, 'X'))

    def testDoubleStatus(self):
        """Test status after doubling the die."""
        self.bot_x.replies = ['Yes']
        self.bot_o.replies = ['1']
        self.game.double(self.bot_x, 'X')
        self.assertEqual('O', self.game.doubling_status)

    def testNoDoubleDouble(self):
        """Test the player not doubling not doubling."""
        self.bot_x.replies = ['No']
        self.game.double(self.bot_x, 'X')
        self.assertEqual(1, self.game.doubling_die)

    def testNoDoubleReturn(self):
        """Test continuing the turn after the player not doubling."""
        self.bot_x.replies = ['No']
        self.assertTrue(self.game.double(self.bot_x, 'X'))

    def testRefuseContinue(self):
        """Test no match win after a doubling is refused."""
        self.bot_x.replies = ['yes', '']
        self.bot_o.replies = ['no']
        self.game.scores = {self.bot_x.name: 2, self.bot_o.name: 1}
        self.game.doubling_die = 1
        self.game.match = 8
        self.game.force_end = ''
        self.game.double(self.bot_o, 'O')
        self.assertEqual('', self.game.force_end)

    def testRefuseLoss(self):
        """Test O winning the game after a doubling is refused."""
        self.bot_x.replies = ['nein', '']
        self.bot_o.replies = ['Si']
        self.game.scores = {self.bot_x.name: 2, self.bot_o.name: 1}
        self.game.doubling_die = 8
        self.game.match = 8
        self.game.player_index = 1 - self.game.player_index
        self.game.force_end = ''
        self.game.double(self.bot_o, 'O')
        self.assertEqual('loss', self.game.force_end)

    def testRefuseLossMessage(self):
        """Test the message after O wins the game after a doubling is refused."""
        self.bot_x.replies = ['nein', '']
        self.bot_o.replies = ['Si']
        self.game.scores = {self.bot_x.name: 2, self.bot_o.name: 1}
        self.game.doubling_die = 8
        self.game.match = 8
        self.game.player_index = 1 - self.game.player_index
        self.game.force_end = ''
        self.game.double(self.bot_o, 'O')
        self.assertEqual('You lost the match. :(\n', self.bot_x.info[-1])

    def testRefuseMatchMessage(self):
        """Test the message after a doubling is refused."""
        self.bot_x.replies = ['Yes', '']
        self.bot_o.replies = ['nein']
        self.game.scores = {self.bot_x.name: 1, self.bot_o.name: 2}
        self.game.doubling_die = 2
        self.game.match = 4
        self.game.force_end = ''
        self.game.double(self.bot_x, 'X')
        check = '\nThe match score is now 3 to 2.\n'.format(self.bot_o.name)
        self.assertEqual(check, self.bot_x.info[2])

    def testRefuseMessage(self):
        """Test the message after a doubling is refused."""
        self.bot_x.replies = ['Yes', '']
        self.bot_o.replies = ['nein']
        self.game.scores = {self.bot_x.name: 2, self.bot_o.name: 1}
        self.game.double(self.bot_x, 'X')
        check = '\n{} refuses the double, you win the game.\n'.format(self.bot_o.name)
        self.assertEqual(check, self.bot_x.info[1])

    def testRefuseScore(self):
        """Test the score after a doubling is refused."""
        self.bot_x.replies = ['Yes', '']
        self.bot_o.replies = ['nein']
        self.game.scores = {self.bot_x.name: 1, self.bot_o.name: 1}
        self.game.double(self.bot_x, 'X')
        self.assertEqual(2, self.game.scores[self.bot_x.name])

    def testRefuseWin(self):
        """Test X winning the game after a doubling is refused."""
        self.bot_x.replies = ['Yes', '']
        self.bot_o.replies = ['nein']
        self.game.scores = {self.bot_x.name: 2, self.bot_o.name: 1}
        self.game.doubling_die = 2
        self.game.match = 4
        self.game.double(self.bot_x, 'X')
        self.assertEqual('win', self.game.force_end)

    def testRefuseWinMessage(self):
        """Test the message after X wins the game after a doubling is refused."""
        self.bot_x.replies = ['Yes', '']
        self.bot_o.replies = ['nein']
        self.game.scores = {self.bot_x.name: 2, self.bot_o.name: 1}
        self.game.doubling_die = 2
        self.game.match = 4
        self.game.double(self.bot_x, 'X')
        self.assertEqual('You won the match. :)\n', self.bot_x.info[-1])


class BackGameOverTest(unittest.TestCase):
    """Test checking for Backgammon game end and final score. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.game = backgammon.Backgammon(self.bot, 'none')
        self.game.set_up()
        self.game.scores = {player.name: 0 for player in self.game.players}
        self.game.win_loss_draw = [0, 0, 0]

    def testContinueContinue(self):
        """Test a human game continue w/l/d record."""
        self.game.game_over()
        self.assertEqual([0, 0, 0], self.game.win_loss_draw)

    def testContinueMessage(self):
        """Test a human game continue message."""
        self.game.game_over()
        self.assertEqual(1, len(self.bot.info))

    def testContinueResult(self):
        """Test a human game continue result."""
        self.assertFalse(self.game.game_over())

    def testContinueScore(self):
        """Test a human game continue score."""
        self.game.game_over()
        self.assertEqual(0, self.game.scores[self.game.bot.name])

    def testLoseLose(self):
        """Test a human game loss w/l/d record."""
        self.game.board.cells[OUT].contents = ['O'] * 15 + ['X']
        self.game.game_over()
        self.assertEqual([0, 1, 0], self.game.win_loss_draw)

    def testLoseMessage(self):
        """Test a human game loss message."""
        self.game.board.cells[OUT].contents = ['O'] * 15 + ['X']
        self.game.game_over()
        self.assertEqual('\nYou lose. :(\n', self.bot.info[1])

    def testLoseResult(self):
        """Test a human game loss result."""
        self.game.board.cells[OUT].contents = ['O'] * 15 + ['X']
        self.assertTrue(self.game.game_over())

    def testLoseScore(self):
        """Test a human game loss score."""
        self.game.board.cells[OUT].contents = ['O'] * 15 + ['X']
        self.game.game_over()
        self.assertEqual(1, self.game.scores[self.game.bot.name])

    def testMatchContinueContinue(self):
        """Test a human game continue w/l/d record."""
        self.game.board.cells[OUT].contents = ['O'] * 15 + ['X']
        self.game.match = 4
        self.game.game_over()
        self.assertEqual([0, 0, 0], self.game.win_loss_draw)

    def testMatchContinueMessage(self):
        """Test a human game continue message."""
        self.game.board.cells[OUT].contents = ['O'] * 15 + ['X']
        self.game.match = 4
        self.game.game_over()
        self.assertEqual(['\nYou lose. :(\n', 'The match score is 0 to 1.\n'], self.bot.info[1:])

    def testMatchContinueResult(self):
        """Test a human game continue result."""
        self.game.board.cells[OUT].contents = ['O'] * 15 + ['X']
        self.game.match = 4
        self.assertFalse(self.game.game_over())

    def testMatchContinueScore(self):
        """Test a human game continue score."""
        self.game.board.cells[OUT].contents = ['O'] * 15 + ['X']
        self.game.match = 4
        self.game.game_over()
        self.assertEqual(1, self.game.scores[self.game.bot.name])

    def testMatchLoseLose(self):
        """Test a human game loss w/l/d record."""
        self.game.board.cells[OUT].contents = ['O'] * 15
        self.game.match = 4
        self.game.scores[self.game.bot.name] = 1
        self.game.game_over()
        self.assertEqual([0, 1, 0], self.game.win_loss_draw)

    def testMatchLoseMessage(self):
        """Test a human game loss message."""
        self.game.board.cells[OUT].contents = ['O'] * 15
        self.game.match = 4
        self.game.scores[self.game.bot.name] = 1
        self.game.game_over()
        check = ['\nBackgammon!\n', '\nYou lose. :(\n', 'The match score is 0 to 4.\n']
        self.assertEqual(check, self.bot.info[1:])

    def testMatchLoseResult(self):
        """Test a human game loss result."""
        self.game.board.cells[OUT].contents = ['O'] * 15
        self.game.match = 4
        self.game.scores[self.game.bot.name] = 1
        self.assertTrue(self.game.game_over())

    def testMatchLoseScore(self):
        """Test a human game loss score."""
        self.game.board.cells[OUT].contents = ['O'] * 15
        self.game.match = 4
        self.game.scores[self.game.bot.name] = 1
        self.game.game_over()
        self.assertEqual(4, self.game.scores[self.game.bot.name])

    def testMatchWinMessage(self):
        """Test a human game win message."""
        self.game.board.cells[OUT].contents = ['X'] * 15
        self.game.match = 4
        self.game.scores[self.bot.name] = 1
        self.game.game_over()
        check = ['\nBackgammon!\n', '\nYou win!\n', 'The match score is 4 to 0.\n']
        self.assertEqual(check, self.bot.info[1:])

    def tesMatchWinResult(self):
        """Test a human game win result."""
        self.game.board.cells[OUT].contents = ['X'] * 15
        self.game.match = 4
        self.game.scores[self.bot.name] = 1
        self.assertTrue(self.game.game_over())

    def tesMatchWinScore(self):
        """Test a human game win score."""
        self.game.board.cells[OUT].contents = ['X'] * 15
        self.game.match = 4
        self.game.scores[self.bot.name] = 1
        self.game.game_over()
        self.assertEqual(3, self.game.scores[self.bot.name])

    def testMatchWinWin(self):
        """Test a human game win w/l/d record."""
        self.game.board.cells[OUT].contents = ['X'] * 15
        self.game.match = 4
        self.game.scores[self.bot.name] = 1
        self.game.game_over()
        self.assertEqual([1, 0, 0], self.game.win_loss_draw)

    def testWinMessage(self):
        """Test a human game win message."""
        self.game.board.cells[OUT].contents = ['X'] * 15 + ['O']
        self.game.game_over()
        self.assertEqual('\nYou win!\n', self.bot.info[1])

    def testWinResult(self):
        """Test a human game win result."""
        self.game.board.cells[OUT].contents = ['X'] * 15 + ['O']
        self.assertTrue(self.game.game_over())

    def testWinScore(self):
        """Test a human game win score."""
        self.game.board.cells[OUT].contents = ['X'] * 15 + ['O']
        self.game.game_over()
        self.assertEqual(1, self.game.scores[self.bot.name])

    def testWinWin(self):
        """Test a human game win w/l/d record."""
        self.game.board.cells[OUT].contents = ['X'] * 15 + ['O']
        self.game.game_over()
        self.assertEqual([1, 0, 0], self.game.win_loss_draw)


class BackGetRollsTest(unittest.TestCase):
    """Test getting the rolls from the dice. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.game = backgammon.Backgammon(self.bot, 'none')
        self.game.set_up()

    def testDoubles(self):
        """Test getting rolls with the both dice equal."""
        self.game.dice.values = [6, 6]
        self.game.get_rolls()
        self.assertEqual([6, 6, 6, 6], self.game.rolls)

    def testHighLow(self):
        """Test getting rolls with the high die first."""
        self.game.dice.values = [6, 1]
        self.game.get_rolls()
        self.assertEqual([6, 1], self.game.rolls)

    def testLowHigh(self):
        """Test getting rolls with the low die first."""
        self.game.dice.values = [3, 4]
        self.game.get_rolls()
        self.assertEqual([3, 4], self.game.rolls)


class BackGetStartTest(unittest.TestCase):
    """Tests of getting the start of a move. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.game = backgammon.Backgammon(self.bot, 'none')
        self.game.bot = unitility.AutoBot()
        self.game.players[1] = self.game.bot
        if self.bot.name == self.game.bot.name:
            self.game.bot.name = 'Evil {}'.format(self.bot.name)
        self.game.set_up()

    def testAmbiguousError(self):
        """Test an ambiguous end point's error."""
        self.game.rolls = [4, 2]
        self.game.get_start(4, -1, self.bot, 'X')
        self.assertEqual(['That move is ambiguous.\n'], self.bot.errors)

    def testAmbiguousReturn(self):
        """Test an ambiguous end point's return value."""
        self.game.rolls = [6, 1]
        self.assertEqual(-99, self.game.get_start(18, 1, self.game.bot, 'O'))

    def testBarO(self):
        """Test a starting point on the bar for O."""
        self.game.rolls = [6, 5]
        self.game.board.cells[BAR].contents = ['O']
        self.assertEqual(BAR, self.game.get_start(11, 1, self.game.bot, 'O'))

    def testBarX(self):
        """Test a starting point on the bar for X."""
        self.game.rolls = [6, 5]
        self.game.board.cells[BAR].contents = ['X']
        self.assertEqual(BAR, self.game.get_start(20, -1, self.bot, 'X'))

    def testDoubles(self):
        """Test gettig the start using three of four doubles."""
        self.game.rolls = [5, 5, 5, 5]
        self.assertEqual(1, self.game.get_start(16, 1, self.game.bot, 'O'))

    def testHighStart(self):
        """Test getting the start using the high die."""
        self.game.rolls = [6, 2]
        self.assertEqual(12, self.game.get_start(18, 1, self.game.bot, 'O'))

    def testInvalidError(self):
        """Test an invalid end point's error message."""
        self.game.rolls = [6, 6, 6, 6]
        self.game.get_start(9, -1, self.bot, 'X')
        self.assertEqual(['There is no legal move to that point.\n'], self.bot.errors)

    def testInvalidReturn(self):
        """Test an invalid end point's return value."""
        self.game.rolls = [1, 2]
        self.assertEqual(-99, self.game.get_start(23, 1, self.game.bot, 'O'))

    def testLowStart(self):
        """Test getting the start using the low die."""
        self.game.rolls = [1, 4]
        self.assertEqual(8, self.game.get_start(7, -1, self.bot, 'X'))

    def testSumStart(self):
        """Test getting the start using the sum of the dice."""
        self.game.rolls = [3, 1]
        self.assertEqual(24, self.game.get_start(21, -1, self.bot, 'X'))


class BackGetTotalsTest(unittest.TestCase):
    """Test totalling dice in Backgammon. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.game = backgammon.Backgammon(self.bot, 'none')

    def testOne(self):
        """Test the totals for a single die."""
        self.game.rolls = [5]
        self.assertEqual({5: [5]}, self.game.get_totals())

    def testTwo(self):
        """Test the totals for two dice."""
        self.game.rolls = [2, 3]
        self.assertEqual({2: [2], 3: [3], 5: [2, 3]}, self.game.get_totals())

    def testThree(self):
        """Test the totals for three dice."""
        self.game.rolls = [3, 3, 3]
        self.assertEqual({3: [3], 6: [3, 3], 9: [3, 3, 3]}, self.game.get_totals())

    def testFour(self):
        """Test the totals for four dice."""
        self.game.rolls = [4, 4, 4, 4]
        self.assertEqual({4: [4], 8: [4, 4], 12: [4, 4, 4], 16: [4, 4, 4, 4]}, self.game.get_totals())


class BackMoveTest(unittest.TestCase):
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


class BackPipCountTest(BackBoardSetTest):
    """Tests of BackgammonBoard.get_pip_count. (BackBoardSetTest)"""

    def getDoublePip(self):
        """Get both pip counts at the same time. (tuple of int)"""
        return (self.board.get_pip_count('X'), self.board.get_pip_count('O'))

    def testHyper(self):
        """Test the pip counts at the beginning of hypergammon."""
        self.setBoard(layout = ((24, 1), (23, 1), (22, 1)))
        self.assertEqual((69, 69), self.getDoublePip())

    def testLate(self):
        """Test the pip counts late in the game."""
        self.setBoard(layout = ((1, 4), (2, 2), (3, 2)), moves = [(23, OUT), (24, OUT)])
        self.assertEqual((14, 11), self.getDoublePip())

    def testSixOne(self):
        """Test the pip counts after X gets six-one"""
        self.setBoard(moves = [(13, 7), (8, 7)])
        self.assertEqual((160, 167), self.getDoublePip())

    def testStart(self):
        """Test the pip counts at the beginning of the game."""
        self.setBoard()
        self.assertEqual((167, 167), self.getDoublePip())


class BackPlayTest(BackBoardSetTest):
    """Test backgammon play generation. (BackBoardSetTest)"""

    def setBoard(self, layout = ((6, 5), (8, 3), (13, 5), (24, 2)), moves = [], piece = 'O',
        rolls = [6, 5], bar = []):
        """Set up the board for a test. (None)"""
        super(BackPlayTest, self).setBoard(layout, moves, piece, rolls, bar)
        raw_moves = self.board.get_plays(piece, rolls)
        self.legal_moves = set(tuple(move) for move in raw_moves)

    def testBasicRepr(self):
        """Test debugging text representation of a standard move."""
        play = backgammon.BackgammonPlay(13, 7, 6)
        self.assertEqual('<BackgammonPlay [(13, 7, 6)]>', repr(play))

    def testBasicStr(self):
        """Test human readable representation of a standard move."""
        play = backgammon.BackgammonPlay(13, 7, 6)
        play.add_move(8, 7, 1)
        self.assertEqual('6-1: 13/7 8/7', str(play))

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

    def testBearStr(self):
        """Test human readable representation of a bearing off move."""
        play = backgammon.BackgammonPlay(21, OUT, 5)
        play.add_move(20, OUT, 4)
        self.assertEqual('5-4: 21/out 20/out', str(play))

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

    def testDoublesStr(self):
        """Test human readable representation of move with doubles."""
        play = backgammon.BackgammonPlay(13, 7, 6)
        play.add_move(13, 7, 6)
        play.add_move(24, 18, 6)
        play.add_move(24, 18, 6)
        self.assertEqual('6-6: 13/7 (2) 24/18 (2)', str(play))

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

    def testEnterStr(self):
        """Test human readable representation of an entering move."""
        play = backgammon.BackgammonPlay(BAR, 5, 5)
        play.add_move(2, 5, 3)
        self.assertEqual('5-3: bar/5 2/5', str(play))

    def testNone(self):
        """Test a situation with no legal moves."""
        self.setBoard(layout = ((7, 2), (6, 2), (5, 2), (4, 2), (3, 2), (2, 2), (24, 2)), rolls = [6, 6])
        self.assertEqual(set(), self.legal_moves)

    def testPartial(self):
        """Test moves where only part of the move is legal."""
        self.setBoard(layout = ((24, 1), (23, 1), (3, 2)), moves = [(24, 23)], rolls = [1, 1])
        check = [((1, 2),)]
        self.assertEqual(set(check), self.legal_moves)

    def testPartialStr(self):
        """Test human readable representation of a partial."""
        play = backgammon.BackgammonPlay(BAR, 5, 5)
        self.assertEqual('5: bar/5', str(play))

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


class BackPrintTest(unittest.TestCase):
    """Test printing of the board on the screen. (TestCase)"""

    def setUp(self):
        """Set up the test case. (None)"""
        self.board = backgammon.BackgammonBoard()
        self.maxDiff = None

    def testBarO(self):
        """Test printing with a piece on the bar from O's perspective."""
        self.board.cells[BAR].contents = ['O']
        check = START_TEXT_O + '\n\nBar: O'
        self.assertEqual(check, self.board.get_text('O'))

    def testBarX(self):
        """Test printing with a piece on the bar."""
        self.board.cells[BAR].contents = ['X']
        check = START_TEXT_X + '\n\nBar: X'
        self.assertEqual(check, self.board.get_text('X'))

    def testSixHighO(self):
        """Test printing an O board with more than five O's on a point."""
        self.board.cells[12].contents = ['O'] * 6
        check = START_TEXT_O[:117] + '6' + START_TEXT_O[118:]
        self.assertEqual(check, self.board.get_text('O'))

    def testSixHighX(self):
        """Test printing an X board with more than five X's on a point."""
        self.board.cells[13].contents = ['X'] * 6
        check = START_TEXT_X[:93] + '6' + START_TEXT_X[94:]
        self.assertEqual(check, self.board.get_text('X'))

    def testSixLowO(self):
        """Test printing an O board with more than five X's on a point."""
        self.board.cells[13].contents = ['X'] * 6
        check = START_TEXT_O[:417] + '6' + START_TEXT_O[418:]
        self.assertEqual(check, self.board.get_text('O'))

    def testSixLowX(self):
        """Test printing an X board with more than five O's on a point."""
        self.board.cells[12].contents = ['O'] * 6
        check = START_TEXT_X[:393] + '6' + START_TEXT_X[394:]
        self.assertEqual(check, self.board.get_text('X'))

    def testStartO(self):
        """Test printing the starting board from O's perspective."""
        self.assertEqual(START_TEXT_O, self.board.get_text('O'))

    def testStartX(self):
        """Test printing the starting board."""
        self.assertEqual(START_TEXT_X, self.board.get_text('X'))

    def testTenHighO(self):
        """Test printing an O board with more than nine X's on a point."""
        self.board.cells[6].contents = ['X'] * 10
        check = START_TEXT_O[:103] + '1' + START_TEXT_O[104:133] + '0' + START_TEXT_O[134:]
        self.assertEqual(check, self.board.get_text('O'))

    def testTenHighX(self):
        """Test printing an X board with more than nine O's on a point."""
        self.board.cells[19].contents = ['O'] * 10
        check = START_TEXT_X[:107] + '1' + START_TEXT_X[108:137] + '0' + START_TEXT_X[138:]
        self.assertEqual(check, self.board.get_text('X'))

    def testTenLowO(self):
        """Test printing an O board with more than nine O's on a point."""
        self.board.cells[19].contents = ['O'] * 10
        check = START_TEXT_O[:373] + '1' + START_TEXT_O[374:403] + '0' + START_TEXT_O[404:]
        self.assertEqual(check, self.board.get_text('O'))

    def testTenLowX(self):
        """Test printing a board with more than nine X's on a point."""
        self.board.cells[6].contents = ['X'] * 10
        check = START_TEXT_X[:377] + '1' + START_TEXT_X[378:407] + '0' + START_TEXT_X[408:]
        self.assertEqual(check, self.board.get_text('X'))


class BackSetUpTest(unittest.TestCase):
    """Tests of setting up the board. (unittest.TestCase)"""

    def setUp(self):
        self.board = backgammon.BackgammonBoard()

    def testHigh(self):
        """Test pieces being placed on the high half of the board."""
        self.assertEqual(['X', 'X'], self.board.cells[24].contents)

    def testHighCross(self):
        """Test pieces being placed across from the high half of the board."""
        self.assertEqual(['O'] * 5, self.board.cells[12].contents)

    def testLow(self):
        """Test pieces being placed on the low half of the board."""
        self.assertEqual(['X'] * 5, self.board.cells[6].contents)

    def testLowCross(self):
        """Test pieces being placed on the low half of the board."""
        self.assertEqual(['O'] * 3, self.board.cells[17].contents)


class BackValidateMoveTest(unittest.TestCase):
    """Test validating moves in Backgammon. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.game = backgammon.Backgammon(self.bot, 'none')
        self.game.bot = unitility.AutoBot()
        self.game.players[1] = self.game.bot
        if self.bot.name == self.game.bot.name:
            self.game.bot.name = 'Evil {}'.format(self.bot.name)
        self.game.set_up()

    def legalPlays(self, player_piece):
        """
        Get the legal plays. (set)

        Parameters:
        player_piece: The piece to get legal plays for. (str)
        """
        legal_plays = self.game.board.get_plays(player_piece, self.game.rolls)
        legal_moves = set()
        for play in legal_plays:
            for move in play:
                legal_moves.add(move)
        return legal_moves

    def testBarError(self):
        """Test the error from a piece on the bar blocking a move."""
        self.game.rolls = [1, 4]
        self.game.board.cells[BAR].contents = ['X']
        self.game.validate_move(13, 8, -1, self.legalPlays('X'), self.bot, 'X')
        check = ['You must re-enter your piece on the bar before making any other move.\n']
        self.assertEqual(check, self.bot.errors)

    def testBarReturn(self):
        """Test the return value from a piece on the bar blocking a move."""
        self.game.rolls = [1, 4]
        self.game.board.cells[BAR].contents = ['X']
        self.assertEqual([], self.game.validate_move(13, 7, -1, self.legalPlays('X'), self.bot, 'X'))

    def testBlockedOneError(self):
        """Test the error from a one-die move being blocked."""
        self.game.rolls = [5, 3]
        self.game.validate_move(1, 6, 1, self.legalPlays('O'), self.game.bot, 'O')
        self.assertEqual(['That move is blocked.\n'], self.game.bot.errors)

    def testBlockedOneReturn(self):
        """Test the return value from a one-die move being blocked."""
        self.game.rolls = [5, 3]
        self.assertEqual([], self.game.validate_move(1, 6, 1, self.legalPlays('O'), self.game.bot, 'O'))

    def testBlockedTwoError(self):
        """Test the error from a two-die move being blocked."""
        self.game.rolls = [1, 1, 1, 1]
        self.game.validate_move(13, 11, -1, self.legalPlays('X'), self.bot, 'X')
        self.assertEqual(['That move is blocked.\n'], self.bot.errors)

    def testBlockedTwoReturn(self):
        """Test the return value from a two-die move being blocked."""
        self.game.rolls = [1, 1, 1, 1]
        self.assertEqual([], self.game.validate_move(13, 11, -1, self.legalPlays('X'), self.bot, 'X'))

    def testNoPieceError(self):
        """Test the error from having no piece on the start point."""
        self.game.rolls = [5]
        self.game.validate_move(18, 13, -1, self.legalPlays('X'), self.bot, 'X')
        self.assertEqual(['You do not have a piece on that starting point.\n'], self.bot.errors)

    def testNoPieceReturn(self):
        """Test the return value from having no piece on the start point."""
        self.game.rolls = [5]
        self.assertEqual([], self.game.validate_move(18, 13, -1, self.legalPlays('X'), self.bot, 'X'))

    def testNoRollError(self):
        """Test the error from not having a roll matching the move."""
        self.game.rolls = [2, 3]
        self.game.validate_move(12, 18, 1, self.legalPlays('O'), self.game.bot, 'O')
        self.assertEqual(['You do not have a die roll matching that move.\n'], self.game.bot.errors)

    def testNoRollReturn(self):
        """Test the return value from not having a roll matching the move."""
        self.game.rolls = [2, 3]
        self.assertEqual([], self.game.validate_move(12, 18, 1, self.legalPlays('O'), self.game.bot, 'O'))

    def testNotBothError(self):
        """Test the error from not using both dice."""
        self.game.board.clear()
        self.game.board.set_up(((15, 2), (7, 1), (3, 2)))
        self.game.board.cells[16].contents = ['X', 'X']
        self.game.rolls = [6, 1]
        self.game.validate_move(18, 19, 1, self.legalPlays('O'), self.game.bot, 'O')
        check = ['That move would not allow for the maximum possible play.\n']
        self.assertEqual(check, self.game.bot.errors)

    def testNotBothReturn(self):
        """Test the return value from not using both dice."""
        self.game.board.clear()
        self.game.board.set_up(((15, 2), (7, 1), (3, 2)))
        self.game.board.cells[16].contents = ['X', 'X']
        self.game.rolls = [6, 1]
        self.assertEqual([], self.game.validate_move(18, 19, 1, self.legalPlays('O'), self.game.bot, 'O'))

    def testNotMaxError(self):
        """Test the error from not making the maximum possible move."""
        self.game.board.clear()
        self.game.board.cells[6].contents = ['O', 'O']
        self.game.board.cells[13].contents = ['X']
        self.game.rolls = [5, 2]
        self.game.validate_move(13, 11, -1, self.legalPlays('X'), self.bot, 'X')
        check = ['That move would not allow for the maximum possible play.\n']
        self.assertEqual(check, self.bot.errors)

    def testNotMaxReturn(self):
        """Test the return value from not making the maximum possible move."""
        self.game.board.clear()
        self.game.board.cells[6].contents = ['O', 'O']
        self.game.board.cells[13].contents = ['X']
        self.game.rolls = [5, 2]
        self.assertEqual([], self.game.validate_move(13, 11, -1, self.legalPlays('X'), self.bot, 'X'))


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