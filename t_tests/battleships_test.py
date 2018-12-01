"""
battleships_test.py

Unit testing of t_games/board_games/battleships_game.py

Classes:
GameOverTest: Tests of Battleships.game_over. (unittest.TestCase)
SeaBoardAdjTest: Test of adjacent squares on a Battleships' board. (TestCase)
SeaBoardFireTest: Test of firing on a Battleships' board. (unittest.TestCase)
SeaBoardTextTest: Tests of text versions of a Battleships' board. (TestCase)
"""


import unittest

import t_games.board_games.battleships_game as battleships
import t_tests.unitility as unitility


class GameOverTest(unittest.TestCase):
    """Tests of Battleships.game_over. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot(['r'] * 5)
        self.game = battleships.Battleships(self.bot, 'none')
        self.game.set_up()
        self.game.win_loss_draw = [0, 0, 0]
        self.game.scores = {player.name: 0 for player in self.game.players}

    def testContinueReturn(self):
        """Test the return value from an unfinished game."""
        self.assertFalse(self.game.game_over())

    def testDrawMessage(self):
        """Test the message displayed for a draw."""
        self.game.boards[self.bot.name].fleet = []
        self.game.boards[self.game.bot.name].fleet = []
        self.game.game_over()
        check = "\nIt's a draw! You destroyed each other's fleets at the same time.\n"
        self.assertEqual(check, self.bot.info[-1])

    def testDrawResults(self):
        """Test the results after a draw."""
        self.game.boards[self.bot.name].fleet = []
        self.game.boards[self.game.bot.name].fleet = []
        self.game.game_over()
        self.assertEqual([0, 0, 1], self.game.win_loss_draw)

    def testDrawReturn(self):
        """Test the return value from for a draw."""
        self.game.boards[self.bot.name].fleet = []
        self.game.boards[self.game.bot.name].fleet = []
        self.assertTrue(self.game.game_over())

    def testLossMessage(self):
        """Test the messages displayed for a loss."""
        self.game.boards[self.bot.name].fleet = []
        self.game.game_over()
        check = ["\n{} sank your fleet. You lose.\n".format(self.game.bot.name)]
        check.append('{} had 17 squares of ships left.\n'.format(self.game.bot.name))
        self.assertEqual(check, self.bot.info[-2:])

    def testLossResults(self):
        """Test the results after a loss."""
        self.game.boards[self.bot.name].fleet = []
        self.game.game_over()
        self.assertEqual([0, 1, 0], self.game.win_loss_draw)

    def testLossReturn(self):
        """Test the return value from a loss."""
        self.game.boards[self.bot.name].fleet = []
        self.game.game_over()
        self.assertTrue(self.game.game_over())

    def testLossScore(self):
        """Test the score a loss."""
        self.game.boards[self.bot.name].fleet = []
        self.game.game_over()
        self.assertEqual(-17, self.game.scores[self.bot.name])

    def testWinMessage(self):
        """Test the messages displayed for a win."""
        self.game.boards[self.game.bot.name].fleet = []
        self.game.game_over()
        check = ["\nYou sank {}'s fleet and won!\n".format(self.game.bot.name)]
        check.append('You have 17 squares of ships left.\n')
        self.assertEqual(check, self.bot.info[-2:])

    def testWinResults(self):
        """Test the results after a win."""
        self.game.boards[self.game.bot.name].fleet = []
        self.game.game_over()
        self.assertEqual([1, 0, 0], self.game.win_loss_draw)

    def testWinReturn(self):
        """Test the return value from a win."""
        self.game.boards[self.game.bot.name].fleet = []
        self.game.game_over()
        self.assertTrue(self.game.game_over())

    def testWinScore(self):
        """Test the score a win."""
        self.game.boards[self.game.bot.name].fleet = []
        self.game.game_over()
        self.assertEqual(17, self.game.scores[self.bot.name])


class SeaBoardAdjTest(unittest.TestCase):
    """Test of adjacent squares on a Battleships' board. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot(['r'] * 5)
        self.board = battleships.SeaBoard(self.bot)

    def testBottom(self):
        """Test adjacent squares of a square on the bottom."""
        self.assertEqual(['B1', 'A0', 'A2'], self.board.adjacent_squares('A1'))

    def testBottomLeft(self):
        """Test adjacent squares of a square on the bottom left."""
        self.assertEqual(['B0', 'A1'], self.board.adjacent_squares('A0'))

    def testLeft(self):
        """Test adjacent squares of a square on the left."""
        self.assertEqual(['D0', 'F0', 'E1'], self.board.adjacent_squares('E0'))

    def testLeftTop(self):
        """Test adjacent squares of a square on the left top."""
        self.assertEqual(['I0', 'J1'], self.board.adjacent_squares('J0'))

    def testMiddle(self):
        """Test adjacent squares of a square in the middle."""
        self.assertEqual(['B4', 'D4', 'C3', 'C5'], self.board.adjacent_squares('C4'))

    def testRight(self):
        """Test adjacent squares of a square on the right."""
        self.assertEqual(['F9', 'H9', 'G8'], self.board.adjacent_squares('G9'))

    def testRightBottom(self):
        """Test adjacent squares of a square on the right bottom."""
        self.assertEqual(['I0', 'J1'], self.board.adjacent_squares('J0'))

    def testTop(self):
        """Test adjacent squares of a square on the top."""
        self.assertEqual(['I5', 'J4', 'J6'], self.board.adjacent_squares('J5'))

    def testTopRight(self):
        """Test adjacent squares of a square on the top right."""
        self.assertEqual(['I9', 'J8'], self.board.adjacent_squares('J9'))


class SeaBoardFireTest(unittest.TestCase):
    """Test of firing on a Battleships' board. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot(['J0 J4', 'H0 H3', 'F0 F2', 'D0 D2', 'B0 B1'])
        self.board = battleships.SeaBoard(self.bot)
        self.foe = unitility.AutoBot()

    def testHitHit(self):
        """Test a basic hit getting recorded."""
        self.board.fire('J0', self.foe)
        self.assertIn('J0', self.board.hits)

    def testHitMessage(self):
        """Test notification of a basic hit."""
        self.board.fire('H1', self.foe)
        self.assertEqual(['You hit.\n'], self.foe.info)

    def testHitRemoval(self):
        """Test a basic hit being marked on the ship."""
        self.board.fire('F2', self.foe)
        self.assertNotIn('F2', self.board.fleet[2][1])

    def testMissMessage(self):
        """Test notification of a basic miss."""
        self.board.fire('C4', self.foe)
        self.assertEqual(['You missed.\n'], self.foe.info)

    def testMissMiss(self):
        """Test a basic miss being recorded."""
        self.board.fire('J9', self.foe)
        self.assertEqual({'J9'}, self.board.misses)

    def testSinkFleet(self):
        """Test updating a fleet when all ships are sunk."""
        for square in 'J0 J1 J2 J3 J4 H0 H1 H2 H3 F0 F1 F2 D0 D1 D2 B0 B1'.split():
            self.board.fire(square, self.foe)
        self.assertEqual([], self.board.fleet)

    def testSinkMessageFoe(self):
        """Test notifying the attacker of a sunk ship."""
        self.board.fire('B0', self.foe)
        self.board.fire('B1', self.foe)
        self.assertEqual(['You hit.\n', 'You hit.\n', 'You sank a destroyer.\n'], self.foe.info)

    def testSinkMessagePlayer(self):
        """Test notifying the owner of a sunk ship."""
        self.board.fire('D0', self.foe)
        self.board.fire('D1', self.foe)
        self.board.fire('D2', self.foe)
        self.assertEqual(['Your submarine has been sunk.\n'], self.bot.info[5:])


class SeaBoardTextTest(unittest.TestCase):
    """Tests of text versions of a Battleships' board. (unittest.TestCase)"""

    def setUp(self):
        self.bot = battleships.BattleBot()
        self.bot.name = 'Ramius'
        self.board = battleships.SeaBoard(self.bot)

    def testRepr(self):
        """Test the computer readable representaiton of a starting SeaBoard."""
        self.assertEqual('<SeaBoard for <BattleBot Ramius> with 0 of 17 hits>', repr(self.board))

    def testReprHit(self):
        """Test the computer readable representaiton of a SeaBoard with some hits."""
        # Hit a ship but don't sink it.
        ship, squares = self.board.fleet[0]
        for square in squares[:-1]:
            self.board.fire(square, unitility.AutoBot())
        # Check the repr.
        self.assertEqual('<SeaBoard for <BattleBot Ramius> with 4 of 17 hits>', repr(self.board))

    def testReprSunk(self):
        """Test the computer readable representaiton of a SeaBoard with a ship sunk."""
        # Sink a ship
        ship, squares = self.board.fleet[0]
        for square in squares[:]:
            self.board.fire(square, unitility.AutoBot())
        # Check the repr.
        self.assertEqual('<SeaBoard for <BattleBot Ramius> with 5 of 17 hits>', repr(self.board))


if __name__ == '__main__':
    unittest.main()
