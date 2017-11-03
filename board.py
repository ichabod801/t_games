"""
board.py

Boards for text games.

!! I need to think about generalization. Should BoardCell be generalized, or
should boards accept a cell class. Location can easily be generalized. Single
piece vs. multiple pieces not so much.

Classes:
BoardCell: A square (or other shape) in a board. (object)
Coordinate: A cartesian coordinate in an n-dimensional space. (tuple)
GridBoard: A rectangular board of squares. (object)
"""


class BoardCell(object):
    """
    A square (or other shape) in a board. (object)

    The piece attribute may be any object, but it should convert to a string that
    correctly displays it on the board.

    Attributes:
    empty: How the cell looks when empty. (str)
    location: Where on the board the cell is. (Coordinate)
    piece: The piece occupying the board. (object)

    Overridden Methods:
    __init__
    __hash__
    __repr__
    """

    def __init__(self, column, row, piece = None, empty = ' '):
        """
        Initialize the cell. (None)

        Parameters:
        column: The column the cell is in. (int)
        row: The row the cell is in. (row)
        piece: The piece initially in the cell. (object)
        empty: How the cell looks when empty. (str)
        """
        self.location = Coordinate((column, row))
        self.piece = piece
        self.empty = empty

    def __hash__(self):
        """
        Hash function on the cell. (int)
        """
        return hash(self.location)

    def __repr__(self):
        """
        Computer readable text representation. (str)
        """
        # poisitional parameters
        text = 'BoardCell({}, {}'.format(self.location[0], self.location[1])
        # keyword parameters
        if self.piece is not None:
            text += ', piece = {!r}'.format(self.piece)
        if self.empty != ' ':
            text += ', empty = {!r}'.format(self.empty)
        # complete and return
        return text + ')'

    def __str__(self):
        """
        Human readable text representation. (str)
        """
        if self.piece:
            return str(self.piece)
        else:
            return self.empty

    def clear(self):
        """
        Remove any piece from the cell. (None)
        """
        self.piece = None


class Coordinate(tuple):
    """
    A cartesian coordinate in an n-dimensional space. (tuple)

    Overridden Methods:
    __abs__
    __add__
    __mul__
    __neg__
    __radd__
    __rmul__
    __rsub__
    __sub__
    """

    def __abs__(self):
        """
        Absolute value (Cooordinate)
        """
        return Coordinate([abs(a) for a in self])

    def __add__(self, other):
        """
        Coordinate addition

        Coordinates add with lists, tuples, and Coordinates of the same length.

        Parameters:
        other: The coordinate to add to (list, tuple, or Coordinate)
        """
        if isinstance(other, (Coordinate, tuple, list)):
            if len(self) == len(other):
                return Coordinate([a + b for a, b in zip(self, other)])
            else:
                raise ValueError('Coordinates can only add in the same dimension.')
        else:
            return NotImplemented

    def __mul__(self, other):
        """
        Scalar multiplication. (Coordinate)

        Parameters:
        other: The scale to multiply by. (int or float)
        """
        return Coordinate([a * other for a in self])

    def __neg__(self):
        """
        Negation (Coordinate)
        """
        return Coordinate([-a for a in self])

    def __radd__(self, other):
        """
        Right side coordinate addition. (Coordinate)

        Coordinates add with lists, tuples, and Coordinates of the same length.

        Parameters:
        other: The coordinate to add to (list, tuple, or Coordinate)
        """
        return self + other

    def __rmul__(self, other):
        """
        Right side scalar multiplication. (Coordinate)

        Parameters:
        other: The scale to multiply by. (int or float)
        """
        return other * self

    def __rsub__(self, other):
        """
        Right side coordiante subtraction. (Coordinate)

        Parameters:
        other: The coordinate to subtract from. (list, tuple, or Coordinate)
        """
        return -(self - other)

    def __sub__(self, other):
        """
        Coordiante subtraction. (Coordinate)

        Parameters:
        other: The coordinate to subtract. (list, tuple, or Coordinate)
        """
        if isinstance(other, (Coordinate, tuple, list)):
            if len(self) == len(other):
                return Coordinate([a - b for a, b in zip(self, other)])
            else:
                raise ValueError('Coordinates can only add in the same dimension.')
        else:
            return NotImplemented


class Board(object):
    """
    A playing board for a game. (object)

    Methods:
    clear: Clear all pieces off the board. (None)
    move: Move a piece from one cell to another. (object)
    offset: Return a cell offset from another cell (BoardCell)
    place: Place a piece in a cell. (None)

    Overriddent Methods:
    __init__
    __iter__
    """

    def __init__(self):
        """Set up the cells. (None)"""
        self.cells = {}

    def __iter__(self):
        """
        Iterator for the board (iterator)

        the iterator for a board iterates over the cell locations (keys).
        """
        return iter(self.cells)

    def clear(self):
        """Clear all pieces off the board. (None)"""
        for cell in self.cells.values():
            cell.clear()

    def move(self, start, end):
        """
        Move a piece from one cell to another. (object)

        The object returned is any piece that is in the destination cell before the
        move. The parameters should be keys appropriate to cells on the board.

        Parameters:
        start: The location containing the piece to move. (Coordinate)
        end: The location to move the piece to. (Coordinate)
        """
        # store the captured piece
        capture = self.cells[end].piece
        # move the piece
        self.cells[end].piece = self.cells[start].piece
        self.cells[start].piece = None
        return capture

    def offset(self, cell, offset):
        """
        Return a cell offset from another cell (BoardCell)

        Parameters:
        cell: The location of the starting cell. (Coordinate)
        offset: The relative location of the target cell. (Coordinate)
        """
        return self.cells[cell + offset]

    def place(self, piece, cell):
        """
        Place a piece in a cell. (None)

        The piece parameter should be a key appropriate to cells on the board.

        Paramters:
        piece: The piece to place on the board. (See BoardCell)
        cell: The location to place the piece in. (Coordinate)
        """
        self.cells[cell].piece = piece


class GridBoard(Board):
    """
    A rectangular board of squares. (Board)

    Methods:
    copy: Create a copy of the board. (GridBoard)

    Overridden Methods:
    __init__
    """

    def __init__(self, columns, rows):
        """
        Set up the grid of cells. (None)

        Paramters:
        columns: The number of columns on the board. (int)
        rows: The number of rows on the board. (int)
        """
        # store dimensions
        self.columns = columns
        self.rows = rows
        # create cells
        self.cells = {}
        for column in range(columns):
            for row in range(rows):
                self.cells[Coordinate((column, row))] = BoardCell(column, row)

    def copy(self, **kwargs):
        """Create a copy of the board. (GridBoard)"""
        # clone the cells
        clone = self.__class__(self.columns, self.rows, **kwargs)
        # clone the cell contents
        for location in clone:
            clone.cells[location].piece = self.cells[location].piece
        return clone


class LineBoard(object):
    """
    A linear board of points. (Board)

    Overridden Methods:
    __init__
    """

    def __init__(self, points):
        """
        Set up the line of cells. (None)

        Parameters:
        points: The number of points on the board. (int)
        """
        # Store the dimension.
        self.points = points
        # Create the cells.
        for point in range(points):
            self.cells[point] = BoardCell(point)