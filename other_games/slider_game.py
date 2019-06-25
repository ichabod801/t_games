"""
slider_game.py

A classic puzzle with sliding tiles.

Classes:
Slider: A classic puzzle with sliding tiles. (game.Game)
TileBoard: A board of sliding tiles. (board.DimBoard)
"""


import random
import string

from .. import board
from .. import game


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
The board has one empty space. Any tile horizontally or vertically adjacent to
that space may be slid into that space. The goal is to get all of the tiles in
order, with the space at the bottom right.

Note that the correct order for the default game is 123456789ABCDEF.
"""


class Slider(game.Game):
    """
    A classic puzzle with sliding tiles. (game.Game)

    Attributes:
    columns: The number of tiles across the puzzle. (int)
    rows: The number of tiles up and down the puzzle. (int)
    text: The characters to arrange the tiles into. (str)

    Class Attributes:
    tiles: The potential characters for tiles in the puzzle. (str)

    Overridden Methods:
    handle_options
    set_up
    """

    aka = ['Slider', 'slpu']
    aliases = {'m': 'move'}
    categories = ['Other Games']
    name = 'Slider Puzzle'
    tiles = '123456789' + string.ascii_uppercase + string.ascii_lowercase

    def do_move(self, argument):
        """
        Move the specified tile.

        The argument is the tile (or tiles) to move. Each on in order is moved into the
        blank space. Spaces are ignored in the argument, but any invalid move stops the
        movement.
        """
        for char in argument:
            # Skip spaces.
            if char == ' ':
                continue
            # Find the cell to move.
            for cell in self.board.cells.values():
                if cell.contents == char:
                    break
            else:
                self.human.error('{} is not a tile in the puzzle.'.format(char))
                break
            # Confirm the cell is next to the blank cell.
            for offset in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                if self.blank_cell.location + offset == cell.location:
                    break
            else:
                self.human.error('The {} tile is not next to the blank space.'.format(char))
                break
            # Move the piece.
            self.board.move(cell.location, self.blank_cell.location, char)
            self.blank_cell = cell
            self.turns += 1

    def game_over(self):
        """Determine if the puzzle is solved. (None)"""
        current = ''.join([str(self.board.cells[location]) for location in self.board])
        return current[:-1] == self.text

    def handle_options(self):
        """Game the options for the game. (None)"""
        self.columns = 4
        self.rows = 4
        self.text = self.tiles[:(self.columns * self.rows - 1)]

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        print(self.board)
        move = player.ask('\nWhat is your move? ')
        return self.handle_cmd(move)

    def set_up(self):
        """Set up the board for the game. (None)"""
        tiles = list(self.text)
        random.shuffle(tiles)
        self.board = TileBoard((self.columns, self.rows))
        for location, tile in zip(self.board, tiles):
            self.board.place(location, tile)
        for blank_cell in self.board.cells.values():
            if blank_cell.contents is None:
                break
        self.blank_cell = blank_cell


class TileBoard(board.DimBoard):
    """
    A board of sliding tiles. (board.DimBoard)

    Overridden Methods:
    move
    safe
    """

    def __str__(self):
        """Human readable text representation. (str)"""
        text = ''
        for column in range(self.dimensions[0]):
            text += '\n'
            for row in range(self.dimensions[1]):
                text += str(self.cells[(column + 1, row + 1)])
        return text

    def move(self, start, end, piece = None):
        """
        Move a piece from one cell to another with displace capture. (object)

        Parameters:
        start: The location containing the piece to move. (Coordinate)
        end: The location to move the piece to. (Coordinate)
        piece: The piece to move. (object)
        """
        if not self.cells[end].contents:
            self.cells[start].contents = None
            self.cells[end].contents = piece
        else:
            raise ValueError('End square is not empty.')
