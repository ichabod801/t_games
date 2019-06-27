"""
slider_game.py

A classic puzzle with sliding tiles.

Constants:
CREDITS: The credits for Slider Puzzle.
RULES: The rules to Slider Puzzle.

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

You may move tiles by the character on them using the move command (m). You may
move the tile above the blank spot with the north command (n). Similar commands
exist for east (e), south (s), and west (w).
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

    Methods:
    direction_move: Move a piece a given offset from the blank spot. (None)
    do_east: Move the tile to the east of the blank spot. (None)
    do_move: Move the specified tile. (None)
    do_north: Move the tile to the north of the blank spot. (None)
    do_south: Move the tile to the south of the blank spot. (None)
    do_west: Move the tile to the west of the blank spot. (None)

    Overridden Methods:
    game_over
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['Slider', 'slpu']
    aliases = {'e': 'east', 'm': 'move', 'n': 'north', 's': 'south', 'w': 'west'}
    categories = ['Other Games']
    name = 'Slider Puzzle'
    tiles = '123456789' + string.ascii_uppercase + string.ascii_lowercase

    def direction_move(self, offset, direction):
        """
        Move a piece a given offset from the blank spot. (None)

        Parameters:
        offset: The relative coordinate of the tile to move. (tuple of int)
        direction: The name of the direction of the tile to move. (str)
        """
        # Check for a valid tile.
        try:
            start = self.board.offset(self.blank_cell.location, offset)
        except KeyError:
            self.human.error('There is no tile {} of the blank spot.'.format(direction))
        else:
            # Move the valid tile.
            self.board.move(start.location, self.blank_cell.location, start.contents)
            self.blank_cell = start

    def do_east(self, argument):
        """
        Move the tile to the east of the blank spot. (e)
        """
        self.direction_move((0, 1), 'east')

    def do_move(self, argument):
        """
        Move the specified tile. (m)

        The argument is the tile (or tiles) to move. Each on in order is moved into the
        blank space. Spaces are ignored in the argument, but any invalid move stops the
        movement.
        """
        if self.auto_cap:
            argument = argument.upper()
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

    def do_north(self, argument):
        """
        Move the tile to the north of the blank spot. (n)
        """
        self.direction_move((-1, 0), 'north')

    def do_south(self, argument):
        """
        Move the tile to the south of the blank spot. (s)
        """
        self.direction_move((1, 0), 'south')

    def do_west(self, argument):
        """
        Move the tile to the west of the blank spot. (w)
        """
        self.direction_move((0, -1), 'west')

    def game_over(self):
        """Determine if the puzzle is solved. (None)"""
        # Compare the current board to the winning text.
        current = str(self.board).replace('\n', '')
        if current[:-1] == self.text:
            self.human.tell('You solved the puzzle!')
            self.win_loss_draw[0] = 1
            self.scores[self.human.name] = self.rows * self.columns - 1
            return True
        else:
            return False

    def handle_options(self):
        """Game the options for the game. (None)"""
        # Parse the user's option choices.
        super(Slider, self).handle_options()
        # Set autocapitalize.
        text_len = self.columns * self.rows - 1
        self.auto_cap = not self.text and text_len < 36
        # Make sure the text is the right size.
        if self.text and len(self.text) < text_len:
            self.human.error('Puzzle text padded because it is too short.')
        elif len(self.text) > text_len:
            self.human.error('Puzzle text truncated because it is too long.')
        self.text = (self.text + self.tiles)[:text_len]

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        print(self.board)
        move = player.ask('\nWhat is your move? ')
        return self.handle_cmd(move)

    def set_options(self):
        """Set up the game options. (None)"""
        self.option_set.add_option('columns', ['c'], int, 4,
            question = 'How many columns should the board have (return for 4)? ')
        self.option_set.add_option('rows', ['r'], int, 4,
            question = 'How many columns should the board have (return for 4)? ')
        self.option_set.add_option('text', ['t'], default = '',
            question = 'What text should the solution be (return for numbers + letters)? ')

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
