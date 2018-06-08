"""
solitaire.py

Base class for solitaire games.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
Solitaire: A generalized solitaire game. (game.game)
MultiSolitaire: A game of solitaire that uses multiple decks. (Solitaire)
"""

import t_games.cards as cards
import t_games.game as game
from t_games.card_games.solitaire_games.rule_checkers import *

class Solitaire(game.Game):
    """
    A generalized solitaire game. (game.game)

    As an example of how this generally works: the foo command is handled by
    the do_foo method, which parse the command and uses the foo_check method
    to confirm a valid move. The foo_check method checks basic rules common
    to all games, and then uses the foo_checker attribute (a list of
    functions) to check rules specific to the game.

    Attributes:
    build_checkers: Functions for determining valid builds. (list of callable)
    cells: Holding spaces for manuevering cards. (list of Card)
    deck: The deck of cards for the game. (cards.TrackingDeck)
    dealers: The deal functions for setting up the tableau. (list of callable)
    foundations: The piles to fill to win the game. (list of list of Card)
    free_checkers: Functions for determining valid cell moves. (list of callable)
    match_checkers: Functions for determining valid matches. (list of callable)
    max_passes: The number of allowed passes through the stock. (int)
    moves: The moves taken in the game. (list of list)
    num_cells: The number of cells in the game. (int)
    reserve: Piles where building is not permitted. (list of list of Card)
    sort_checkers: Functions for validating foundation moves. (list of callable)
    stock: A face down pile of cards for later play. (list of Card)
    stock_passes: The number of times the waste has been gone through. (int)
    tableau: The main playing area. (list of list of card.TrackingCard)
    turn_count: The number of cards to turn from the stock each time. (int)
    undo_count: The number of undos taken in the game. (int)
    waste: A face up pile of cards that can be played from. (list of Card)
    wrap_ranks: Flag for building by rank wrappng from king to ace. (bool)

    Methods:
    build_check: Check for a valid build. (bool)
    cell_text: Generate the text for the cards in cells. (str)
    deal: Deal the initial set up for the game. (None)
    do_auto: Automatically play cards into the foundations. (bool)
    do_build: Build card(s) into stacks on the tableau. (bool)
    do_free: Move a card to one of the free cells. (bool)
    do_lane: Move a card into an empty lane. (None)
    do_match: Match two cards and discard them. (None)
    do_sort: Move a card to the foundation. (bool)
    do_turn: Turn cards from the stock into the waste. (bool)
    do_undo: Undo one or more previous moves. (bool)
    find_foundation: Find the foundation a card should sort to. (list of Card)
    foundation_text: Generate the text for the foundation piles. (str)
    free_check: Check that a card can be moved to a free cell. (bool)
    game_over: Check for the foundations being full. (bool)
    guess: Guess what move to make for a particular card. (None)
    lane_check: Check for a valid move into a lane. (bool)
    match_check: Check for a valid match of two cards. (bool)
    reserve_text: Generate text for the reserve piles. (str)
    set_solitaire: Special initialization for solitaire games. (None)
    set_up: Set up the game. (None)
    sort_check: Check for a valid sort. (bool)
    stack_check: Check for a valid stack to move. (bool)
    stock_text: Generate text for the stock and waste. (str)
    super_stack: Find and validate any stack being moved. (list of Card)
    tableau_text: Generate text for the tableau piles. (str)
    transfer: Move a stack of cards from one game location to another. (None)

    Overridden Methods:
    __str__
    default
    set_options
    set_up
    """

    aliases = {'a': 'auto', 'b': 'build', 'f': 'free', 'l': 'lane', 'm': 'match', 'otto': 'auto', 
        's': 'sort', 'q': 'quit', 't': 'turn', 'u': 'undo'}
    name = 'Solitaire Base'
    
    def __str__(self):
        """
        Human readable text representation. (str)
        """
        lines = ['']
        # foundations
        lines.append(self.foundation_text())
        # cells
        if self.num_cells:
            lines.append(self.cell_text())
        # tableau
        lines.append(self.tableau_text())
        # reserve
        if self.reserve:
            lines.append(self.reserve_text())
        # stock and waste
        if self.stock or self.waste:
            lines.append(self.stock_text())
        return '\n\n'.join(lines) + '\n'
    
    def build_check(self, mover, target, moving_stack, show_error = True):
        """
        Check for a valid build. (bool)
        
        Parameters:
        mover: The card to move. (Card)
        target: The destination card. (Card)
        moving_stack: The stack of cards that would move with mover. (Card)
        show_error: A flag for displaying why the build failed. (bool)
        """
        error = ''
        # check for valid destination
        if target.game_location not in self.tableau or target != target.game_location[-1]:
            error = 'The destination (the {}) is not on top of a tableau pile.'.format(target.name)
        # check for moving foundation cards
        elif mover.game_location in self.foundations:
            error = 'Cards may not be moved from the foundation.'
        # check for face down cards
        elif not mover.up:
            error = 'The {} is face down and cannot be moved.'.format(mover.name)
        # check for a valid stack to move
        elif not moving_stack:
            error = '{} is not the base of a movable stack.'.format(mover)
        # check valid stack
        else:
            error = self.build_pair(mover, target)
            if not error:
                for checker in self.build_checkers:
                    error = checker(self, mover, target, moving_stack)
                    if error:
                        break
        # handle determination
        if error and show_error:
            self.human.error(error)
        return not error
        
    def build_pair(self, mover, target):
        """
        Check for a valid pair of building cards. (str)
        
        Returns any error resulting from the build.
        
        Parameters:
        mover: The card to move. (Card)
        target: The destination card. (Card)
        """
        error = ''
        for checker in self.pair_checkers:
            error = checker(self, mover, target)
            if error:
                break
        return error
    
    def cell_text(self):
        """Generate the text for the cards in cells. (str)"""
        return ' '.join([str(card) for card in self.cells])

    def deal(self):
        """Deal the initial set up for the game. (None)"""
        for dealer in self.dealers:
            dealer(self)

    def default(self, line):
        """
        Handle unrecognized commands. (bool)

        line: The user's input. (str)
        """
        cards = self.deck.card_re.findall(line)
        if not cards:
            self.human.error('I do not recognize that command.')
        elif len(cards) == 1:
            return self.guess(cards[0])
        elif len(cards) == 2:
            mover, target = [self.deck.find(card) for card in cards]
            moving_stack = self.super_stack(mover)
            if self.build_check(mover, target, moving_stack, False):
                self.do_build('{} {}'.format(mover, target))
            elif self.match_check([mover, target], False):
                self.do_match('{} {}'.format(mover, target))
            else:
                self.human.error('There are no legal moves using the {} and the {}.'.format(mover, target))
        else:
            self.human.error("I don't know what to do with that many cards.")
        
    def do_auto(self, max_rank):
        """
        Automatically play cards into the foundations. (bool)
        
        Parameters:
        max_rank: The maximum rank to auto sort. (str)
        """
        # convert max rank to int
        max_rank = max_rank.upper()
        if max_rank.strip() == '':
            max_rank = len(self.deck.ranks) - 1
        elif max_rank in self.deck.ranks:
            max_rank = self.deck.ranks.index(max_rank)
        else:
            self.human.error('There was an error: the rank specified is not in the deck.')
            return True
        # loop until there are no sortable cards
        while True:
            # reset loop
            sorts = 0
            # check free cells
            for card in self.cells:
                card_foundation = self.find_foundation(card)
                if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                    self.do_sort(str(card))
                    sorts += 1
            # check tableau
            for pile in self.tableau:
                if pile:
                    card = pile[-1]
                    card_foundation = self.find_foundation(card)
                    if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                        self.do_sort(str(card))
                        sorts += 1
            # check the waste
            if self.waste:
                card = self.waste[-1]
                card_foundation = self.find_foundation(card)
                if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                    self.do_sort(str(card))
                    sorts += 1
            # check the reserve
            for pile in self.reserve:
                if pile:
                    card = pile[-1]
                    card_foundation = self.find_foundation(card)
                    if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                        self.do_sort(str(card))
                        sorts += 1
            if not sorts:
                break
        return False
    
    def do_build(self, arguments):
        """
        Build card(s) into stacks on the tableau. (bool)
        
        Parameters:
        arguments: The card to move and the card to move it onto. (str)
        """
        # parse the arguments
        card_arguments = self.deck.card_re.findall(arguments.upper())
        if len(card_arguments) != 2:
            self.human.error('Invalid arguments to build command: {!r}.'.format(arguments))
            return True
        mover, target = card_arguments
        # get the details on all the cards
        mover = self.deck.find(mover)
        target = self.deck.find(target)
        moving_stack = self.super_stack(mover)
        # check for a valid move
        if self.build_check(mover, target, moving_stack):
            self.transfer(moving_stack, target.game_location)
            return False
        else:
            return True
        
    def do_free(self, card):
        """
        Move a card to one of the free cells. (bool)
        
        Parameters:
        card: The card to be freed. (str)
        """
        # parse the arguments
        card_arguments = self.deck.card_re.findall(card.upper())
        if len(card_arguments) != 1:
            self.human.error('Invalid arguments to build command: {!r}.'.format(arguments))
            return True
        # get the details on the card to be freed.
        card = self.deck.find(card_arguments[0])
        # free the card
        if self.free_check(card):
            self.transfer([card], self.cells)
            return False
        else:
            return True
        
    def do_lane(self, card):
        """
        Move a card into an empty lane. (bool)
        
        Parameters:
        card: The string identifying the card. (str)
        """
        # get the card and the cards to be moved
        if not self.deck.card_re.match(card):
            self.human.error('Invalid card passed to lane command: {!r}.'.format(card))
            return True
        card = self.deck.find(card)
        moving_stack = self.super_stack(card)
        # check for validity and move
        if self.lane_check(card, moving_stack):
            self.transfer(moving_stack, self.tableau[self.tableau.index([])])
            return False
        else:
            return True

    def do_match(self, cards):
        """
        Match two cards and discard them.

        Parameters:
        cards: The cards being matched. (str)
        """
        cards = self.deck.card_re.findall(cards)
        if len(cards) != 2:
            self.human.error('You must provide two valid cards to the match command.')
            return True
        cards = [self.deck.find(card) for card in cards]
        if self.match_check(cards):
            self.transfer([cards[0]], self.foundations[0])
            self.transfer([cards[1]], self.foundations[0])
    
    def do_sort(self, card):
        """
        Move a card to the foundation. (bool)
        
        Parameters:
        card: The card being moved. (str)
        """
        # get the card
        if not self.deck.card_re.match(card):
            self.human.error('Invalid card passed to sort command: {!r}.'.format(card))
            return True
        card = self.deck.find(card)
        foundation = self.find_foundation(card)
        if self.sort_check(card, foundation):
            self.transfer([card], foundation)
            return False
        else:
            return True
    
    def do_turn(self, arguments):
        """
        Turn cards from the stock into the waste. (bool)

        Parameters:
        arguments: The (ignored) arguments to the turn command. (str)
        """
        if self.stock_passes != self.max_passes:
            # put the waste back in the stock if necessary
            if not self.stock:
                self.transfer(self.waste[:], self.stock, face_up = False)
                self.stock.reverse()
            # flip over cards turn count cards
            for card_ndx in range(self.turn_count):
                self.transfer(self.stock[-1:], self.waste, undo_ndx = card_ndx)
                # stop when the stock runs out
                if not self.stock:
                    break
            if not self.stock:
                self.stock_passes += 1
            return False
        else:
            self.human.error('You may not make any more passes through the stock.')
            return True
    
    def do_undo(self, num_moves):
        """
        Undo one or more previous moves. (bool)
        
        Parameters:
        num_moves: The number of moves to undo. (str)
        """
        if not num_moves.strip():
            num_moves = 1
        num_moves = int(num_moves)
        moves_undone = False
        for move_ndx in range(num_moves):
            # check for there being a move to undo.
            if self.moves:
                # update move tracking
                move_stack, old_location, new_location, undo_ndx, flip = self.moves.pop()
                self.undo_count += 1
                moves_undone = True
                # undo the move
                if flip:
                    old_location[-1].up = False
                self.transfer(move_stack, old_location, track = False)
                if undo_ndx:
                    self.undo_count -= 1
                    self.do_undo()
            # no move to undo
            else:
                self.human.error('There are no moves to undo.')
                break
        return not moves_undone
            
    def find_foundation(self, card):
        """Determine which foundation a card should sort to. (list of Card)"""
        return self.foundations[self.deck.suits.index(card.suit)]
    
    def foundation_text(self):
        """Generate the text for the foundation piles. (str)"""
        return ' '.join([str(pile[-1]) for pile in self.foundations if pile])
    
    def free_check(self, card, show_error = True):
        """
        Check that a card can be moved to a free cell. (bool)
        
        Parameters:
        card: The card to be freed. (Card)
        show_error: A flag for showing why the card can't be freed. (bool)
        """
        error = ''
        # check for open cells
        if len(self.cells) == self.num_cells:
            error = 'There are no free cells to place the {} into.'.format(card.name.lower())
        # check for foundation card
        elif card.game_location in self.foundations:
            error = 'Cards cannot be freed from the foundation.'
        # check for blocked card
        elif card.game_location[-1] != card:
            error = 'The {} is not available to be freed.'.format(card.name)
        # check game specific rules
        else:
            for checker in self.free_checkers:
                error = checker(self, card)
                if error:
                    break
        # handle determination
        if error and show_error:
            print(error)
        return not error

    def game_over(self):
        """Check for the foundations being full. (bool)"""
        check = sum([len(foundation) for foundation in self.foundations])
        target = len(self.deck.cards) + len(self.deck.in_play) + len(self.deck.discards)
        if check == target:
            message = 'Congratulations! You won in {} moves (with {} undos), for a score of {}.'
            moves = len(self.moves) + 2 * self.undo_count
            self.human.tell(message.format(moves, self.undo_count, self.scores[self.human.name]))
            self.win_loss_draw[0] = 1
            return True
        else:
            return False
    
    def guess(self, card):
        """
        Guess what move to make for a particular card. (None)
        
        Parameters:
        card: The card to move. (str)
        """
        # get the card.
        card = self.deck.find(card)
        # check sorting
        if self.foundations and self.sort_check(card, self.find_foundation(card), False):
            self.do_sort(str(card))
        else:
            # check building
            moving_stack = self.super_stack(card)
            for pile in self.tableau:
                if pile and self.build_check(card, pile[-1], moving_stack, False):
                    self.do_build('{} {}'.format(str(card), str(pile[-1])))
                    break
            else:
                # check freeing
                if card.game_location is not self.cells and self.free_check(card, False):
                    self.do_free(str(card))
                # check laning
                elif self.lane_check(card, moving_stack, False):
                    self.do_lane(str(card))
                else:
                    # error out if nothing else works
                    print('There are no valid moves for the {}.'.format(card.name))
    
    def lane_check(self, card, moving_stack, show_error = True):
        """
        Check for a valid move into a lane. (bool)
        
        Parameters:
        card: The card to move into the lane. (Card)
        moving_stack: The cards on top of the card moving. (list of Card)
        show_error: A flag for showing why the card can't be moved. (bool)
        """
        error = ''
        # check for sorted cards
        if card.game_location in self.foundations:
            error = 'The {} is sorted and cannot be moved.'.format(card.name)
        # check for face down cards
        elif not card.up:
            error = 'The {} is face down and cannot be moved.'.format(card.name)
        # check for open lanes
        elif not self.tableau.count([]):
            error = 'There are no open lanes.'
        # check for a valid stack
        elif not moving_stack:
            error = 'The {} is not the base of a valid stack to move.'.format(card.name)
        # check game specific rules
        else:
            for checker in self.lane_checkers:
                error = checker(self, card, moving_stack)
                if error:
                    break
        # handle determination
        if error and show_error:
            self.human.error(error)
        return not error

    def match_check(self, cards, show_error = True):
        """
        Check ofr a valid match of two cards. (bool)

        Parameters:
        cards: The two cards being moved. (list of card.TrackingCard)
        show_error: A flag for showing why the card can't be moved. (bool)
        """
        error = ''
        # check for sorted cards
        if cards[0].game_location in self.foundations:
            error = 'The {} is sorted and cannot be moved.'.format(cards[0].name)
        elif cards[1].game_location in self.foundations:
            error = 'The {} is sorted and cannot be moved.'.format(cards[1].name)
        # check for face down cards
        elif not cards[0].up:
            error = 'The {} is face down and cannot be moved.'.format(cards[0].name)
        elif not cards[1].up:
            error = 'The {} is face down and cannot be moved.'.format(cards[1].name)
        # check game specific rules
        else:
            for checker in self.match_checkers:
                error = checker(self, cards)
                if error:
                    break
        # handle determination
        if error and show_error:
            self.human.error(error)
        return not error

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        The return value is a flag for the player's turn being done.

        Parameters:
        player: The player whose turn it is. (Player)
        """
        player.tell(self)
        move = player.ask('What is your move? ')
        keep_playing = self.handle_cmd(move)
        move_count = len(self.moves) + 2 * self.undo_count
        sorted_count = sum([len(foundation) for foundation in self.foundations])
        self.scores[self.human.name] = 801 - move_count + sorted_count * 2
    
    def reserve_text(self):
        """Generate text for the reserve piles. (str)"""
        reserve_text = []
        for pile in self.reserve:
            if pile:
                reserve_text.append(str(pile[-1]))
            else:
                reserve_text.append('  ')
        return ' '.join(reserve_text)

    def set_checkers(self):
        """Set the game specific rules. (None)"""
        # checkers
        self.build_checkers = []
        self.free_checkers = []
        self.lane_checkers = []
        self.match_checkers = [match_none]
        self.pair_checkers = []
        self.sort_checkers = []
        # dealers
        self.dealers = [deal_free]

    def set_options(self):
        """Handle game options and set the player list. (None)"""
        self.options = {}

    def set_solitaire(self):
        """
        Special initialization for solitaire games. (None)
        
        For an ulimited number of passes through the stock, set max_passes to -1.
        """
        options = {'deck-specs': [], 'num-tableau': 7, 'num-foundations': 4, 'num-reserve': 0,
            'num-cells': 0, 'turn-count': 3, 'max-passes': -1, 'wrap-ranks': False}
        options.update(self.options)
        # initialize specified attributes
        self.num_cells = options['num-cells']
        self.wrap_ranks = options['wrap-ranks']
        self.turn_count = options['turn-count']
        self.max_passes = options['max-passes']
        # initialize derived attributes
        self.deck = cards.TrackingDeck(self, *options['deck-specs'])
        deal_num = -1
        deal_text_index = self.option_set.settings_text.find('deal-num')
        if deal_text_index != -1:
            self.option_set.settings_text = self.option_set.settings_text[:(deal_text_index - 1)]
        if self.raw_options.lower() != 'none':
            prompt = 'Enter the deal number, or return for a random deal: '
            deal_num = self.human.ask_int(prompt, low = 1, default = -1, cmd = False)
        if deal_num == -1:
            deal_num = None
        else:
            self.option_set.settings_text += ' deal-num={}'.format(deal_num)
        self.deck.shuffle(number = deal_num)
        self.tableau = [[] for ndx in range(options['num-tableau'])]
        self.foundations = [[] for ndx in range(options['num-foundations'])]
        self.reserve = [[] for ndx in range(options['num-reserve'])]
        # initialize default attributes
        # piles
        self.cells = []
        self.stock = []
        self.stock_passes = 0
        self.waste = []
        # undo history
        self.moves = []
        self.undo_count = 0
        self.commands = []
        # game specific rules
        self.set_checkers()

    def set_up(self):
        """Set up the game. (None)"""
        self.set_solitaire()
        self.deal()
    
    def sort_check(self, card, foundation, show_error = True):
        """
        Check for a valid sort. (bool)
        
        Parameters:
        card: The card to be sorted. (Card)
        foundation: The target foundation. (list of Card)
        show_error: A flag for showing why the card can't be sorted. (bool)
        """
        error = ''
        # check for moving foundation cards
        if card.game_location in self.foundations:
            error = 'The {} is already sorted.'.format(card.name)
        # check for face down cards
        elif not card.up:
            error = 'The {} is face down and cannot be sorted.'.format(card.name)
        # check for blocked cards
        elif (card.game_location in self.tableau + self.reserve + [self.waste] 
            and card.game_location[-1] != card):
            error = 'The {} is blocked and cannot be sorted.'.format(card.name)
        # check game specific rules
        else:
            for checker in self.sort_checkers:
                error = checker(self, card, foundation)
                if error:
                    break
        # handle determination
        if error and show_error:
            print(error)
        return not error
    
    def stack_check(self, stack):
        """
        Check for a valid stack to move. (bool)
        
        Parameters:
        stack: The stack of cards to check. (list of Card)
        """
        valid = True
        if len(stack) > 1:
            for card_ndx, card in enumerate(stack[:-1]):
                next_card = stack[card_ndx + 1]
                if self.build_pair(next_card, card): # note that build_pair returns an error str if invalid
                    valid = False
                    break
        return valid
    
    def stock_text(self):
        """Generate text for the stock and waste. (str)"""
        # stock
        if self.stock:
            stock_text = '??'
        else:
            stock_text = '  '
        # waste
        for card in self.waste[-self.turn_count:]:
            stock_text += ' ' + str(card)
        stock_text += ' ' * (3 * self.turn_count + 2 - len(stock_text))
        return stock_text
    
    def super_stack(self, card):
        """
        Find and validate any stack being moved. (list of Card)
        
        If the stack is invalid, an empty list is returned.
        
        Parameters:
        card: The card at the base of the stack to be moved.
        """
        stack = []
        if card.game_location is self.cells:
            # a card in a cell is just the card
            stack = [card]
        elif card.game_location in self.reserve + [self.waste]:
            # a card in the reserve or waste is a just the card, if it's on top
            if card == card.game_location[-1]:
                stack = [card]
            else:
                stack = []
        else:
            # otherwise (it's in the tableau) check the full stack
            stack = card.game_location[card.game_location.index(card):]
            if not self.stack_check(stack):
                stack = []
        return stack
    
    def tableau_text(self):
        """Generate text for the tableau piles. (str)"""
        max_tableau = max([len(pile) for pile in self.tableau])
        tableau_lines = [['  ' for pile in self.tableau] for ndx in range(max_tableau)]
        for pile_ndx, pile in enumerate(self.tableau):
            for card_ndx, card in enumerate(pile):
                tableau_lines[card_ndx][pile_ndx] = str(card)
        return '\n'.join([' '.join(line) for line in tableau_lines])
    
    def transfer(self, move_stack, new_location, track = True, face_up = True, undo_ndx = 0):
        """
        Move a stack of cards from one game location to another. (None)
        
        This handles the card's knowledge of where it is and tracking game moves.
        
        Parameters:
        move_stack: The stack of cards to move. (list of Card)
        new_location: The new game location for the cards. (list of Card)
        track: A flag for tracking the move. (bool)
        face_up: A flag for the cards being face up. (bool)
        """
        # record the move
        old_location = move_stack[0].game_location
        if track:
            self.moves.append([move_stack[:], old_location, new_location, undo_ndx])
        # move the cards
        for card in move_stack:
            old_location.remove(card)
            card.up = face_up
        new_location.extend(move_stack)
        # turn over any revealed cards
        if old_location and old_location is not self.stock and not old_location[-1].up:
            old_location[-1].up = True
            # track turning over revealed cards
            if track:
                self.moves[-1].append(True)
        elif track:
            self.moves[-1].append(False)
        # reset location tracking
        for card in move_stack:
            card.game_location = new_location


class MultiSolitaire(Solitaire):
    """
    A game of solitaire that uses multiple decks. (Solitaire)

    You could have one class, and if there is only one deck, return a list of
    one, but you would lose specificity of errors.

    Attributes:
    alt_moves: Alternate possibilities for the last move. (list of tuple)

    Methods:
    do_alternate: Redo the last command with different but matching cards. (bool)

    Overridden Methods:
    do_match
    find_foundation
    """

    aliases = {'alt': 'alternate'}
    name = 'Solitaire Base'
    
    def do_alternate(self, argument):
        """
        Redo the last command with different but matching cards. (bool)
        
        This is for when there are two cards of the same rank and suit that 
        can make the same move, and the game makes the wrong one.

        Parameters:
        argument: The (ignored) argument to the command. (str)
        """
        if self.alt_moves:
            # find the last move from the user
            move_ndx = -1
            while self.moves[move_ndx][3]:
                move_ndx -= 1
            base_move = self.moves[move_ndx]
            # undo the last move without penalty
            self.do_undo('1', clear_alt = False)
            self.undo_count -= 1
            # redo the move with the next move
            self.transfer(*self.alt_moves.pop())
            return False
        else:
            self.human.error('The last move is not alternatable.')
            return True
        
    def do_auto(self, max_rank):
        """
        Automatically play cards into the foundations. (bool)
        
        Parameters:
        max_rank: The maximum rank to auto sort. (str)
        """
        # convert max rank to int
        max_rank = max_rank.upper()
        if max_rank.strip() == '':
            max_rank = len(self.deck.ranks) - 1
        elif max_rank in self.deck.ranks:
            max_rank = self.deck.ranks.index(max_rank)
        else:
            self.human.error('There was an error: the rank specified is not in the deck.')
            return True
        # loop until there are no sortable cards
        while True:
            # reset loop
            sorts = 0
            # check free cells
            for card in self.cells:
                foundations = self.find_foundation(card)
                for card_foundation in foundations:
                    if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                        self.do_sort(str(card))
                        sorts += 1
            # check tableau
            for pile in self.tableau:
                if pile:
                    card = pile[-1]
                    foundations = self.find_foundation(card)
                    for card_foundation in foundations:
                        if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                            self.do_sort(str(card))
                            sorts += 1
            # check the waste
            if self.waste:
                card = self.waste[-1]
                foundations = self.find_foundation(card)
                for card_foundation in foundations:
                    if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                        self.do_sort(str(card))
                        sorts += 1
            # check the reserve
            for pile in self.reserve:
                if pile:
                    card = pile[-1]
                    foundations = self.find_foundation(card)
                    for card_foundation in foundations:
                        if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                            self.do_sort(str(card))
                            sorts += 1
            if not sorts:
                break
        return False
    
    def do_build(self, arguments):
        """
        Build card(s) into stacks on the tableau. (bool)
        
        Parameters:
        arguments: The card to move and the card to move it onto. (str)
        """
        # parse the arguments
        card_arguments = self.deck.card_re.findall(arguments.upper())
        if len(card_arguments) != 2:
            self.human.error('Invalid arguments to build command: {!r}.'.format(arguments))
            return True
        mover, target = card_arguments
        # get the details on all the cards
        movers = self.deck.find(mover)
        targets = self.deck.find(target)
        self.alt_moves = []
        for mover in movers:
            moving_stack = self.super_stack(mover)
            for target in targets:
                # check for a valid move
                if self.build_check(mover, target, moving_stack, show_error = False):
                    self.alt_moves.append((moving_stack, target.game_location))
        if self.alt_moves:
            self.transfer(*self.alt_moves.pop())
            return False
        else:
            message = 'There are no valid moves for building a {} onto a {}.'
            self.human.error(message.format(*card_arguments))
            return True
        
    def do_free(self, card):
        """
        Move a card to one of the free cells. (bool)
        
        Parameters:
        card: The card to be freed. (str)
        """
        # parse the arguments
        card_arguments = self.deck.card_re.findall(card.upper())
        if len(card_arguments) != 1:
            self.human.error('Invalid arguments to build command: {!r}.'.format(arguments))
            return True
        # get the details on the card to be freed.
        cards = self.deck.find(card_arguments[0])
        # free the card
        self.alt_moves = []
        for card in cards:
            if self.free_check(card):
                self.alt_moves.append(([card], self.cells))
        if self.alt_moves:
            self.transfer(*self.alt_moves.pop())
            return False
        else:
            self.human.error('There are no valid moves for freeing a {}.'.format(card))
            return True
        
    def do_lane(self, card):
        """
        Move a card into an empty lane. (bool)
        
        Parameters:
        card: The string identifying the card. (str)
        """
        # get the card and the cards to be moved
        if not self.deck.card_re.match(card):
            self.human.error('Invalid card passed to lane command: {!r}.'.format(card))
            return True
        cards = self.deck.find(card)
        self.alt_moves = []
        for card in cards:
            moving_stack = self.super_stack(card)
            # check for validity and move
            if self.lane_check(card, moving_stack, False):
                self.alt_moves.append((moving_stack, self.tableau[self.tableau.index([])]))
        if self.alt_moves:
            self.transfer(*self.alt_moves.pop())
            return False
        else:
            self.human.error('There are no valid moves for laning a {}.'.format(card))
            return True

    def do_match(self, card):
        """
        Match two cards and discard them.

        Parameters:
        cards: The cards being matched. (str)
        """
        # Get the cards to match.
        cards = self.deck.card_re.findall(cards)
        # Check for a valid number of cards.
        if len(cards) != 2:
            self.human.error('You must provide two valid cards to the match command.')
            return True
        # Check the actual cards.
        cards = [self.deck.find(card) for card in cards]
        # Check all possibled combinations of cards for valid moves.
        for card_a in cards[0]:
            for card_b in cards[1]:
                if self.match_check([card_a, card_b], False):
                    self.alt_moves.append((card_a, card_b))
        if self.alt_moves:
            # If there are valid moves, make one of them.
            cards = self.alt_moves.pop()
            self.transfer([card[0]], self.foundations[0])
            self.transfer([card[1]], self.foundations[0])
            return False
        else:
            # If there are no valid moves, warn the user.
            self.human.error('There are not valid moves for matching a {} and a {}.'.format(*cards))
            return True
    
    def do_sort(self, card):
        """
        Move a card to the foundation. (bool)
        
        Parameters:
        card: The card being moved. (str)
        """
        # get the card
        if not self.deck.card_re.match(card):
            self.human.error('Invalid card passed to sort command: {!r}.'.format(card))
            return True
        cards = self.deck.find(card)
        self.alt_moves = []
        for card in cards:
            foundations = self.find_foundation(card)
            for foundation in foundations:
                if self.sort_check(card, foundation, False):
                    self.alt_moves.append(([card], foundation))
        if self.alt_moves:
            self.transfer(*self.alt_moves.pop())
            return False
        else:
            self.human.error('There are no valid moves for sorting a {}.'.format(card))
            return True
    
    def do_turn(self, arguments):
        """
        Turn cards from the stock into the waste. (bool)

        Parameters:
        arguments: The (ignored) arguments to the turn command. (str)
        """
        self.alt_moves = []
        return super(MultiSolitaire, self).do_turn(arguments)
    
    def do_undo(self, num_moves, clear_alt = True):
        """
        Undo one or more previous moves. (bool)
        
        Parameters:
        num_moves: The number of moves to undo. (str)
        """
        if clear_alt:
            self.alt_moves = []
        return super(MultiSolitaire, self).do_undo(num_moves)

    def find_foundation(self, card):
        """
        Find the foundations a card can be sorted to. (list of list)

        Parameters:
        card: The card to sort. (str)
        """
        first_index = self.deck.suits.index(card.suit)
        foundations = []
        for deck_index in range(self.deck.decks):
            foundations.append(self.foundations[first_index + len(self.deck.suits) * deck_index])
        return foundations
    
    def guess(self, card_arg):
        """
        Guess what move to make for a particular card. (None)
        
        Parameters:
        card_arg: The card to move. (str)
        """
        # Loop through the possible cards.
        cards = self.deck.find(card_arg)
        moves = []
        for card in cards:
            # check sorting
            if self.foundations:
                for foundation in self.find_foundation(card):
                    if self.sort_check(card, foundation, False):
                        moves.append('sort {}'.format(card))
            if not moves:
                # check bulding
                moving_stack = self.super_stack(card)
                for pile in self.tableau:
                    if pile and self.build_check(card, pile[-1], moving_stack, False):
                        moves.append('build {} {}'.format(card, pile[-1]))
                        break
                else:
                    # check freeing
                    if card.game_location is not self.cells and self.free_check(card, False):
                        moves.append('free {}'.format(card))
                    # check laning
                    elif self.lane_check(card, moving_stack, False):
                        moves.append('lane {}'.format(card))
            if moves:
                break
        if moves:
            self.handle_cmd(moves.pop())
        else:
            self.human.error('There is no valid move for a {}.'.format(card_arg))

    def set_solitaire(self):
        """
        Special initialization for solitaire games. (None)
        
        For an ulimited number of passes through the stock, set max_passes to -1.
        """
        options = {'deck-specs': [], 'num-tableau': 7, 'num-foundations': 4, 'num-reserve': 0,
            'num-cells': 0, 'turn-count': 3, 'max-passes': -1, 'wrap-ranks': False}
        options.update(self.options)
        # initialize specified attributes
        self.num_cells = options['num-cells']
        self.wrap_ranks = options['wrap-ranks']
        self.turn_count = options['turn-count']
        self.max_passes = options['max-passes']
        # initialize derived attributes
        self.deck = cards.MultiTrackingDeck(self, *options['deck-specs'])
        deal_num = -1
        deal_text_index = self.option_set.settings_text.find('deal-num')
        if deal_text_index != -1:
            self.option_set.settings_text = self.option_set.settings_text[:(deal_text_index - 1)]
        if self.raw_options.lower() != 'none':
            prompt = 'Enter the deal number, or return for a random deal: '
            deal_num = self.human.ask_int(prompt, low = 1, default = -1, cmd = False)
        if deal_num == -1:
            deal_num = None
        else:
            self.option_set.settings_text += ' deal-num={}'.format(deal_num)
        self.deck.shuffle(number = deal_num)
        self.tableau = [[] for ndx in range(options['num-tableau'])]
        self.foundations = [[] for ndx in range(options['num-foundations'])]
        self.reserve = [[] for ndx in range(options['num-reserve'])]
        # initialize default attributes
        # piles
        self.cells = []
        self.stock = []
        self.stock_passes = 0
        self.waste = []
        # undo history
        self.moves = []
        self.undo_count = 0
        self.commands = []
        # game specific rules
        self.set_checkers()


if __name__ == '__main__':
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    solo = Solitaire(player.Player(name), '')
    solo.play()