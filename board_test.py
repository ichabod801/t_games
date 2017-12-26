"""
board_test.py

Unit testing of board.py.

Classes:
BoardCellTest: Tests of the board cell class. (TestCase)
CoordinateTest: Tests of n-dimensional coordinates. (TestCase)
MultiCellTest: Tests of the multi-cell class. (TestCase)
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

class CoordinateTest(unittest.TestCase):
    """Tests of multi-dimensional coordinates. (TestCase)"""

    def testAbs(self):
        """Test the absolute value of coordinates."""
        self.assertEqual(board.Coordinate((8, 1)), abs(board.Coordinate((-8, 1))))

    def testAdd(self):
        """Test addition of coordinates."""
        a = board.Coordinate((8, 0, 1))
        b = board.Coordinate((1, 2, 3))
        self.assertEqual(board.Coordinate((9, 2, 4)), a + b)

    def testAddNegative(self):
        """Test addition of coordinates with a negative coordinate."""
        a = board.Coordinate((8, 0, 1))
        b = board.Coordinate((-1, -2, -3))
        self.assertEqual(board.Coordinate((7, -2, -2)), a + b)

    def testAddRight(self):
        """Test addition of tuple to a coordinate on the right"""
        total = (5, 4) + board.Coordinate((3, 2))
        self.assertEqual(board.Coordinate((8, 6)), total)
        self.assertTrue(isinstance(total, board.Coordinate))

    def testAddTuple(self):
        """Test adding a coordinate to a tuple."""
        total = board.Coordinate((3, 2)) + (5, 4)
        self.assertEqual(board.Coordinate((8, 6)), total)
        self.assertTrue(isinstance(total, board.Coordinate))

    def testMultiply(self):
        """Test multiplying a coordinate by a scalar."""
        product = board.Coordinate((3, 2)) * 5
        self.assertEqual(board.Coordinate((15, 10)), product)
        self.assertTrue(isinstance(product, board.Coordinate))

    def testMultiplyRight(self):
        """Test multiplying a coordinate on the right by a scalar."""
        product = 5 * board.Coordinate((3, 2))
        self.assertEqual(board.Coordinate((15, 10)), product)
        self.assertTrue(isinstance(product, board.Coordinate))

    def testNegate(self):
        """Test negation of a coordinate"""
        self.assertEqual(-board.Coordinate((1, -2, 3)), board.Coordinate((-1, 2, -3)))

    def testSubtract(self):
        """Test subtraction of coordinates."""
        a = board.Coordinate((8, 0, 1))
        b = board.Coordinate((1, 2, 3))
        self.assertEqual(board.Coordinate((7, -2, -2)), a - b)

    def testSubtractionNegative(self):
        """Test subtraction of coordinates with a negative coordinate."""
        a = board.Coordinate((8, 0, 1))
        b = board.Coordinate((-1, -2, -3))
        self.assertEqual(board.Coordinate((9, 2, 4)), a - b)

    def testSubtractRight(self):
        """Test subtraction of a tuple from a coordinate."""
        total = (5, 4) - board.Coordinate((3, 2))
        self.assertEqual(board.Coordinate((2, 2)), total)
        self.assertTrue(isinstance(total, board.Coordinate))

    def testSubtractTuple(self):
        """Test subtraction of a coordinate from a tuple."""
        total = board.Coordinate((3, 2)) - (5, 4)
        self.assertEqual(board.Coordinate((-2, -2)), total)
        self.assertTrue(isinstance(total, board.Coordinate))


class MultiCellTest(unittest.TestCase):
    """Tests of the multi-cell class. (TestCase)"""

    def setUp(self):
        self.cell = board.MultiCell('here', ['@', '@'])

    def testClear(self):
        """Test clearing a MultiCell."""
        self.cell.clear()
        self.assertEqual([], self.cell.contents)

    def testClearSpecific(self):
        """Test clearing a MultiCell with a specified nothing."""
        self.cell.clear(set())
        self.assertEqual(set(), self.cell.contents)

    def testContains(self):
        """Test the in operator for MultiCell."""
        self.assertTrue('@' in self.cell)

    def testContainsNot(self):
        """The failure of the in operator for MultiCell."""
        self.assertFalse('&' in self.cell)

    def testCopyIndependence(self):
        """Test that the copied piece is independent of the MultiCell piece."""
        piece = self.cell.copy_piece()
        self.cell.add_piece('&')
        self.assertNotEqual(piece, self.cell.contents)

    def testCopyValue(self):
        """Test that MultiCell.copy_piece gives the correct value."""
        self.assertEqual(['@', '@'], self.cell.copy_piece())

    def testGetPiece(self):
        """Test getting a piece from the MultiCell."""
        self.assertEqual(['@', '@'], self.cell.get_piece())

    def testIteration(self):
        """Test iteration of a MultiCell."""
        self.assertEqual(['@', '@'], list(self.cell))

    def testIterationEmpty(self):
        """Test iteration of an empty MultiCell."""
        self.cell.contents = []
        self.assertEqual([], list(self.cell))

    def testLength(self):
        """Test the length of a MultiCell."""
        self.assertEqual(2, len(self.cell))

    def testLengthEmpty(self):
        """Test the length of an empty MultiCell."""
        self.cell.contents = []
        self.assertEqual(0, len(self.cell))

    def testRemoveContents(self):
        """Test MultiCell contents after removing a piece."""
        piece = self.cell.remove_piece()
        self.assertEqual(['@'], self.cell.contents)

    def testRemoveReturn(self):
        """Test that removing a piece returns the correct value."""
        self.assertEqual('@', self.cell.remove_piece())

    def testRemoveSpecCon(self):
        """Test MultiCell contents after removing a specified piece."""
        self.cell.add_piece('&')
        piece = self.cell.remove_piece('@')
        self.assertEqual(['@', '&'], self.cell.contents)

    def testRemoveSpecRet(self):
        """Test return value of removing a specific piece from a MultiCell."""
        self.cell.add_piece('&')
        piece = self.cell.remove_piece('@')
        self.assertEqual('@', piece)

    def testRepr(self):
        """Test the repr of a MultiCell."""
        self.assertEqual("MultiCell('here', pieces = ['@', '@'])", repr(self.cell))

    def testReprEmpty(self):
        """Test the repr of an empty MultiCell."""
        self.cell.contents = []
        self.assertEqual("MultiCell('here')", repr(self.cell))

    def testReprDesign(self):
        """Test the repr of a MultiCell with a board design."""
        self.cell.empty = '+'
        self.assertEqual("MultiCell('here', pieces = ['@', '@'], empty = '+')", repr(self.cell))

    def testPlace(self):
        """Test adding a piece to a MultiCell."""
        self.cell.add_piece('&')
        self.assertEqual(['@', '@', '&'], self.cell.contents)

    def testStr(self):
        """Test the string of a MultiCell."""
        self.assertEqual('@, @', str(self.cell))

    def testStrEmpty(self):
        """Test the string of an empty MultiCell."""
        self.cell.contents = []
        self.assertEqual(' ', str(self.cell))


if __name__ == '__main__':
    unittest.main()