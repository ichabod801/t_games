"""
backgammon_game.py

A game of Backgammon and related variants.

!! reword attributes to roll (the number on a die), move (one roll's move), 
    and play (a full turn of moves).

?? Should the move validation be done by the board?

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

# The rules of Backgammon. !! not finished
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
    held_moves: Moves planned but not yet made through ask. (list of tuple)

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
            if self.held_moves:
                # Play any planned moves.
                move = self.held_moves.pop(0)
            else:
                # Evaluate all the legal plays.
                possibles = []
                board = self.game.board
                for play in board.get_moves(self.piece, self.game.moves):
                    sub_board = board.copy()
                    for move in play:
                        capture = sub_board.move(*move)
                        sub_board.bar.piece.extend(capture)
                    possibles.append((self.eval_board(sub_board), play))
                # Choose the play with the highest evaluation.
                possibles.sort(reverse = True)
                best = possibles[0][1]
                # Split out any held moves.
                move = best[0]
                self.held_moves = best[1:]
            # Return the move with the correct syntax.
            if move[1] < (0,):
                return 'bear {}'.format(move[0][0] + 1)
            elif move[0] < (0,):
                return 'enter {}'.format(move[1][0] + 1)
            else:
                return '{} {}'.format(move[0][0] + 1, move[1][0] + 1)
        # Respond to no-move notifications.
        elif prompt.startswith('You have no legal moves'):
            self.game.human.tell('{} has no legal moves.'.format(self.name))
            return ''
        # Raise an error for any other question.
        else:
            raise ValueError('Unexpected question to BackgammonBot: {}'.format(prompt))

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
            if len(cell.piece) > 1:
                controlled[cell.piece[0]].append(cell.location)
            elif len(cell.piece) == 1:
                blots[cell.piece[0]].append(cell.location)
        captured = {piece: board.bar.piece.count(piece) for piece in 'XO'}
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
                    if foe_piece in offcell.piece:
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
        self.held_moves = []
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
        if len(self.board.out[piece].piece) == 15:
            result = self.doubling_die
            # Check for gammon/backgammon.
            if not len(self.board.out[other_piece].piece):
                if other_piece in self.board.bar.piece:
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
            rolls = [int(word) for word in words]
        except ValueError:
            # Warn on bad arguments.
            player.error('Invalid argument to the bear command: {}.'.format(argument))
            return True
        locations = [loc for loc, cell in self.board.cells.items() if piece in cell.piece]
        # Check for all pieces in the player's home.
        if (piece == 'X' and max(locations) > (5,)) or (piece == 'O' and min(locations) < (18,)):
            player.error('You do not have all of your pieces in your home yet.')
        # Check for captured piece
        elif piece in self.board.bar.piece:
            player.error('You still have a piece on the bar.')
        else:
            # Play any legal moves
            for roll in rolls:
                # Get the correct point
                point = roll - 1
                if piece == '0':
                    point = 23 - point
                # Check for a valid point
                if not self.board.cells[(point,)].piece:
                    player.error('You do not have a piece on the {} point.'.format(roll))
                    continue
                # Remove the correct roll.
                elif roll in self.moves:
                    self.moves.remove(roll)
                elif roll < max(self.moves):
                    self.moves.remove(max(self.moves))
                else:
                    # Warn for no valid roll.
                    player.error('There is no valid move for the {} point.'.format(roll))
                    continue
                # Bear off the piece
                self.board.out[piece].piece.append(self.board.cells[(point,)].piece.pop())
        # Continue the turn if there are still rolls to move.
        return self.moves

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
        if needed_roll not in self.moves:
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
        self.board.bar.piece.extend(capture)
        self.moves.remove(needed_roll)
        return self.moves

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
        self.moves = self.dice.values[:]
        if self.moves[0] == self.moves[1]:
            self.moves.extend(self.moves)

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # !! can move with a piece on the bar. but only for human.
        # Get the player.
        player_piece = self.pieces[player.name]
        # Show the board.
        player.tell(self.board.get_text(player_piece))
        # Roll the dice if it's the start of the turn.
        if not self.moves:
            self.dice.roll()
            self.dice.sort()
            self.get_rolls()
        player.tell('\nThe roll to you is {}.'.format(', '.join([str(x) for x in self.moves])))
        # Check for no legal moves
        # !! if this is just for one roll, I don't need to do move validation. Just check if it's in
        # !! legal moves. However, this would lose detail in the error messages.
        legal_moves = self.board.get_moves(player_piece, self.moves)
        if not legal_moves:
            player.ask('You have no legal moves. Press enter to continue: ')
            self.moves = []
            return False
        # Get the player's move.
        move = player.ask_int_list('\nWhat is your move? ', low = 1, high = 24, valid_lens = [1, 2])
        if isinstance(move, str):
            return self.handle_cmd(move)
        # Convert moves with just the end point.
        if len(move) == 1:
            possible = []
            for maybe in set(self.moves):
                start = move[0] + maybe
                if player_piece in self.board.cells[(start,)].piece:
                    possible.append(start)
            if len(possible) == 1:
                start = possible[0]
                end = move[0]
            elif len(possible) > 1:
                player.error('That move is ambiguous.')
                return True
            else:
                player.error('There is no legal move to that point.')
                return True
        else:
            start, end = [x - 1 for x in move]
        # !! Need to handle one move that represents two rolls.
        # Get the details of the move.
        start_pieces = self.board.cells[(start,)].piece
        end_pieces = self.board.cells[(end,)].piece
        direction = {'X': -1 , 'O': 1}[player_piece]
        # Check for valid staring point.
        if not (start_pieces and start_pieces[0] == player_piece):
            player.error('You do not have a piece on that starting point.')
            return True
        # Check for valid die roll.
        elif (end - start) * direction not in self.moves:
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
        else:
            # Make the valid move
            capture = self.board.move((start,), (end,))
            # !! should this be in board.move()? Yes.
            if capture:
                self.board.bar.piece.extend(capture)
            self.moves.remove(abs(start - end))
        # Continue if there are still rolls to handle.
        return self.moves

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


class BackgammonBoard(board.MultiBoard):
    """
    A board for Backgammon. (board.LineBoard)

    Attributes:
    bar: The cell holding captured pieces. (board.BoardCell)
    out: The cells holding pieces that have been borne off. (dict)

    Methods:
    board_text: Generate a text lines for the pieces on the board. (list of str)
    get_moves: Get the legal moves for a given set of rolls. (list)
    get_moves_help: Recurse get_move using another board. (list of tuple)
    get_pip_count: Get the pip count for a given player. (int)
    get_text: Get the board text from a particular player's perspective. (str)

    Overridden Methods:
    __init__
    """

    def __init__(self, dimensions = (24,), layout = ((6, 5), (8, 3), (13, 5), (24, 2))):
        """
        Set up the grid of cells. (None)

        The layout parameter is a tuple of two-integer tuples. Each pair of integers 
        indicate a point and the number of piece on that point. This is only provided 
        for one player, and then done symetrically for the other player.

        Paramters:
        dimensions: The dimensions of the board, in cells. (tuple of int)
        layout: The initial layout of the pieces. (tuple of tuple)
        """
        # Set up the base board.
        super(BackgammonBoard, self).__init__(dimensions)
        # Set up the special cells.
        self.bar = board.BoardCell((-1,), [])
        self.out = {'X': board.BoardCell((-2,), []), 'O': board.BoardCell((-3,), [])}
        self.cells.update({(-1,): self.bar, (-2,): self.out['X'], (-3,): self.out['O']})
        # Place the starting pieces.
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
            for bar_check, location in enumerate(locations):
                pieces = len(self.cells[(location,)].piece)
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
                        row_text += '{} '.format(self.cells[(location,)].piece[0])
                else:
                    # Handle board design.
                    row_text += '{} '.format(':.'[location % 2])
                if bar_check == 5:
                    # Handle the bar.
                    row_text += '| '
            lines.append(row_text + '|')
        return lines

    def get_moves(self, piece, rolls, moves = None):
        """
        Get the legal moves for a given set of rolls. (list)

        This method recurses using get_moves_help.

        Parameters:
        piece: The piece symbol to get moves for. (str)
        rolls: The rolls to get moves for. (str)
        moves: The moves already made. (list of tuple)
        """
        # Handle default moves.
        if moves == None:
            moves = []
        # Loop through the rolls.
        full_moves = []
        from_cells = [coord for coord in self.cells if piece in self.cells[coord].piece]
        direction = {'X': -1, 'O': 1}[piece]
        home = {'X': tuple(range(6)), 'O': tuple(range(23, 16, -1))}[piece]
        for roll in set(rolls):
            # Get the rolls without the current roll.
            sub_rolls = rolls[:]
            sub_rolls.remove(roll)
            if piece in self.bar.piece:
                # Generate moves when a piece is captured.
                coord = self.bar.location
                if piece != self.bar.piece[-1]:
                    self.bar.piece.remove(piece)
                    self.bar.piece.append(piece)
                if piece == 'X':
                    end_coord = (23 - roll,)
                else:
                    end_coord = (roll - 1,)
                end_cell = self.cells[end_coord]
                if piece in end_cell.piece or len(end_cell.piece) < 2:
                    full_moves = self.get_moves_help(piece, coord, end_coord, moves, full_moves, sub_rolls)
            elif all([coord[0] in home or coord == self.out[piece].location for coord in from_cells]):
                # Generate bearing off moves.
                coord = (home[roll - 1],)
                end_coord = self.out[piece].location
                max_index = [ndx for ndx, pt in enumerate(home) if piece in self.cells[(pt,)].piece][-1]
                if piece in self.cells[coord].piece:
                    full_moves = self.get_moves_help(piece, coord, end_coord, moves, full_moves, sub_rolls)
                elif roll > max_index:
                    coord = (home[max_index],)
                    full_moves = self.get_moves_help(piece, coord, end_coord, moves, full_moves, sub_rolls)
                for home_index in range(roll, max_index + 1):
                    coord = (home[home_index],)
                    end_coord = (coord[0] + roll * direction,)
                    full_moves = self.get_moves_help(piece, coord, end_coord, moves, full_moves, sub_rolls)
            else:
                # Generate moves with no special conditions.
                for coord in from_cells:
                    end_coord = coord + (roll * direction,)
                    if not ((0,) <= coord < self.dimensions and (0,) <= end_coord < self.dimensions):
                        continue
                    end_cell = self.cells[end_coord]
                    if piece not in end_cell.piece and len(end_cell.piece) > 1:
                        continue
                    full_moves = self.get_moves_help(piece, coord, end_coord, moves, full_moves, sub_rolls)
        # Eliminate duplicate moves.
        final_moves = []
        sorted_moves = []
        for move in full_moves:
            if move not in final_moves and list(sorted(move)) not in sorted_moves:
                final_moves.append(move)
                sorted_moves.append(list(sorted(move)))
        return final_moves

    def get_moves_help(self, piece, coord, end_coord, moves, full_moves, sub_rolls):
        """
        Recurse the get_move method by creating another board. (list of tuple)

        Parameters:
        piece: The piece symbol to get moves for. (str)
        coord: The starting point of the move. (tuple of int)
        end_coord: The ending point of the move. (tuple of int)
        moves: The moves already made. (list of tuple)
        full_moves: The moves already recorded. (list of tuple)
        sub_rolls: The rolls to get moves for. (str)
        """
        # Create a board with the move.
        sub_board = self.copy(layout = ())
        capture = sub_board.move(coord, end_coord)
        if capture:
            sub_board.bar.piece.append(capture)
        # Add to the move to the moves so far.
        new_moves = moves + [(coord, end_coord)]
        if sub_rolls:
            # Recurse if necessary
            sub_moves = sub_board.get_moves(piece, sub_rolls, new_moves)
            if sub_moves:
                full_moves.extend(sub_moves)
            else:
                # Capture partial moves.
                full_moves.append(new_moves)
        else:
            # Termination of recursion
            full_moves.append(new_moves)
        # Return the moves back up the recursion.
        return full_moves

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
            point = cell.location[0] + 1
            if point == 0:
                point = 25
            elif point < 0:
                point = 0
            elif piece == 'O':
                point = 25 - point
            # Get the pip count for each piece.
            points += point * cell.piece.count(piece)
        return points

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
        if self.bar.piece:
            lines.extend(['', 'Bar: {}'.format(''.join(self.bar.piece))])
        # Return the text.
        return '\n'.join(lines)

    def set_up(self, layout):
        """
        Put the starting pieces on the board. (None)

        See __init__ for the details of the layout parameter.

        Parameters:
        layout: The pieces counts and the points to play them on. (tuple of tuple)
        """
        # Layout the pieces for X, and mirrored for O.
        for location, count in layout:
            self.cells[(location - 1,)].piece = ['X'] * count
            self.cells[(24 - location,)].piece = ['O'] * count


if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    game = Battleships(player.Player(name), '')
    game.play()