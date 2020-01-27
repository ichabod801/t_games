"""
board.py

Boards for text games.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
BoardCell: A square (or other shape) in a board that holds one piece. (object)
MultiCell: A position on a board that holds multiple pieces. (object)
Coordinate: A cartesian coordinate in an n-dimensional space. (tuple)
Board: A playing board for a game. (object)
DimBoard: A board of squares in variable dimensions. (Board)
LineBoard: A board of spaces in a line. (Board)
MultiBoard: A board with multiple pieces per cell. (Board)
"""


try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence
import itertools


class BoardCell(object):
    """
    A square (or other shape) in a board that holds one piece. (object)

    The piece attribute may be any object, but it should convert to a string that
    correctly displays it on the board. Likewise, the location can be any object,
    but it should be hashable and support addition.

    Attributes:
    contents: The piece that is in the cell. (object)
    empty: How the cell looks when empty. (str)
    location: Where on the board the cell is. (object)

    Methods:
    add_piece: Add a piece to the cell. (object)
    clear: Remove any piece from the cell. (None)
    count: Count the number of times a piece is in the cell. (int)
    copy_piece: Copy the piece in the cell. (object)
    get_piece: Get the cell's piece. (object)
    remove_piece: Remove a piece from the cell. (object)

    Overridden Methods:
    __init__
    __contains__
    __eq__
    __hash__
    __iter__
    __len__
    __repr__
    __str__
    """

    def __init__(self, location, piece = None, empty = ' '):
        """
        Initialize the cell. (None)

        Parameters:
        location: The location of the cell on the board. (hashable)
        piece: The piece initially in the cell. (object)
        empty: How the cell looks when empty. (str)
        """
        self.location = location
        self.contents = piece
        self.empty = empty

    def __contains__(self, other):
        """
        Check for a piece in the cell. (bool)

        other: The piece to check for. (object)
        """
        return self.contents == other

    def __eq__(self, other):
        """
        Check for equality (of location and contents) with another cell. (bool)

        Other: The piece to check equality for. (object)
        """
        if isinstance(other, BoardCell):
            return self.location == other.location and self.contents == other.contents
        else:
            return NotImplemented

    def __hash__(self):
        """
        Hash function on the cell. (int)
        """
        return hash(self.location)

    def __iter__(self):
        """Iterate over the piece in the cell. (iterator)"""
        if self.contents is None:
            return iter([])
        else:
            return iter([self.contents])

    def __len__(self):
        """Return the number of pieces in the cell. (int)"""
        return 0 self.contents if is None else 1

    def __repr__(self):
        """
        Generate a computer readable text representation. (str)
        """
        # keyword parameters
        if self.contents:
            piece_text = ', piece = {!r}'.format(self.contents)
        else:
            piece_text = ''
        if self.empty != ' ':
            empty_text = ', empty = {!r}'.format(self.empty)
        else:
            empty_text = ''
        # complete and return
        return '{}({!r}{}{})'.format(self.__class__.__name__, self.location, piece_text, empty_text)

    def __str__(self):
        """
        Generate a human readable text representation. (str)
        """
        if self.contents:
            return str(self.contents)
        else:
            return self.empty

    def add_piece(self, piece):
        """
        Add a piece to the cell. (object)

        The return value is the piece that was in the cell before.

        Parameters:
        piece: The piece to add to the cell. (object)
        """
        capture = self.contents
        self.contents = piece
        return capture

    def clear(self, nothing = None):
        """
        Remove any piece from the cell. (None)
        """
        self.contents = nothing

    def copy_piece(self):
        """
        Copy the piece in the cell. (object)

        This should be overridden for boards with mutable pieces.
        """
        return self.contents

    def count(self, piece):
        """
        Count the number of times a piece is in the cell. (int)

        Parameters:
        piece: The piece to count. (object)
        """
        return self.contents == piece

    def get_piece(self):
        """Get the cell's piece. (object)"""
        return self.contents

    def remove_piece(self, piece = None):
        """
        Remove a piece from the cell. (object)

        Parameters:
        piece: The piece to remove from the cell. (object)
        """
        piece = self.contents
        self.clear()
        return piece


class MultiCell(BoardCell):
    """
    A position on a board that holds multiple pieces. (object)

    The pieces attribute is a list of objects. Each object should convert to a
    string that correctly displays it on the board. Likewise, the location can
    be any object, but it should be hashable and support addition.

    Methods:
    add_piece: Add a piece to the cell. (None)
    append: Add a piece to the cell. (None)
    clear: Remove any piece from the cell. (None)
    copy_piece: Copy the piece in the cell. (object)
    count: Count the number of times a piece is in the cell. (int)
    extend: Add pieces to the cell. (object)
    index: Return the location of a piece in the cell. (int)
    insert: Insert a piece into the cell. (None)
    pop: Remove and return a piece from the cell. (object)
    remove: Remove a piece from the cell. (object)
    remove_piece: Remove and return a piece from the cell. (object)
    reverse: Reverse the order of the pieces in the cell. (None)

    Overridden Methods:
    __init__
    __contains__
    __delitem__
    __getitem__
    __iter__
    __len__
    __repr__
    __reversed__
    __setitem__
    __str__
    """

    def __init__(self, location, pieces = None, empty = ' '):
        """
        Initialize the cell. (None)

        Parameters:
        location: The location of the cell on the board. (hashable)
        pieces: The pieces initially in the cell. (list)
        empty: How the cell looks when empty. (str)
        """
        self.location = location
        self.empty = empty
        if pieces is None:
            self.contents = []
        else:
            self.contents = pieces

    def __contains__(self, other):
        """
        Check for a piece in the cell. (bool)

        other: The piece to check for. (object)
        """
        return other in self.contents

    def __delitem__(self, key):
        """
        Remove an item or items from the cell. (object or list of objects)

        Parameters:
        key: The location of the items to remove. (index or slice)
        """
        del self.contents[key]

    def __getitem__(self, index):
        """
        Get an item or items from the cell. (object or list of objects)

        Parameters:
        index: The location of the items to get. (index or slice)
        """
        return self.contents[index]

    def __iter__(self):
        """Iterate over the piece in the cell. (iterator)"""
        return iter(self.contents)

    def __len__(self):
        """Return the number of pieces in the cell. (int)"""
        return len(self.contents)

    def __repr__(self):
        """
        Generate a computer readable text representation. (str)
        """
        # keyword parameters
        if self.contents:
            piece_text = ', pieces = {!r}'.format(self.contents)
        else:
            piece_text = ''
        if self.empty != ' ':
            empty_text = ', empty = {!r}'.format(self.empty)
        else:
            empty_text = ''
        # complete and return
        return '{}({!r}{}{})'.format(self.__class__.__name__, self.location, piece_text, empty_text)

    def __reversed__(self):
        """Iterate over the contents backwards. (iterator)"""
        return reversed(self.contents)

    def __setitem__(self, key, value):
        """
        Set a piece in the cell. (None)

        Parameters:
        key: The location of the item to set. (int or slice)
        value: The new value of that location. (object)
        """
        self.contents[key] = value

    def __str__(self):
        """
        Generate a human readable text representation. (str)
        """
        if self.contents:
            return ', '.join([str(piece) for piece in self.contents])
        else:
            return self.empty

    def add_piece(self, piece):
        """
        Add a piece to the cell. (object)

        Parameters:
        piece: The piece to add to the cell. (object)
        """
        self.contents.append(piece)

    def append(self, piece):
        """
        Add a piece to the cell. (object)

        Parameters:
        piece: The piece to add to the cell. (object)
        """
        self.contents.append(piece)

    def clear(self, nothing = None):
        """
        Remove any piece from the cell. (None)
        """
        if nothing is None:
            nothing = []
        self.contents = nothing

    def copy_piece(self):
        """
        Copy the piece in the cell. (object)

        This should be overridden for boards with mutable pieces.
        """
        return self.contents[:]

    def count(self, piece):
        """
        Count the number of times a piece is in the cell. (int)

        Parameters:
        piece: The piece to count. (object)
        """
        return self.contents.count(piece)

    def extend(self, pieces):
        """
        Add pieces to the cell. (object)

        Parameters:
        pieces: The pieces to add to the cell. (sequence of object)
        """
        self.contents.extend(pieces)

    def index(self, piece):
        """
        Return the location of a piece in the cell. (int)

        Parameters:
        piece: The piece to get an index for. (object)
        """
        return self.contents.index(piece)

    def insert(self, index, piece):
        """
        Insert a piece into the cell. (None)

        Parameters:
        index: Where to insert the piece. (int)
        piece: The piece to insert. (object)
        """
        self.contents.insert(index, piece)

    def pop(self, index = -1):
        """
        Remove and return a piece from the cell. (object)

        Parameters:
        index: The location of the piece to remove. (int)
        """
        return self.contents.pop(index)

    def remove(self, piece):
        """
        Remove a piece from the cell. (None)

        Parameters:
        piece: The piece to remove from the cell. (object)
        """
        self.contents.remove(piece)

    def remove_piece(self, piece = None):
        """
        Remove and return a piece from the cell. (object)

        Parameters:
        piece: The piece to remove from the cell. (object)
        """
        if piece:
            self.contents.remove(piece)
        else:
            piece = self.contents.pop()
        return piece

    def reverse(self):
        """Reverse the order of the pieces in the cell. (None)"""
        self.contents.reverse()


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
        return self * other

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

    Attributes:
    cells: The locations that make up the board. (dict of Coordinate: BoardCell)
    extra_cells: A list of non-standard locations. (list of BoardCell)

    Methods:
    clear: Clear all pieces off the board. (None)
    copy_pices: Copy all of the pieces from another board. (None)
    displace: Move a piece from one cell to another w/ displace capture. (object)
    move: Move a piece from one cell to another. (object)
    offset: Return a cell offset from another cell (BoardCell)
    place: Place a piece in a cell. (None)
    safe: Determine if a cell is safe from capture. (bool)
    safe_displace: Move a piece with displace capture if target not safe. (object)

    Overriddent Methods:
    __init__
    __iter__
    __repr__
    """

    def __init__(self, locations = [], cell_class = BoardCell):
        """
        Set up the cells. (None)

        Parameters:
        locations: The locations of the cells on the board. (list of hashable)
        cell_class: The class for the cells on the board. (class)
        """
        self.cells = {location: cell_class(location) for location in locations}
        self.extra_cells = []

    def __iter__(self):
        """
        Iterator for the board (iterator)

        the iterator for a board iterates over the cell locations (keys).
        """
        return iter(self.cells)

    def __repr__(self):
        """Generate a debugging text representation. (str)"""
        cell_count = len(self.cells) + len(self.extra_cells)
        cell_class_name = next(iter(self.cells.values())).__class__.__name__
        return '<{} with {} {}s>'.format(self.__class__.__name__, cell_count, cell_class_name)

    def clear(self):
        """Clear all pieces off the board. (None)"""
        for cell in self.cells.values():
            cell.clear()

    def copy_pieces(self, parent):
        """
        Copy all of the pieces from another board. (None)

        Parameters:
        parent: The board to copy pieces from. (Board)
        """
        for location in parent.cells:
            self.cells[location].contents = parent.cells[location].copy_piece()

    def displace(self, start, end, piece = None):
        """
        Move a piece from one cell to another with displace capture. (object)

        Parameters:
        start: The location containing the piece to move. (Coordinate)
        end: The location to move the piece to. (Coordinate)
        piece: The piece to move. (object)
        """
        # store the captured piece
        capture = self.cells[end].get_piece()
        # move the piece
        mover = self.cells[start].remove_piece(piece)
        self.cells[end].clear()
        self.cells[end].add_piece(mover)
        return capture

    def move(self, start, end, piece = None):
        """
        Move a piece from one cell to another with displace capture. (object)

        This should be overridden for the specific capture type of the board.

        Parameters:
        start: The location containing the piece to move. (Coordinate)
        end: The location to move the piece to. (Coordinate)
        piece: The piece to move. (object)
        """
        # default is displace capture.
        return self.displace(start, end, piece)

    def offset(self, cell, offset):
        """
        Return a cell offset from another cell (BoardCell)

        Parameters:
        cell: The location of the starting cell. (Coordinate)
        offset: The relative location of the target cell. (Coordinate)
        """
        return self.cells[cell + offset]

    def place(self, cell, piece):
        """
        Place a piece in a cell. (None)

        The cell parameter should be a key appropriate to cells on the board.

        Paramters:
        piece: The piece to place on the board. (See BoardCell)
        cell: The location to place the piece in. (Coordinate)
        """
        self.cells[cell].clear()
        self.cells[cell].contents = piece

    def safe(self, location, piece):
        """
        Determine if a cell is safe from capture. (bool)

        Parameter:
        location: The location of the cell to check. (hashable)
        piece: The piece that would move to that spot. (object)
        """
        cell = self.cells[location]
        return piece not in cell and len(cell) > 1 and location not in self.extra_cells

    def safe_displace(self, start, end, piece = None):
        """
        Move a piece with displace capture if target not safe. (object)

        Parameters:
        start: The location containing the piece to move. (Coordinate)
        end: The location to move the piece to. (Coordinate)
        piece: The piece to move. (object)
        """
        # Check for a safe move.
        mover = self.cells[start].remove_piece(piece)
        if self.safe(end, mover):
            self.cells[start].add_piece(mover)
            raise ValueError('Attempt to capture safe cell {!r}.'.format(end))
        # Check the desitnation for capture situations.
        end_pieces = self.cells[end].contents
        if mover in end_pieces or not end_pieces or end in self.extra_cells:
            # Do a simple move to an empty destination.
            self.cells[end].add_piece(mover)
            return []
        else:
            # Move to a occupied location and return the occupants as the capture.
            capture = self.cells[end].get_piece()
            self.cells[end].clear()
            self.cells[end].add_piece(mover)
            return capture


class DimBoard(Board):
    """
    A board of squares in variable dimensions. (Board)

    Attributes:
    cell_class: The class defining the individual cells. (type)
    dimensions: The dimensions of the board, in cells. (tuple of int)

    Methods:
    copy: Create a copy of the board. (DimBoard)

    Overridden Methods:
    __init__
    __repr__
    """

    def __init__(self, dimensions, cell_class = BoardCell):
        """
        Set up the grid of cells. (None)

        Parameters:
        dimensions: The dimensions of the board, in cells. (tuple of int)
        cell_class: The class for the cells on the board. (class)
        """
        # Store the definition.
        self.dimensions = dimensions
        self.cell_class = cell_class
        # Calculate the locations.
        locations = itertools.product(*[range(1, dimension + 1) for dimension in self.dimensions])
        locations = [Coordinate(location) for location in locations]
        # Set up the cells.
        super(DimBoard, self).__init__(locations, cell_class)

    def __repr__(self):
        """Create a debugging text representation. (str)"""
        dimension_text = 'x'.join([str(dimension) for dimension in self.dimensions])
        my_class_name = self.__class__.__name__
        return '<{} with {} {}s>'.format(my_class_name, dimension_text, self.cell_class.__name__)

    def copy(self, **kwargs):
        """Create a copy of the board. (DimBoard)"""
        clone = self.__class__(self.dimensions, self.cell_class, **kwargs)
        clone.copy_pieces(self)
        return clone


class LineBoard(Board):
    """
    A board of spaces in a line. (Board)

    The line may be bent or looped.

    Attributes:
    cell_class: The class defining the individual cells. (type)
    length: How many cells are in the board. (int)

    Methods:
    copy: Create a copy of the board. (LineBoard)

    Overridden Methods:
    __init__
    """

    def __init__(self, length, cell_class = MultiCell, extra_cells = []):
        """
        Set up the line of cells. (None)

        Parameters:
        length: The number of cells in the board. (int)
        cell_class: The class for the cells on the board. (class)
        extra_cells: The keys for any cells outside the line. (list of hashable)
        """
        # Set up the standard board cells.
        self.length = length
        self.cell_class = cell_class
        super(LineBoard, self).__init__(range(1, length + 1), cell_class)
        # Set up any extra cells.
        self.extra_cells = extra_cells
        for location in self.extra_cells:
            self.cells[location] = cell_class(location)

    def copy(self, **kwargs):
        """Create a copy of the board. (LineBoard)"""
        clone = self.__class__(self.length, self.cell_class, **kwargs)
        clone.copy_pieces(self)
        return clone


class MultiBoard(DimBoard):
    """
    A board with multiple pieces per cell. (Board)

    Methods:
    copy: Create a copy of the board. (MultiBoard)

    Overridden Methods:
    __init__
    move
    place
    """

    def __init__(self, dimensions):
        """
        Set up the grid of cells. (None)

        Paramters:
        dimensions: The dimensions of the board, in cells. (tuple of int)
        """
        super(MultiBoard, self).__init__(dimensions, list)

    def copy(self, **kwargs):
        """Create a copy of the board. (MultiBoard)"""
        # clone the cells
        clone = self.__class__(self.dimensions, **kwargs)
        # clone the cell contents
        for location in clone:
            clone.cells[location].piece = self.cells[location].piece[:]
        return clone

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
        capture = self.cells[end].piece[:]
        # move the piece
        mover = self.cells[start].piece.pop()
        if not (capture == self.default_piece() or mover == capture[0]):
            self.cells[end].piece = self.default_piece()
        else:
            capture = self.default_piece()
        self.cells[end].piece.append(mover)
        return capture

    def place(self, piece, cell):
        """
        Place a piece in a cell. (None)

        The piece parameter should be a key appropriate to cells on the board.

        Paramters:
        piece: The piece to place on the board. (See BoardCell)
        cell: The location to place the piece in. (Coordinate)
        """
        self.cells[cell].piece.append(piece)


if __name__ == '__main__':
    # Run the unit testing.
    from t_tests.board_test import *
    unittest.main()
