"""
battleships_test.py

Unit testing of t_games/board_games/battleships_game.py

Classes:
GameOverTest: Tests of Battleships.game_over. (unittest.TestCase)
SeaBoardTest: Tests of a player's Battleships' board. (unittest.TestCase)
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


class SeaBoardTest(unittest.TestCase):
    """Tests of a player's Battleships' board. (unittest.TestCase)"""

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
