"""
wumpus_test.py

Unit testing of t_games/other_games/wumpus_game.py

Classes:
CaveTest: Tests of caves in the dungeon. (unittest.TestCase)
WumpusTest: Test the interface for Hunt the Wumpus. (unittest.TestCase)
"""


import unittest

from t_games.adventure_games import wumpus_game as wumpus
import unitility as unitility


class CaveTest(unittest.TestCase):
    """Tests of caves in the dungeon. (unittest.TestCase)"""

    def testReprPlain(self):
        """Test the debugging text of an empty cave."""
        cave = wumpus.Cave(18)
        self.assertEqual('<Cave 18>', repr(cave))

    def testReprWumpus(self):
        """Test the debugging text of a cave with a flag."""
        cave = wumpus.Cave(5)
        cave.wumpus = True
        self.assertEqual('<Cave 5 Wumpus>', repr(cave))


class WumpusTest(unittest.TestCase):
    """Test the interface for Hunt the Wumpus. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.game = wumpus.Wumpus(self.bot, 'none')

    def testBlank(self):
        self.bot.replies = ['', '!']
        self.game.play()
        self.assertEqual(["\nI do not recognize the command ''.\n"], self.bot.errors)


if __name__ == '__main__':
    unittest.main()
