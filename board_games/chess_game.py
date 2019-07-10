# coding=utf-8
"""
chess_game.py

A t_games wrapper for Sunfish by Thomas Ahle.
(https://github.com/thomasahle/sunfish)

Constants:
CREDITS: The credits for Chess. (str)

Classes:
Chess: A t_games wrapper for Sunfish. (game.Game)
"""


import re

from .. import game
from .. import player
import sunfish


CREDITS = """
Game Design: Traditional
Game Programmming: Thomas Ahle (Sunfish chess engine)
    Craig O'Brien (t_games wrapper for Sunfish)
"""


class Chess(game.Game):
    """
    A t_games wrapper for Sunfish. (game.Game)

    I want to be able to accept algebraic notation and ICCF numeric notation, in
    addition to Sunfish's use of coordinate notation. But worry about that after
    I get the basics done. Also allow for positions to be entered in FEN if I have
    time.

    Note that the Sunfish board is always from the perspective of white. So there
    are a lot of reversals and cases changes of the board and the moves in the code
    for the wrapper. Also, 'if self.player_index' is frequently used as a proxy for
    'if the current player is playing black' in those sections of the code.

    Class Attributes:
    castle_re: A regular expression for castling moves. (re.SRE_Pattern)
    move_re: A regular expression for an algebraic move. (re.SRE_Pattern)
    unicode_pieces: Translation of ascii to unicode for pieces. (dict of str: str)

    Methods:
    do_move: Make a move in the game. (bool)
    parse_move: Parse a move into one Sunfish recognizes. (str)

    Overridden Methods:
    __str__
    default
    game_over
    player_action
    set_options
    set_up
    """

    aliases = {'m': 'move'}
    castle_re = re.compile('o-o(-o)?')
    categories = ['Board Games']
    move_re = re.compile('([a-h])?([1-8])?([bnrqk])?[ -x/]?([a-h][1-8])')
    name = 'Chess'
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
        for row_index, row in enumerate(position.board.split()):
            if self.unicode:
                row = [self.unicode_pieces.get(piece, piece) for piece in row]
            if not black:
                row_index = 7 - row_index
            lines.append(' {} {}'.format(row_index + 1, ' '.join(row)))
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
            self.position = self.position.move(sun_move)
            player.tell(self.board_text(self.position.rotate(), self.player_index))
            return False

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
        self.players = [SunfishBot(), self.human]

    def parse_move(self, text):
        """
        Parse a move into one Sunfish recognizes. (str)

        Parameters:
        text: The text version of the move provided by the user. (str)
        """
        match = self.move_re.match(text.lower())
        groups = match.groups()
        match_type = sum(2 ** index for index, group in enumerate(groups) if group is not None)
        if match_type == 11:
            start = sunfish.parse('{}{}'.format(*groups[:2]))
            end = sunfish.parse(groups[3])
            return (start, end)
        else:
            return None

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        player.tell(self)
        move = player.ask('\nWhat is your move? ')
        return self.handle_cmd(move)

    def set_options(self):
        """Set the options for the game. (None)"""
        self.option_set.add_option('unicode', ['uni', 'u'])

    def set_up(self):
        """Set up the game. (None)"""
        self.position = sunfish.Position(sunfish.initial, 0, (True,True), (True,True), 0, 0)
        self.players.reverse()


class SunfishBot(player.Bot):
    """
    A bot for making Sunfish moves. (player.Bot)

    Overridden Methods:
    ask
    set_up
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        if prompt == '\nWhat is your move? ':
            move, score = self.searcher.search(self.game.position, secs = 2)
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
