"""
connect_four_test.py

Automated testing for connect_four_game.py.

Classes:
ABFindShortsTest: Tests of finding two or three pieces in a row. (TestCase)
"""


import unittest

import t_games.board_game.connect_four_game as connect_four
import t_tests.unitility as unitility


class ABFindShortsTest(unittest.TestCase):
    """Tests of finding two or three pieces in a row. (unittest.TestCase)"""

    def setUp(self):
        self.bot = connect_four.AlphaBetaBot()
        pieces = [(2, 0), (3, 0), (4, 0), (3, 1), (2, 2), (3, 2), (5, 2), (4, 3), (6, 3), (3, 4), (5, 4)]
        pieces.append((3, 5))
        self.shorts = self.bot.find_shorts(pieces)

