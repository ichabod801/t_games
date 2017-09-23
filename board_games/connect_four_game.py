"""
connect4_game.py

Connect four and related games.

Once commmented this module will be on hold until alpha beta pruning is fixed. 
Work on correcting that is being (will be) done in the tictactoe_game module.

Constants:
CREDITS: The design and programming credits for Connect Four. (str)
RULES: The rules to Connect Four. (str)

Classes:
ConnectFour: A game of connect four. (game.Game)
C4Board: A board for Connect Four type games. (board.GridBoard)
C4BotAlphaBeta: A Connect Four bot with a tree search and alpha beta 
    pruning. (player.Bot)
C4BotGamma: An alpha-beta Connect Four bot with a better eval 
    function. (C4BotAlphaBeta)
"""


from __future__ import print_function

import random
import string

import tgames.board as board
import tgames.game as game
import tgames.player as player
import tgames.utility as utility


# The design and programming credits for Connect Four.
CREDITS = """
Game Design: Ned Strongin and Howard Wexler
Game Programming: Craig "Ichabod" O'Brien

Connect Four was originally published by Milton Bradley in 1974.
"""

# The rules to Connect Four.
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
rows: (r): How many rows the board should have (4-20, default 6).
"""


class C4Board(board.GridBoard):
    """
    A board for Connect Four type games. (board.GridBoard)

    Attributes:
    pieces: The pieces to be played. (str)
    wins: Winning four in a row combinations. (list of set of tuple)

    Methods:
    check_win: See if the game has been won. (str)
    column_height: Get the number of pieces in a column. (int)
    get_moves: Get all legal moves from the current position. (list of int)
    make_move: Make a valid move. (None)

    Overridden Methods:
    __repr__
    __str__
    """

    def __init__(self, columns = 7, rows = 6, pieces = [], wins = []):
        """
        Set up the board and the winning positions. (None)

        Parameters:
        columns: The number of columns on the board. (int)
        rows: The number of rows on the board. (int)
        pieces: The symbols for player pieces. (list of str)
        wins: The winning four in a row combinations (list of set of tuple)
        """
        # basic set up
        super(C4Board, self).__init__(columns, rows)
        self.pieces = pieces
        # set up winning positions
        self.wins = wins
        if not self.wins:
            for col in range(self.columns):
                for row in range(self.rows):
                    if col < self.columns - 3:
                        win = ((col, row), (col + 1, row), (col + 2, row), (col + 3, row))
                        self.wins.append(set([board.Coordinate(xy) for xy in win]))
                    if row < self.rows - 3:
                        win = ((col, row), (col, row + 1), (col, row + 2), (col, row + 3))
                        self.wins.append(set(set([board.Coordinate(xy) for xy in win])))
                    if col < self.rows - 3 and row < self.columns - 3:
                        win = ((col, row), (col + 1, row + 1), (col + 2, row + 2), (col + 3, row + 3))
                        self.wins.append(set([board.Coordinate(xy) for xy in win]))
                        win = ((col + 3, row), (col + 2, row + 1), (col + 1, row + 2), (col, row + 3))
                        self.wins.append(set([board.Coordinate(xy) for xy in win]))

    def __repr__(self):
        """
        Debugging text representation.
        """
        return 'C4Board({}, {})'.format(self.columns, self.rows)

    def __str__(self):
        """
        Human readable text representation. (str)
        """
        ones, tens = '+', '+'
        for column in range(1, self.columns + 1):
            ones += str(column % 10)
            tens += str(column // 10)
        if self.columns > 9:
            head_foot = '{}\n{}\n'.format(tens, ones)
        else:
            head_foot = ones + '+\n'
        text = head_foot
        for row_index in range(self.rows - 1, -1, -1):
            row_text = '|'
            for column_index in range(self.columns):
                row_text += str(self.cells[(column_index, row_index)])
            text += row_text + '|\n'
        return text + head_foot
                    
    def check_win(self):
        """
        See if the game has been won. (str)
        """
        # get the last played piece
        last_piece = self.last_piece()
        # get the locations with those pieces
        played = set([cell.location for cell in self.cells.values() if cell.piece == last_piece])
        # check against the winning positions
        for win in self.wins: 
            if len(win.intersection(played)) == 4:
                 return 'win'
        # check for a draw
        filled = [cell for cell in self.cells.values() if cell.piece]
        if len(filled) == self.columns * self.rows:
            return 'draw'
        # default to game on
        return 'game on'

    def column_height(self, column):
        """
        Get the number of pieces in a column. (int)

        Parameters:
        column: The column to check. (int)
        """
        # check rows til you get an empty cell
        for row in range(self.rows):
            if not self.cells[(column, row)].piece:
                break
        return row

    def copy(self):
        """
        Create a copy of the board for AI searches. (Connect4Board)
        """
        return super(C4Board, self).copy(pieces = self.pieces, wins = self.wins)

    def get_moves(self):
        """
        Get all legal moves from the current position. (list of (int, string))
        """
        # get the current piece
        pieces_played = len([cell for cell in self.cells.values() if cell.piece])
        current_piece = self.pieces[pieces_played % 2]
        # return the current piece with the open columns
        columns = [column for column in range(self.columns) if self.cells[(column, self.rows - 1)].piece is None]
        return [(column, current_piece) for column in columns]

    def last_piece(self):
        """
        Get the last piece played. (str)
        """
        pieces_played = len([cell for cell in self.cells.values() if cell.piece])
        return self.pieces[1 - pieces_played % 2]

    def make_move(self, move):
        """
        Make a valid move. (None)

        Parameters:
        move: A column and a piece to drop in it. (tuple of int, string)
        """
        # get the details of the move
        column, piece = move
        height = self.column_height(column)
        # attempt the move
        if height < self.rows:
            self.place(piece, (column, height))
        else:
            raise ValueError('Invalid move: column {} is full'.format(column + 1))


class ConnectFour(game.Game):
    """
    A game of Connect Four. (game.Game)

    !! implement rules variants from wikipedia.

    Attributes:
    board: The game board. (C4Board)
    symbols: The symbols for the players pieces. (list of str)

    Overridden methods:
    __str__
    clean_up
    game_over
    handle_options
    player_turn
    set_up
    """

    categories = ['Board Games', 'Space Games']
    credits = CREDITS
    name = 'Connect Four'
    rules = RULES

    def __str__(self):
        """Human readable text representation. (str)"""
        return str(self.board)

    def clean_up(self):
        """Post-game clean up. (None)"""
        self.human.tell(self)

    def game_over(self):
        """Check for the end of the game. (bool)"""
        win = self.board.check_win()
        player = self.players[1 - self.turns % 2]
        if win != 'game on':
            if win == 'win':
                if player == self.human:
                    self.win_loss_draw[0] = 1
                else:
                    self.win_loss_draw[1] = 1
            else:
                self.win_loss_draw[2] = 1
            return True
        else:
            return False

    def handle_options(self):
        """Determine and handle the options for the game. (None)"""
        # !! refactor, too long.
        # Set default options.
        bot_level = 'medium'
        self.columns = 7
        self.rows = 6
        # Handle no options.
        if self.raw_options.lower() == 'none':
            pass
        # Handle options from the interface.
        elif self.raw_options:
            for word in self.raw_options.lower().split():
                if word in ('easy', 'e'):
                    bot_level = 'easy'
                elif word in ('medium', 'm'):
                    bot_level = 'medium'
                elif word in ('hard', 'h'):
                    bot_level = 'hard'
                if '=' in word:
                    option, value = words.split('=')
                    try:
                        int_value = int(value)
                    except ValueError:
                        self.human.tell('Invalid value for {} option: {!r}.'.format(option, value))
                        continue
                    if option in ('columns', 'c'):
                        if 4 <= int_value <= 35:
                            self.columns = int_value
                        else:
                            self.human.tell('The columns option must be 4 to 35.')
                    elif option in ('rows', 'r'):
                        if 4 <= int_value <= 20:
                            self.rows = int_value
                        else:
                            self.human.tell('The rows option must be 4 to 20.')
        # Ask the user for option settings.
        else:
            if self.human.ask('Would you like to change the options? ').lower() in utility.YES:
                prompt = 'What level bot would you like to play against (return for medium)? '
                while True:
                    bot_level = self.human.ask(prompt).lower()
                    if not bot_level:
                        bot_level = 'medium'
                    if bot_level in ('easy', 'e', 'medium', 'm', 'hard', 'h'):
                        break
                    self.human.tell('That is not a valid bot level. Please pick easy, medium, or hard.')
                prompt = 'How many columns should there be on the board (return for 7)? '
                self.columns = self.human.ask_int(prompt, low = 4, high = 35, default = 7, cmd = False)
                prompt = 'How many rows should there be on the board (return for 6)? '
                self.rows = self.human.ask_int(prompt, low = 4, high = 20, default = 6, cmd = False)
        # Set the bot.
        if bot_level in ('easy', 'e'):
            self.bot = C4BotAlphaBeta(taken_names = [self.human.name])
        elif bot_level in ('medium', 'm'):
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
                    symbol = player.ask('What symbol would you like to use? ')
                    if symbol in invalid:
                        player.tell('That symbols is already being used by another player.')
                    else:
                        break
                self.symbols.append(symbol)
        
    def player_turn(self, player):
        """
        Play one turn for the given player. (None)

        Parameters:
        player: The player to play a turn for. (Player)
        """
        # show the board
        player.tell(self)
        # get the move
        open_columns = [move[0] + 1 for move in self.board.get_moves()]
        prompt = 'Which column would you like to play in? '
        column_index = player.ask_int(prompt, valid = open_columns)
        self.board.make_move((column_index - 1, self.symbols[self.players.index(player)]))

    def set_up(self):
        """
        Set up the game. (None)
        """
        # shuffle players and symbols
        saved_players = self.players[:]
        random.shuffle(self.players)
        if self.players != saved_players:
            self.symbols.reverse()
        # reset board
        self.board = C4Board(self.columns, self.rows)
        self.board.pieces = self.symbols
        # reset the bot
        self.bot.set_up()

class C4BotAlphaBeta(player.AlphaBetaBot):
    """
    A Connect Four bot with a tree search and alpha beta pruning. (player.Bot)

    Methods:
    eval_player: Evaluate one player's position. (int)
    find_shorts: Find all two or three pieces in a row. (tuple of list of tuple)

    Overridden Methods:
    __init__
    ask
    ask_int
    eval_board
    """

    # !! needs to be expanded based on board size.
    # !! pattern is across the bottom then up.
    board_strength = [[3, 4, 5, 5, 4, 3], [4, 6, 8, 8, 6, 4], [5, 8, 11, 11, 8, 5], [7, 10, 13, 13, 10, 7],
        [5, 8, 11, 11, 8, 5], [4, 6, 8, 8, 6, 4], [3, 4, 5, 5, 4, 3]]

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
        if prompt == 'What symbol would you like to use? ':
            self.symbol = random.choice('@#XO')
            return self.symbol

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
        return results[0][0] + 1

    def eval_board(self, board):
        """
        Evaluate the board. (int)

        This is just the specified player's evaluation minus the other player's.

        Parameters:
        board: The board to evaluate. (Connect4Board)
        player_index: The index of the player to evaluate the board for. (int)
        """
        if board.check_win() == 'win':
            if self.symbol == board.last_piece():
                result = 10000
            else:
                result = -10000
        else:
            index = self.game.players.index(self)
            result = self.eval_player(board, index) - self.eval_player(board, 1 - index)
        """print(board)
        print(result)
        print()"""
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
        locations = [location for location, cell in board.cells.items() if cell.piece == piece]
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
        base = list(range(3, 3 + self.game.columns // 2))
        if self.game.columns % 2:
            base = base + [base[-1] + 2] + base[::-1]
        else:
            base[-1] += 1
            base = base + base[::-1]
        mod = [3] * len(base)
        mod[:2] = [1, 2]
        mod[-2:] = [2, 1]
        board_strength = [base]
        while len(board_strength) < self.game.rows / 2:
            board_strength.append([a + b for a, b in zip(board_strength[-1], mod)])
        if not self.game.rows % 2:
            board_strength.append(board_strength[-1])
        while len(board_strength) < self.game.rows:
            board_strength.append([a - b for a, b in zip(board_strength[-1], mod)])
        self.board_strength = list(zip(*board_strength))

class C4BotGamma(C4BotAlphaBeta):
    """
    An alpha-beta Connect Four bot with a better eval function. (C4BotAlphaBeta)

    Eval based on two-way twos, one-way threes, and two-way threes; with modifications for those that are
    currently playable and eventually playable.

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
        raw_twos, raw_threes = self.find_shorts(locations)
        bins = {'2-0': 0, '2-1': 0, '2-2': 0, '3-0': 0, '3-1': 0, '3-2': 0}
        for chain in raw_twos + raw_threes:
            offset = chain[1] - chain[0]
            forward = chain[-1] + offset
            backward = chain[0] - offset
            blocks = 0
            if forward not in self.game.board.cells or self.game.board.cells[forward].piece:
                blocks += 1
            if backward not in self.game.board.cells or self.game.board.cells[backward].piece:
                blocks += 1
            bins['{}-{}'.format(len(chain), blocks)] += 1
        return bins

    def eval_player(self, board, player_index):
        """
        Evaluate one player's position. (int)

        The value of the board is based on piece location and two or threes in  a row, 
        considering how blocked they are.

        !! still needs to consider odd/even open ends (I think, check for strategy)

        Parameters:
        board: The game board. (C4Board)
        player_index: The index (turn order) of the player to evaluate. (int)
        """
        # get the player's piece symbol
        piece = self.game.symbols[player_index]
        # check board value of pieces
        locations = [location for location, cell in board.cells.items() if cell.piece == piece]
        score = 0
        for column, row in locations:
            score += self.board_strength[column][row]
        # check for n-in-a-rows.
        bins = self.bin_shorts(locations)
        for bin in bins:
            score += bins[bin] * self.bin_values[bin]
        return score

if __name__ == '__main__':
    from collections import namedtuple
    Gaem = namedtuple('Gaem', ['columns', 'rows'])
    game = Gaem(7, 6)
    bot = C4BotAlphaBeta()
    static = bot.board_strength
    bot.game = game
    bot.set_up()
    print(static)
    print(bot.board_strength)
    print(static == bot.board_strength)
