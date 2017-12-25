"""
board_test.py

Unit testing of board.py.

Classes:
BoardCellTest: Tests of the board cell class. (TestCase)
"""


import unittest

import tgames.board as board


class BoardCellTest(unittest.TestCase):
    """Tests of the board cell class. (TestCase)"""

    def setUp(self):
        self.cell = board.BoardCell('here', '@')

    def testContains(self):
        """Test the in operator for BoardCell."""
        self.assertTrue('@' in self.cell)

    def testContainsNot(self):
        """The failure of the in operator for BoardCell."""
        self.assertFalse('p' in self.cell)

    def testHash(self):
        """Test for the expected hash of a BoardCell."""
        self.assertEqual(hash('here'), hash(self.cell))

    def testHashEquals(self):
        """Test for the same has for two BoardCells with the same location."""
        test_cell = board.BoardCell('here', 'knight')
        self.assertEqual(hash(test_cell), hash(self.cell))

    def testIteration(self):
        """Test iteration of a BoardCell."""
        self.assertEqual(['@'], list(self.cell))

    def testIterationEmpty(self):
        """Test iteration of an empty BoardCell."""
        self.cell.contents = None
        self.assertEqual([], list(self.cell))

    def testLength(self):
        """Test the length of a BoardCell."""
        self.assertEqual(1, len(self.cell))

    def testLengthEmpty(self):
        """Test the length of an empty BoardCell."""
        self.cell.contents = None
        self.assertEqual(0, len(self.cell))

    def testRepr(self):
        """Test the repr of a BoardCell."""
        self.assertEqual("BoardCell('here', piece = '@')", repr(self.cell))

    def testReprEmpty(self):
        """Test the repr of an empty BoardCell."""
        self.cell.contents = None
        self.assertEqual("BoardCell('here')", repr(self.cell))

    def testReprDesign(self):
        """Test the repr of a BoardCell."""
        self.cell.empty = '+'
        self.assertEqual("BoardCell('here', piece = '@', empty = '+')", repr(self.cell))


if __name__ == '__main__':
    unittest.main()