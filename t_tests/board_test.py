"""
board_test.py

Unit testing of board.py.

Classes:
BoardTest: Tests of the parent Board class. (TestCase)
BoardCellTest: Tests of the board cell class. (TestCase)
CoordinateTest: Tests of n-dimensional coordinates. (TestCase)
DimBoardTest: Tests of a multi-dimensional board. (TestCase)
LineBoardTest: Tests of a one dimensional board. (TestCase)
MultiCellTest: Tests of the multi-cell class. (TestCase)
"""


import unittest

import t_games.board as board


class BoardTest(unittest.TestCase):
    """Tests of the parent Board class. (TestCase)"""

    def setUp(self):
        self.board = board.Board(range(5))
        self.board.place(2, '@')
        self.board.place(4, '&')

    def testIteration(self):
        """Test interating over a board."""
        locations = [cell for cell in self.board]
        locations.sort()
        self.assertEqual([0, 1, 2, 3, 4], locations)

    def testClear(self):
        """Test clearing the board."""
        self.board.clear()
        pieces = [cell.contents for cell in self.board.cells.values()]
        self.assertEqual([None] * 5, pieces)

    def testCopyPieces(self):
        """Test copying pieces from one board to another."""
        other_board = board.Board(range(5))
        other_board.copy_pieces(self.board)
        pieces = [self.board.cells[index].contents for index in range(5)]
        other_pieces = [other_board.cells[index].contents for index in range(5)]
        self.assertEqual(other_pieces, pieces)

    def testDisplaceCapCap(self):
        """Test the capture of displace movement with capture."""
        capture = self.board.displace(2, 4)
        self.assertEqual('&', capture)

    def testDisplaceCapEnd(self):
        """Test the end square of displace movement with capture."""
        capture = self.board.displace(2, 4)
        self.assertEqual('@', self.board.cells[4].contents)

    def testDisplaceCapStart(self):
        """Test the start square of displace movement with capture."""
        capture = self.board.displace(2, 4)
        self.assertIsNone(self.board.cells[2].contents)

    def testDisplaceNoCapCap(self):
        """Test the capture of displace movement with no capture."""
        capture = self.board.displace(2, 3)
        self.assertIsNone(capture)

    def testDisplaceNoCapEnd(self):
        """Test the end square of displace movement with no capture."""
        capture = self.board.displace(2, 3)
        self.assertEqual('@', self.board.cells[3].contents)

    def testDisplaceNoCapStart(self):
        """Test the start square of displace movement with no capture."""
        capture = self.board.displace(2, 3)
        self.assertIsNone(self.board.cells[2].contents)

    def testOffsetClass(self):
        """Test the class of an offset."""
        self.assertTrue(isinstance(self.board.offset(2, 2), board.BoardCell))

    def testOffsetValue(self):
        """Test the value of an offset."""
        self.assertEqual(4, self.board.offset(2, 2).location)

    def testPlaceEmpty(self):
        """Test placing a piece on an empty spot."""
        self.board.place(3, '?')
        self.assertEqual('?', self.board.cells[3].contents)

    def testPlaceNonEmpty(self):
        """Test placing a piece on a non-empty spot."""
        self.board.place(2, '?')
        self.assertEqual('?', self.board.cells[2].contents)

    def testRepr(self):
        """Test debugging text representation."""
        self.assertEqual('<Board with 5 BoardCells>', repr(self.board))

    def testReprMultiCell(self):
        """Test debugging text representation with MultiCells."""
        test_board = board.Board(range(5), board.MultiCell)
        self.assertEqual('<Board with 5 MultiCells>', repr(test_board))

    def testReprStringLocations(self):
        """Test debugging text representation with string locations."""
        test_board = board.Board(['a', 'B', '3'])
        self.assertEqual('<Board with 3 BoardCells>', repr(test_board))


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

    def testCount(self):
        """Test the count method of BoardCell."""
        self.assertEqual(1, self.cell.count('@'))

    def testCountNone(self):
        """Test the count of an empty BoardCell."""
        self.cell.clear()
        self.assertEqual(0, self.cell.count('@'))

    def testCountNot(self):
        """Test the count of a piece not in a BoardCell"""
        self.assertEqual(0, self.cell.count('&'))

    def testCopyIndependence(self):
        """Test that the copied piece is independent of the BoardCell piece."""
        piece = self.cell.copy_piece()
        self.cell.add_piece('&')
        self.assertNotEqual(piece, self.cell.contents)

    def testCopyValue(self):
        """Test that copy_piece gives the correct value."""
        self.assertEqual('@', self.cell.copy_piece())

    def testEquality(self):
        """Test equality with another BoardCell."""
        self.assertEqual(board.BoardCell('here', '@'), self.cell)

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

    def testNotEqualClass(self):
        """Test inequality with another BoardCell because of class."""
        self.assertNotEqual(('here', '@'), self.cell)

    def testNotEqualContents(self):
        """Test inequality with another BoardCell because of contents."""
        self.assertNotEqual(board.BoardCell('here', '&'), self.cell)

    def testNotEqualLocation(self):
        """Test inequality with another BoardCell because of location."""
        self.assertNotEqual(board.BoardCell('there', '@'), self.cell)

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

    def testReprDesign(self):
        """Test the repr of a BoardCell with a board design."""
        self.cell.empty = '+'
        self.assertEqual("BoardCell('here', piece = '@', empty = '+')", repr(self.cell))

    def testReprNoPiece(self):
        """Test the repr of an empty BoardCell."""
        self.cell.contents = None
        self.assertEqual("BoardCell('here')", repr(self.cell))

    def testReprNoPieceDesign(self):
        """Test the repr of an empty BoardCell."""
        self.cell.contents = None
        self.cell.empty = '+'
        self.assertEqual("BoardCell('here', empty = '+')", repr(self.cell))

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


class DimBoardTest(unittest.TestCase):
    """Tests of a multi-dimensional board. (TestCase)"""

    def setUp(self):
        self.board = board.DimBoard((3, 3))
        self.board.place((1, 2), '@')
        self.board.place((3, 2), '&')

    def testCopyIndependence(self):
        """Test the indenpendence of a copy of the board."""
        new_board = self.board.copy()
        self.board.move((1, 2), (2, 3))
        self.assertNotEqual(new_board.cells[(1, 2)].contents, self.board.cells[(1, 2)].contents)
        self.assertNotEqual(new_board.cells[(2, 3)].contents, self.board.cells[(2, 3)].contents)

    def testCopyValues(self):
        """Test the correctness of a copy of the board."""
        new_board = self.board.copy()
        self.assertEqual(new_board.cells, self.board.cells)

    def testLocations(self):
        """Test the locations of a dim board."""
        check = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)]
        locations = sorted(self.board.cells.keys())
        self.assertEqual(check, locations)

    def testOffsetValue(self):
        """Test the value of an offset."""
        center = board.Coordinate((2, 2))
        self.assertEqual((1, 3), self.board.offset(center, (-1, 1)).location)

    def testRepr(self):
        """Test the debugging text representation."""
        self.assertEqual('<DimBoard with 3x3 BoardCells>', repr(self.board))

    def testRepr3D(self):
        """Test the three-dimensional debugging text representation."""
        test_board = board.DimBoard((2, 3, 4))
        self.assertEqual('<DimBoard with 2x3x4 BoardCells>', repr(test_board))

    def testReprMultiCell(self):
        """Test the debugging text representation with MultiCells."""
        test_board = board.DimBoard((3, 3), board.MultiCell)
        self.assertEqual('<DimBoard with 3x3 MultiCells>', repr(test_board))


class LineBoardTest(unittest.TestCase):
    """Tests of a one dimensional board. (TestCase)"""

    def setUp(self):
        self.board = board.LineBoard(5)
        self.board.place(2, ['@', '@'])
        self.board.place(4, ['&'])

    def testClear(self):
        """Test clearing the board."""
        self.board.clear()
        pieces = [cell.contents for cell in self.board.cells.values()]
        self.assertEqual([[] for dummy in range(5)], pieces)

    def testCopyIndependence(self):
        """Test the independence of a copy of a line board."""
        new_board = self.board.copy()
        self.board.move(2, 3)
        self.assertNotEqual(new_board.cells[2].contents, self.board.cells[2].contents)
        self.assertNotEqual(new_board.cells[3].contents, self.board.cells[3].contents)

    def testCopyPieces(self):
        """Test copying pieces from one board to another."""
        other_board = board.LineBoard(5)
        other_board.copy_pieces(self.board)
        pieces = [self.board.cells[index].contents for index in range(1, 6)]
        other_pieces = [other_board.cells[index].contents for index in range(1, 6)]
        self.assertEqual(other_pieces, pieces)

    def testCopyValues(self):
        """Test the correctness of a copy of a line board."""
        new_board = self.board.copy()
        self.assertEqual(new_board.cells, self.board.cells)

    def testDisplaceCapCap(self):
        """Test the capture of displace movement with capture."""
        capture = self.board.displace(2, 4)
        self.assertEqual(['&'], capture)

    def testDisplaceCapEnd(self):
        """Test the end square of displace movement with capture."""
        capture = self.board.displace(2, 4)
        self.assertEqual(['@'], self.board.cells[4].contents)

    def testDisplaceCapStart(self):
        """Test the start square of displace movement with capture."""
        capture = self.board.displace(2, 4)
        self.assertEqual(['@'], self.board.cells[4].contents)

    def testDisplaceNoCapCap(self):
        """Test the capture of displace movement with no capture."""
        capture = self.board.displace(2, 3)
        self.assertEqual([], capture)

    def testDisplaceNoCapEnd(self):
        """Test the end square of displace movement with no capture."""
        capture = self.board.displace(2, 3)
        self.assertEqual(['@'], self.board.cells[3].contents)

    def testDisplaceNoCapStart(self):
        """Test the start square of displace movement with no capture."""
        capture = self.board.displace(2, 3)
        self.assertEqual(['@'], self.board.cells[2].contents)

    def testLocations(self):
        """Test the locations of a line board."""
        check = [1, 2, 3, 4, 5]
        locations = sorted(self.board.cells.keys())
        self.assertEqual(check, locations)

    def testOffsetClass(self):
        """Test the class of an offset."""
        self.assertTrue(isinstance(self.board.offset(2, 2), board.MultiCell))

    def testPlaceEmpty(self):
        """Test placing a piece on an empty spot."""
        self.board.place(3, ['?'])
        self.assertEqual(['?'], self.board.cells[3].contents)

    def testPlaceNonEmpty(self):
        """Test placing a piece on a non-empty spot."""
        self.board.place(2, ['?'])
        self.assertEqual(['?'], self.board.cells[2].contents)

    def testRepr(self):
        """Test the debugging text representation."""
        self.assertEqual('<LineBoard with 5 MultiCells>', repr(self.board))

    def testSafeDisplaceCapture(self):
        """Test capture during a safe displace."""
        capture = self.board.safe_displace(2, 4)
        self.assertEqual(['&'], capture)

    def testSafeDisplaceEnd(self):
        """Test end square of a safe displace."""
        capture = self.board.safe_displace(2, 4)
        self.assertEqual(['@'], self.board.cells[4].contents)

    def testSafeDisplaceStart(self):
        """Test starting square of a safe displace."""
        capture = self.board.safe_displace(2, 4)
        self.assertEqual(['@'], self.board.cells[2].contents)

    def testSafeNot(self):
        """Test safety of an unsafe space."""
        self.assertTrue(self.board.safe(2, '&'))

    def testSafeNotDisCap(self):
        """Test capture of safe displace with no capture."""
        self.board.place(1, ['@'])
        capture = self.board.safe_displace(1, 2)
        self.assertEqual([], capture)

    def testSafeNotDisEnd(self):
        """Test end point of safe displace with no capture."""
        self.board.place(1, ['@'])
        capture = self.board.safe_displace(1, 2)
        self.assertEqual(['@', '@', '@'], self.board.cells[2].contents)

    def testSafeNotDisStart(self):
        """Test starting point of safe displace with no capture."""
        self.board.place(1, ['@'])
        capture = self.board.safe_displace(1, 2)
        self.assertEqual([], self.board.cells[1].contents)

    def testSafeSame(self):
        """Test safety of a square with the same piece."""
        self.assertFalse(self.board.safe(2, '@'))

    def testSafeSmall(self):
        """Test safety of a square with too few pieces."""
        self.assertFalse(self.board.safe(3, '@'))

    def testUnsafeDisplaceRaise(self):
        """Test unsafe displace raising an exception."""
        # !! redo with assertRaises
        try:
            capture = self.board.safe_displace(4, 2)
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

    def testUnsafeDisplaceStart(self):
        """Test unsafe displace retaining start position."""
        try:
            capture = self.board.safe_displace(4, 2)
        except ValueError:
            pass
        self.assertEqual(['&'], self.board.cells[4].contents)

class MultiCellTest(unittest.TestCase):
    """Tests of the multi-cell class. (TestCase)"""

    def setUp(self):
        self.cell = board.MultiCell('here', ['@', '@'])

    def testClear(self):
        """Test clearing a MultiCell."""
        self.cell.clear()
        self.assertEqual([], self.cell.contents)

    def testClearIndependence(self):
        """Test the independence of cleared cells."""
        other_cell = board.MultiCell('here')
        self.cell.clear()
        other_cell.clear()
        self.cell.add_piece(['&', '?'])
        self.assertNotEqual(['&', '?'], other_cell.contents)

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

    def testCount(self):
        """Test the count method of a MultiCell."""
        self.assertEqual(2, self.cell.count('@'))

    def testCountEmpty(self):
        """Test the count of an empty MultiCell."""
        self.cell.clear()
        self.assertEqual(0, self.cell.count('@'))

    def testCountNot(self):
        """Test the count of pice not in the MultiCell."""
        self.assertEqual(0, self.cell.count('&'))

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

    def testReprDesign(self):
        """Test the repr of a MultiCell with a board design."""
        self.cell.empty = '+'
        self.assertEqual("MultiCell('here', pieces = ['@', '@'], empty = '+')", repr(self.cell))

    def testReprNoPiece(self):
        """Test the repr of an empty MultiCell."""
        self.cell.contents = []
        self.assertEqual("MultiCell('here')", repr(self.cell))

    def testReprNoPieceDesign(self):
        """Test the repr of an empty MultiCell."""
        self.cell.contents = []
        self.cell.empty = '+'
        self.assertEqual("MultiCell('here', empty = '+')", repr(self.cell))

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