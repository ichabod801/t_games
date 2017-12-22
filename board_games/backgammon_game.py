"""
backgammon_game.py

A game of Backgammon and related variants.

Terminology:
    roll: The number on a die.
    move: One roll's move.
    play: A full turn of moves.

!! Ichabod's Rule: Instead of capturing, hitting a blot bears the moving
    piece off the board.

Constants:
CREDITS: The credits for the game. (str)
FRAME_HIGH: The top of the frame for displaying the board. (list of str)
FRAME_LOW: The bottom of the frame for displaying the board. (list of str)

Classes:
BackgammonBot: A bot for a game of Backgammon(player.bot)
Backgammon: A game of Backgammon. (game.Game)
BackgammonBoard: A board for Backgammon. (board.LineBoard)
"""


from __future__ import print_function

import tgames.board as board
import tgames.dice as dice
import tgames.game as game
import tgames.options as options
import tgames.player as player


# The credits for the game.
CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

# The top of the frame for displaying the board.
FRAME_HIGH = ['  1 1 1 1 1 1   1 2 2 2 2 2  ', '  3 4 5 6 7 8   9 0 1 2 3 4  ', 
    '+-------------+-------------+']

# The bottom of the frame for displaying the board.
FRAME_LOW = ['+-------------+-------------+',  '  1 1 1                      ', 
    '  2 1 0 9 8 7   6 5 4 3 2 1  ']

# The rules of Backgammon.
RULES = """
Each player starts the game rolling one die, and the higher roll moves using 
the two numbers rolled. From then on turns alternate, each player rolling two
dice on their turn. If doubles are rolled, they count double (as four or the
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

Options:
o: The human player plays with the red (O) pieces.
layout: Which layout to use: standard or hyper. (l)
match: The winning match score. Defaults to 1, or non-match play. (m)
"""


class BackgammonBot(player.Bot):
    """
    A bot for a game of Backgammon(player.bot)

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
                        capture = sub_board.move(*move)
                    possibles.append((self.eval_board(sub_board), play))
                # Choose the play with the highest evaluation.
                possibles.sort(reverse = True)
                self.held_moves = possibles[0][1]
            # Return the move with the correct syntax.
            move = self.held_moves.next_move()
            if move[1] == 'out':
                point = move[0]
                if point > 6:
                    point = 25 - point
                return 'bear {}'.format(point)
            elif move[0] == 'bar':
                return 'enter {}'.format(move[1])
            else:
                return '{} {}'.format(move[0], move[1])
        # Respond to no-move notifications.
        elif prompt.startswith('You have no legal moves'):
            self.game.human.tell('{} has no legal moves.'.format(self.name))
            return ''
        # Raise an error for any other question.
        else:
            raise ValueError('Unexpected question to BackgammonBot: {}'.format(prompt))

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

    def eval_board(self, board):
        """
        Evaluate a board position. (list of int)

        The evaluation is a list of integers. This can be used on it's own or as 
        input to another evaluation function.

        The items in the evaluation list are (in order):
            * The difference in the number of captured pieces.
            * The difference in the number of blots.
            * The difference in direct hits to blots.
            * The difference in indirect hits to blots. (!! Not calcualted correctly)
            * The difference in pip count.
            * The difference in the number of controlled points.
        All are calculated so that higher numbers are better for the bot.

        Parameters:
        board: A board with the position to evaluate. (BackgammonBoard)
        """
        # Find controlled and blot points.
        controlled = {'X': [], 'O': []}
        blots = {'X': [], 'O': []}
        for cell in board.cells.values():
            if cell.location < (0,):
                continue
            if len(cell.contents) > 1:
                controlled[cell.contents[0]].append(cell.location)
            elif len(cell.contents) == 1:
                blots[cell.contents[0]].append(cell.location)
        captured = {piece: board.cells['bar'].contents.count(piece) for piece in 'XO'}
        pip_count = {piece: board.get_pip_count(piece) for piece in 'XO'}
        # Calculate hits.
        direct_hits = {'X': 0, 'O': 0}
        indirect_hits = {'X': 0, 'O': 0}
        for piece in 'XO':
            foe_direction = {'X': -1, 'O': 1}[piece]
            foe_piece = {'X': 'O', 'O': 'X'}[piece]
            for blot in blots[piece]:
                for offset in range(1, 13):
                    try:
                        offcell = board.offset(blot, (offset * foe_direction,))
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
        score.append(len(blots[foe_piece]) - len(blots[my_piece]))
        score.append(direct_hits[foe_piece] - direct_hits[my_piece])
        score.append(indirect_hits[foe_piece] - indirect_hits[my_piece])
        score.append(pip_count[my_piece] - pip_count[foe_piece])
        score.append(len(controlled[my_piece]) - len(controlled[foe_piece]))
        return(score)

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
    player_turn
    set_options
    set_up
    """

    aliases = {'b': 'bear', 'd': 'double', 'e': 'enter'}
    categories = ['Board Games', 'Race Games']
    credits = CREDITS
    layouts = {'hyper': ((24, 1), (23, 1), (22, 1)), 'standard': ((6, 5), (8, 3), (13, 5), (24, 2))}
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
        if self.board.cells['out'].count(piece) == 15:
            result = self.doubling_die
            # Check for gammon/backgammon.
            if other_piece not in self.board.cells['out']:
                if piece == 'X':
                    home = range(1, 7)
                else:
                    home = range(19, 25)
                home_pieces = sum([self.board.cells[point].contents for point in home], [])
                if other_piece in self.board.cells['bar'] or other_piece in home_pieces:
                    result *= 3
                else:
                    result *= 2
        return result 

    def do_bear(self, argument):
        """
        Bear a piece off of the board. (bool)

        Parameters:
        argument: The point or points to bear off from. (str)
        """
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
        points = [loc for loc, cell in self.board.cells.items() if piece in cell and isinstance(loc, int)]
        # Check for all pieces in the player's home.
        if (piece == 'X' and max(points) > 5) or (piece == 'O' and min(points) < 18):
            player.error('You do not have all of your pieces in your home yet.')
        # Check for captured piece
        elif piece in self.board.cells['bar']:
            player.error('You still have a piece on the bar.')
        else:
            # Play any legal moves
            for bear in bears:
                # Get the correct point
                roll = bear
                if bear == 'O':
                    bear = 23 - bear
                # Check for a valid point
                if not self.board.cells[bear]:
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
                self.board.cells['out'].add_piece(self.board.cells[bear].remove_piece())
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
        point = needed_roll - 1
        if piece == 'X':
            point = 23 - point
        # Check for valid roll.
        if needed_roll not in self.rolls:
            player.error('You need to roll a {} to enter on that point.'.format(needed_roll))
            return True
        # Check for a piece to enter.
        elif piece not in self.board.bar.piece:
            player.error('You do not have a piece on the bar.')
            return True
        # Check for a valid entry point.
        end_cell = self.board.cells[(point,)]
        if piece not in end_cell.piece and len(end_cell.piece) > 1:
            player.error('That point is blocked.')
            return True
        # Make the move.
        capture = self.board.move((-1,), (point,))
        self.rolls.remove(needed_roll)
        return self.rolls

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # !! incorrect for match play. Need +=, and maybe reset game.
        # Check human win.
        human_win = self.check_win(self.pieces[self.human.name])
        if human_win:
            self.win_loss_draw[0] = human_win
        bot_win = self.check_win(self.pieces[self.bot.name])
        # Check bot win.
        if bot_win:
            self.win_loss_draw[1] = bot_win
        return max(self.win_loss_draw) >= self.match

    def get_rolls(self):
        """Determine the rolls you can move with from the dice roll. (None)"""
        self.rolls = self.dice.values[:]
        if self.rolls[0] == self.rolls[1]:
            self.rolls.extend(self.rolls)

    def player_turn(self, player):
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
            self.dice.roll()
            self.dice.sort()
            self.get_rolls()
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
        else:
            move = [x - 1 for x in move]
        direction = {'X': -1 , 'O': 1}[player_piece]
        # Convert moves with just the end point.
        if len(move) == 1:
            possible = []
            for maybe in set(self.rolls):
                start = move[0] - maybe * direction
                if (start,) in self.board.cells and player_piece in self.board.cells[(start,)].piece:
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
        start_pieces = self.board.cells[(start,)].piece
        end_pieces = self.board.cells[(end,)].piece
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
        elif player_piece in self.board.bar.piece and start != -1:
            player.error('You re-enter your piece on the bar before making any other move.')
            return True
        elif ((start,), (end,)) not in legal_moves:
            player.error('That move would not allow for the maximum possible play.')
        else:
            # Make the valid move
            capture = self.board.move((start,), (end,))
            self.rolls.remove(abs(start - end))
        # Continue if there are still rolls to handle.
        return self.rolls

    def set_options(self):
        """Define the options for the game. (None)"""
        self.option_set.default_bots = [(BackgammonBot, ())]
        self.option_set.add_option('o', target = 'human_piece', value = 'O', default = 'X',
            question = 'Would you like to play with the O piece? bool')
        self.option_set.add_option('match', ['m'], int, 1, check = lambda x: x > 0,
            question = 'What should be the winning match score (return for 1)? ')
        self.option_set.add_option('layout', ['l'], options.lower, action = 'map', value = self.layouts, 
            default = 'standard',
            question = 'What layout would you like to use (return for standard)? ')

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the board.
        self.board = BackgammonBoard((24,), self.layout)
        # Set up the players.
        self.bot = self.players[-1]
        self.pieces = {self.human.name: self.human_piece}
        if self.human_piece == 'X':
            self.pieces[self.bot.name] = 'O'
        else:
            self.pieces[self.bot.name] = 'X'
        # Set up the dice.
        self.doubling_die = 1
        self.doubling_status = ''
        self.dice = dice.Pool()
        while self.dice.values[0] == self.dice.values[1]:
            self.dice.roll()
        if self.dice.values[0] < self.dice.values[1]:
            self.players.reverse()
        self.get_rolls()


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
        super(BackgammonBoard, self).__init__(24, extra_cells = ['bar', 'out'])
        self.set_up(layout)

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
            for bar_check, location in enumerate(range(1, 25)):
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

        !! The only good discussion of this I can find (www.bkgm.com, about BKG) says it generates
        a tree of moves recursively. Then it scans the tree for legal moves by the maximum use of
        roll criteria. I think what I have would work for that IF it recorded how much of the roll
        was used for each play. Then I could scan for the max easily, and remove not max plays with
        a list comprehension. I think an object for the plays would help track things separately.
        This will require three levels of function: main, generate, recurse.

        !! consider factoring out play generation for the three phases of the game.

        Parameters:
        piece: The piece symbol to get moves for. (str)
        rolls: The rolls to get moves for. (str)
        moves: The moves already made. (list of tuple)
        """
        # Loop through the rolls.
        full_plays = []
        for roll in set(rolls):
            # Get the rolls without the current roll.
            sub_rolls = rolls[:]
            sub_rolls.remove(roll)
            # Generate moves based on the phase of the game.
            if piece in self.bar.piece:
                full_plays = self.get_moves_enter(piece, moves, full_plays, sub_rolls, roll)
            elif all([coord[0] in home or coord == self.out[piece].location for coord in from_cells]):
                full_plays = self.get_moves_home(piece, moves, full_plays, sub_rolls, roll)
            else:
                full_plays = self.get_moves_normal(piece, moves, full_plays, sub_rolls, roll)

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
        if piece != self.cells['bar'].contents[-1]:
            self.cells['bar'].remove_piece(piece)
            self.cells['bar'].add_piece(piece)
        if piece == 'X':
            end_coord = 25 - roll
        else:
            end_coord = roll
        end_cell = self.cells[end_coord]
        if piece in end_cell or len(end_cell) < 2:
            full_plays = self.get_moves_help(piece, 'bar', end_coord, moves, full_plays, sub_rolls, roll)
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
        new_moves = moves + [(point, end_point, roll)]
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

    def get_moves_home(self, piece, moves, full_plays, sub_rolls, roll):
        """
        Get the legal moves when all pieces are home. (list of BackgammonPlay)

        Parameters:
        piece: The piece symbol to get moves for. (str)
        moves: The moves already made. (BackgammonPlay)
        full_plays: The plays already recorded. (list of BackgammonPlay)
        sub_rolls: The rolls to get moves for. (list of int)
        roll: The current roll being moved. (int)
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
            full_plays = self.get_moves_help(piece, coord, 'out', moves, full_plays, sub_rolls, roll)
        elif roll > max_index + 1:
            # Generate bearing off moves with over roll.
            coord = home[max_index]
            full_plays = self.get_moves_help(piece, coord, 'out', moves, full_plays, sub_rolls, roll)
        for home_index in range(6):
            # Generate moves within the home board.
            start = home[home_index]
            end = start + roll * direction
            if 0 <= end <= 23:
                if piece in self.cells[start] and (piece in self.cells[end] or len(self.cells[end]) < 2):
                    full_plays = self.get_moves_help(piece, start, end, moves, full_plays, sub_rolls, roll)
        return full_plays

    def get_moves_normal(self, piece, moves, full_plays, sub_rolls, roll):
        """
        Generate legal moves during normal play. (list of BackgammonPlay)

        Parameters:
        piece: The piece symbol to get moves for. (str)
        moves: The moves already made. (BackgammonPlay)
        full_plays: The plays already recorded. (list of BackgammonPlay)
        sub_rolls: The rolls to get moves for. (list of int)
        roll: The current roll being moved. (int)
        """
        from_cells = [point for point in self.cells if piece in self.cells[point]]
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
            if point == 'bar':
                point = 25
            elif point == 'out':
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
            max_roll = max(play.total_roll for play in plays)
            max_moves = max(len(play) for play in plays)
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
        order_high = list(range(12, 24))
        order_low = list(range(11, -1, -1))
        # Convert the details if the text is for O
        if piece == 'O':
            frame_high = [line[::-1] for line in frame_high]
            frame_low = [line[::-1] for line in frame_low]
            order_high = list(range(0, 12))
            order_low = list(range(23, 11, -1))
        # Get the top half of the board.
        lines = frame_high[:]
        lines.extend(self.board_text(order_high))
        # Get the middle and bottom half of the board.
        lines.append('|             |             |')
        lines.extend(reversed(self.board_text(order_low)))
        lines.extend(frame_low)
        # Include a line for any pieces on the bar.
        if self.cells['bar'].contents:
            lines.extend(['', 'Bar: {}'.format(''.join(self.cells['bar'].contents))])
        # Return the text.
        return '\n'.join(lines)

    def move(self, start, end):
        """
        Move a piece from one cell to another. (object)

        The object returned is any piece that is in the destination cell before the
        move. The parameters should be keys appropriate to cells on the board.

        Parameters:
        start: The location containing the piece to move. (Coordinate)
        end: The location to move the piece to. (Coordinate)
        """
        if not (len(self.cells[end]) < 2 or self.cells[start].contents[0] != self.cells[end].contents[0]):
            raise ValueError('Invalid backgammon move ({}/{}).'.format(start, end))
        capture = super(BackgammonBoard, self).move(start, end)
        self.cells['bar'].add_piece(capture)
        self.legal_plays = []
        return capture

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
        other: A move to add. (tuple or str or int)
        """
        if isinstance(other, tuple) and len(other) == 3:
            new_play = BackgammonPlay()
            new_play.moves = self.moves[:]
            new_play.total_roll = self.total_roll
            new_play.add_move(*other)
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
            return self.moves == other.moves
        else:
            return NotImplemented

    def __hash__(self):
        """Generate an integer has for the play. (int)"""
        return hash(tuple(self.moves))

    def __iter__(self):
        """Iterate over moves not including rolls. (iterator)"""
        return (move[:2] for move in self.moves)

    def __len__(self):
        """Number of moves in the play. (int)"""
        return len(self.moves)

    def add_move(self, start = 0, end = 0, roll = 0):
        """
        Add a move to the play. (None)

        Parameters:
        start: the starting point of the move. (int or str)
        end: the end point of the move. (int or str)
        roll: the roll used for the move. (int)
        """
        self.moves.append((start, end, roll))
        self.moves.sort()
        self.total_roll += roll

    def next_move(self):
        """Return a move to make. (tuple)"""
        self.moves.pop(0)


if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    game = Backgammon(player.Player(name), '')
    game.play()