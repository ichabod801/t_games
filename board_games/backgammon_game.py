"""
backgammon_game.py

A game of Backgammon and related variants.

Terminology:
    roll: The number on a die.
    move: One roll's move.
    play: A full turn of moves.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
BAR: The index of the bar. (int)
CONTACT_WEIGHTS: Weights for PubEvalBot while there's' contact. (list of float)
CREDITS: The credits for the game. (str)
FRAME_HIGH: The top of the frame for displaying the board. (list of str)
FRAME_LOW: The bottom of the frame for displaying the board. (list of str)
OPTIONS: The options for Backgammon. (str)
OUT: The index for pieces born off the board. (int)
RACE_WEIGHTS: Weights for PubEvalBot while it's a race. (list of float)
RULES: The rules of Backgammon. (str)
START: The index for pieces not yet in the game. (int)

Classes:
BackgammonBot: A bot for a game of Backgammon. (player.bot)
AdditiveBot: A genetic algorithm improvement of BackgammonBot. (BackgammonBot)
BackGeneBot: A Backgammon bot for genetic engineering. (BackgammonBot)
PubEvalBot: A bot based on Gerry Tesauro's pubeval algorithm. (BackgammonBot)
Backgammon: A game of Backgammon. (game.Game)
BackgammonBoard: A board for Backgammon. (board.LineBoard)
BackgammonPlay: A possible play (set of moves) in Backgammon. (object)
"""


from __future__ import print_function

import itertools
import random

from .. import board
from .. import dice
from .. import game
from .. import options
from .. import player
from .. import utility


BAR = -1

CONTACT_WEIGHTS = [.25696, -.66937, -1.66135, -2.02487, -2.53398, -.16092, -1.11725, -1.06654, -.92830,
    -1.99558, -1.10388, -.80802, .09856, -.62086, -1.27999, -.59220, -.73667, .89032, -.38933, -1.59847,
    -1.50197, -.60966, 1.56166, -.47389, -1.80390, -.83425, -.97741, -1.41371, .24500, .10970, -1.36476,
    -1.05572, 1.15420, .11069, -.38319, -.74816, -.59244, .81116, -.39511, .11424, -.73169, -.56074,
    1.09792, .15977, .13786, -1.18435, -.43363, 1.06169, -.21329, .04798, -.94373, -.22982, 1.22737,
    -.13099, -.06295, -.75882, -.13658, 1.78389, .30416, .36797, -.69851, .13003, 1.23070, .40868, -.21081,
    -.64073, .31061, 1.59554, .65718, .25429, -.80789, .08240, 1.78964, .54304, .41174, -1.06161, .07851,
    2.01451, .49786, .91936, -.90750, .05941, 1.83120, .58722, 1.28777, -.83711, -.33248, 2.64983, .52698,
    .82132, -.58897, -1.18223, 3.35809, .62017, .57353, -.07276, -.36214, 4.37655, .45481, .21746, .10504,
    -.61977, 3.54001, .04612, -.18108, .63211, -.87046, 2.47673, -.48016, -1.27157, .86505, -1.11342,
    1.24612, -.82385, -2.77082, 1.23606, -1.59529, .10438, -1.30206, -4.11520, 5.62596, -2.75800]

CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
Bot Programming: Gerry Tesauro
"""

FRAME_HIGH = ['  1 1 1 1 1 1   1 2 2 2 2 2  ', '  3 4 5 6 7 8   9 0 1 2 3 4  ',
    '+-------------+-------------+']

FRAME_LOW = ['+-------------+-------------+', '  1 1 1                      ',
    '  2 1 0 9 8 7   6 5 4 3 2 1  ']

OPTIONS = """
gonzo (gz): Equivalent to 'layout = hyper match = 18'.
layout (l): Which layout to use: long (lg), standard (st), nack (nk), or
    hyper (hy).
match (m): The winning match score. Defaults to 1, or non-match play.
o: The human player plays with the red (O) pieces.
"""

OUT = -2

RACE_WEIGHTS = [0, -.17160, .27010, .29906, -.08471, 0, -1.40375, -1.05121, .07217, -.01351, 0, -1.29506,
    -2.16183, .13246, -1.03508, 0, -2.29847, -2.34631, .17253, .08302, 0, -1.27266, -2.87401, -.07456,
    -.34240, 0, -1.34640, -2.46556, -.13022, -.01591, 0, .27448, .60015, .48302, .25236, 0, .39521, .68178,
    .05281, .09266, 0, .24855, -.06844, -.37646, .05685, 0, .17405, .00430, .74427, .00576, 0, .12392,
    .31202, -.91035, -.16270, 0, .01418, -.10839, -.02781, -.88035, 0, 1.07274, 2.00366, 1.16242, .22520,
    0, .85631, 1.06349, 1.49549, .18966, 0, .37183, -.50352, -.14818, .12039, 0, .13681, .13978, 1.11245,
    -.12707, 0, -.22082, .20178, -.06285, -.52728, 0, -.13597, -.19412, -.09308, -1.26062, 0, 3.05454,
    5.16874, 1.50680, 5.35000, 0, 2.19605, 3.85390, .88296, 2.30052, 0, .92321, 1.08744, -.11696, -.78560,
    0, -.09795, -.83050, -1.09167, -4.94251, 0, -1.00316, -3.66465, -2.56906, -9.67677, 0, -2.77982,
    -7.26713, -3.40177, -12.32252, 0, 3.42040]

RULES = """
Each player starts the game rolling one die, and the higher roll moves using
the two numbers rolled. From then on turns alternate, each player rolling two
dice on their turn. If doubles are rolled, they count double (as four of the
rolled number having been rolled). Doubles rolled at the beginning of the game
are rerolled.

For each number rolled, the player may move one piece that many points (spots
on the board). Each roll may move a different piece or the same piece, as the
player choses. Players move opposite directions, with X moving widdershins
from the top right, and O moving clockwise from the bottom right. The last six
points in a player's moving direction (the bottom right for X, the top right
for O) is called the player's home board or home.

Pieces may not be moved to points containing two or more of the opponent's
pieces. If a piece is moved to a point with only one opponent's piece on it,
the opponent's piece is captured and placed on the bar. If you have piece on
the bar, you must re-enter the piece into your opponent's home before you can
make any other move. A 1 moves it to the furthest point from your own home, a
2 to the next furthest point, and so on. As per normal movement, if the piece
entering lands on a single opponent's piece, the opponent's piece is captured
and put on the bar.

Once all of your pieces are in your home board, you may bear them off,
removing them from the board. This is done similarly to entering from the bar,
with a roll of one removing a piece farthest into your home board, and two
removing a piece next farthest into your home board, and so on. If your roll
is for an empty point, and there are no pieces on higher points, you may bear
off a piece on the highest point lower than the roll. So if you roll a five,
and only have pieces on the three and four points, you may bear a piece off
the four point. The first play to bear all of their pieces off the board wins
the game.

To move, indicate the starting point and ending point. Traditionally this is
done with a slash, as in '13/7', but it can be done with a space or a comma
as well. If the move is unambiguous, you may just use the end point. To enter
a piece from the bar use the enter command (or 'e') and the point you want to
enter onto. To bear a piece off the board, use the bear command (or 'bear off'
or 'b') and the point your want to bear off from (NOT the roll). Using the
bear command without any arguments will automatically bear off pieces, to the
extent that there are obvious bearing off moves. You may repeat a move by
putting the number of times to repeat the move after the move either after
an asterisk (13 7 * 2) or in parentheses (13 7 (2)).

Backgammon is often played in match play, to even out the luck of the dice.
When using match play, a game won when the opponent has not born any pieces
off the board counts double, and a game won when the opponent still has a
piece on the bar counts triple. Furthermore, there is a doubling die that
can be used to double the stakes. At the beginning of their turn, each player
is asked if they want to double the stakes of the game. The other player must
accept the doubled stakes or concede the game. After the initial doubling of
the stakes, control of the doubling die goes to the player who accepted the
doubling of the stakes, and only they can double the stakes again.

You may get both players' pip counts at any time with the pips command.
"""

START = -3


class BackgammonBot(player.Bot):
    """
    A bot for a game of Backgammon. (player.Bot)

    Attributes:
    held_moves: Moves planned but not yet made through ask. (BackgammonPlay)
    piece: The symbol for the bot's pieces on the baord. (str)

    Methods:
    describe_board: Determine the features of the current board layout. (list)
    eval_board: Evaluate a board position. (list of int)
    get_endgame: Get the moves at the end of the game. (BackgammonPlay)
    get_split_move: Get a move when the game has become a race to get home. (str)
    get_stretch_move: Get a move when all my pieces are home. (str)

    Overridden Methods:
    ask
    ask_int_list
    error
    set_up
    tell
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        # Respond to no-move notifications.
        if prompt.startswith('You have no legal moves'):
            roll_text = '-'.join(str(x) for x in self.game.rolls[:2])
            self.game.human.tell('\n{} rolled {} and has no legal moves.'.format(self.name, roll_text))
            return ''
        # Respond to being able to double.
        elif prompt.startswith('\nWould you like to double the stakes'):
            features, points = self.describe_board(self.game.board)
            if self.eval_board(features, 'accept') > 25:
                return '1'
            else:
                return '0'
        # Respond to opponent doubling.
        elif prompt.startswith('\nYour opponent wants to double'):
            features, points = self.describe_board(self.game.board)
            if self.eval_board(features, 'accept') > -25:
                return '1'
            else:
                return '0'
        # Handle pauses in game play.
        elif prompt.startswith('Press Enter'):
            return 'Cowabunga'
        # Respond to be able to double.
        elif prompt.startswith('Would you like to double'):
            features, points = self.describe_board(self.game.board)
            if self.eval_board(features, 'double') > 25:
                return '1'
            else:
                return '0'
        # Raise an error for any other question.
        else:
            raise player.BotError('Unexpected question to BackgammonBot: {}'.format(prompt))

    def ask_int_list(self, prompt, low = None, high = None, valid = [], valid_lens = [], default = None,
        cmd = True):
        """
        Get a multiple integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (list or None)
        high: The highest acceptable value for the integer. (laist or None)
        valid: The valid values for the integer. (list of int)
        valid_lens: The valid numbers of values. (list of int)
        default: The default choice. (list or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        # Respond to move requests.
        if prompt.strip() == 'What is your move?':
            if not self.held_moves:
                # Get the current state of the game.
                board = self.game.board
                features, points = self.describe_board(board)
                my_points = points[self.piece]
                foe_points = points['X' if self.piece == 'O' else 'O']
                # Make end of game moves.
                if max(my_points + [0]) + max(foe_points + [0]) <= 24 and not board[BAR]:
                    self.held_moves = self.get_endgame(board, my_points)
                else:
                    # Evaluate all the legal plays.
                    possibles = []
                    for play in board.get_plays(self.piece, self.game.rolls):
                        # Make the play.
                        sub_board = board.copy()
                        for move in play:
                            capture = sub_board.move(*move, piece = self.piece)
                        # Get the board features.
                        features, points = self.describe_board(sub_board)
                        max_x = max(points['X']) if points['X'] else 0
                        max_o = max(points['O']) if points['O'] else 0
                        # Get the game phase.
                        if max_x + max_o > 24 or sub_board[BAR]:
                            phase = 'mixed'
                        elif max_x <= 6 and max_o < 6:
                            phase = 'stretch'
                        else:
                            phase = 'split'
                        # Store the evaluation with the move.
                        possibles.append((self.eval_board(features, phase), play))
                    # Choose the play with the highest evaluation.
                    possibles.sort(reverse = True)
                    self.held_moves = possibles[0][1]
                self.tell_move()
            # Return the move with the correct syntax.
            move = self.held_moves.next_move()
            if move[1] == OUT:
                # Return bearing of the board syntax.
                point = move[0]
                if point > 6:
                    point = 25 - point
                return 'bear {}'.format(point)
            elif move[0] == BAR:
                # Return entering the board syntax.
                point = move[1]
                if point > 6:
                    point = 25 - point
                return 'enter {}'.format(point)
            else:
                # Return an integer list for standard moves.
                return move[:2]
        # Raise an error for any other question.
        else:
            raise player.BotError('Unexpected question to BackgammonBot: {}'.format(prompt))

    def calculate_hits(self, board, blots):
        """
        Calculate the possible captures in the given position. (tuple of dict)

        The return value is two dictionaries, one with the direct hits and one with the
        indirect hits. Each is keyed by the piece symbol that would be captured.

        Paramters:
        board: The position being checked. (BackgammonBoard)
        blots: The vulnerable positions for each piece. (dict of str: list)
        """
        direct_hits = {'X': 0, 'O': 0}
        indirect_hits = {'X': 0, 'O': 0}
        for piece in 'XO':
            # Get info about your opponent's moves.
            foe_direction = {'X': -1, 'O': 1}[piece]
            foe_piece = {'X': 'O', 'O': 'X'}[piece]
            # Go through all of your blots.
            for blot in blots[piece]:
                # Go through all possible capture starts.
                for offset in range(1, 13):
                    # Make sure start is on the board.
                    try:
                        offcell = board.offset(blot, offset * foe_direction)
                    except KeyError:
                        break
                    # Classify possibles as direct or indirect.
                    if foe_piece in offcell:
                        if offset < 7:
                            direct_hits[piece] += 1
                        if offset > 1:
                            # Only count indirect hits that aren't blocked.
                            for die in range(1, offset - 1):
                                subcell = board.offset(blot, die * foe_direction)
                                if subcell[:2] != [self.piece, self.piece]:
                                    indirect_hits[piece] += 1
        return direct_hits, indirect_hits

    def describe_board(self, board):
        """
        Determine the features of the current board layout. (list of int)

        The evaluation is a list of integers. This can be used on it's own or as
        input to another evaluation function.

        The items in the evaluation list are (in order):
            * The difference in the number of captured pieces.
            * The difference in the number of pieces born off the board.
            * The difference in the number of blots.
            * The difference in direct hits to blots.
            * The difference in probability of indirect hits to blots.
            * The difference in pip count.
            * The difference in the farthest piece from being born off.
            * The difference in the number of controlled points.
        All are calculated so that higher numbers are better for the bot.

        Parameters:
        board: A board with the position to evaluate. (BackgammonBoard)
        """
        # Find controlled and blot points.
        controlled = {'X': [], 'O': []}
        blots = {'X': [], 'O': []}
        for cell in board.values():
            if cell.location < 0:
                continue
            if len(cell) > 1:
                controlled[cell[0]].append(cell.location)
            elif len(cell) == 1:
                blots[cell[0]].append(cell.location)
        # Get all the points for each player.
        points = {piece: controlled[piece] + blots[piece] for piece in 'XO'}
        points['O'] = [25 - point for point in points['O']]
        # Count the off board pieces.
        captured = {piece: board[BAR].count(piece) for piece in 'XO'}
        off = {piece: board[OUT].count(piece) for piece in 'XO'}
        # Get the pip counts and furthest piece from home.
        pip_count = {piece: board.get_pip_count(piece) for piece in 'XO'}
        max_pip = {}
        for piece in 'XO':
            if captured[piece]:
                max_pip[piece] = 25
            if points[piece]:
                max_pip[piece] = max(points[piece])
            else:
                max_pip[piece] = 0
        # Calculate hits.
        direct_hits, indirect_hits = self.calculate_hits(board, blots)
        # Get list of score factors.
        my_piece = self.game.pieces[self.name]
        foe_piece = {'X': 'O', 'O': 'X'}[my_piece]
        score = [captured[foe_piece] - captured[my_piece]]
        score.append(off[my_piece] - off[foe_piece])
        score.append(len(blots[foe_piece]) - len(blots[my_piece]))
        score.append(direct_hits[foe_piece] - direct_hits[my_piece])
        score.append(indirect_hits[foe_piece] - indirect_hits[my_piece])
        score.append(pip_count[foe_piece] - pip_count[my_piece])
        score.append(max_pip[foe_piece] - max_pip[my_piece])
        score.append(len(controlled[my_piece]) - len(controlled[foe_piece]))
        return score, points

    def error(self, *args, **kwargs):
        """
        Warn the player about an invalid play. (None)

        Parameters:
        The parameters are as the built-in print function.
        """
        # Old print lining from development of the bot.
        board = self.game.board
        human = self.game.human
        human.tell('\nERROR INFO\n')
        human.tell(board.get_text(self.piece))
        human.tell(board.get_plays(self.piece, self.game.rolls))
        # Raise the error.
        super(BackgammonBot, self).error(*args, **kwargs)

    def eval_board(self, board_features, phase):
        """
        Evauluate a board position based on phase of play. (int or list)

        For doubling checks, an binary integer is returned (accept/double or not).
        Otherwise, it returns the board_features.

        Parameters:
        board_features: The summary of the board position. (list of int)
        phase: The current phase of play, or what is being asked of the bot. (str)
        """
        # Get the pip counts.
        my_pips = self.game.board.get_pip_count(self.piece)
        their_pips = self.game.board.get_pip_count({'X': 'O', 'O': 'X'}[self.piece])
        # Check for doubling.
        if phase == 'double':
            if their_pips > 8 and my_pips / their_pips < 0.75:
                return 1
            else:
                return 0
        # Check for accepting a double.
        elif phase == 'accept':
            if their_pips > 8 and my_pips / their_pips < 1.33:
                return 1
            else:
                return 0
        # Check for normal play.
        else:
            return board_features

    def get_endgame(self, board, my_points):
        """
        Get the moves at the end of the game. (BackgammonPlay)

        Parameters:
        board: The current board position. (BackgammonBoard)
        my_points: The points the bot's pieces are on. (list of int)
        """
        # Copy the game state.
        board = board.copy()
        rolls = self.game.rolls[:]
        # Put the moves into a play.
        play = BackgammonPlay()
        while rolls:
            # Get the right move for the phase.
            if max(my_points) < 7:
                play.add_move(*self.get_stretch_move(board, my_points, rolls))
            else:
                play.add_move(*self.get_split_move(board, my_points, rolls))
            # Update the game tracking.
            features, points = self.describe_board(board)
            my_points = points[self.piece]
            # Check for all of my pieces being of the board.
            if not my_points:
                break
        return play

    def get_split_move(self, board, my_points, rolls):
        """
        Get a move when the game has become a race to get home. (str)

        Parameters:
        board: The current position. (BackBoard)
        my_points: The points where the bot has a piece. (list of int)
        rolls: The rolls available for moves. (list of int)
        """
        # Get the next roll to move.
        max_roll = max(rolls)
        # If you can get a piece home exactly, do it.
        if max_roll + 6 in my_points:
            move = [max_roll + 6, 6]
        # Otherwise get your farthest piece closer.
        else:
            my_max = max(my_points)
            move = [my_max, my_max - max_roll]
        # Convert the points if necessary.
        if self.piece == 'O':
            move = [25 - point for point in move]
        # Make the move
        board.move(move[0], move[1], self.piece)
        rolls.remove(max_roll)
        return move + [max_roll]

    def get_stretch_move(self, board, my_points, rolls):
        """
        Get a move when all my pieces are home. (str)

        Parameters:
        board: The current position. (BackBoard)
        my_points: The points where the bot has a piece. (list of int)
        rolls: The rolls available for moves. (list of int)
        """
        # Get the next roll to move.
        max_roll = max(rolls)
        # Check for bearing.
        if max_roll in my_points:
            move = [max_roll, OUT]
        elif max_roll > max(my_points):
            move = [max(my_points), OUT]
        else:
            # If you can't bear, fill empty spots.
            for point in sorted(my_points, reverse = True):
                if max_roll < point and point - max_roll not in my_points:
                    move = [point, point - max_roll]
                    break
            else:
                my_max = max(my_points)
                move = [my_max, my_max - max_roll]
        # Convert the points if necessary.
        if self.piece == 'O':
            move[0] = 25 - move[0]
            if move[1] > 0:
                move[1] = 25 - move[1]
        # Make the move
        board.move(move[0], move[1], self.piece)
        rolls.remove(max_roll)
        return move + [max_roll]

    def set_up(self):
        """Set up the bot. (None)"""
        self.held_moves = BackgammonPlay()
        self.piece = self.game.pieces[self.name]

    def tell(self, text):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        pass

    def tell_move(self):
        """Tell the human player what the bot's move is."""
        self.game.human.tell("\n{}'s move is {}".format(self.name, self.held_moves))


class AdditiveBot(BackgammonBot):
    """
    A genetic algorithm improvement of BackgammonBot. (BackgammonBot)

    Attributes:
    vectors: The weights for evaluating positions in different phases. (dict)

    Overridden Methods:
    __init__
    eval_board
    """

    def __init__(self, taken_names = []):
        """
        Set up the bot. (None)

        Parameters:
        taken_names: The names already in use by other players. (list of str)
        """
        super(AdditiveBot, self).__init__(taken_names = taken_names)
        self.vectors = {}
        self.vectors['mixed'] = [7, 42, 92, 17, 87, 93, 29, 66]
        self.vectors['split'] = [4, 12, 22, 23, 30, 41, 57, 8]
        self.vectors['stretch'] = [98, 26, 15, 64, 88, 86, 100, 78]
        self.vectors['double'] = [-70, 52, 28, -83, 11, 93, -76, -67]
        self.vectors['accept'] = [-28, 46, 79, 37, 30, 17, -69, 32]

    def eval_board(self, board_features, phase):
        """
        Evauluate a board position based on phase of play. (int)

        Parameters:
        board_features: The summary of the board position. (list of int)
        phase: The current phase of play, or what is being asked of the bot. (str)
        """
        return sum([f * r for f, r in zip(self.vectors[phase], board_features)])


class BackGeneBot(BackgammonBot):
    """
    A Backgammon bot for genetic engineering. (BackgammonBot)

    Class Attributes:
    phases: The different phases of the game. (list of str)

    Overridden Methods:
    __init__
    eval_board
    tell
    """

    phases = ['mixed', 'split', 'stretch', 'double', 'accept']

    def __init__(self, taken_names = [], mother = None, father = None):
        """
        Set up the bot. (None)

        Parameters:
        taken_names: The names already in use by other players. (list of str)
        mother: The bot's mother. (BackGeneBot or None)
        father: The bot's father. (BackGeneBot or None)
        """
        # Do the base initialization.
        super(BackGeneBot, self).__init__(taken_names = taken_names)
        # Set up the vectors of weights.
        self.vectors = {}
        if mother is None:
            # No mother means a randomly generated bot.
            for phase in self.phases:
                if phase in ('double', 'accept'):
                    self.vectors[phase] = [random.randint(-100, 100) for dummy in range(8)]
                else:
                    self.vectors[phase] = [random.randint(0, 100) for dummy in range(8)]
        else:
            # Otherwise, randomly select weights from the mother and father.
            for phase in self.phases:
                pairs = zip(mother.vectors[phase], father.vectors[phase])
                self.vectors[phase] = [random.choice(pair) for pair in pairs]

    def eval_board(self, board_features, phase):
        """
        Evauluate a board position based on phase of play. (int)

        Parameters:
        board_features: The summary of the board position. (list of int)
        phase: The current phase of play, or what is being asked of the bot. (str)
        """
        return sum([f * r for f, r in zip(self.vectors[phase], board_features)])

    def tell_move(self):
        """Tell the human player what the bot's move is."""
        pass


class PubEvalBot(BackgammonBot):
    """
    A Backgammon bot based on Gerry Tesauro's pubeval algorithm. (BackgammonBot)

    This is a linear weights system. There are five weights for each point on the
    board, each one for a different number of pieces being on the point. There are
    also two sets of weights: one for a race situation, and one for when contact
    is still possible.

    Methods:
    get_position: Generate a pubeval position vector for a board. (list of int)
    pub_eval: Backgammon board evaluation function. (float)
    set_vector: Creates an input vector based on the position. (list of int)

    Overridden Methods:
    ask
    ask_int_list
    eval_board
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        # Respond to no-move notifications.
        if prompt.startswith('You have no legal moves'):
            roll_text = '-'.join(str(x) for x in self.game.rolls[:2])
            self.game.human.tell('\n{} rolled {} and has no legal moves.'.format(self.name, roll_text))
            return ''
        # Respond to being able to double.
        elif prompt.startswith('\nWould you like to double the stakes'):
            if self.eval_board(self.game.board.copy()) > 25:
                return '1'
            else:
                return '0'
        # Respond to doubling requests.
        elif prompt.startswith('\nYour opponent wants to double'):
            if self.eval_board(self.game.board.copy()) < -25:
                return '1'
            else:
                return '0'
        # Handle pauses in game play.
        elif prompt.startswith('Press Enter'):
            return 'Bazinga'
        # Raise an error for any other question.
        else:
            raise ValueError('Unexpected question to PubEvalBot: {}'.format(prompt))

    def ask_int_list(self, prompt, low = None, high = None, valid = [], valid_lens = [], default = None,
        cmd = True):
        """
        Get a multiple integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (list or None)
        high: The highest acceptable value for the integer. (laist or None)
        valid: The valid values for the integer. (list of int)
        valid_lens: The valid numbers of values. (list of int)
        default: The default choice. (list or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        # Respond to move requests.
        if prompt.strip() == 'What is your move?':
            if not self.held_moves:
                # Evaluate all the legal plays.
                possibles = []
                board = self.game.board
                for play in board.get_plays(self.piece, self.game.rolls):
                    sub_board = board.copy()
                    for move in play:
                        capture = sub_board.move(*move, piece = self.piece)
                    possibles.append((self.eval_board(board), play))
                # Choose the play with the highest evaluation.
                possibles.sort(reverse = True)
                self.held_moves = possibles[0][1]
                self.tell_move()
            # Return the move with the correct syntax.
            move = self.held_moves.next_move()
            if move[1] == OUT:
                # Return bearing off syntax.
                point = move[0]
                if point > 6:
                    point = 25 - point
                return 'bear {}'.format(point)
            elif move[0] == BAR:
                # Return entering the board syntax.
                point = move[1]
                if point > 6:
                    point = 25 - point
                return 'enter {}'.format(point)
            else:
                # Return integer list for standard moves.
                return move[:2]
        # Raise an error for any other question.
        else:
            raise ValueError('Unexpected question to BackgammonBot: {}'.format(prompt))

    def eval_board(self, board):
        """
        Evaluate a board position. (float)

        Parameters:
        board: The board to evaluate. (BackgammonBoard)
        """
        # Get the board vector.
        position = self.get_position(board)
        left, right, = [], []
        for index, men in enumerate(position[1:25]):
            if men < 0:
                left.append(abs(men))
            elif men > 0:
                right.append(men)
        try:
            race = max(left) > min(right)
        except ValueError:
            race = True
        return self.pub_eval(race, position)

    def get_position(self, board):
        """
        Generate a pubeval position vector for a board. (list of int)

        The position list is as follows:
            * 0: Opponents men on bar.
            * 1-24: Board positons 1-24 from bot's perspective.
            * 25: Bot's men on bar.
            * 26: Bot's men off board.
            * 27: Opponent's men off board.
        The bot's men are represented by positive integers, the opponent's men are
        always represented by negative integers, even in slots 0 and 27.

        Parameters:
        board: The board to vectorize. (BackgammonBoard)
        """
        # Set up the loop.
        foe_piece = {'X': 'O', 'O': 'X'}[self.piece]
        position = [board[BAR].count(foe_piece) * -1]
        points = []
        # Loop through the locations.
        for location in range(1, 24):
            pieces = board[location]
            value = len(pieces)
            # Your pieces are positive, theirs are negative.
            if self.piece not in pieces:
                value *= -1
            points.append(value)
        # Revers the board positions as necessary.
        if self.piece == 'O':
            points.reverse()
        # Fill out the positions.
        position.extend(points)
        position.append(board[BAR].count(self.piece))
        position.append(board[OUT].count(self.piece))
        position.append(board[OUT].count(foe_piece) * -1)
        return position

    def pub_eval(self, race, position):
        """
        Backgammon board evaluation function. (float)

        Parameters:
        race: A flag for a race position. (bool)
        position: A board position. (list of int)
        """
        # Check for a win.
        if position[26] == 15:
            return utility.MAX_INT
        # Get the vector.
        vector = self.set_vector(position)
        # Get the weights.
        if race:
            weights = RACE_WEIGHTS
        else:
            weights = CONTACT_WEIGHTS
        # apply the weights.
        score = [v * w for v, w in zip(vector, weights)]
        return sum(score)

    def set_vector(self, position):
        """
        Creates an input vector based on the position. (list of int)

        Parameters:
        position: A board position. (list of int)
        """
        vector = [0] * 122
        # Encode board positions.
        for point in range(1, 25):
            men = position[25 - point]
            if men:
                if men == -1:
                    vector[5 * point - 5] = 1
                elif men == 1:
                    vector[5 * point - 4] = 1
                elif men >= 2:
                    vector[5 * point - 3] = 1
                    if men == 3:
                        vector[5 * point - 2] = 1
                    elif men >= 4:
                        vector[5 * point - 1] = (men - 3) / 2
        # Encode foes on bar.
        vector[120] = position[0] / -2
        # Encode friends off.
        vector[121] = position[26] / 15
        return vector


class Backgammon(game.Game):
    """
    A game of Backgammon. (game.Game)

    See BackgammonBoard for the details of the layout attribute.

    Class Attributes:
    layouts: Different possible starting layouts. (dict of str: tuple)

    Attributes:
    board: The board the game is played on. (board.DimBoard)
    bot: The bot that the human is playing against. (player.Bot)
    dice: The dice that are rolled to determine moves. (dice.Pool)
    doubling_die: The die recording the match score for the game. (int)
    doubling_status: Who can double the die. (str)
    human_piece: The symbol for the human's pieces. (str)
    layout: The name of the starting layouts, with aliases. (str)
    match: The winning match score. (int)
    pieces: The symbols for the players' pieces. (dict of str: str)
    rolls: The numbers that can be used to move. (list of int)

    Methods:
    auto_bear: Bear pieces automatically. (bool)
    check_win: Check to see if a given player has won. (int)
    do_bear: Bear a piece of the board. (bool)
    do_enter: Bring a piece back into play from the bar. (bool)
    do_pips: Show the pip counts. (bool)
    double: Check if the user can/wants to double. (bool)
    get_rolls: Determine the rolls you can move with from the dice roll. (None)
    get_start: Get the start of a move only specified by the end. (int)
    get_totals: Get all the possible total rolls. (dict of int: list of int)
    reset: Reset the game state during match play. (None)
    validate_move: Check for a valid move. (bool)
    win_count: The number of pieces needed to bear off for a win. (int)

    Overridden Methods:
    default
    game_over
    player_action
    set_options
    set_up
    """

    aka = ['Back']
    aliases = {'b': 'bear', 'd': 'double', 'e': 'enter', 'p': 'pips', 's': 'start'}
    categories = ['Board Games']
    credits = CREDITS
    layouts = {'hyper': ((24, 1), (23, 1), (22, 1)), 'hy': ((24, 1), (23, 1), (22, 1)), 'long': ((24, 15),),
        'lg': ((24, 15),), 'nack': ((6, 4), (8, 3), (13, 4), (23, 2), (24, 2)),
        'nk': ((6, 4), (8, 3), (13, 4), (23, 2), (24, 2)), 'standard': ((6, 5), (8, 3), (13, 5), (24, 2)),
        'st': ((6, 5), (8, 3), (13, 5), (24, 2))}
    name = 'Backgammon'
    num_options = 3
    options = OPTIONS
    rules = RULES

    def auto_bear(self, player, piece):
        """
        Bear pieces automatically. (bool)

        Parameters:
        player: The player to bear pieces for (player.Player)
        piece: The piece to bear off. (str)
        """
        # Assume the turn will continue.
        unchanged = object()
        go = unchanged
        # Get the rolls needed for the points the player is on.
        player_points = [point for point, cell in self.board.items() if piece in cell]
        if piece == 'O':
            player_points = [25 - point for point in player_points if point > 0]
        # Loop through the rolls.
        for roll in sorted(self.rolls, reverse = True):
            max_player = max(player_points)
            # Ensure exact matches bear.
            if roll in player_points:
                max_player = roll
            # Get the board's perspective from the player's perspective.
            if piece == 'O':
                max_board = 25 - max_player
            else:
                max_board = max_player
            # Bear a piece if you can.
            if roll >= max_player:
                self.rolls.remove(roll)
                self.board.move(max_board, OUT)
                # Check for the point still being valid.
                if not self.board[max_board]:
                    player_points.remove(max_player)
                    # Check for the game being over.
                    if not player_points:
                        break
                go = self.rolls
        # Warn if no successful moves were made.
        if go is unchanged:
            player.error('There are no pieces that can be auto-built.')
        return go

    def check_win(self, piece):
        """
        Check to see if a given player has won. (int)

        The return value is the match score of the win (0 for no win yet).

        Parameters:
        piece: The piece used by the player being checked. (str)
        """
        other_piece = 'O' if piece == 'X' else 'X'
        result = 0
        # Check for win.
        if self.board[OUT].count(piece) == self.win_count:
            result = self.doubling_die
            # Check for gammon/backgammon.
            if other_piece not in self.board[OUT]:
                if piece == 'X':
                    home = range(1, 7)
                else:
                    home = range(19, 25)
                home_pieces = sum([self.board[point] for point in home], [])
                if other_piece in self.board[BAR] or other_piece in home_pieces:
                    self.human.tell('\nBackgammon!')
                    result *= 3
                else:
                    self.human.tell('\nGammon!')
                    result *= 2
        return result

    def default(self, line):
        """
        Handle unrecognized commands. (bool)

        Parameters:
        text: The raw text input by the user. (str)
        """
        # Set up the check.
        player = self.current_player
        count = 0
        # Check for multiplication notation.
        if '*' in line:
            move, symbol, count = line.partition('*')
        # Check for standard notation.
        if line.endswith(')'):
            move, symbol, count = line[:-1].partition('(')
        # Try to parse if any notation fournd.
        if count:
            try:
                self.current_player.held_inputs = [move.strip()] * int(count) + player.held_inputs
                return True
            except ValueError:
                pass
        # Warn the user on unknown or incorrect notation.
        player.error('I do not understand that move.')
        return True

    def do_bear(self, argument):
        """
        Bear a piece off of the board.

        The argument is the pieces to bear, a space delimited list of numbers. The
        numbers should be the points of the pieces to bear, not the die rolls used to
        bear them. The computer will figure out the numbers to use.

        If bear is used without arguments, it will bear whatever pieces it can, but it
        will not move pieces to make them bearable.
        """
        # Get the current player.
        player = self.current_player
        piece = self.pieces[player.name]
        # Convert the arguments.
        words = argument.split()
        if words and words[0].lower() == 'off':
            words = words[1:]
        try:
            bears = [int(word) for word in words]
        except ValueError:
            # Warn on bad arguments.
            player.error('Invalid argument to the bear command: {}.'.format(argument))
            return True
        points = [loc for loc, cell in self.board.items() if piece in cell and loc > 0]
        # Check for all pieces in the player's home.
        if (piece == 'X' and max(points) > 6) or (piece == 'O' and min(points) < 19):
            player.error('You do not have all of your pieces in your home yet.')
        # Check for captured piece.
        elif piece in self.board[BAR]:
            player.error('You still have a piece on the bar.')
        else:
            # Check for automatic bearing
            if not bears:
                return self.auto_bear(player, piece)
            # Play any legal moves.
            for bear in bears:
                # Get the correct point.
                roll = bear
                if piece == 'O':
                    bear = 25 - bear
                # Check for a valid point.
                if piece not in self.board[bear]:
                    player.error('You do not have a piece on the {} point.'.format(roll))
                    continue
                # Remove the correct roll.
                elif roll in self.rolls:
                    self.rolls.remove(roll)
                elif (piece == 'X' and bear < max(points)) or (piece == 'O' and bear > min(points)):
                    # Warn for over roll with an under piece.
                    player.error('You must clear the pieces above the {} point first.'.format(roll))
                    break
                elif roll < max(self.rolls):
                    self.rolls.remove(max(self.rolls))
                else:
                    # Warn for no valid roll.
                    player.error('You need a higher roll to bear from the {} point.'.format(roll))
                    break
                # Bear off the piece
                self.board.move(bear, OUT)
                if not self.board[bear]:
                    points.remove(bear)
        # Continue the turn if there are still rolls to move.
        return self.rolls

    def do_enter(self, argument):
        """
        Bring a piece back into play from the bar.

        The argument is a single integer, representing the die number used to enter
        the piece into your opponent's home.
        """
        # Get the current piece.
        piece = self.pieces[self.current_player.name]
        # Convert the arguments.
        try:
            needed_roll = int(argument)
        except ValueError:
            self.current_player.error('Invalid argument to the enter command: {!r}.'.format(argument))
            return True
        point = needed_roll
        if piece == 'X':
            point = 25 - point
        # Check for valid roll.
        if needed_roll not in self.rolls:
            self.current_player.error('You need to roll a {} to enter on that point.'.format(needed_roll))
            return True
        # Check for a piece to enter.
        elif piece not in self.board[BAR]:
            self.current_player.error('You do not have a piece on the bar.')
            return True
        # Check for a valid entry point.
        end_cell = self.board[point]
        if piece not in end_cell and len(end_cell) > 1:
            self.current_player.error('That point is blocked.')
            return True
        # Make the move.
        capture = self.board.move(BAR, point, piece)
        self.rolls.remove(needed_roll)
        return self.rolls

    def do_gipf(self, arguments):
        """
        Connect Four allows you to move a piece vertically.

        Hearts gives you a free turn if you rolled a non-double less than seven.
        """
        game, losses = self.gipf_check(arguments, ('connect four', 'hearts'))
        go = True
        # Check for Connect Four edge.
        if game == 'connect four':
            if not losses:
                # Get the current piece.
                piece = self.pieces[self.current_player.name]
                # Remind the player of the board state.
                self.current_player.tell(self.board.get_text(piece))
                while True:
                    # Get a point.
                    query = '\nPick a point to move a piece verically from: '
                    point = self.current_player.ask_int(query, low = 1, high = 24)
                    target = 25 - point
                    # Validate the point.
                    if piece not in self.board[point]:
                        self.current_player.tell('You do not have a piece on that point.')
                    elif len(self.board[target]) > 2 and piece not in self.board[target]:
                        self.current_player.tell('You could not move a piece to that square normally.')
                    else:
                        break
                # Make the move.
                self.board.move(point, target, piece)
                go = False
        # Hearts gets you a free turn if your roll sucked.
        if game == 'hearts':
            if not losses:
                roll = self.dice.values[:]
                if roll[0] != roll[1] and sum(roll) < 7:
                    self.free_turn = True
        # I'm confused.
        else:
            self.current_player.tell("I'm sorry, I didn't catch that.")
        return go

    def do_pips(self, argument):
        """
        Show the pip counts for the two players.
        """
        # Show the pip counts.
        self.current_player.tell('\nX:', self.board.get_pip_count('X'))
        self.current_player.tell('O:', self.board.get_pip_count('O'))
        # Keep playing
        return True

    def double(self, player, piece):
        """
        Check for doubling the stakes of the game.

        Parameters:
        player: The current player. (player.Player)
        piece: The current player's piece symbol. (str)
        """
        # Check for valid doubling.
        if self.doubling_status in ('', piece):
            # Ask for a double.
            query = '\nWould you like to double the stakes from {} to {} (return to roll)? '
            double = player.ask(query.format(self.doubling_die, self.doubling_die *2))
            if double.lower() not in utility.YES:
                return True
            # See if the opponent accepts.
            opponent = self.players[1 - self.player_index]
            opponent.tell(self.board.get_text(self.pieces[opponent.name]))
            query = '\nYour opponent wants to double the stakes to {}. Do you accept the new stakes? '
            accept = opponent.ask(query.format(self.doubling_die * 2))
            if accept.lower() in utility.YES:
                # Process acceptance
                self.doubling_die *= 2
                self.doubling_status = 'O' if piece == 'X' else 'X'
                message = '\n{} accepts the double, the doubling die is now at {}.'
                player.tell(message.format(opponent.name, self.doubling_die))
            else:
                # Process rejection.
                player.tell('\n{} refuses the double, you win the game.'.format(opponent.name))
                # Set the match score.
                self.scores[player.name] += self.doubling_die
                # Check for the end of the match (or reset for the next game).
                if self.scores[self.human.name] >= self.match:
                    self.force_end = 'win'
                elif self.scores[self.bot.name] >= self.match:
                    self.force_end = 'loss'
                else:
                    self.reset()
                # Update the human on the match status.
                match_score = self.scores[self.human.name], self.scores[self.bot.name]
                self.human.tell('\nThe match score is now {} to {}.'.format(*match_score))
                if self.force_end == 'win':
                    self.human.tell('You won the match. :)'.format(self.force_end))
                elif self.force_end:
                    self.human.tell('You lost the match. :(')
                else:
                    self.human.ask('Press Enter to continue: ')
                return False
        return True

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # Check human win.
        human_win = self.check_win(self.pieces[self.human.name])
        if human_win:
            self.scores[self.human.name] += human_win
            if self.scores[self.human.name] >= self.match:
                self.win_loss_draw[0] = 1
            self.human.tell('\nYou win!')
        # Check bot win.
        bot_win = self.check_win(self.pieces[self.bot.name])
        if bot_win:
            self.scores[self.bot.name] += bot_win
            if self.scores[self.bot.name] >= self.match:
                self.win_loss_draw[1] = 1
            self.human.tell('\nYou lose. :(')
        # Reset the game.
        if (human_win or bot_win) and self.match > 1:
            scores = self.scores[self.human.name], self.scores[self.bot.name]
            self.human.tell('The match score is {} to {}.'.format(*scores))
            self.reset()
        return max(self.scores.values()) >= self.match

    def get_rolls(self):
        """Determine the rolls you can move with from the dice roll. (None)"""
        self.rolls = self.dice.values[:]
        if self.rolls[0] == self.rolls[1]:
            self.rolls.extend(self.rolls)

    def get_start(self, end, direction, player, player_piece):
        """
        Get the start of a move only specified by the end. (int)

        Parameters:
        end: The end of the move (int)
        direction: The direction of the move. (int)
        player: The player moving. (player.Player)
        player_piece: The symbol for the player moving. (str)
        """
        # Get all possible moves to the given end point.
        all_totals = self.get_totals()
        possible = []
        for maybe in all_totals:
            start = end - maybe * direction
            # Check for valid standard move.
            if player_piece in self.board.get(start, []):
                # Check for blocked move, checking all possible move orders.
                for move_order in itertools.permutations(all_totals[maybe]):
                    point = start
                    # Check each step for being blocked.
                    for roll in move_order:
                        point += roll * direction
                        point_pieces = self.board[point].contents
                        if point_pieces and point_pieces[0] != player_piece and len(point_pieces) > 1:
                            break
                    else:
                        possible.append(start)
                        break
            # Check for valid enter move.
            if (start == 25 and direction == -1) or (start == 0 and direction == 1):
                if player_piece in self.board[BAR]:
                    possible.append(BAR)
        # Only return valid single moves.
        if len(possible) == 1:
            return possible[0]
        # Warn the user about invalid moves.
        elif len(possible) > 1:
            player.error('That move is ambiguous.')
            return -99
        else:
            player.error('There is no legal move to that point.')
            return -99

    def get_totals(self):
        """Get all the possible total rolls. (dict of int: list of int)"""
        # Get the single die totals.
        totals = {roll: [roll] for roll in self.rolls}
        num_rolls = len(self.rolls)
        if num_rolls > 1:
            if self.rolls[0] == self.rolls[1]:
                # Add the multiples of paired dice.
                for count in range(2, num_rolls + 1):
                    totals[self.rolls[0] * count] = [self.rolls[0]] * count
            else:
                # Add the sum of two dice.
                totals[sum(self.rolls)] = self.rolls[:]
        return totals

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Get the player.
        player_piece = self.pieces[player.name]
        # Show the board.
        player.tell(self.board.get_text(player_piece))
        # Roll the dice if it's the start of the turn.
        if not self.rolls:
            # Check for doubling.
            if max(self.scores.values()) + self.doubling_die < self.match:
                accepted = self.double(player, player_piece)
                if not accepted:
                    return False
            # Roll the dice.
            self.dice.roll()
            self.dice.sort()
            self.get_rolls()
            if self.turns > 500:
                self.force_end = 'win'
        player.tell('\nThe roll to you is {}.'.format(', '.join([str(x) for x in self.rolls])))
        # Check for no legal moves
        legal_plays = self.board.get_plays(player_piece, self.rolls)
        if not legal_plays:
            if self.board[OUT].count(player_piece) != self.win_count:
                player.ask('You have no legal moves. Press enter to continue: ')
            self.rolls = []
            return False
        legal_moves = set()
        for play in legal_plays:
            for move in play:
                legal_moves.add(move)
        # Get the player's move.
        move = player.ask_int_list('\nWhat is your move? ', low = 1, high = 24, valid_lens = [1, 2])
        if isinstance(move, str):
            return self.handle_cmd(move)
        direction = -1 if player_piece == 'X' else 1
        # Convert moves with just the end point.
        if len(move) == 1:
            start, end = self.get_start(move[0], direction, player, player_piece), move[0]
            # Handle invalid starts.
            if start == -99:
                return True
            # Handle starts from the bar.
            elif start == BAR:
                if end > 6:
                    end = 25 - end
                return self.do_enter(end)
        else:
            start, end = move
        # Check for valid move and get the steps to take.
        rolls = self.validate_move(start, end, direction, legal_moves, player, player_piece)
        if rolls:
            # Make each step of the roll.
            for roll in rolls:
                sub_end = start + roll * direction
                capture = self.board.move(start, sub_end)
                self.rolls.remove(roll)
                start = sub_end
        else:
            return True
        # Continue if there are still rolls to handle.
        if not self.rolls and self.free_turn:
            self.player_index -= 1
            self.free_turn = False
        return self.rolls

    def reset(self):
        """Reset the game state during match play. (None)"""
        # Set up the board.
        self.board = BackgammonBoard(24, layout = self.layout)
        # Set up the dice.
        self.doubling_die = 1
        self.doubling_status = ''
        self.dice = dice.Pool()
        while self.dice.values[0] == self.dice.values[1]:
            self.dice.roll()
        if self.dice.values[0] < self.dice.values[1]:
            self.players.reverse()
        self.get_rolls()
        # Set up the game.
        if self.match > 1:
            self.flags |= 256
        self.turns = 0
        self.win_count = sum(count for point, count in self.layout)
        self.free_turn = False

    def set_options(self):
        """Define the options for the game. (None)"""
        self.option_set.default_bots = [(AdditiveBot, ())]
        self.option_set.add_option('match', ['m'], int, 1, check = lambda x: x > 0,
            question = 'What should be the winning match score (return for 1)? ')
        self.option_set.add_option('layout', ['l'], options.lower, action = 'map', value = self.layouts,
            default = 'standard', question = 'What layout would you like to use (return for standard)? ')
        self.option_set.add_option('o', target = 'human_piece', value = 'O', default = 'X',
            question = 'Would you like to play with the O piece? bool')
        self.option_set.add_group('gonzo', ['gz'], 'layout = hyper match = 18')

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the players.
        self.bot = [player for player in self.players if player.name != self.human.name][0]
        self.pieces = {self.human.name: self.human_piece}
        if self.human_piece == 'X':
            self.pieces[self.bot.name] = 'O'
        else:
            self.pieces[self.bot.name] = 'X'
        # Set up the board and dice.
        self.reset()

    def validate_move(self, start, end, direction, legal_moves, player, player_piece):
        """
        Check for a valid move. (bool)

        The return value is the steps to take, in terms of which die values/number of
        points to using in sequence.

        Parameters:
        start: The starting point for the move. (int)
        end: The ending point for the move. (int)
        direction: The direction of the move. (int)
        legal_moves: The moves that can possibly be made. (list of BackgammonPlay)
        player: The player moving. (player.Player)
        player_piece: The symbol for the player moving. (str)
        """
        # Get the details of the move.
        start_pieces = self.board[start].contents
        end_pieces = self.board[end].contents
        # Get the combinations of rolls and moves.
        all_totals = self.get_totals()
        valid = []
        # Check for a piece on the start.
        if not (start_pieces and start_pieces[0] == player_piece):
            player.error('You do not have a piece on that starting point.')
        # Check for valid die roll.
        elif (end - start) * direction not in all_totals:
            player.error('You do not have a die roll matching that move.')
        # Check for a piece on the bar.
        elif player_piece in self.board[BAR] and start != BAR:
            player.error('You must re-enter your piece on the bar before making any other move.')
        else:
            # Check for blocked move, checking all possible move orders.
            for move_order in itertools.permutations(all_totals[(end - start) * direction]):
                point = start
                # Check each step for being blocked.
                for roll in move_order:
                    point += roll * direction
                    point_pieces = self.board[point].contents
                    if point_pieces and point_pieces[0] != player_piece and len(point_pieces) > 1:
                        break
                else:
                    # Use the first unblocked set of moves found.
                    valid = move_order
                    break
            else:
                # Warn the user about blocked moves.
                player.error('That move is blocked.')
                return []
            # Get the path followed by the move order.
            steps = []
            point = start
            for roll in move_order:
                steps.append((point, point + roll * direction))
                point = steps[-1][1]
            # Check each step in the path for being a legal play.
            for step in steps:
                if step not in legal_moves:
                    player.error('That move would not allow for the maximum possible play.')
                    valid = []
                    break
        return valid


class BackgammonBoard(board.LineBoard):
    """
    A board for Backgammon. (board.LineBoard)

    Attributes:
    eks: The view from the X player's side. (dict of int: BoardCell)
    oh: The view from the O player's side. (dict of int: BoardCell)

    Methods:
    board_text: Generate a text lines for the pieces on the board. (list of str)
    get_plays: Get the legal plays for a given set of rolls. (list)
    get_moves_enter: Get the legal moves when a piece is on the bar. (list)
    get_moves_help: Recurse get_plays using another board. (list of tuple)
    get_moves_home: Get the legal moves when all pieces are home. (list)
    get_moves_normal: Generate legal moves during normal play. (list of BackgammonPlay)
    get_pip_count: Get the pip count for a given player. (int)
    get_plays: Get all the legal plays for a given set of rolls. (list of BackgammonPlay)
    get_text: Get the board text from a particular player's perspective. (str)
    set_up: Put the starting pieces on the board. (None)

    Overridden Methods:
    __init__
    move
    safe
    """

    def __init__(self, length = 24, cell_class = 0, layout = ((6, 5), (8, 3), (13, 5), (24, 2))):
        """
        Set up the grid of cells. (None)

        The layout parameter is a tuple of two-integer tuples. Each pair of integers
        indicate a point and the number of piece on that point. This is only provided
        for one player, and then done symetrically for the other player.

        Paramters:
        layout: The initial layout of the pieces. (tuple of tuple)
        """
        # Set up the board.
        super(BackgammonBoard, self).__init__(24, extra_cells = [BAR, OUT])
        self.set_up(layout)
        # Set up attributes
        self.legal_plays = []

    def board_text(self, locations, reverse = False):
        """
        Generate a text lines for the pieces on the board. (list of str)

        Parameters:
        locations: The order for displaying the points. (list of int)
        reverse: A flag for reversing the rows.
        """
        # Loop through placements within points.
        lines = []
        for row in range(5):
            row_text = '| '
            # Loop through the points.
            for bar_check, location in enumerate(locations):
                pieces = len(self.cells[location])
                if pieces > row:
                    # Handle first row numbers.
                    if row == 0 and pieces > 5:
                        if pieces > 9 and reverse:
                            row_text += '{} '.format(pieces % 10)
                        elif pieces > 9:
                            row_text += '{} '.format(pieces // 10)
                        elif pieces > 5:
                            row_text += '{} '.format(pieces)
                    # Handle second row number.
                    elif row == 1 and pieces > 9:
                        if reverse:
                            row_text += '{} '.format(pieces // 10)
                        else:
                            row_text += '{} '.format(pieces % 10)
                    # Handle piece symbols.
                    else:
                        row_text += '{} '.format(self.cells[location][0])
                else:
                    # Handle board design.
                    row_text += '{} '.format('.' if location % 2 else ':')
                if bar_check == 5:
                    # Handle the bar.
                    row_text += '| '
            lines.append(row_text + '|')
        # Reverse the lines if requested.
        if reverse:
            lines.reverse()
        return lines

    def get_moves(self, piece, rolls, moves):
        """
        Get the legal moves for a given set of rolls. (list)

        This method is one level of recursion for get_plays, although the actual
        recursion is done in get_moves_help after calls to one of the ohter
        get_moves methods.

        Parameters:
        piece: The piece symbol to get moves for. (str)
        rolls: The rolls to get moves for. (str)
        moves: The moves already made. (list of tuple)
        """
        # Loop through the rolls.
        full_plays = []
        from_cells = [point for point in self.cells if piece in self.cells[point]]
        home = {'X': tuple(range(1, 7)), 'O': tuple(range(24, 18, -1))}[piece]
        for roll in set(rolls):
            # Get the rolls without the current roll.
            sub_rolls = rolls[:]
            sub_rolls.remove(roll)
            # Generate moves based on the phase of the game.
            if piece in self.cells[BAR]:
                full_plays = self.get_moves_enter(piece, moves, full_plays, sub_rolls, roll)
            elif all([coord in home or coord == OUT for coord in from_cells]):
                full_plays = self.get_moves_home(piece, moves, full_plays, sub_rolls, roll, from_cells)
            else:
                full_plays = self.get_moves_normal(piece, moves, full_plays, sub_rolls, roll, from_cells)
        return full_plays

    def get_moves_enter(self, piece, moves, full_plays, sub_rolls, roll):
        """
        Get the legal moves when a piece is on the bar. (list of BackgammonPlay)

        Parameters:
        piece: The piece symbol to get moves for. (str)
        moves: The moves already made. (BackgammonPlay)
        full_plays: The plays already recorded. (list of BackgammonPlay)
        sub_rolls: The rolls to get moves for. (list of int)
        roll: The current roll being moved. (int)
        """
        # Get the bar piece at the end for popping.
        if piece != self.cells[BAR][-1]:
            self.cells[BAR].remove_piece(piece)
            self.cells[BAR].add_piece(piece)
        # Get the end point
        if piece == 'X':
            end_coord = 25 - roll
        else:
            end_coord = roll
        end_cell = self.cells[end_coord]
        # Get the moves.
        if piece in end_cell or len(end_cell) < 2:
            full_plays = self.get_moves_help(piece, BAR, end_coord, moves, full_plays, sub_rolls, roll)
        return full_plays

    def get_moves_help(self, piece, point, end_point, moves, full_plays, sub_rolls, roll):
        """
        Recurse the get_move method by creating another board. (list of tuple)

        Parameters:
        piece: The piece symbol to get moves for. (str)
        point: The starting point of the move. (tuple of int)
        end_point: The ending point of the move. (tuple of int)
        moves: The moves already made. (list of tuple)
        full_plays: The moves already recorded. (list of tuple)
        sub_rolls: The rolls to get moves for. (str)
        roll: The roll being used for this move. (int)
        """
        # Create a board with the move.
        sub_board = self.copy(layout = ())
        capture = sub_board.move(point, end_point)
        # Add to the move to the moves so far.
        new_moves = moves + (point, end_point, roll)
        if sub_rolls:
            # Recurse if necessary
            sub_plays = sub_board.get_moves(piece, sub_rolls, new_moves)
            if sub_plays:
                full_plays.extend(sub_plays)
            else:
                # Capture partial moves.
                full_plays.append(new_moves)
        else:
            # Termination of recursion
            full_plays.append(new_moves)
        # Return the moves back up the recursion.
        return full_plays

    def get_moves_home(self, piece, moves, full_plays, sub_rolls, roll, from_cells):
        """
        Get the legal moves when all pieces are home. (list of BackgammonPlay)

        Parameters:
        piece: The piece symbol to get moves for. (str)
        moves: The moves already made. (BackgammonPlay)
        full_plays: The plays already recorded. (list of BackgammonPlay)
        sub_rolls: The rolls to get moves for. (list of int)
        roll: The current roll being moved. (int)
        from_cells: The points that pieces can move from. (list of int or str)
        """
        # Get the game state information.
        home = {'X': tuple(range(1, 7)), 'O': tuple(range(24, 18, -1))}[piece]
        direction = {'X': -1, 'O': 1}[piece]
        coord = home[roll - 1]
        # Check for pieces left to move.
        piece_indexes = [index for index, point in enumerate(home) if piece in self.cells[point]]
        if piece_indexes:
            max_index = piece_indexes[-1]
        else:
            return full_plays
        if piece in self.cells[coord]:
            # Generate standard bearing off moves.
            full_plays = self.get_moves_help(piece, coord, OUT, moves, full_plays, sub_rolls, roll)
        elif roll > max_index + 1:
            # Generate bearing off moves with over roll.
            coord = home[max_index]
            full_plays = self.get_moves_help(piece, coord, OUT, moves, full_plays, sub_rolls, roll)
        for home_index in range(6):
            # Generate moves within the home board.
            start = home[home_index]
            end = start + roll * direction
            if 1 <= end <= 24:
                if piece in self.cells[start] and (piece in self.cells[end] or len(self.cells[end]) < 2):
                    full_plays = self.get_moves_help(piece, start, end, moves, full_plays, sub_rolls, roll)
        return full_plays

    def get_moves_normal(self, piece, moves, full_plays, sub_rolls, roll, from_cells):
        """
        Generate legal moves during normal play. (list of BackgammonPlay)

        Parameters:
        piece: The piece symbol to get moves for. (str)
        moves: The moves already made. (BackgammonPlay)
        full_plays: The plays already recorded. (list of BackgammonPlay)
        sub_rolls: The rolls to get moves for. (list of int)
        roll: The current roll being moved. (int)
        from_cells: The points that pieces can move from. (list of int or str)
        """
        # Loop through possible points.
        direction = {'X': -1, 'O': 1}[piece]
        for point in from_cells:
            # Check the point.
            end_point = point + roll * direction
            if not (0 < point <= self.length and 0 < end_point <= self.length):
                continue
            # Check the cell.
            end_cell = self.cells[end_point]
            if piece not in end_cell and len(end_cell) > 1:
                continue
            # Find the moves.
            full_plays = self.get_moves_help(piece, point, end_point, moves, full_plays, sub_rolls, roll)
        return full_plays

    def get_pip_count(self, piece):
        """
        Get the pip count for a given player. (int)

        Parameters:
        piece: The piece of the player to get a pip count for. (str)
        """
        # Loop through the board locations.
        points = 0
        for cell in self.cells.values():
            # Get the correct pip count.
            point = cell.location
            if point == BAR:
                point = 25
            elif point == OUT:
                point = 0
            elif piece == 'O':
                point = 25 - point
            # Get the pip count for each piece.
            points += point * cell.count(piece)
        return points

    def get_plays(self, piece, rolls):
        """
        Get all the legal plays for a given set of rolls. (list of BackgammonPlay)

        The initial moves are obtained recursively through get_moves, and then cleaned
        up here.

        Parameters:
        piece: The piece symbol to move. (str)
        rolls: The rolls available to move with. (list of int)
        """
        if not self.legal_plays:
            # Get unique plays.
            plays = self.get_moves(piece, rolls, BackgammonPlay())
            plays = list(set(plays))
            # Check for maximum use of the roll.
            max_roll = max(play.total_roll for play in plays) if plays else 0
            max_moves = max(len(play) for play in plays) if plays else 0
            self.legal_plays = []
            for play in plays:
                if play.total_roll == max_roll and len(play) == max_moves:
                    self.legal_plays.append(play)
        return self.legal_plays

    def get_text(self, piece):
        """
        Get the board text from a particular player's perspective. (str)

        Parameters:
        piece: The piece for the player to display. (str)
        """
        # Start with a blank line.
        lines = ['']
        # Get the details (for X).
        frame_high = FRAME_HIGH
        frame_low = FRAME_LOW
        order_high = list(range(13, 25))
        order_low = list(range(12, 0, -1))
        # Convert the details if the text is for O
        if piece == 'O':
            frame_high = [line[::-1] for line in frame_high[2:] + frame_high[:2]]
            frame_low = [line[::-1] for line in frame_low[1:] + frame_low[:1]]
            frame_high, frame_low = frame_low, frame_high
            order_high = list(range(1, 13))
            order_low = list(range(24, 12, -1))
        # Get the top half of the board.
        lines.extend(frame_high[:])
        lines.extend(self.board_text(order_high))
        # Get the middle and bottom half of the board.
        lines.append('|             |             |')
        lines.extend(self.board_text(order_low, reverse = True))
        lines.extend(frame_low)
        # Include a line for any pieces on the bar.
        if self.cells[BAR]:
            lines.extend(['', 'Bar: {}'.format(''.join(self.cells[BAR]))])
        # Return the text.
        return '\n'.join(lines)

    def move(self, start, end, piece = None):
        """
        Move a piece from one cell to another. (object)

        The object returned is any piece that is in the destination cell before the
        move. The parameters should be keys appropriate to cells on the board.

        Parameters:
        start: The location containing the piece to move. (Coordinate)
        end: The location to move the piece to. (Coordinate)
        """
        # Move and handle the capture
        capture = self.safe_displace(start, end, piece)
        for piece in capture:
            self.cells[BAR].add_piece(piece)
        # Reset board tracking.
        self.legal_plays = []
        return capture

    def safe(self, location, piece):
        """
        Determine if a cell is safe from capture. (bool)

        Parameter:
        location: The location of the cell to check. (hashable)
        piece: The piece that would move to that spot. (object)
        """
        if isinstance(location, str):
            return False
        else:
            return super(BackgammonBoard, self).safe(location, piece)

    def set_up(self, layout):
        """
        Put the starting pieces on the board. (None)

        See __init__ for the details of the layout parameter.

        Parameters:
        layout: The pieces counts and the points to play them on. (tuple of tuple)
        """
        # Layout the pieces for X, and mirrored for O.
        for location, count in layout:
            self.cells[location].contents = ['X'] * count
            self.cells[25 - location].contents = ['O'] * count

    def set_views(self):
        """Set up the alternate mappings for the board. (None)"""
        # Set the X piece view.
        self.eks = self.cells
        # Translate that into the O piece view.
        self.oh = {}
        for point in range(1, 25):
            self.oh[point] = self.cells[25 - point]
        self.oh[BAR] = self.cells[BAR]
        self.oh[OUT] = self.cells[OUT]
        # Set up the views attribute.
        self.views = itertools.cycle([self.oh, self.eks])


class BackgammonPlay(object):
    """
    A possible play (set of moves) in Backgammon. (object)

    The moves attribute is a tuple of three integers: the start point of the move,
    the end point of the move, and the roll used.

    Attributes:
    moves: The moves that make up the play. (list of tuple)
    total_roll: The total roll used for the move. (int)

    Methods:
    add_move: Add a move to the play. (None)
    next_move: Return a move to make. (tuple)

    Overridden Methods:
    __init__
    __add__
    __bool__
    __eq__
    __hash__
    __iter__
    __len__
    __lt__
    __repr__
    __str__
    """

    def __init__(self, start = 0, end = 0, roll = 0):
        """
        Set up the play, possibly with an intial move. (None)

        If start is 0 or '', no initial move is recorded.

        Parameters:
        start: the starting point of the initial move. (int or str)
        end: the end point of the initial move. (int or str)
        roll: the roll used for the initial move. (int)
        """
        if start:
            # Set up with initial move.
            self.moves = [(start, end, roll)]
            self.total_roll = roll
        else:
            # Set up without initial move.
            self.moves = []
            self.total_roll = 0

    def __add__(self, other):
        """
        Add a new move to the play. (BackgammonPlay)

        Parameters:
        other: A move to add. (tuple of str or int)
        """
        if isinstance(other, tuple) and len(other) == 3:
            # Add a tuple using add_move.
            new_play = BackgammonPlay()
            new_play.moves = self.moves[:]
            new_play.total_roll = self.total_roll
            new_play.add_move(*other)
            return new_play
        elif isinstance(other, BackgammonPlay):
            # Add another BackgammonPlay by adding attributes.
            new_play = BackgammonPlay()
            new_play.moves = sorted(self.moves + other.moves)
            new_play.total_roll = self.total_roll + other.total_roll
            return new_play
        else:
            return NotImplemented

    def __bool__(self):
        """Are there any moves left? (bool)"""
        return bool(self.moves)

    def __eq__(self, other):
        """
        Check for equality between moves. (bool)

        Parameters:
        other: The play to compare against. (BackgammonPlay)
        """
        # Equality is the same moves, regardless of order.
        if isinstance(other, BackgammonPlay):
            return sorted(self.moves) == sorted(other.moves)
        else:
            return NotImplemented

    def __hash__(self):
        """Generate an integer has for the play. (int)"""
        return hash(tuple(sorted(self.moves)))

    def __iter__(self):
        """Iterate over moves not including rolls. (iterator)"""
        return (move[:2] for move in self.moves)

    def __len__(self):
        """Number of moves in the play. (int)"""
        return len(self.moves)

    def __lt__(self, other):
        """
        Check for order between moves. (bool)

        Parameters:
        other: The play to compare against. (BackgammonPlay)
        """
        # Order is by sorted moves.
        if isinstance(other, BackgammonPlay):
            return sorted(self.moves) < sorted(other.moves)
        else:
            return NotImplemented

    def __repr__(self):
        """Generate a debugging text representation. (str)"""
        return '<BackgammonPlay {!r}>'.format(self.moves)

    def __str__(self):
        """Generates a human readable text representation. (str)"""
        # Get the text for the roll.
        if len(self.moves) > 1:
            roll_text = '{}-{}: '.format(self.moves[0][2], self.moves[1][2])
        elif self.moves:
            roll_text = '{}: '.format(self.moves[0][2])
        else:
            'Empty Backgammon play.'
        # Get a word for each move.
        base_words = ['{}/{}'.format(*move[:2]) for move in self.moves]
        # Trim out duplicate moves, with appropriate notation.
        move_words = []
        skip = 0
        for word in base_words:
            # Skip already done moves.
            if skip:
                skip -= 1
                continue
            # Check for duplicate moves.
            count = base_words.count(word)
            if count > 1:
                # Record duplicate moves and skip count.
                move_words.append('{} ({})'.format(word, count))
                skip = count - 1
            else:
                # Record normal moves.
                move_words.append(word)
        # Use bar and out in the move text.
        move_text = ' '.join(move_words)
        move_text = move_text.replace('-1', 'bar')
        move_text = move_text.replace('-2', 'out')
        # Return the combined text for the roll and the moves.
        return '{}{}'.format(roll_text, move_text)

    def add_move(self, start = 0, end = 0, roll = 0):
        """
        Add a move to the play. (None)

        Parameters:
        start: the starting point of the move. (int or str)
        end: the end point of the move. (int or str)
        roll: the roll used for the move. (int)
        """
        self.moves.append((start, end, roll))
        self.total_roll += roll

    def next_move(self):
        """Return a move to make. (tuple)"""
        return self.moves.pop(0)
