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


import itertools
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

You may move tiles by the character on them using the move command (m). You can
enter multiple tiles with the move command. Additionally, if there are no lower
case characters in the puzzle, the argument to the move command is
automatically capitalized. Alternatively, you may move the tile above the blank
spot with the north command (n). Similar commands exist for east (e), south
(s), and west (w). You can give a string of directional commands as an argument
to another directional command. For example 'e nsw' would move the eastern
tile, then the northern, southern, and western tiles.

Options:
columns= (c=): The number of columns in the puzzle.
rows= (r=): The number of rows in the puzzle.
size= (s=): The number of columns and rows in the table.
shuffle= (sh=): The number of times to shuffle the solved puzzle before play.
text= (t=): The text to use in the puzzle.
"""


class Slider(game.Game):
    """
    A classic puzzle with sliding tiles. (game.Game)

    Attributes:
    auto_cap: A flag for capitalizing user input. (bool)
    blank_cell: The current space that tiles can slide into. (board.BoardCell)
    board: The "board" the puzzle is played on. (TileBoard)
    columns: The number of tiles across the puzzle. (int)
    moves: How many moves the player has made. (int)
    rows: The number of tiles up and down the puzzle. (int)
    shuffles: How many times to shuffle the tiles. (int)
    size: The number of rows and columns, if they match. (int)
    text: The characters representing the default tiles. (str)

    Class Attributes:
    tiles: The potential characters for tiles in the puzzle. (str)

    Methods:
    direction_move: Move a piece a given offset from the blank spot. (None)
    do_east: Move the tile to the east of the blank spot. (None)
    do_move: Move the specified tile. (None)
    do_north: Move the tile to the north of the blank spot. (None)
    do_south: Move the tile to the south of the blank spot. (None)
    do_west: Move the tile to the west of the blank spot. (None)
    place_text: Put the text into the puzzle. (None)

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

    def direction_move(self, offset, direction, argument):
        """
        Move a piece a given offset from the blank spot. (None)

        Parameters:
        offset: The relative coordinate of the tile to move. (tuple of int)
        direction: The name of the direction of the tile to move. (str)
        argument: The argument to the original directional command. (str)
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
            self.moves += 1
            # Do any further directional moves.
            for char in argument.lower():
                if char in 'ensw':
                    self.handle_cmd(char)
                else:
                    break

    def do_east(self, argument):
        """
        Move the tile to the east of the blank spot. (e)
        """
        self.direction_move((0, 1), 'east', argument)

    def do_gipf(self, arguments):
        """
        Prisoner's Dilemma lets you rotate three adjacent tiles.

        Thoughful Solitaire solves the next unsovled row.
        """
        game, losses = self.gipf_check(arguments, ("prisoner's dilemma", 'thoughtful solitaire'))
        go = False
        if game == "prisoner's dilemma":
            if not losses:
                # Get three tiles to rotate.
                player = self.players[self.player_index]
                player.tell(self.board)
                while True:
                    tiles = player.ask('\nEnter three tiles to rotate (123 -> 231): ')
                    if self.auto_cap:
                        tiles = tiles.upper()
                    if len(tiles) != len(set(tiles)):
                        player.tell('Please enter three tiles with no spaces.')
                    elif all(char in self.text for char in tiles):
                        break
                    else:
                        player.tell('Please enter valid tiles.')
                # Find the tiles.
                cells = []
                for cell in self.board.cells.values():
                    if cell.contents and cell.contents in tiles:
                        cells.append(cell)
                tiles = [cell.contents for cell in cells]
                # Rotate and place the tiles.
                tiles.append(tiles.pop(0))
                for tile, cell in zip(tiles, cells):
                    cell.contents = tile
        elif game == 'thoughtful solitaire':
            if not losses:
                # Figure out what rows are solved.
                for row in range(1, self.rows + 1):
                    # Get what the row is.
                    row_text = ''
                    for column in range(1, self.columns + 1):
                        tile = self.board.cells[(column, row)].contents
                        if tile is not None:
                            row_text = '{}{}'.format(row_text, tile)
                    # Compare the row to what it should be.
                    target_text = self.text[((row - 1) * self.columns):(row * self.columns)]
                    if target_text != row_text:
                        break
                # Solve everything.
                self.place_text()
                # Mix up the rows to be left unsolved.
                if row != self.rows:
                    column_range = range(1, self.columns + 1)
                    row_range = range(row + 1, self.rows + 1)
                    row_locations = itertools.product(column_range, row_range)
                    self.shuffle(shuffle_cells = set(board.Coordinate(pair) for pair in row_locations))
        else:
            self.human.tell('Language!')
            go = True
        return go

    def do_move(self, argument):
        """
        Move the specified tile. (m)

        The argument is the tile (or tiles) to move. Each one in order is moved into
        the blank space. Spaces are ignored in the argument, but any invalid move stops
        the movement.
        """
        if self.auto_cap:
            argument = argument.upper()
        for char in argument:
            # Skip spaces.
            if char == ' ':
                continue
            # Find the cell to move.
            movers = []
            # Only search movable squares.
            for offset in ((-1, 0), (0, -1), (0, 1), (1, 0)):
                try:
                    possible = self.board.offset(self.blank_cell.location, offset)
                except KeyError:
                    continue
                if char in possible:
                    movers.append(possible)
            # Check for illegal moves.
            if len(movers) > 1:
                self.human.error('The move {} is ambiguous.'.format(char))
                break
            elif not movers:
                if char in self.text:
                    self.human.error('The {} tile cannot be moved.'.format(char))
                else:
                    self.human.error('There is no {} tile in the puzzle.'.format(char))
                break
            # Move the piece.
            self.board.move(movers[0].location, self.blank_cell.location, char)
            self.blank_cell = movers[0]
            self.moves += 1

    def do_north(self, argument):
        """
        Move the tile to the north of the blank spot. (n)
        """
        self.direction_move((-1, 0), 'north', argument)

    def do_south(self, argument):
        """
        Move the tile to the south of the blank spot. (s)
        """
        self.direction_move((1, 0), 'south', argument)

    def do_west(self, argument):
        """
        Move the tile to the west of the blank spot. (w)
        """
        self.direction_move((0, -1), 'west', argument)

    def game_over(self):
        """Determine if the puzzle is solved. (None)"""
        # Compare the current board to the winning text.
        current = str(self.board).replace('\n', '')
        if current[:-1] == self.text:
            self.human.tell('')
            self.human.tell(self.board)
            self.human.tell('\nYou solved the puzzle!')
            self.human.tell('It took you {} moves to solve the puzzle.'.format(self.moves))
            self.win_loss_draw[0] = 1
            self.scores[self.human.name] = self.rows * self.columns - 1
            self.turns = self.moves
            return True
        else:
            return False

    def handle_options(self):
        """Game the options for the game. (None)"""
        # Parse the user's option choices.
        super(Slider, self).handle_options()
        # Make size override rows and columns
        if self.size:
            self.rows = self.size
            self.columns = self.size
        elif self.rows == self.columns:
            self.size = self.rows
        # Set autocapitalize.
        text_len = self.columns * self.rows - 1
        self.auto_cap = not self.text and text_len < 36
        # Make sure the text is the right size.
        if self.text and len(self.text) < text_len:
            self.human.error('Puzzle text padded because it is too short.')
        elif len(self.text) > text_len:
            self.human.error('Puzzle text truncated because it is too long.')
        self.text = (self.text + self.tiles)[:text_len]

    def place_text(self):
        """Put the text into the puzzle. (None)"""
        for row in range(self.rows):
            for column in range(self.columns):
                if column + 1 == self.columns and row + 1 == self.rows:
                    break
                self.board.place((column + 1, row + 1), self.text[row * self.columns + column])
        self.blank_cell = self.board.cells[(self.columns, self.rows)]
        self.blank_cell.clear()

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        player.tell('')
        player.tell(self.board)
        move = player.ask('\nWhat is your move? ')
        return self.handle_cmd(move)

    def set_options(self):
        """Set up the game options. (None)"""
        self.option_set.add_option('columns', ['c'], int, 4, check = lambda x: x > 0,
            question = 'How many columns should the board have (return for 4)? ')
        self.option_set.add_option('rows', ['r'], int, 4, check = lambda x: x > 0,
            question = 'How many columns should the board have (return for 4)? ')
        self.option_set.add_option('size', ['s'], int, 4, check = lambda x: x > 0,
            question = 'How many columns and rows should the board have (return for 4)? ')
        self.option_set.add_option('text', ['t'], default = '',
            question = 'What text should the solution be (return for numbers + letters)? ')
        self.option_set.add_option('shuffles', ['sh'], default = 3, check = lambda x: x > 0,
            question = 'How many times should the puzzle be shuffled (return for 3)? ')

    def set_up(self):
        """Set up the board for the game. (None)"""
        self.moves = 0
        self.board = TileBoard((self.columns, self.rows))
        self.place_text()
        self.shuffle()

    def shuffle(self, shuffle_cells = []):
        """
        Shuffle the board. (None)

        Parameters:
        shuffle_cells: The locations of the cells to shuffle. (set of board.Coordinate)
        """
        if not shuffle_cells:
            shuffle_cells = set(self.board.cells.keys())
        blanks = set([self.blank_cell.location])
        for mix in range(self.shuffles):
            while len(blanks) < len(shuffle_cells):
                offset = random.choice(((-1, 0), (0, -1), (0, 1), (1, 0)))
                target = self.blank_cell.location + offset
                if target in shuffle_cells:
                    target_cell = self.board.cells[target]
                    self.board.move(target, self.blank_cell.location, target_cell.contents)
                    self.blank_cell = target_cell
                    blanks.add(target_cell)
            blanks = set()


class TileBoard(board.DimBoard):
    """
    A board of sliding tiles. (board.DimBoard)

    Overridden Methods:
    move
    safe
    """

    def __str__(self):
        """Human readable text representation. (str)"""
        lines = []
        for row in range(self.dimensions[1]):
            lines.append([])
            for column in range(self.dimensions[0]):
                lines[-1].append(str(self.cells[(column + 1, row + 1)]))
        return '\n'.join([''.join(line) for line in lines])

    def move(self, start, end, piece = None):
        """
        Move a piece from one cell to a blank cell. (object)

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
