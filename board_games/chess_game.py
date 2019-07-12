# coding=utf-8
"""
chess_game.py

A t_games wrapper for Sunfish by Thomas Ahle.
(https://github.com/thomasahle/sunfish)

Constants:
CREDITS: The credits for Chess. (str)

Classes:
Chess: A t_games wrapper for Sunfish. (game.Game)
SunfishBot: A bot for making Sunfish moves. (player.Bot)
"""


import random
import re

from .. import game
from .. import options
from .. import player
import sunfish


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
square you want to move it to.

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

    I want to be able to accept algebraic notation and ICCF numeric notation, in
    addition to Sunfish's use of coordinate notation. But worry about that after
    I get the basics done. Also allow for positions to be entered in FEN if I have
    time, and Chess960 if I can figure it out. Note that changing A1/H1 will not be
    sufficient for Shuffle Chess. A1 especially is used for other things, like
    parsing moves. I would need to come up with other variables just for castling.
    I think that would go in Position, maybe with a set_shuffle method.

    Note that the Sunfish board is always from the perspective of white. So there
    are a lot of reversals and cases changes of the board and the moves in the code
    for the wrapper. Also, 'if self.player_index' is frequently used as a proxy for
    'if the current player is playing black' in those sections of the code.

    Class Attributes:
    castle_re: A regular expression for castling moves. (re.SRE_Pattern)
    move_re: A regular expression for an algebraic move. (re.SRE_Pattern)
    openings: FEN strings for vailable starting positions. (dict of str: str)
    unicode_pieces: Translation of ascii to unicode for pieces. (dict of str: str)

    Methods:
    board_text: Get the text for a given position. (str)
    do_move: Make a move in the game. (bool)
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
    move_re = re.compile('([a-h])?([1-8])?([bnrqk])?[ -x/]?([a-h][1-8])')
    name = 'Chess'
    openings = {'': '',
        'castle-test': 'r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R|w|KQkq|-|0|1',
        'caro-kann': 'rnbqkbnr/ppp2ppp/2p5/3p4/3PP3/8/RNBQKBNR|w|KQkq|-|0|3',
        'french': 'rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/RNBQKBNR|w|KQkq|-|0|3',
        'indian': 'rnbqkb1r/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR|w|KQkq|-|0|2',
        'italian': 'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R|w|KQkq|-|0|3',
        'pirc': 'rnbqkb1r/3p1n2/8/3PP3/2N5/PPP2PPP/R1BQKBNR|b|KQkq|-|0|3',
        'queens-gambit': 'rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/RNBQKBNR|b|KQkq|-|0|2',
        'ruy-lopez': 'r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R|w|KQkq|-|0|3',
        'sicilian': 'rnbqkbnr/pp1ppppp/8/2p5/4P3/8/RNBQKBNR|w|KQkq|-|0|2'}
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
        lines = ['']
        for row_index, row in enumerate(position.board.split(), start = 1):
            if self.unicode:
                row = [self.unicode_pieces.get(piece, piece) for piece in row]
            if not black:
                row_index = 8 - row_index
            lines.append(' {} {}'.format(row_index, ' '.join(row)))
        if black:
            lines.append('   h g f e d c b a')
        else:
            lines.append('   A B C D E F G H')
        text = '\n'.join(lines)
        if black:
            text = text.swapcase()
        return text

    def default(self, text):
        """
        Handle unrecognized commands. (bool)

        Parameters:
        text: The raw text input by the user. (str)
        """
        if self.move_re.match(text.lower()) or self.castle_re.match(text.lower()):
            return self.do_move(text)
        else:
            return super(Chess, self).default(text)

    def do_move(self, arguments):
        """
        Make a move in the game.

        Currently moves are only accepted in coordinate notation.

        Aliases: m
        """
        player = self.players[self.player_index]
        sun_move = self.parse_move(arguments)
        if sun_move is None:
            player.error('I do not recognize that move. Please use coordinate notation (e2e4).')
            return True
        else:
            if self.player_index:
                sun_move = (119 - sun_move[0], 119 - sun_move[1])
            if sun_move in self.position.gen_moves():
                self.position = self.position.move(sun_move)
                player.tell(self.board_text(self.position.rotate(), self.player_index))
                return False
            else:
                player.error('{} is not a legal move.'.format(arguments))
                return True

    def game_over(self):
        """Determine if the game is over or not. (bool)"""
        if self.position <= -sunfish.MATE_LOWER:
            player = self.players[self.player_index]
            self.human.tell('{} won the game.')
            if player == self.human:
                self.wins_loss_draw = [1, 0, 0]
            else:
                self.wins_loss_draw = [0, 1, 0]
            return True
        else:
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

    def parse_fen(self, fen):
        """
        Parse a position from Forsyth-Edwards Notation to Sunfish. (sunfish.Position)

        Note that since parameters in t_games can't contain spaces, this method
        assumes the notation has pipes (|) where normal FEN would have spaces.

        Parameters:
        fen: A position in Forsyth-Edwards Notation. (str)
        """
        pieces, player, castling, en_passant, half_moves, moves = fen.split('|')
        lines = ['          ', '          ']
        for row in pieces.split('/'):
            line = ' '
            for square in row:
                if square.isdigit():
                    line = '{}{}'.format(line, '.' * int(square))
                else:
                    line = '{}{}'.format(line, square)
            lines.append('{} '.format(line))
        lines.extend(['          ', '          '])
        board = ''.join(lines)
        if player == 'b':
            board = board[::-1].swapcase()
            self.skip_white = True
        white_castle = ('Q' in castling, 'K' in castling)
        black_castle = ('q' in castling, 'k' in castling)
        sun_passant = sunfish.parse(en_passant) if en_passant != '-' else 0
        position = sunfish.Position(board, 0, white_castle, black_castle, sun_passant, 0)
        return position

    def parse_move(self, text):
        """
        Parse a move into one Sunfish recognizes. (str)

        Parameters:
        text: The text version of the move provided by the user. (str)
        """
        text = text.strip().lower()
        match = self.move_re.match(text)
        castle = self.castle_re.match(text)
        if match:
            groups = match.groups()
            match_type = sum(2 ** index for index, group in enumerate(groups) if group is not None)
            if match_type == 11:
                start = sunfish.parse('{}{}'.format(*groups[:2]))
                end = sunfish.parse(groups[3])
                return (start, end)
            else:
                return None
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
        else:
            return None

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        if self.skip_white and self.player_index == 0:
            self.skip_white = False
            return False
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
        self.skip_white = False
        if self.opening:
            self.position = self.parse_fen(self.opening)
        elif self.fen:
            self.position = self.parse_fen(self.fen)
        else:
            self.position = sunfish.Position(sunfish.initial, 0, (True,True), (True,True), 0, 0)
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
        if prompt == '\nWhat is your move? ':
            move, score = self.searcher.search(self.game.position, secs = self.game.difficulty / 10.0)
            if self.game.player_index:
                move_text = '{}{}'.format(sunfish.render(119 - move[0]), sunfish.render(119 - move[1]))
            else:
                move_text = '{}{}'.format(sunfish.render(move[0]), sunfish.render(move[1]))
            self.game.human.tell("\n{}'s move is {}.".format(self.name, move_text))
            return move_text
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
