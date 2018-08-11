"""
yacht_test.py

Unit testing of t_games/dice_games/yacht_game.py.

Classes:
ScoreCategoryTest: Tests of score categories. (unittest.TestCase)
"""


import unittest

import t_games.dice_games.yacht_game as yacht


class ScoreCategory(unittest.TestCase):
    """Tests of score categories. (unittest.TestCase)"""

    def testReprFirst(self):
        """Test a simple points score category repr."""
        category = yacht.ScoreCategory('Broken Straight', 'Nothing', self.zero, '30', 42)
        self.assertEqual('<ScoreCategory Broken Straight (30/42)>', repr(category))

    def testReprNumber(self):
        """Test a simple points score category repr."""
        category = yacht.ScoreCategory('Straight', 'Ascending Ranks', self.zero, '30')
        self.assertEqual('<ScoreCategory Straight (30)>', repr(category))

    def testReprSubTotal(self):
        """Test the default sub-total category repr."""
        category = yacht.ScoreCategory('Eights', 'Eights', self.zero)
        self.assertEqual('<ScoreCategory Eights (Sub-total)>', repr(category))

    def testReprTotal(self):
        """Test a total scoring category repr."""
        category = yacht.ScoreCategory('Second Chance', 'Whatev', self.zero, 'total')
        self.assertEqual('<ScoreCategory Second Chance (Total)>', repr(category))

    def testReprTotalBonus(self):
        """Test a total scoring (with a bonus) category repr."""
        category = yacht.ScoreCategory('Third Chance', 'Whatever', self.zero, 'total+33')
        self.assertEqual('<ScoreCategory Third Chance (Total + 33)>', repr(category))

    def zero(self):
        """Dummy score function for testing score categories."""
        return 0


if __name__ == '__main__':
    unittest.main()
