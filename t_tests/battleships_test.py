"""
battleships_test.py

Unit testing of t_games/board_games/battleships_game.py

Classes:
SeaBoardTest: Tests of a player's Battleships' board. (unittest.TestCase)
"""


import unittest

import t_games.board_games.battleships_game as battleships
import unitility


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
