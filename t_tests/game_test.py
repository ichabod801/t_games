"""
game_test.py

Unit tests of t_games/game.py.

Classes:
GameTest: Tests of the base game class. (unittest.TestCase)
"""


import unittest

import t_games.game as game
import t_games.player as player
import unitility


class GameTest(unittest.TestCase):
    """Tests of the base game class. (unittest.TestCase)"""

    def setUp(self):
        self.game = game.Game(unitility.AutoBot(), '')

    def testRepr(self):
        """Test the game's debugging text representation."""
        self.assertEqual('<Game of Null with 1 player>', repr(self.game))

    def testReprMulti(self):
        """Test the game's debugging text representation with multiple players."""
        self.game.players.append(player.Bot())
        self.game.players.append(player.Bot())
        self.assertEqual('<Game of Null with 3 players>', repr(self.game))


if __name__ == '__main__':
    unittest.main()
