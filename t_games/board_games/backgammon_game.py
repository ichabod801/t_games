"""
backgammon_game.py

A game of Backgammon and related variants.

Terminology:
    roll: The number on a die.
    move: One roll's move.
    play: A full turn of moves.

!! Ichabod's Rule: Instead of capturing, hitting a blot bears the moving
    piece off the board. Makes it a pure race game.

I need to read up on backgammon strategy. See if I can find a better set of
board features to redo additive bot with. Get a good additive bot, then move
on to expectamax or a neural net.

Constants:
BAR: The index of the bar. (int)
CREDITS: The credits for the game. (str)
FRAME_HIGH: The top of the frame for displaying the board. (list of str)
FRAME_LOW: The bottom of the frame for displaying the board. (list of str)
OUT: The index for pieces born off the board. (int)
RULES: The rules of Backgammon. (str)
START: The index for pieces not yet in the game. (int)

Classes:
BackgammonBot: A bot for a game of Backgammon(player.bot)
BackGeneBot: A Backgammon bot for genetic engineering. (BackgammonBot)
PubEvalBot: A bot based on Gerry Tesauro's pubeval algorithm. (BackgammonBot)
Backgammon: A game of Backgammon. (game.Game)
BackgammonBoard: A board for Backgammon. (board.LineBoard)

Functions:
move_key: Convert a move to a sortable key. (list of int)
"""


from __future__ import print_function

import random

import t_games.board as board
import t_games.dice as dice
import t_games.game as game
import t_games.options as options
import t_games.player as player
import t_games.utility as utility


# The index of the bar.
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

# The credits for the game.
CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
Bot Programming: Gerry Tesauro
"""

# The top of the frame for displaying the board.
FRAME_HIGH = ['  1 1 1 1 1 1   1 2 2 2 2 2  ', '  3 4 5 6 7 8   9 0 1 2 3 4  ', 
    '+-------------+-------------+']

# The bottom of the frame for displaying the board.
FRAME_LOW = ['+-------------+-------------+',  '  1 1 1                      ', 
    '  2 1 0 9 8 7   6 5 4 3 2 1  ']

# The index for pieces born off the board.
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

# The rules of Backgammon.
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
or 'b') and the point your want to bear off from (NOT the roll).

Backgammon is often played in match play, to even out the luck of the dice.
When using match play, a game won when the opponent has not born any pieces
off the board counts double, and a game won when the opponent still has a
piece on the bar counts triple. Furthermore, there is a doubling die that 
can be used to double the stakes. At the beginning of the game, either
player may double the stakes using the double command. The other player must
accept the doubled stakes or concede the game. After the initial doubling of
the stakes, control of the doubling die goes to the player who accepted the
doubling of the stakes, and only they can double the stakes again.

You may get both players' pip counts at any time with the pips command.

Options:
o: The human player plays with the red (O) pieces.
layout: Which layout to use: long, standard, or hyper. (l)
match: The winning match score. Defaults to 1, or non-match play. (m)
"""

# The index for pieces not yet in the game.
START = -3


class BackgammonBot(player.Bot):
    """
    A bot for a game of Backgammon(player.Bot)

    Attributes:
    held_moves: Moves planned but not yet made through ask. (BackgammonPlay)

    Methods:
    eval_board: Evaluate a board position. (list of int)

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
                    features, points = self.describe_board(sub_board)
                    max_x = max(points['X']) if points['X'] else 0
                    max_o = max(points['O']) if points['O'] else 0
                    if max_x + max_o > 24 or sub_board.cells[BAR].contents:
                        phase = 'mixed'
                    elif max_x <= 6 and max_o < 6:
                        phase = 'stretch'
                    else:
                        phase = 'split'
                    possibles.append((self.eval_board(features, phase), play))
                # Choose the play with the highest evaluation.
                possibles.sort(reverse = True)
                self.held_moves = possibles[0][1]
            # Return the move with the correct syntax.
            move = self.held_moves.next_move()
            if move[1] == OUT:
                point = move[0]
                if point > 6:
                    point = 25 - point
                return 'bear {}'.format(point)
            elif move[0] == BAR:
                point = move[1]
                if point > 6:
                    point = 25 - point
                return 'enter {}'.format(point)
            else:
                return '{} {}'.format(move[0], move[1])
        # Respond to no-move notifications.
        elif prompt.startswith('You have no legal moves'):
            self.game.human.tell('{} has no legal moves.'.format(self.name))
            return ''
        elif prompt.startswith('Your opponent wants to double'):
            features, points = self.describe_board(self.game.board)
            if self.eval_board(features, 'accept') < -25:
                return '1'
            else:
                return '0'
        elif prompt.startswith('Would you like to double'):
            features, points = self.describe_board(self.game.board)
            if self.eval_board(features, 'double') > 25:
                return '1'
            else:
                return '0'
        # Raise an error for any other question.
        else:
            raise ValueError('Unexpected question to BackgammonBot: {}'.format(prompt))

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
            * The difference in indirect hits to blots. (!! Not calcualted correctly)
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
        for cell in board.cells.values():
            if cell.location < 0:
                continue
            if len(cell.contents) > 1:
                controlled[cell.contents[0]].append(cell.location)
            elif len(cell.contents) == 1:
                blots[cell.contents[0]].append(cell.location)
        points = {piece: controlled[piece] + blots[piece] for piece in 'XO'}
        points['O'] = [24 - point for point in points['O']]
        captured = {piece: board.cells[BAR].contents.count(piece) for piece in 'XO'}
        off = {piece: board.cells[OUT].contents.count(piece) for piece in 'XO'}
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
        direct_hits = {'X': 0, 'O': 0}
        indirect_hits = {'X': 0, 'O': 0}
        for piece in 'XO':
            foe_direction = {'X': -1, 'O': 1}[piece]
            foe_piece = {'X': 'O', 'O': 'X'}[piece]
            for blot in blots[piece]:
                for offset in range(1, 13):
                    try:
                        offcell = board.offset(blot, offset * foe_direction)
                    except KeyError:
                        break
                    if foe_piece in offcell:
                        if offset < 7:
                            direct_hits[piece] += 1
                        if offset > 1:
                            indirect_hits[piece] += 1
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
        board = self.game.board
        human = self.game.human
        human.tell('\nERROR INFO\n')
        human.tell(board.get_text(self.piece))
        human.tell(board.get_plays(self.piece, self.game.rolls))
        super(BackgammonBot, self).error(*args, **kwargs)

    def eval_board(self, board_features, phase):
        my_pips = self.game.board.get_pip_count(self.piece)
        their_pips = self.game.board.get_pip_count({'X': 'O', 'O': 'X'}[self.piece])
        if phase == 'double':
            if their_pips > 8 and my_pips / their_pips < 0.75:
                return 1
            else:
                return 0
        elif phase == 'accept':
            if their_pips > 8 and my_pips / their_pips < 1.33:
                return 1
            else:
                return 0
        else:
            return board_features

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
        # Don't say anything while making multiple moves
        if not self.held_moves:
            super(BackgammonBot, self).tell(text)


class AdditiveBot(BackgammonBot):

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
        return sum([f * r for f, r in zip(self.vectors[phase], board_features)])


class BackGeneBot(BackgammonBot):
    """
    A Backgammon bot for genetic engineering. (BackgammonBot)
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
        super(BackGeneBot, self).__init__(taken_names = taken_names)
        self.vectors = {}
        if mother is None:
            for phase in self.phases:
                if phase in ('double', 'accept'):
                    self.vectors[phase] = [random.randint(-100, 100) for dummy in range(8)]
                else:
                    self.vectors[phase] = [random.randint(0, 100) for dummy in range(8)]
        else:
            for phase in self.phases:
                pairs = zip(mother.vectors[phase], father.vectors[phase])
                self.vectors[phase] = [random.choice(pair) for pair in pairs]

    def eval_board(self, board_features, phase):
        return sum([f * r for f, r in zip(self.vectors[phase], board_features)])

    def tell(self, *args, **kwargs):
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
    eval_board
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
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
            # Return the move with the correct syntax.
            move = self.held_moves.next_move()
            if move[1] == OUT:
                point = move[0]
                if point > 6:
                    point = 25 - point
                return 'bear {}'.format(point)
            elif move[0] == BAR:
                point = move[1]
                if point > 6:
                    point = 25 - point
                return 'enter {}'.format(point)
            else:
                return '{} {}'.format(move[0], move[1])
        # Respond to no-move notifications.
        elif prompt.startswith('You have no legal moves'):
            self.game.human.tell('{} has no legal moves.'.format(self.name))
            return ''
        elif prompt.startswith('Your opponent wants to double'):
            features, points = self.describe_board(self.game.board)
            if self.eval_board(features, 'accept') < -25:
                return '1'
            else:
                return '0'
        elif prompt.startswith('Would you like to double'):
            features, points = self.describe_board(self.game.board)
            if self.eval_board(features, 'double') > 25:
                return '1'
            else:
                return '0'
        # Raise an error for any other question.
        else:
            raise ValueError('Unexpected question to BackgammonBot: {}'.format(prompt))

    def eval_board(self, board):
        """
        Evaluate a board position. (float)

        Parameters:
        board: The board to evaluate. (BackgammonBoard)
        """
        position = self.get_position(board)
        left, right, = [], []
        for index, men in enumerate(position[1:25]):
            if men < 0:
                left.append(men)
            elif men > 0:
                right.append(men)
        race = max(left) > min(right)
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
        foe_piece = {'X': 'O', 'O': 'X'}[self.piece]
        position = [board.cells[BAR].count(foe_piece) * -1]
        points = []
        for location in range(1, 24):
            pieces = board.cells[location]
            value = len(pieces)
            if self.piece not in pieces:
                value *= -1
            points.append(value)
        if self.piece == 'O':
            position.reverse()
        position.extend(points)
        position.append(board.cells[BAR].count(self.piece))
        position.append(board.cells[OUT].count(self.piece))
        position.append(board.cells[OUT].count(foe_piece) * -1)
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
        vector = self.set_vector(position)
        if race:
            weights = RACE_WEIGHTS
        else:
            weights = CONTACT_WEIGHTS
        score = [v * w for v, w in zip(vector, weights)]

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
                        vector[5 * point - 1] =  (men - 3) / 2
        # Ecode foes on bar.
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

    Methods:
    check_win: Check to see if a given player has won. (int)
    do_bear: Bear a piece of the board. (bool)
    do_enter: Bring a piece back into play from the bar. (bool)
    get_rolls: Determine the rolls you can move with from the dice roll. (None)

    Overridden Methods:
    game_over
    player_action
    set_options
    set_up
    """

    aliases = {'b': 'bear', 'd': 'double', 'e': 'enter', 'p': 'pips', 's': 'start'}
    categories = ['Board Games', 'Race Games']
    credits = CREDITS
    layouts = {'hyper': ((24, 1), (23, 1), (22, 1)), 'long': ((24, 15),), 
        'nack': ((6, 4), (8, 3), (13, 4), (23, 2), (24, 2)), 
        'standard': ((6, 5), (8, 3), (13, 5), (24, 2))}
    name = 'Backgammon'
    num_options = 3
    rules = RULES

    def check_win(self, piece):
        """
        Check to see if a given player has won. (int)

        The return value is the match score of the win (0 for no win yet).

        Parameters:
        piece: The piece used by the player being checked. (str)
        """
        other_piece = 'XO'['OX'.index(piece)]
        result = 0
        # Check for win.
        if self.board.cells[OUT].count(piece) == 15:
            result = self.doubling_die
            # Check for gammon/backgammon.
            if other_piece not in self.board.cells[OUT]:
                if piece == 'X':
                    home = range(1, 7)
                else:
                    home = range(19, 25)
                home_pieces = sum([self.board.cells[point].contents for point in home], [])
                if other_piece in self.board.cells[BAR] or other_piece in home_pieces:
                    self.human.tell('Backgammon!')
                    result *= 3
                else:
                    self.human.tell('Gammon!')
                    result *= 2
        return result 

    def do_bear(self, argument):
        """
        Bear a piece off of the board. (bool)

        Parameters:
        argument: The point or points to bear off from. (str)
        """
        # !! bot can't bear
        # Get the current player.
        player = self.players[self.player_index]
        piece = self.pieces[player.name]
        # Convert the arguments.
        words = argument.split()
        if words[0].lower() == 'off':
            words = words[1:]
        try:
            bears = [int(word) for word in words]
        except ValueError:
            # Warn on bad arguments.
            player.error('Invalid argument to the bear command: {}.'.format(argument))
            return True
        points = [loc for loc, cell in self.board.cells.items() if piece in cell and loc > 0]
        # Check for all pieces in the player's home.
        if (piece == 'X' and max(points) > 6) or (piece == 'O' and min(points) < 19):
            player.error('You do not have all of your pieces in your home yet.')
        # Check for captured piece
        elif piece in self.board.cells[BAR]:
            player.error('You still have a piece on the bar.')
        else:
            # Play any legal moves
            for bear in bears:
                # Get the correct point
                roll = bear
                if piece == 'O':
                    bear = 25 - bear
                # Check for a valid point
                if piece not in self.board.cells[bear]:
                    player.error('You do not have a piece on the {} point.'.format(roll))
                    continue
                # Remove the correct roll.
                elif roll in self.rolls:
                    self.rolls.remove(roll)
                elif roll < max(self.rolls):
                    self.rolls.remove(max(self.rolls))
                else:
                    # Warn for no valid roll.
                    player.error('There is no valid move for the {} point.'.format(roll))
                    continue
                # Bear off the piece
                self.board.move(bear, OUT)
        # Continue the turn if there are still rolls to move.
        return self.rolls

    def do_enter(self, argument): 
        """
        Bring a piece back into play from the bar. (bool)

        Parameters:
        argument: The point to enter onto. (str)
        """
        # Get the current player.
        player = self.players[self.player_index]
        piece = self.pieces[player.name]
        # Convert the arguments.
        try:
            needed_roll = int(argument)
        except ValueError:
            player.error('Invalid argument to the enter command: {}.'.format(argument))
            return True
        point = needed_roll
        if piece == 'X':
            point = 25 - point
        # Check for valid roll.
        if needed_roll not in self.rolls:
            player.error('You need to roll a {} to enter on that point.'.format(needed_roll))
            return True
        # Check for a piece to enter.
        elif piece not in self.board.cells[BAR]:
            player.error('You do not have a piece on the bar.')
            return True
        # Check for a valid entry point.
        end_cell = self.board.cells[point]
        if piece not in end_cell and len(end_cell) > 1:
            player.error('That point is blocked.')
            return True
        # Make the move.
        capture = self.board.move(BAR, point, piece)
        self.rolls.remove(needed_roll)
        return self.rolls

    def do_gipf(self, arguments):
        """
        Gipf

        Parameters:
        arguments: The name of the game to gipf to. (str)
        """
        game, losses = self.gipf_check(arguments, ('connect four',))
        # Hunt the Wumpus
        if game == 'connect four':
            if not losses:
                player = self.players[self.player_index]
                piece = self.pieces[player.name]
                player.tell(self.board.get_text(piece))
                while True:
                    query = '\nPick a point to move a piece verically from: '
                    point = player.ask_int(query, low = 1, high = 24)
                    target = 25 - point
                    if piece not in self.board.cells[point]:
                        player.tell('You do not have a piece on that point.')
                    elif len(self.board.cells[target]) > 2 and piece not in self.board.cells[target]:
                        player.tell('You could not move a piece to that square normally.')
                    else:
                        break
                self.board.move(point, target, piece)
                go = False
        else:
            player.tell("I'm sorry, I didn't catch that.")
            go = True
        return go

    def do_pips(self, argument):
        """
        Show the pip counts for the two players. (True)

        Parameters:
        argument: The (ingored) argument to the command. (str)
        """
        # Get the current player.
        player = self.players[self.player_index]
        # Show the pip counts.
        player.tell('\nX:', self.board.get_pip_count('X'))
        player.tell('O:', self.board.get_pip_count('O'), '\n')
        # Keep playing
        return True

    def double(self, player):
        """
        Double the doubling die. (bool)

        Parameters:
        player: The player doubling the stakes. (player.Player)
        """
        # Get the player's piece.
        piece = self.pieces[player.name]
        if self.doubling_status in ('', piece):
            opponent = self.players[1 - self.player_index]
            query = 'Your opponent wants to double the stakes to {}. Do you accept the new stakes? '
            accept = opponent.ask(query.format(self.doubling_die * 2))
            if accept.lower() in utility.YES:
                self.doubling_die *= 2
                self.doubling_status = {'X': 'O', 'O': 'X'}[piece]
                message = 'Your opponent accepts the double, the doubling die is now at {}'
                player.tell(message.format(self.doubling_die))
            else:
                player.tell('Your opponent refuses the double, you win.')
                if player == self.human:
                    self.win_loss_draw[1] += self.doubling_die
                else:
                    self.win_loss_draw[0] += self.doubling_die
                if self.win_loss_draw[0] >= self.match:
                    self.force_end = 'win'
                elif self.win_loss_draw[1] >= self.match:
                    self.force_end = 'loss'
                else:
                    self.reset()
                return False
        else:
            player.error("The doubling die is in your opponent's control")
        return True

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # Check human win.
        human_win = self.check_win(self.pieces[self.human.name])
        if human_win:
            self.win_loss_draw[0] += human_win
            self.human.tell('\nYou win!\n')
        bot_win = self.check_win(self.pieces[self.bot.name])
        # Check bot win.
        if bot_win:
            self.win_loss_draw[1] += bot_win
            self.human.tell('\nYou lose. :(\n')
        # Reset the game.
        if (human_win or bot_win) and self.match > 1:
            self.human.tell('The match score is {} to {}.\n'.format(*self.win_loss_draw[:2]))
            self.reset()
        return max(self.win_loss_draw) >= self.match

    def get_rolls(self):
        """Determine the rolls you can move with from the dice roll. (None)"""
        self.rolls = self.dice.values[:]
        if self.rolls[0] == self.rolls[1]:
            self.rolls.extend(self.rolls)

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
            if self.doubling_status in ('', player_piece) and self.doubling_die < self.match:
                double = player.ask('Would you like to double the stakes (return to roll)? ')
                if double in utility.YES:
                    game_on = self.double(player)
                    if not game_on:
                        return False
            self.dice.roll()
            self.dice.sort()
            self.get_rolls()
            if self.turns > 500:
                self.force_end = 'win'
        player.tell('\nThe roll to you is {}.'.format(', '.join([str(x) for x in self.rolls])))
        # Check for no legal moves
        legal_plays = self.board.get_plays(player_piece, self.rolls)
        if not legal_plays:
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
        direction = {'X': -1 , 'O': 1}[player_piece]
        # Convert moves with just the end point.
        if len(move) == 1:
            possible = []
            for maybe in set(self.rolls):
                start = move[0] - maybe * direction
                if start in self.board.cells and player_piece in self.board.cells[start]:
                    possible.append(start)
            if len(possible) == 1:
                start = possible[0]
                end = move[0]
            elif len(possible) > 1:
                player.error('That move is ambiguous.')
                return True
            else:
                player.error('There is no legal single move to that point.')
                return True
        else:
            start, end = move
        # Get the details of the move.
        start_pieces = self.board.cells[start].contents
        end_pieces = self.board.cells[end].contents
        # Check for valid staring point.
        if not (start_pieces and start_pieces[0] == player_piece):
            player.error('You do not have a piece on that starting point.')
            return True
        # Check for valid die roll.
        elif (end - start) * direction not in self.rolls:
            player.error('You do not have a die roll matching that move.')
            return True
        # Check for valide end point
        elif end_pieces and end_pieces[0] != player_piece and len(end_pieces) > 1:
            player.error('That end point is blocked.')
            return True
        # Check for a piece on the bar.
        elif player_piece in self.board.cells[BAR].contents and start != BAR:
            player.error('You must re-enter your piece on the bar before making any other move.')
            return True
        elif (start, end) not in legal_moves:
            player.error('That move would not allow for the maximum possible play.')
        else:
            # Make the valid move
            capture = self.board.move(start, end)
            self.rolls.remove(abs(start - end))
        # Continue if there are still rolls to handle.
        return self.rolls

    def reset(self):
        """Reset the game state during match play."""
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

    def set_options(self):
        """Define the options for the game. (None)"""
        self.option_set.default_bots = [(AdditiveBot, ())]
        self.option_set.add_option('o', target = 'human_piece', value = 'O', default = 'X',
            question = 'Would you like to play with the O piece? bool')
        self.option_set.add_option('match', ['m'], int, 1, check = lambda x: x > 0,
            question = 'What should be the winning match score (return for 1)? ')
        self.option_set.add_option('layout', ['l'], options.lower, action = 'map', value = self.layouts, 
            default = 'standard',
            question = 'What layout would you like to use (return for standard)? ')

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


class BackgammonBoard(board.LineBoard):
    """
    A board for Backgammon. (board.LineBoard)

    Methods:
    board_text: Generate a text lines for the pieces on the board. (list of str)
    get_plays: Get the legal plays for a given set of rolls. (list)
    get_moves_help: Recurse get_plays using another board. (list of tuple)
    get_pip_count: Get the pip count for a given player. (int)
    get_text: Get the board text from a particular player's perspective. (str)

    Overridden Methods:
    __init__
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

    def board_text(self, locations):
        """
        Generate a text lines for the pieces on the board. (list of str)

        Parameters:
        locations: The order for displaying the points. (list of int)
        """
        lines = []
        # Loop through placements within points.
        for row in range(5):
            row_text = '| '
            # Loop through the points.
            for bar_check, location in enumerate(locations):
                pieces = len(self.cells[location])
                if pieces > row:
                    # Handle first row numbers.
                    if row == 0 and pieces > 5:
                        if pieces > 9:
                            row_text += '{} '.format(pieces % 10)
                        elif pieces > 5:
                            row_text += '{} '.format(pieces)
                    # Handle second row number.
                    elif row == 1 and pieces > 9:
                        row_text += '1 '
                    # Handle piece symbols
                    else:
                        row_text += '{} '.format(self.cells[location].contents[0])
                else:
                    # Handle board design.
                    row_text += '{} '.format(':.'[location % 2])
                if bar_check == 5:
                    # Handle the bar.
                    row_text += '| '
            lines.append(row_text + '|')
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
        if piece != self.cells[BAR].contents[-1]:
            self.cells[BAR].remove_piece(piece)
            self.cells[BAR].add_piece(piece)
        if piece == 'X':
            end_coord = 25 - roll
        else:
            end_coord = roll
        end_cell = self.cells[end_coord]
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
        home = {'X': tuple(range(1, 7)), 'O': tuple(range(24, 18, -1))}[piece]
        direction = {'X': -1, 'O': 1}[piece]
        coord = home[roll - 1]
        # Check for pieces left to move.
        piece_indexes = [ndx for ndx, pt in enumerate(home) if piece in self.cells[pt]]
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
        direction = {'X': -1, 'O': 1}[piece]
        for point in from_cells:
            end_point = point + roll * direction
            if not (0 < point <= self.length and 0 < end_point <= self.length):
                continue
            end_cell = self.cells[end_point]
            if piece not in end_cell and len(end_cell) > 1:
                continue
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
            points += point * cell.contents.count(piece)
        return points

    def get_plays(self, piece, rolls):
        """
        Get all the legal plays for a given set of rolls.

        The initial moves are obtained recursively through get_moves, and then cleaned
        up here.

        Parameters:
        piece: The piece symbol to move. (str)
        rolls: The rolls available to move with. (list of int)
        """
        if not self.legal_plays:
            plays = self.get_moves(piece, rolls, BackgammonPlay())
            plays = list(set(plays))
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
        # Get the details (for X).
        frame_high = FRAME_HIGH
        frame_low = FRAME_LOW
        order_high = list(range(13, 25))
        order_low = list(range(12, 0, -1))
        # Convert the details if the text is for O
        if piece == 'O':
            frame_high = [line[::-1] for line in frame_high]
            frame_low = [line[::-1] for line in frame_low]
            order_high = list(range(1, 13))
            order_low = list(range(24, 12, -1))
        # Get the top half of the board.
        lines = frame_high[:]
        lines.extend(self.board_text(order_high))
        # Get the middle and bottom half of the board.
        lines.append('|             |             |')
        lines.extend(reversed(self.board_text(order_low)))
        lines.extend(frame_low)
        # Include a line for any pieces on the bar.
        if self.cells[BAR].contents:
            lines.extend(['', 'Bar: {}'.format(''.join(self.cells[BAR].contents))])
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
        capture = self.safe_displace(start, end, piece)
        for piece in capture:
            self.cells[BAR].add_piece(piece)
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


class BackgammonPlay(object):
    """
    A possible play (set of moves) in Backgammon. (object)

    !! consider having a sorted_moves attribute for efficiency.

    The moves attribute is a tuple of three integers: the start point of the move,
    the end point of the move, and the roll used.

    Attributes:
    total_roll: The total roll used for the move. (int)
    moves: The moves that make up the play. (list of tuple)

    Methods:
    add_move: Add a move to the play. (None)

    Overridden Methods:
    __init__
    __add__
    __eq__
    __len__
    __repr__
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
            new_play = BackgammonPlay()
            new_play.moves = self.moves[:]
            new_play.total_roll = self.total_roll
            new_play.add_move(*other)
            return new_play
        elif isinstance(other, BackgammonPlay):
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

    def __repr__(self):
        """Computer readable text representation. (str)"""
        return '<BackgammonPlay {!r}>'.format(self.moves)

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


if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    game = Backgammon(player.Player(name), '')
    game.play()