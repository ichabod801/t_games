"""
connect4_game.py

Connect four and related games.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The design and programming credits for Connect Four. (str)
RULES: The rules to Connect Four. (str)

Classes:
C4BotAlphaBeta: A Connect Four bot with a tree search and alpha beta
    pruning. (player.Bot)
C4BotGamma: An alpha-beta Connect Four bot with a better eval
    function. (C4BotAlphaBeta)
C4Board: A board for Connect Four type games. (board.DimBoard)
ConnectFour: A game of connect four. (game.Game)
"""


from __future__ import print_function

import random
import string

import t_games.board as board
import t_games.game as game
import t_games.player as player
import t_games.utility as utility


CREDITS = """
Game Design: Ned Strongin and Howard Wexler
Game Programming: Craig "Ichabod" O'Brien

Connect Four was originally published by Milton Bradley in 1974.
"""

RULES = """
Connect Four is played on a grid six high and seven wide. Players alternate
placing a piece of their color in one of the columns. The piece played becomes
the top piece in the column. The first player to get four pieces in a row,
orthogonally or diagonally, is the winner. If all of the spaces on the board
are filled, the game is a draw.

Options:
columns (c): How many columns the board should have (4-35, default 7).
easy (e): Play against an easy bot.
hard (h): Play against a hard bot.
medium (m): Play against a bot that's just right (the default bot).
pop (p): Allow pop moves, where you remove a piece of yours that is at the
    bottom of a column.
rows: (r): How many rows the board should have (4-20, default 6).
"""


class C4BotAlphaBeta(player.AlphaBetaBot):
    """
    A Connect Four bot with a tree search and alpha beta pruning. (player.Bot)

    Attributes:
    board_strength: A strength rating for each cell on the board. (list of list)
    symbol: The symbol representing the bot in the game. (str)

    Methods:
    eval_player: Evaluate one player's position. (int)
    find_shorts: Find all two or three pieces in a row. (tuple of list of tuple)

    Overridden Methods:
    __init__
    ask
    ask_int
    eval_board
    set_up
    """

    def __init__(self, depth = 6, fudge = 1, taken_names = [], initial = ''):
        """
        Set up the bot. (None)

        Parameters:
        depth: The depth of the search. (int)
        fudge: A fudge factor to avoid early capitulation. (int or float)
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        super(C4BotAlphaBeta, self).__init__(depth, fudge, taken_names, initial)

    def ask(self, prompt):
        """
        Get info from the bot. (str)

        Parameters:
        prompt: The information needed from the player. (str)
        """
        if prompt == '\nWhat symbol would you like to use? ':
            self.symbol = random.choice('@#XO')
            return self.symbol
        else:
            super(C4BotAlphaBeta, self).ask(prompt)

    def ask_int(self, prompt, valid = [], low = 0, high = 0):
        """
        Get an integer from the user. (str)

        If valid is empty and high and low are both 0, any integer is considered
        a valid input.

        Parameters:
        prompt: The text to prompt the user with. (str)
        valid: The list of valid inputs. (list of int)
        low: The lowest valid input. (int)
        high: The highest valid input. (int)
        """
        clone = self.game.board.copy()
        results = self.alpha_beta(clone, self.depth, -utility.MAX_INT, utility.MAX_INT, True)
        return results[0][0]

    def eval_board(self, board):
        """
        Evaluate the board. (int)

        This is just the specified player's evaluation minus the other player's.

        Parameters:
        board: The board to evaluate. (Connect4Board)
        """
        status = board.check_win()
        # Get the standard board evaluation during play.
        if status == 'game on':
            index = self.game.players.index(self)
            result = self.eval_player(board, index) - self.eval_player(board, 1 - index)
        # Otherwise get the end of game evaluation based on the result.
        elif status == 'draw':
            result = 0
        elif status == self.symbol:
            result = 10000
        else:
            result = -10000
        return result

    def eval_player(self, board, player_index):
        """
        Evaluate one player's position. (int)

        The value of the board is the board value of all the pieces, plus 10
        for each two-in-a-row and 100 for each three-in-a-row. A win is worth
        10,000, and a draw is worth 0.

        Parameters:
        board: The game board. (C4Board)
        player_index: The index (turn order) of the player to evaluate. (int)
        """
        # get the player's piece symbol
        piece = self.game.symbols[player_index]
        # check board value of pieces
        locations = [location for location, cell in board.cells.items() if cell.contents == piece]
        score = 0
        for column, row in locations:
            score += self.board_strength[column][row]
        # check for n-in-a-rows.
        twos, threes = self.find_shorts(locations)
        score += 10 * len(twos)
        score += 100 * len(threes)
        return score

    def find_shorts(self, locations):
        """
        Find all two or three pieces in a row. (tuple of list of tuple)

        Parameters:
        locations: The locations of one player's pieces. (list of tuple)
        """
        twos, threes = [], []
        # loop through cells, checking forward and backward
        for coordinate in locations:
            for offset in ((0, 1), (1, 1), (1, 0), (1, -1)):
                forward = coordinate + offset
                backward = coordinate - offset
                # check for threes
                if forward in locations and backward in locations:
                    threes.append((backward, coordinate, forward))
                # check for twos, only forward to avoid doubles
                elif forward in locations:
                    twos.append((coordinate, forward))
        return twos, threes

    def set_up(self):
        """Set up the bot for play. (None)"""
        # Get the value of the first row of cells.
        base = list(range(3, 3 + self.game.columns // 2))
        if self.game.columns % 2:
            base = base + [base[-1] + 2] + base[::-1]
        else:
            base[-1] += 1
            base = base + base[::-1]
        base = [0] + base
        # Get the increase in value as rows get closer to the middle.
        mod = [3] * len(base)
        mod[:3] = [0, 1, 2]
        mod[-2:] = [2, 1]
        # Build up the values for the whole board.
        board_strength = [base]
        while len(board_strength) <= self.game.rows / 2:
            board_strength.append([a + b for a, b in zip(board_strength[-1], mod)])
        if not self.game.rows % 2:
            board_strength.append(board_strength[-1])
        while len(board_strength) <= self.game.rows:
            board_strength.append([a - b for a, b in zip(board_strength[-1], mod)])
        # Rotate the values and add a blank column (there not being a 0 play).
        self.board_strength = list(zip(*board_strength))
        self.board_strength = [[]] + self.board_strength


class C4BotGamma(C4BotAlphaBeta):
    """
    An alpha-beta Connect Four bot with a better eval function. (C4BotAlphaBeta)

    Eval based on two-way twos, one-way threes, and two-way threes; with modifications for those that are
    currently playable and eventually playable.

    Class Attributes:
    bin_values: The relative values of different lines of pieces. (dict)

    Methods:
    bin_shorts: Categorize n-in-a-rows by blockage. (dict of str: int)

    Overridden Methods:
    eval_player
    """

    bin_values = {'2-0': 50, '2-1': 25, '2-2': 0, '3-0': 200, '3-1': 100, '3-2': 0}

    def bin_shorts(self, locations):
        """
        Categorize n-in-a-rows by blockage. (dict of str: int)

        The keys of the return value are length of chain dash ends blocked.

        Parameters:
        locations: The locations of one player's pieces. (list of tuple)
        """
        # Get the short sequences of pieces.
        raw_twos, raw_threes = self.find_shorts(locations)
        # Count the short sequences.
        bins = {'2-0': 0, '2-1': 0, '2-2': 0, '3-0': 0, '3-1': 0, '3-2': 0}
        for chain in raw_twos + raw_threes:
            # Find the spots beyond the short sequences.
            offset = chain[1] - chain[0]
            forward = chain[-1] + offset
            backward = chain[0] - offset
            # Use those to determine blocks.
            blocks = 0
            if forward not in self.game.board.cells or self.game.board.cells[forward].contents:
                blocks += 1
            if backward not in self.game.board.cells or self.game.board.cells[backward].contents:
                blocks += 1
            # Update the count for that situation.
            bins['{}-{}'.format(len(chain), blocks)] += 1
        return bins

    def eval_player(self, board, player_index):
        """
        Evaluate one player's position. (int)

        The value of the board is based on piece location and two or threes in  a row,
        considering how blocked they are.

        Parameters:
        board: The game board. (C4Board)
        player_index: The index (turn order) of the player to evaluate. (int)
        """
        # get the player's piece symbol.
        piece = self.game.symbols[player_index]
        # Check board value of pieces.
        locations = [location for location, cell in board.cells.items() if cell.contents == piece]
        score = 0
        for column, row in locations:
            score += self.board_strength[column][row]
        # Check for n-in-a-rows.
        bins = self.bin_shorts(locations)
        for bin in bins:
            score += bins[bin] * self.bin_values[bin]
        return score


class C4Board(board.DimBoard):
    """
    A board for Connect Four type games. (board.DimBoard)

    Attributes:
    pieces: The pieces to be played. (str)
    poppable: A flag for being able to pop pieces. (bool)
    pops: How many pieces have been popped. (int)
    wins: Winning four in a row combinations. (list of set of tuple)

    Methods:
    check_win: See if the game has been won. (str)
    column_height: Get the number of pieces in a column. (int)
    last_piece: Get the last piece played. (str)
    make_move: Make a valid move. (None)
    pop: Remove the bottom piece of a column. (None)

    Overridden Methods:
    __init__
    __repr__
    __str__
    copy
    get_moves
    """

    def __init__(self, dimensions = (7, 6), pieces = [], wins = [], poppable = False):
        """
        Set up the board and the winning positions. (None)

        Parameters:
        dimensions: The columns and rows of the board, in cells. (tuple of int)
        pieces: The symbols for player pieces. (list of str)
        wins: The winning four in a row combinations (list of set of tuple)
        poppable: A flag for being able to pop pieces. (bool)
        """
        # Do the basic board set up.
        super(C4Board, self).__init__(dimensions)
        # Set the specified attributes.
        self.pieces = pieces
        self.poppable = poppable
        # Set the default attribute.
        self.pops = 0
        # set up winning positions
        self.wins = wins
        if not self.wins:
            # Loop through all the spaces.
            for col in range(1, dimensions[0] + 1):
                for row in range(1, dimensions[1] + 1):
                    # Record any win to the right.
                    if col < dimensions[0] - 2:
                        win = ((col, row), (col + 1, row), (col + 2, row), (col + 3, row))
                        self.wins.append(set([board.Coordinate(xy) for xy in win]))
                    if row < dimensions[0] - 2:
                        # Record any win up.
                        win = ((col, row), (col, row + 1), (col, row + 2), (col, row + 3))
                        self.wins.append(set(set([board.Coordinate(xy) for xy in win])))
                        if col < dimensions[0] - 2:
                            # Record any win up to the right.
                            win = ((col, row), (col + 1, row + 1), (col + 2, row + 2), (col + 3, row + 3))
                            self.wins.append(set([board.Coordinate(xy) for xy in win]))
                        if col > 3:
                            # Record any win up to the left.
                            win = ((col, row), (col - 1, row + 1), (col - 2, row + 2), (col - 3, row + 3))
                            self.wins.append(set([board.Coordinate(xy) for xy in win]))

    def __repr__(self):
        """Generate a debugging text representation."""
        return 'C4Board({})'.format(self.dimensions)

    def __str__(self):
        """Generate a human readable text representation. (str)"""
        # Generate the column numbers.
        ones, tens = '+', '+'
        for column in range(1, self.dimensions[0] + 1):
            ones += str(column % 10)
            tens += str(column // 10)
        # Retain the necessary column numbers.
        if self.dimensions[0] > 9:
            head_foot = '{}\n{}\n'.format(tens, ones)
        else:
            head_foot = ones + '+\n'
        text = '\n{}'.format(head_foot)
        # Add the board positions.
        for row_index in range(self.dimensions[1], 0, -1):
            row_text = '|'
            for column_index in range(1, self.dimensions[0] + 1):
                row_text += str(self.cells[(column_index, row_index)])
            text += row_text + '|\n'
        return text + head_foot.rstrip()

    def check_win(self):
        """See if the game has been won. (str)"""
        # Get the locations with each player's pieces
        winners = []
        for piece in self.pieces:
            played = set([cell.location for cell in self.cells.values() if cell.contents == piece])
            # check against the winning positions
            for win in self.wins:
                if len(win.intersection(played)) == 4:
                    winners.append(piece)
                    break
        # Check for a draw.
        full = [cell for cell in self.cells.values() if cell.contents]
        filled = len(full) == self.dimensions[0] * self.dimensions[1]
        if filled or len(winners) == 2:
            result = 'draw'
        # Check for a win.
        elif winners:
            result = winners[0]
        # Default to game on.
        else:
            result = 'game on'
        return result

    def column_height(self, column):
        """
        Get the number of pieces in a column. (int)

        Parameters:
        column: The column to check. (int)
        """
        # Check rows until you get an empty cell.
        for row in range(1, self.dimensions[1] + 1):
            if not self.cells[(column, row)].contents:
                break
        return row - 1

    def copy(self):
        """Create a copy of the board for AI searches. (Connect4Board)"""
        clone = C4Board(self.dimensions, pieces = self.pieces, wins = self.wins, poppable = self.poppable)
        clone.copy_pieces(self)
        return clone

    def get_moves(self):
        """
        Get all legal moves from the current position. (list of (int, string))
        """
        # get the current piece
        pieces_played = len([cell for cell in self.cells.values() if cell.contents]) + self.pops
        current_piece = self.pieces[pieces_played % 2]
        # get the open columns
        columns = []
        for column in range(1, self.dimensions[0] + 1):
            if not self.cells[(column, self.dimensions[1])]:
                columns.append(column)
        # add the poppable columns, if popping is allowed.
        if self.poppable:
            valid_pops = []
            for column in range(1, self.dimensions[0] + 1):
                if self.cells[(column, 1)].contents == current_piece:
                    valid_pops.append(-column)
            columns.extend(valid_pops)
        # return the columns with the current piece.
        return [(column, current_piece) for column in columns]

    def last_piece(self):
        """Get the last piece played. (str)"""
        pieces_played = len([cell for cell in self.cells.values() if cell.contents]) + self.pops
        return self.pieces[1 - pieces_played % 2]

    def make_move(self, move):
        """
        Make a valid move. (None)

        Parameters:
        move: A column and a piece to drop in it. (tuple of int, string)
        """
        # get the details of the move
        column, piece = move
        # Check for a pop move.
        if column < 0 and self.poppable:
            self.pop(column, piece)
        else:
            # Check the validity of the move.
            height = self.column_height(column)
            if height <= self.dimensions[1]:
                self.place((column, height + 1), piece)
            else:
                raise ValueError('Invalid move: column {} is full'.format(column))

    def pop(self, column, piece):
        """
        Remove the bottom piece of a column. (None)

        Parameters:
        column: The negative (one indexed) column to pop. (int)
        piece: The piece to pop. (str)
        """
        # Convert the column.
        column = abs(column)
        # Check for a valid move.
        if self.cells[(column, 1)].contents == piece:
            # Move the pieces down.
            for row in range(2, self.dimensions[1] + 1):
                self.cells[(column, row - 1)].contents = self.cells[(column, row)].contents
            self.cells[(column, self.dimensions[1])].contents = None
            # Record the pop.
            self.pops += 1
        else:
            # Warn on invalid pops.
            raise ValueError('Invalid pop: column {} does not start with {!r}.'.format(column, piece))


class ConnectFour(game.Game):
    """
    A game of Connect Four. (game.Game)

    Class Attributes:
    bot_classes: The classes for the available opponent bots. (dict of str: type)

    Attributes:
    board: The game board. (C4Board)
    bot: The computer opponents. (player.Bot)
    bot_level: The strength of the computer player. (str)
    bot_random: A flag for the next computer move being random. (bool)
    columns: The width of the board. (int)
    poppable: A flag for being able to pop a piece from a column. (bool)
    rows: The height of the board. (int)
    symbols: The symbols for the players pieces. (list of str)

    Overridden methods:
    __str__
    clean_up
    game_over
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['CoFo']
    bot_classes = {'alpha-beta': C4BotAlphaBeta, 'gamma': C4BotGamma}
    categories = ['Board Games']
    credits = CREDITS
    name = 'Connect Four'
    num_options = 4
    rules = RULES

    def __str__(self):
        """Generate a human readable text representation. (str)"""
        return str(self.board)

    def clean_up(self):
        """Post-game clean up. (None)"""
        self.human.tell(self)

    def do_gipf(self, arguments):
        """
        Yeah, just go two blocks up and take a right. You can't miss it.
        """
        # Check/play the gipf game.
        game, losses = self.gipf_check(arguments, ('roulette', 'wumpus'))
        # Handle Roulette edge.
        if game == 'roulette':
            if not losses:
                self.bot_random = True
        # Handle Hunt the Wumpus edge.
        elif game == 'wumpus':
            if not losses:
                # Remind the human.
                self.human.tell(self)
                # Get the column to reverse.
                query = 'Which column would you like to reverse? '
                col = self.human.ask_int(query, low = 1, high = self.board.dimensions[0])
                # Get the cell contents in reverse.
                pieces = []
                for row in range(self.board.dimensions[1], 0, -1):
                    pieces.append(self.board.cells[(col, row)].contents)
                # Put any non-empty cells back on the board.
                row = 1
                for piece in pieces:
                    if piece is not None:
                        self.board.cells[(col, row)].contents = piece
                        row += 1
                return False
        # Handle invalid edge.
        else:
            self.human.tell("Yeah, just go two blocks up and take a right. You can't miss it.")
        return True

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # Check for a win.
        win = self.board.check_win()
        human_piece = self.symbols[self.players.index(self.human)]
        # Categorize end of game.
        if win != 'game on':
            if win == 'draw':
                self.human.tell('\nThe game was a draw. :|')
                self.win_loss_draw[2] = 1
            elif win == human_piece:
                self.human.tell('\nYou won! :)')
                self.win_loss_draw[0] = 1
            else:
                self.human.tell('\nYou lost. :(')
                self.win_loss_draw[1] = 1
            return True
        # Or keep playing.
        else:
            return False

    def handle_options(self):
        """Determine and handle the options for the game. (None)"""
        super(ConnectFour, self).handle_options()
        # Set the bot.
        if self.bot_level == 'easy':
            self.bot = C4BotAlphaBeta(taken_names = [self.human.name])
        elif self.bot_level == 'medium':
            self.bot = C4BotGamma(taken_names = [self.human.name])
        else:
            self.bot = C4BotGamma(depth = 8, taken_names = [self.human.name])
        self.players = [self.human, self.bot]
        # get symbols
        self.symbols = []
        if not self.symbols:
            for player in self.players:
                invalid = ''.join(self.symbols)
                while True:
                    symbol = player.ask('\nWhat symbol would you like to use? ')
                    if symbol in invalid:
                        player.tell('That symbols is already being used by another player.')
                    else:
                        break
                self.symbols.append(symbol)

    def set_options(self):
        """Define the options for the game. (None)"""
        # Set the board options.
        self.option_set.add_option('columns', ['c'], int, 7, valid = range(4, 36),
            question = 'How many columns should there be on the board (return for 7)? ')
        self.option_set.add_option('rows', ['r'], int, 6, valid = range(4, 20),
            question = 'How many rows should there be on the board (return for 6)? ')
        # Set the play option.
        self.option_set.add_option('pop', ['p'], target = 'poppable',
            question = 'Should you be able to pop out the bottom piece in a row? bool')
        # Set the bot option.
        self.option_set.add_option('bot-level', ['b'],
            valid = ['easy', 'medium', 'hard'], default = 'medium',
            question = 'How hard of a bot do you want to play against (return for medium)? ')

    def player_action(self, now_player):
        """
        Play one turn for the given player. (None)

        Parameters:
        now_player: The player to play a turn for. (Player)
        """
        # show the board
        now_player.tell(self)
        # get the move
        open_columns = [move[0] for move in self.board.get_moves()]
        if self.bot_random and isinstance(now_player, player.Bot):
            column_index = random.choice(open_columns)
            self.bot_random = False
        else:
            prompt = '\nWhich column would you like to play in? '
            column_index = now_player.ask_int(prompt, valid = open_columns)
        # Handle non-move commands.
        if isinstance(column_index, str):
            return self.handle_cmd(column_index)
        # Ohterwise make the move.
        self.board.make_move((column_index, self.symbols[self.players.index(now_player)]))

    def set_up(self):
        """Set up the game. (None)"""
        # shuffle players and symbols
        saved_players = self.players[:]
        random.shuffle(self.players)
        if self.players != saved_players:
            self.symbols.reverse()
        # reset board
        self.board = C4Board((self.columns, self.rows), poppable = self.poppable)
        self.board.pieces = self.symbols
        # reset the bot
        self.bot.set_up()
        self.bot_random = False


if __name__ == '__main__':
    # Play the game without the interface.
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    connect_four = ConnectFour(player.Humanoid(name), '')
    connect_four.play()
