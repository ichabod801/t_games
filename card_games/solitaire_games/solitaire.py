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

    Attributes:
    cells: Holding spaces for manuevering cards. (list of Card)
    deck: The deck of cards for the game. (cards.TrackingDeck)
    foundations: The piles to fill to win the game. (list of list of Card)
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
    do_auto: Automatically play cards into the foundations. (bool)
    do_build: Build card(s) into stacks on the tableau. (bool)
    set_solitaire: Special initialization for solitaire games. (None)

    Overridden Methods:
    __str__
    """

    aliases = {'a': 'auto', 'otto': 'auto'}
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
        # deal
        self.deal()