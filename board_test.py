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

    def testCapture(self):
        """Test capturing a piece from a BoardCell."""
        capture = self.cell.add_piece('&')
        self.assertEqual('@', capture)

    def testClear(self):
        """Test clearing a BoardCell."""
        self.cell.clear()
        self.assertIsNone(self.cell.contents)

    def testClearSpecific(self):
        """Test clearing a BoardCell with a specified nothing."""
        self.cell.clear(' ')
        self.assertEqual(' ', self.cell.contents)

    def testContains(self):
        """Test the in operator for BoardCell."""
        self.assertTrue('@' in self.cell)

    def testContainsNot(self):
        """The failure of the in operator for BoardCell."""
        self.assertFalse('p' in self.cell)

    def testCopyIndependence(self):
        """Test that the copied piece is independent of the BoardCell piece."""
        piece = self.cell.copy_piece()
        self.cell.add_piece('&')
        self.assertNotEqual(piece, self.cell.contents)

    def testCopyValue(self):
        """Test that copy_piece gives the correct value."""
        self.assertEqual('@', self.cell.copy_piece())

    def testGetPiece(self):
        """Test getting a piece from the cell."""
        self.assertEqual('@', self.cell.get_piece())

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

    def testRemoveContents(self):
        """Test BoardCell contents after removing a piece."""
        piece = self.cell.remove_piece()
        self.assertIsNone(self.cell.contents)

    def testRemoveReturn(self):
        """Test that removing a piece returns the correct value."""
        self.assertEqual('@', self.cell.remove_piece())

    def testRepr(self):
        """Test the repr of a BoardCell."""
        self.assertEqual("BoardCell('here', piece = '@')", repr(self.cell))

    def testReprEmpty(self):
        """Test the repr of an empty BoardCell."""
        self.cell.contents = None
        self.assertEqual("BoardCell('here')", repr(self.cell))

    def testReprDesign(self):
        """Test the repr of a BoardCell with a board design."""
        self.cell.empty = '+'
        self.assertEqual("BoardCell('here', piece = '@', empty = '+')", repr(self.cell))

    def testPlace(self):
        """Test adding a piece to a Board cell."""
        self.cell.add_piece('&')
        self.assertEqual('&', self.cell.contents)

    def testStr(self):
        """Test the string of a BoardCell."""
        self.assertEqual('@', str(self.cell))

    def testStrEmpty(self):
        """Test the string of an empty BoardCell."""
        self.cell.contents = None
        self.assertEqual(' ', str(self.cell))


if __name__ == '__main__':
    unittest.main()