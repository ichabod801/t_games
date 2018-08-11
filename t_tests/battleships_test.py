"""
battleships_test.py

Unit testing of t_games/board_games/battleships_game.py

Classes:
SeaBoardTest: Tests of a player's Battleships' board. (unittest.TestCase)
"""


import unittest

import t_games.board_games.battleships_game as battleships


class SeaBoardTest(unittest.TestCase):
    """Tests of a player's Battleships' board. (unittest.TestCase)"""

    def setUp(self):
        self.bot = battleships.BattleBot()
        self.bot.name = 'Ramius'
        self.board = battleships.SeaBoard(self.bot)

    def testRepr(self):
        """Test the computer readable representaiton of a starting SeaBoard."""
        self.assertEqual('<SeaBoard for <BattleBot Ramius> with 0 of 17 hits>', repr(self.board))

    def testRepr(self):
        """Test the computer readable representaiton of a SeaBoard with some hits."""
        ship, squares = self.board.fleet[0]
        for square in squares[:-1]:
            #square_text = self.board.letters[square[0]] + self.board.numbers[square[1]]
            self.board.fire(square, self.bot)
        self.assertEqual('<SeaBoard for <BattleBot Ramius> with 0 of 17 hits>', repr(self.board))


if __name__ == '__main__':
    unittest.main()
