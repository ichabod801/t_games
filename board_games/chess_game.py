# coding=utf-8
"""
chess_game.py

A t_games wrapper for Sunfish by Thomas Ahle.
(https://github.com/thomasahle/sunfish)

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Chess. (str)
RULES: The rules of Chess. (str)

Classes:
Chess: A t_games wrapper for Sunfish. (game.Game)
SunfishBot: A bot for making Sunfish moves. (player.Bot)
"""


import random
import re

from .. import game
from .. import options
from .. import player
from .. import utility
from . import sunfish


CREDITS = """
Game Design: Traditional
Game Programmming: Thomas Ahle (Sunfish chess engine)
    Craig O'Brien (t_games wrapper for Sunfish)
"""

RULES = """
Each player takes turns moving a piece, starting with the white (capitalized)
pieces. If one piece ends in the same square as an opposing piece, the opposing
piece is captured and removed from the board. Your king may not be moved to a
square where it could be captured. If you have no legal moves left, you are
checkmated, and you lose the game.

Each piece moves differently:

    * Pawns: Pawns can move one space straight forward without capturing, or
      one space diagonally forward while capturing. On their first move, pawns
      may move two space straight forward.
    * Knights: Knights move twos square vertically and then one horizontally,
      or two squares horizontally and then one square vertically. Knights may
      move through other pieces, but must end on an empty or capturing square.
    * Bishops: Bishops move any number of squares diagonally.
    * Rooks: Rooks move any number of squares horizontally or vertically.
    * Queens: Queens move any number of sqaures diagonally, horizontally, or
      vertically.
    * Kings: Kings move one square in any direction.

Special moves:

    * En Passant: If a pawn moves two squares on its first move and ends up
      next to (horizontally) an opposing pawn, the opposing pawn may capture
      it as if it had only move one space, but only if this is done
      immediately.
    * Promotion: If a pawn makes it all the way across the board, it becomes
      a queen (technically it can become any piece, but this version does not
      support that).
    * Castling: If a king and a rook have not moved, and there are no pieces
      between them, and none of the intervening squares are attacked, they may
      castle. The rook moves next to the king, and the king hops over the rook
      to the other side. This is done in the interface by moving the king two
      squares toward the rook.

Entering Moves:

Each square on the board is identified by coordinates as indicated by the
letters along the bottom and the numbers along the side. So the white king
starts on e1. To move a piece, simply enter the square it is on and the
square you want to move it to. Alternatively you can use algebraic notation or
ICCF numeric notation.

Options:
black (b): Play as black. If neither black are or white options are used, the
    color of your pieces is determined randomly.
difficulty= (d=): How many tenths of a second the computer player gets to
    choose their move (defaults to 20).
fen= (f=): The FEN for the starting position. Note that any spaces in the FEN
    string must be replaced with pipes (|).
opening= (o=): The opening position to start with. Options include Caro-Kann,
    French, Indian, Italian, Pirc, Queens-Gambit, Ruy-Lopez, and Sicilian.
unicode (uni, u): Show the unicode chess piece characters, if your terminal
    supports them.
white (w): Play as white. If neither black are or white options are used, the
    color of your pieces is determined randomly.
"""


class Chess(game.Game):
    """
    A t_games wrapper for Sunfish. (game.Game)

    Note that the Sunfish board is always from the perspective of white. So there
    are a lot of reversals and cases changes of the board and the moves in the code
    for the wrapper. Also, 'if self.player_index' is frequently used as a proxy for
    'if the current player is playing black' in those sections of the code.

    Attributes:
    black: A flag for the human playing the black pieces. (bool)
    difficulty: How many tenths of a second the computer has to move. (int)
    draw_moves: The number of half-turns without a pawn move or a capture. (int)
    fen: The FEN notation for the starting position. (str)
    history: A list of board strings for previous moves. (list of str)
    opening: The FEN notation for opening to play. (str)
    skip_white: A flag for the game starting with the black player. (bool)
    unicode: A flag for displaying the board with unicode pieces. (bool)
    white: A flag for the huamn playing the white pieces. (bool)

    Class Attributes:
    castle_re: A regular expression for castling moves. (re.SRE_Pattern)
    move_re: A regular expression for an algebraic move. (re.SRE_Pattern)
    openings: FEN strings for vailable starting positions. (dict of str: str)
    unicode_pieces: Translation of ascii to unicode for pieces. (dict of str: str)

    Methods:
    board_text: Get the text for a given position. (str)
    do_draw: Ask for a draw. (bool)
    do_move: Make a move in the game. (bool)
    parse_algebraic: Parse an algebraic move into a Sunfish move. (tuple)
    parse_fen: Parse a position from Forsyth-Edwards Notation. (Position)
    parse_move: Parse a move into one Sunfish recognizes. (str)

    Overridden Methods:
    __str__
    default
    game_over
    handle_options
    player_action
    set_options
    set_up
    """

    aliases = {'m': 'move'}
    castle_re = re.compile('o-o(-o)?')
    categories = ['Board Games']
    move_re = re.compile('([BNRQK])?([a-h])?([1-8])?[ -x/]?([a-h][1-8])')
    name = 'Chess'
    num_options = 3
    openings = {'': '',
        'castle-test': 'r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R|w|KQkq|-|0|1',
        'caro-kann': 'rnbqkbnr/ppp2ppp/2p5/3p4/3PP3/8/RNBQKBNR|w|KQkq|-|0|3',
        'french': 'rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/RNBQKBNR|w|KQkq|-|0|3',
        'indian': 'rnbqkb1r/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR|w|KQkq|-|0|2',
        'italian': 'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R|w|KQkq|-|0|3',
        'pirc': 'rnbqkb1r/3p1n2/8/3PP3/2N5/PPP2PPP/R1BQKBNR|b|KQkq|-|0|3',
        'queens-gambit': 'rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/RNBQKBNR|b|KQkq|-|0|2',
        'ruy-lopez': 'r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R|w|KQkq|-|0|3',
        'sicilian': 'rnbqkbnr/pp1ppppp/8/2p5/4P3/8/RNBQKBNR|w|KQkq|-|0|2',
        'mate-test': '8/5K1k/8/6Q1/8/8/8/8|w|-|-|0|81'}
    unicode_pieces = {'R':'♜', 'N':'♞', 'B':'♝', 'Q':'♛', 'K':'♚', 'P':'♟',
        'r':'♖', 'n':'♘', 'b':'♗', 'q':'♕', 'k':'♔', 'p':'♙', '.':'·'}

    def __str__(self):
        """Human readable text representation. (str)"""
        return self.board_text(self.position, self.player_index)

    def board_text(self, position, black):
        """
        Get the text for a given position. (str)

        Parameters:
        position: The position to get the text for. (sunfish.Position)
        black: A flag indicating the position is for the black player. (bool)
        """
        # Get the lines of text for the board.
        lines = ['']
        for row_index, row in enumerate(position.board.split(), start = 1):
            if self.unicode:
                row = [self.unicode_pieces.get(piece, piece) for piece in row]
            if not black:
                row_index = 9 - row_index
            lines.append(' {} {}'.format(row_index, ' '.join(row)))
        # Handle the lower frame.
        if black:
            lines.append('   h g f e d c b a')
        else:
            lines.append('   A B C D E F G H')
        # Join the lines.
        text = '\n'.join(lines)
        # Reverse piece 'colors' for black.
        if black:
            text = text.swapcase()
        return text

    def default(self, text):
        """
        Handle unrecognized commands. (bool)

        Parameters:
        text: The raw text input by the user. (str)
        """
        # Treat chess notation as a move.
        if self.move_re.match(text) or self.castle_re.match(text.lower()) or text.isdigit():
            return self.do_move(text)
        else:
            return super(Chess, self).default(text)

    def do_draw(self, arguments):
        """
        Ask for a draw.

        If the current position has been repeated three times or there have been 50
        moves since the last pawn move or capture, the draw will be granted. Otherwise,
        the opponent must agree to the draw.

        Aliases: d
        """
        foe = self.players[1 - self.player_index]
        # Check for three fold repetition.
        if self.history.count(self.position.board) >= 3:
            self.force_end = 'draw'
        # Check for 50 move rule.
        elif self.draw_turns >= 100:
            self.force_end = 'draw'
        # If one can't be claimed, check for an agreed draw.
        elif foe.ask('A draw has been offered, do you accept? ') in utility.YES:
            self.force_end = 'draw'
        else:
            self.players[self.player_index].tell('Your draw offer was rejected.')
        if self.force_end:
            # Handle cases that resulted in a draw.
            self.human.tell('The game is a draw.')
            self.win_loss_draw = [0, 0, 1]
            self.scores[self.human.name] = 1
            return False
        else:
            return True

    def do_gipf(self, arguments):
        """
        Global Thermonuclear War randomly destroys an enemy pawn.

        Mate randomly upgrades one of your pawns into a knight.
        """
        game, losses = self.gipf_check(arguments, ('global thermonuclear war', 'mate'))
        go = True
        if game == 'global thermonuclear war':
            if not losses:
                # Find the pawns.
                board_text = self.position.board
                pawns = []
                start = 0
                while True:
                    try:
                        next_p = board_text.index('p', start)
                    except ValueError:
                        break
                    pawns.append(next_p)
                    start = next_p + 1
                # Change one at random.
                target = random.choice(pawns)
                new_board = board_text[:target] + '.' + board_text[(target + 1):]
                # Reset the position
                self.position = self.position._replace(board = new_board)
        elif game == 'mate':
            if not losses:
                # Find the pawns.
                board_text = self.position.board
                pawns = []
                start = 0
                while True:
                    try:
                        next_p = board_text.index('P', start)
                    except ValueError:
                        break
                    pawns.append(next_p)
                    start = next_p + 1
                # Change one at random.
                target = random.choice(pawns)
                new_board = board_text[:target] + 'N' + board_text[(target + 1):]
                # Reset the position
                self.position = self.position._replace(board = new_board)
        else:
            text = "I'm sorry, but that's a violation of the Laws of Chess, section 10, subsection 8, "
            text += "paragraph 3, line 2, as ammended by the Carlsen Convention of 1809."
            self.human.tell(text)
        return go

    def do_move(self, arguments):
        """
        Make a move in the game.

        Moves are accepted in long algebraic notation, standard algebraic notation, or
        ICCF numeric notation.

        Aliases: m
        """
        # Get the player and the move.
        player = self.players[self.player_index]
        sun_move = self.parse_move(arguments)
        # Check for an error parsing the move.
        if sun_move[0] is None:
            player.error(sun_move[1])
            return True
        else:
            # Transpose the move for black.
            if self.player_index:
                sun_move = (119 - sun_move[0], 119 - sun_move[1])
            # Check for a legal move.
            if sun_move in self.position.gen_moves():
                # Update the tracking for the 50 move rule.
                if self.position.board[sun_move[0]] != 'P' and self.position.board[sun_move[1]] != '.':
                    self.draw_turns += 1
                else:
                    self.draw_turns = 0
                # Make the move.
                self.position = self.position.move(sun_move)
                # Store the move for checking three fold repetition.
                if self.player_index:
                    self.history.append(self.position.board)
                else:
                    self.history.append(self.position.rotate().board)
                # Show the player the resulting position from their perspective.
                player.tell(self.board_text(self.position.rotate(), self.player_index))
                return False
            else:
                # Warn about moves that are not legal.
                player.error('{} is not a legal move.'.format(arguments))
                return True

    def game_over(self):
        """Determine if the game is over or not. (bool)"""
        # Mate detection based on position score does not seem to be working,
        # So I programmed an old fashioned check based on Sunfish being a king-capture engine.
        next_moves = list(self.position.gen_moves())
        if next_moves:
            # Check all possible opponent responses.
            for move in next_moves:
                next_position = self.position.move(move)
                # Check for possible king captures after opponent's respons
                king_square = next_position.board.index('k')
                if not any(response[1] == king_square for response in next_position.gen_moves()):
                    # If there is a response not leading to king capture, it is not mate.
                    break
            else:
                # If there is no break, there is no move avoiding king capture, so it's mate.
                # Confirm mate vs. stalemate (mate means you can currently take the king).
                stale_check = self.position.rotate()
                king_square = stale_check.board.index('k')
                if any(move[1] == king_square for move in stale_check.gen_moves()):
                    # Inform the user of mate.
                    self.human.tell('Checkmate!')
                    winner = self.players[self.player_index]
                    self.human.tell('{} wins the game.'.format(winner.name))
                    # Set the results of the game.
                    if winner == self.human:
                        self.win_loss_draw = [1, 0, 0]
                        self.scores[self.human.name] = 2
                    else:
                        self.win_loss_draw = [0, 1, 0]
                    return True
                else:
                    # If no current king attack, it's stalemate.
                    self.human.tell('Stalemate, the game is a draw.')
                    self.win_loss_draw = [0, 0, 1]
                    self.scores[self.human.name] = 1
                    return True
            return False

    def handle_options(self):
        """Handle the option settings for the game. (None)"""
        super(Chess, self).handle_options()
        # Set up players, assuming set_up will reverse them.
        self.players = [SunfishBot(), self.human]  # white
        if self.black:
            self.players.reverse()                 # black
        elif not self.white:
            random.shuffle(self.players)           # random

    def parse_algebraic(self, text, match):
        """
        Parse an algebraic move into a Sunfish move. (tuple)

        Parameters:
        text: The move as entered by the user. (str)
        match: The match data from the regular expression. (re.SRE_Match)
        """
        # Determine what information was provided.
        groups = match.groups()
        match_type = sum(2 ** index for index, group in enumerate(groups) if group is not None)
        # Handle single squares (pawn moves).
        if match_type in (8, 10):
            end = sunfish.parse(groups[3])
            direction = -10 if self.player_index else 10
            if self.player_index:
                board = self.position.rotate().board
            else:
                board = self.position.board # works
            # Set up disambiguation
            if match_type == 10:
                column = ' abcdefgh'.index(groups[1])
                direction = direction + column - end % 10
            # Make sure there's a pawn that can make the move.
            if board[end + direction] in 'pP':
                return (end + direction, end)
            elif abs(direction) == 10 and board[end + 2 * direction] in 'pP':
                return (end + 2 * direction, end)
            else:
                return (None, '{} is not a legal move.'.format(groups[3]))
        # Handle moves with a piece provided (standard algebraic).
        elif match_type in (9, 11, 13):
            piece = groups[0]
            end = sunfish.parse(groups[3])
            # Set up disambiguation.
            if match_type == 11:
                column = ' abcdefgh'.index(groups[1])
            if match_type == 13:
                row = 10 - int(groups[2])
            # Find valid moves with that end and that piece.
            starts = []
            if self.player_index:
                end = 119 - end
            for move in self.position.gen_moves():
                if move[1] == end and self.position.board[move[0]] == piece:
                    # Match and disambiguation.
                    if match_type == 11 and move[0] % 10 != column:
                        continue
                    elif match_type == 13 and move[0] // 10 != row:
                        continue
                    starts.append(move[0])
            # Check for ambiguous moves.
            if len(starts) == 1:
                if self.player_index:
                    return (119 - starts[0], 119 - end)
                else:
                    return (starts[0], end)
            elif not starts:
                return (None, '{} is not a legal move.'.format(text))
            else:
                return (None, '{} is ambiguous.'.format(text))
        # Handle two squares (long algebraic notation).
        elif match_type == 14:
            start = sunfish.parse('{}{}'.format(*groups[1:3]))
            end = sunfish.parse(groups[3])
            return (start, end)
        else:
            return (None, '{} is not a valid algebraic move.'.format(text))

    def parse_fen(self, fen):
        """
        Parse a position from Forsyth-Edwards Notation to Sunfish. (sunfish.Position)

        Note that since parameters in t_games can't contain spaces, this method
        assumes the notation has pipes (|) where normal FEN would have spaces.

        Parameters:
        fen: A position in Forsyth-Edwards Notation. (str)
        """
        # Parse the parts of the FEN string.
        pieces, player, castling, en_passant, half_moves, moves = fen.split('|')
        # Parse the lines of the board.
        lines = ['         \n', '         \n']
        for row in pieces.split('/'):
            line = ' '
            for square in row:
                if square.isdigit():
                    line = '{}{}'.format(line, '.' * int(square))
                else:
                    line = '{}{}'.format(line, square)
            lines.append('{}\n'.format(line))
        lines.extend(['         \n', '         \n'])
        # Join the lines and correct for black to move.
        board = ''.join(lines)
        if player == 'b':
            board = board[::-1].swapcase()
            self.skip_white = True
        # Parse the castling restrictions
        white_castle = ('Q' in castling, 'K' in castling)
        black_castle = ('q' in castling, 'k' in castling)
        # Parse the en pasant square.
        sun_passant = sunfish.parse(en_passant) if en_passant != '-' else 0
        # Set up the position
        position = sunfish.Position(board, 0, white_castle, black_castle, sun_passant, 0)
        # Set the game tracking variables.
        self.draw_turns = int(half_moves)
        self.turns = int(moves) * 2
        return position

    def parse_move(self, text):
        """
        Parse a move into one Sunfish recognizes. (tuple)

        Parameters:
        text: The text version of the move provided by the user. (str)
        """
        text = text.strip() # ?? unneccesary?
        match = self.move_re.match(text)
        castle = self.castle_re.match(text)
        # Check for algebraic moves.
        if match:
            return self.parse_algebraic(text, match)
        # Check for castling moves.
        elif castle:
            if self.player_index:
                start = 29 - self.position.board.index('k') % 10
            else:
                start = self.position.board.index('K')
            if len(text) == 5:
                end = start - 2
            else:
                end = start + 2
            return (start, end)
        # Check for ICCF Numeric notation.
        elif text.isdigit() and len(text) == 4:
            if '0' in text:
                return (None, '{} is not a valid numeric move.'.format(text))
            start = sunfish.parse('{}{}'.format(' abcdefgh'[int(text[0])], text[1]))
            end = sunfish.parse('{}{}'.format(' abcdefgh'[int(text[2])], text[3]))
            return (start, end)
        else:
            return (None, 'I do not understand that move.')

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Handle black going first.
        if self.skip_white and self.player_index == 0:
            self.skip_white = False
            return False
        # Show the position and handle the move.
        player.tell(self)
        move = player.ask('\nWhat is your move? ')
        return self.handle_cmd(move)

    def set_options(self):
        """Set the options for the game. (None)"""
        # Set display options.
        self.option_set.add_option('unicode', ['uni', 'u'],
            question = 'Should the board be displayed in unicode? bool')
        # Board options.
        self.option_set.add_option('black', ['b'],
            question = 'Do you want to play black? bool')
        self.option_set.add_option('white', ['w'],
            question = 'Do you want to play white? bool')
        self.option_set.add_option('fen', ['f'], default = '',
            question = 'Enter the FEN Notation for the position (return for standard start): ')
        self.option_set.add_option('opening', ['open', 'o'], str.lower, '', action = 'map',
            value = self.openings, question = 'Enter the opening to play (return for standard start): ')
        # Set play options.
        self.option_set.add_option('difficulty', ['d'], int, 20,
            question = 'How many tenths of a second should the bot get to think (return for 20)? ')

    def set_up(self):
        """Set up the game. (None)"""
        # Set the tracking variables.
        self.skip_white = False
        self.draw_turns = 0
        # Set up the position
        if self.opening:
            self.position = self.parse_fen(self.opening)
        elif self.fen:
            self.position = self.parse_fen(self.fen)
        else:
            self.position = sunfish.Position(sunfish.initial, 0, (True,True), (True,True), 0, 0)
        # Set the position history.
        self.history = [self.position.board]
        # Reverse black and white each game.
        self.players.reverse()


class SunfishBot(player.Bot):
    """
    A bot for making Sunfish moves. (player.Bot)

    Overridden Methods:
    ask
    set_up
    tell
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        # Handle making moves.
        if prompt == '\nWhat is your move? ':
            move, score = self.searcher.search(self.game.position, secs = self.game.difficulty / 10.0)
            if self.game.player_index:
                move_text = '{}{}'.format(sunfish.render(119 - move[0]), sunfish.render(119 - move[1]))
            else:
                move_text = '{}{}'.format(sunfish.render(move[0]), sunfish.render(move[1]))
            self.game.human.tell("\n{}'s move is {}.".format(self.name, move_text))
            return move_text
        # Handle accepting draws.
        elif prompt.startswith('A draw has been offered'):
            if self.game.position.score > 50:
                return 'da'
            else:
                return 'nope'
        # Handle everything else.
        else:
            return super(SunfishBot, self).ask(prompt)

    def set_up(self):
        """Set up the bot for play. (str)"""
        self.searcher = sunfish.Searcher()

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        pass
