"""
backgammon_game.py

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


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

FRAME_HIGH = ['  1 1 1 1 1 1   1 2 2 2 2 2  ', '  3 4 5 6 7 8   9 0 1 2 3 4  ', 
    '+-------------+-------------+']

FRAME_LOW = ['+-------------+-------------+',  '  1 1 1                      ', 
    '  2 1 0 9 8 7   6 5 4 3 2 1  ']


class BackgammonBot(player.Bot):
    """
    A bot for a game of Backgammon(player.bot)
    """

    def ask(self, prompt):
        if prompt.strip() == 'What is your move?':
            if self.held_moves:
                move = self.held_moves.pop(0)
            else:
                possibles = []
                board = self.game.board
                for play in board.get_moves(self.piece, self.game.moves):
                    sub_board = board.copy()
                    for move in play:
                        capture = sub_board.move(*move)
                        sub_board.bar.piece.extend(capture)
                    possibles.append((self.eval_board(sub_board), play))
                possibles.sort(reverse = True)
                best = possibles[0][1]
                move = best[0]
                self.held_moves = best[1:]
            if move[1] < (0,):
                return 'bear {}'.format(move[0][0] + 1)
            elif move[0] < (0,):
                return 'enter {}'.format(move[1][0] + 1)
            else:
                return '{} {}'.format(move[0][0] + 1, move[1][0] + 1)
        elif prompt.startswith('You have no legal moves'):
            self.game.human.tell('{} has no legal moves.'.format(self.name))
            return ''
        else:
            raise ValueError('Unexpected question to BackgammonBot: {}'.format(prompt))

    def eval_board(self, board):
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
        if not self.held_moves:
            super(BackgammonBot, self).tell(text)


class Backgammon(game.Game):
    """
    A game of Backgammon. (game.Game)

    Overridden Methods:
    set_up
    """

    aliases = {'b': 'bear', 'd': 'double', 'e': 'enter'}
    categories = ['Board Games', 'Race Games']
    credits = CREDITS
    layouts = {'standard': ((6, 5), (8, 3), (13, 5), (24, 2))}
    name = 'Backgammon'

    def check_win(self, piece):
        other_piece = 'XO'['OX'.index(piece)]
        result = 0
        if len(self.board.out[piece].piece) == 15:
            result = self.doubling_die
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
            player.errpr('Invalid argument to the bear command: {}.'.format(argument))
            return True
        locations = [loc for loc, cell in self.board.cells.items() if piece in cell.piece]
        # Check for all pieces in the player's home.
        if (piece == 'X' and max(locations) > (5,)) or (piece == 'O' and min(locations) < (18,)):
            player.error('You do not have all of your pieces in your home yet.')
        elif piece in self.board.bar.piece:
            player.error('You still have a piece on the bar.')
        else:
            # Play any legal moves
            for roll in rolls:
                point = roll - 1
                if piece == '0':
                    point = 23 - point
                # Check for a valid roll and 
                if not self.board.cells[(point,)].piece:
                    player.error('You do not have a piece on the {} point.'.format(roll))
                    continue
                elif roll in self.moves:
                    self.moves.remove(roll)
                elif roll < max(self.moves):
                    self.moves.remove(max(self.moves))
                else:
                    player.error('There is no valid move for the {} point.'.format(roll))
                    continue
                self.board.out[piece].piece.append(self.board.cells[(point,)].piece.pop())
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
        # Check for valid entry point.
        if needed_roll not in self.moves:
            player.error('You need to roll a {} to enter on that point.'.format(needed_roll))
            return True
        elif piece not in self.board.bar.piece:
            player.error('You do not have a piece on the bar.')
            return True
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
        """Check for the end of the game."""
        human_win = self.check_win(self.pieces[self.human.name])
        if human_win:
            self.win_loss_draw[0] = human_win
        bot_win = self.check_win(self.pieces[self.bot.name])
        if bot_win:
            self.win_loss_draw[1] = bot_win
        return max(self.win_loss_draw) >= self.match

    def get_rolls(self):
        """Determine the rolls you can move with from the dice roll. (None)"""
        self.moves = self.dice.values[:]
        if self.moves[0] == self.moves[1]:
            self.moves.extend(self.moves)

    def player_turn(self, player):
        # !! can move with a piece on the bar. also get moves. but only for human.
        player_piece = self.pieces[player.name]
        player.tell(self.board.get_text(player_piece))
        if not self.moves:
            # !! need to check for doubling.
            self.dice.roll()
            self.dice.sort()
            self.get_rolls()
        player.tell('\nThe roll to you is {}.'.format(', '.join([str(x) for x in self.moves])))
        legal_moves = self.board.get_moves(player_piece, self.moves)
        if not legal_moves:
            player.ask('You have no legal moves. Press enter to continue: ')
            self.moves = []
            return False
        move = player.ask_int_list('\nWhat is your move? ', low = 1, high = 24, valid_lens = [1, 2])
        if isinstance(move, str):
            return self.handle_cmd(move)
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
        start_pieces = self.board.cells[(start,)].piece
        end_pieces = self.board.cells[(end,)].piece
        direction = {'X': -1 , 'O': 1}[player_piece]
        if not (start_pieces and start_pieces[0] == player_piece):
            player.error('You do not have a piece on that starting square.')
            return True
        elif (end - start) * direction not in self.moves:
            player.error('You do not have a die roll matching that move.')
            return True
        elif end_pieces and end_pieces[0] != player_piece and len(end_pieces) > 1:
            player.error('That end point is blocked.')
            return True
        else:
            capture = self.board.move((start,), (end,))
            # !! should this be in board.move()? 
            if capture:
                self.board.bar.piece.extend(capture)
            self.moves.remove(abs(start - end))
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
        self.board = BackgammonBoard((24,), self.layout)
        self.doubling_die = 1
        self.doubling_status = ''
        self.bot = self.players[-1]
        self.pieces = {self.human.name: self.human_piece}
        if self.human_piece == 'X':
            self.pieces[self.bot.name] = 'O'
        else:
            self.pieces[self.bot.name] = 'X'
        self.dice = dice.Pool()
        while self.dice.values[0] == self.dice.values[1]:
            self.dice.roll()
        if self.dice.values[0] < self.dice.values[1]:
            self.players.reverse()
        self.get_rolls()


class BackgammonBoard(board.MultiBoard):
    """
    A board for Backgammon. (board.LineBoard)

    Methods:
    get_moves: Get the legal moves for a given roll. (list)
    """

    def __init__(self, dimensions = (24,), layout = ((6, 5), (8, 3), (13, 5), (24, 2))):
        """
        Set up the grid of cells. (None)

        Paramters:
        dimensions: The dimensions of the board, in cells. (tuple of int)
        """
        super(BackgammonBoard, self).__init__(dimensions)
        self.bar = board.BoardCell((-1,), [])
        self.out = {'X': board.BoardCell((-2,), []), 'O': board.BoardCell((-3,), [])}
        self.cells.update({(-1,): self.bar, (-2,): self.out['X'], (-3,): self.out['O']})
        self.set_up(layout)

    def board_text(self, locations):
        lines = []
        for row in range(5):
            row_text = '| '
            for bar_check, location in enumerate(locations):
                pieces = len(self.cells[(location,)].piece)
                if pieces > row:
                    if row == 0 and pieces > 5:
                        if pieces > 9:
                            row_text += '{} '.format(pieces % 10)
                        elif pieces > 5:
                            row_text += '{} '.format(pieces)
                    elif row == 1 and pieces > 9:
                        row_text += '1 '
                    else:
                        row_text += '{} '.format(self.cells[(location,)].piece[0])
                else:
                    row_text += '{} '.format(':.'[location % 2])
                if bar_check == 5:
                    row_text += '| '
            lines.append(row_text + '|')
        return lines

    def get_moves(self, piece, rolls, moves = None):
        # !! probably not precisely corrent. Partial moves?
        # !! If it can't move them all, it doesn't seem to return any of them.
        # !! but there also will be times when it should return no moves.
        if moves == None:
            moves = []
        full_moves = []
        from_cells = [coord for coord in self.cells if piece in self.cells[coord].piece]
        direction = {'X': -1, 'O': 1}[piece]
        home = {'X': tuple(range(6)), 'O': tuple(range(23, 16, -1))}[piece]
        for roll in set(rolls):
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
        sub_board = self.copy(layout = ())
        capture = sub_board.move(coord, end_coord)
        if capture:
            sub_board.bar.piece.append(capture)
        new_moves = moves + [(coord, end_coord)]
        if sub_rolls:
            sub_moves = sub_board.get_moves(piece, sub_rolls, new_moves)
            if sub_moves:
                full_moves.extend(sub_moves)
            else:
                full_moves.append(new_moves)
        else:
            full_moves.append(new_moves)
        return full_moves

    def get_pip_count(self, piece):
        points = []
        for cell in self.cells.values():
            point = cell.location[0] + 1
            if point == 0:
                point = 25
            elif point < 0:
                point = 0
            elif piece == 'O':
                point = 25 - point
            points.extend([point] * cell.piece.count(piece))
        return sum(points)

    def get_text(self, piece):
        """
        Get the board text from a particular player's perspective. (str)

        Parameters:
        piece: The piece for the player to display. (str)
        """
        frame_high = FRAME_HIGH
        frame_low = FRAME_LOW
        order_high = list(range(12, 24))
        order_low = list(range(11, -1, -1))
        if piece == 'O':
            frame_high = [line[::-1] for line in frame_high]
            frame_low = [line[::-1] for line in frame_low]
            order_high = list(range(0, 12))
            order_low = list(range(23, 11, -1))
        lines = frame_high[:]
        lines.extend(self.board_text(order_high))
        lines.append('|             |             |')
        lines.extend(reversed(self.board_text(order_low)))
        lines.extend(frame_low)
        if self.bar.piece:
            lines.extend(['', 'Bar: {}'.format(''.join(self.bar.piece))])
        return '\n'.join(lines)

    def set_up(self, layout):
        for location, count in layout:
            self.cells[(location - 1,)].piece = ['X'] * count
            self.cells[(24 - location,)].piece = ['O'] * count

if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    bg_board = BackgammonBoard()
    bg_board = BackgammonBoard(layout = ((24, 1), (23, 1), (22, 1)))
    print(bg_board.get_text('X'))
    print()
    print(bg_board.get_text('O'))
    print()
    while True:
        print(bg_board.get_text('X'))
        print()
        pip_x = bg_board.get_pip_count('X')
        pip_o = bg_board.get_pip_count('O')
        print('Pip Counts: X = {}, O = {}.\n'.format(pip_x, pip_o))
        move = input('Move? ')
        print()
        try:
            start, end = [(int(x) - 1,) for x in move.split()]
        except ValueError:
            break
        capture = bg_board.move(start, end)
        if capture:
            bg_board.bar.piece.extend(capture)
    test_moves = bg_board.get_moves('O', [1, 1, 1, 1])
    print(test_moves)