"""
solitaire.py

Base class for solitaire games.

Classes:
Solitaire: A generalized solitaire game. (game.game)
"""

import tgames.game as game

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
    max_passes: The number of allowed passes through the stock. (int)
    moves: The moves taken in the game. (list of list)
    num_cells: The number of cells in the game. (int)
    reserve: Piles where building is not permitted. (list of list of Card)
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
    find_foundation: Find the foundation a card should sort to. (list of Card)
    foundation_text: Generate the text for the foundation piles. (str)
    free_check: Check that a card can be moved to a free cell. (bool)
    game_over: Check for the foundations being full. (bool)
    guess: Guess what move to make for a particular card. (None)
    lane_check: Check for a valid move into a lane. (bool)
    reserve_text: Generate text for the reserve piles. (str)
    set_solitaire: Special initialization for solitaire games. (None)

    Overridden Methods:
    __str__
    default
    set_up
    """

    aliases = {'a': 'auto', 'b': 'build', 'f': 'free', 'l': 'lane', 'otto': 'auto'}
    categories = ['Test Games', 'Solitaire Games']
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
        elif not mover.face_up:
            error = 'The {} is face down and cannot be moved.'.format(mover.name)
        # check for a valid stack to move
        elif not moving_stack:
            error = '{} is not the base of a movable stack.'.format(mover)
        else:
            for checker in self.build_checkers:
                error = checker(self, mover, target):
                if error:
                    break
        # handle determination
        if error and show_error:
            self.human.tell(error)
        return not error
    
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
            self.human.tell('I do not recognize that command.')
        elif len(cards) == 1:
            return self.guess(cards[0])
        elif len(cards) == 2:
            return self.build(' '.join(cards))
        else:
            self.human.tell("I don't know what to do with that many cards.")
        
    def do_auto(self, max_rank):
        """
        Automatically play cards into the foundations. (bool)
        
        Parameters:
        agruments: The maximum rank to auto sort. (str)
        """
        # convert max rank to int
        if arguments == '1':
            max_rank = len(self.deck.ranks) - 1
        elif max_rank in self.deck.ranks:
            max_rank = self.deck.ranks.index(max_rank)
        else:
            self.human.tell('There was an error: the rank specified is not in the deck.')
            return True
        # loop until there are no sortable cards
        while True:
            # reset loop
            sorts = 0
            # check free cells
            for card in self.cells:
                card_foundation = self.find_foundation(card)
                if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                    self.sort(card)
                    sorts += 1
            # check tableau
            for pile in self.tableau:
                if pile:
                    card = pile[-1]
                    card_foundation = self.find_foundation(card)
                    if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                        self.sort(card)
                        sorts += 1
            # check the waste
            if self.waste:
                card = self.waste[-1]
                card_foundation = self.find_foundation(card)
                if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                    self.sort(card)
                    sorts += 1
            # check the reserve
            for pile in self.reserve:
                if pile:
                    card = pile[-1]
                    card_foundation = self.find_foundation(card)
                    if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                        self.sort(card)
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
            self.human.tell('Invalid arguments to build command: {!r}.'.format(arguments))
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
        arguments: The card to be freed. (str)
        """
        # parse the arguments
        card_arguments = self.deck.card_re.findall(arguments.upper())
        if len(card_arguments) != 1:
            self.human.tell('Invalid arguments to build command: {!r}.'.format(arguments))
            return True
        # get the details on the card to be freed.
        card = self.deck.find(card_arguments)
        # free the card
        if self.free_check(card):
            self.transfer([card], self.cells)
            return False
        else:
            return True
        
    def do_lane(self, card):
        """
        Move a card into an empty lane. (None)
        
        Parameters:
        card: The string identifying the card. (str)
        """
        # get the card and the cards to be moved
        card = self.deck.find(card)
        moving_stack = self.super_stack(card)
        # check for validity and move
        if self.lane_check(card, moving_stack):
            self.transfer(moving_stack, self.tableau[self.tableau.index([])])
            return True
            
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
                error = checker(self, card):
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
        return check == target
    
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
                    self.do_build(str(card), str(pile[-1]))
                    break
            else:
                # check freeing
                if card.game_location is not self.cells and self.free_check(card, False):
                    self.free(str(card))
                # check laning
                elif self.lane_check(card, moving_stack, False):
                    self.lane(str(card))
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
        elif not card.face_up:
            error = 'The {} is face down and cannot be moved.'.format(card.name)
        # check for open lanes
        if not self.tableau.count([]):
            error = 'There are no open lanes.'
        # check for a valid stack
        elif not moving_stack:
            error = 'The {} is not the base of a valid stack to move.'.format(card.name)
        # check game specific rules
        else:
            for checker in self.lane_checkers:
                error = checker(self, card):
                if error:
                    break
        # handle determination
        if error and show_error:
            self.human.tell(error)
        return not error
    
    def reserve_text(self):
        """Generate text for the reserve piles. (str)"""
        reserve_text = []
        for pile in self.reserve:
            if pile:
                reserve_text.append(str(pile[-1]))
            else:
                reserve_text.append('  ')
        return ' '.join(reserve_text)

    def set_solitaire(deck_specs = [], num_tableau = 7, num_foundations = 4, num_reserve = 0, 
        num_cells = 0, turn_count = 3, max_passes = -1, wrap_ranks = False):
        """
        Special initialization for solitaire games. (None)
        
        For an ulimited number of passes through the deck, set max_passes to -1.
        
        Parameters:
        deck_specs: The parameters for the deck of cards for the game. (list)
        num_tableau: The number of tableau piles in the game. (int)
        num_foundations: The number of foundation piles in the game. (int)
        num_reserve: The number of reserve piles in the game. (int)
        num_cells: The number of cells in the game. (int)
        turn_count: The number of cards to turn from the stock each time. (int)
        max_passes: The number of allowed passes through the stock. (int)
        wrap_ranks: Flag for building by rank wrappng from king to ace. (bool)
        """
        # initialize specified attributes
        self.num_cells = num_cells
        self.wrap_ranks = wrap_ranks
        self.turn_count = turn_count
        self.max_passes = max_passes
        # initialize derived attributes
        self.set_deck(deck_specs)
        self.tableau = [[] for ndx in range(num_tableau)]
        self.foundations = [[] for ndx in range(num_foundations)]
        self.reserve = [[] for ndx in range(num_reserve)]
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
        # checkers
        self.build_checkers = []
        self.free_checkers = []
        self.lane_checkers = []
        # dealers
        self.dealers = []

    def set_up(self):
        """Set up the game. (None)"""
        self.set_solitaire()
        self.dealers = [free_deal]
        self.deal()