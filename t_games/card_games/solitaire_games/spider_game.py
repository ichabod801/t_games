"""
spider_game.py

A game of Spider.

Constants:
CREDITS: The credits for Spider. (str)
RULES: The rules of Spider. (str)

Classes:
Spider: A game of Spider. (solitaire.MultiSolitaire)
"""


import t_games.cards as cards
import t_games.card_games.solitaire_games.solitaire_game as solitaire


# # The credits for Spider.
CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

# The rules of Spider.
RULES = """
Spider is two deck game, with ten tableau piles. Four of the tableau piles
start with six cards, the rest start with five cards.

Cards on the tableau can be built down in rank regardless of suit. However, 
only stacks of a single suit can be moved as a unit. Otherwise cards must be 
built one at a time.

If you ever build a stack that goes from king to ace in the same suit, the
whole stack will automatically be sorted.

Turning cards over from the stock deals one face up card to the top of each 
tableau pile. You may not turn over cards from the stock if you have any empty
tableau piles.

Options:
one-suit (1s): The deck is all one suit (spades).
open (o): All tableau cards are dealt face up.
relaxed-turn (relaxed, rt): You may turn over cards from the deck when you
    have empty tableau piles.
two-suit (2s): The deck has only two suits: hearts and spades.
"""


class Spider(solitaire.MultiSolitaire):
    """
    A game of Spider. (solitaire.MultiSolitaire)

    Attributes:
    open: A flag for the tableau being totally face up. (bool)
    relaxed_turn: A flag for being able to turn with empty lanes. (bool)

    Methods:
    auto_sort_check: Check if the stack just made is sortable. (None)

    Overridden Methods:
    do_alternate
    do_build
    do_turn
    set_checkers
    set_options
    """

    # The menu categories for the game.
    categories = ['Card Games', 'Solitaire Games', 'Hybrid Games']
    # The credits for Spider.
    credits = CREDITS
    # The name of the game.
    name = 'Spider'
    # The number of game options.
    num_options = 4
    # The rules of Spider.
    rules = RULES

    def auto_sort_check(self):
        """Check if the stack just made is sortable. (None)"""
        # If there are thirteen cards in the new location
        moving_stack, old_location, new_location, undo_index, turn = self.moves[-1]
        stack = new_location[-13:]
        if len(stack) == 13:
            # Check those thirteen for validity.
            for checker in self.lane_checkers:
                if checker(self, stack[0], stack):
                    break
            else:
                # Sort any valid stacks as a whole.
                foundations = self.find_foundation(stack[0])
                foundation = [foundation for foundation in foundations if not foundation][0]
                self.transfer(stack, foundation, undo_ndx = 1)
    
    def do_alternate(self, arguments):
        """
        Redo the last command with different but matching cards. (bool)
        
        This is for when there are two cards of the same rank and suit that 
        can make the same move, and the game makes the wrong one.

        Parameters:
        arguments: The (ignored) argument to the command. (str)
        """
        # Do the building
        go = super(Spider, self).do_alternate(arguments)
        # If there was building, check for a sortable stack.
        if not go:
            self.auto_sort_check()
        return go

    def do_build(self, arguments):
        """
        Build card(s) into stacks on the tableau. (bool)
        
        Parameters:
        arguments: The card to move and the card to move it onto. (str)
        """
        # Do the building
        go = super(Spider, self).do_build(arguments)
        # If there was building, check for a sortable stack.
        if not go:
            self.auto_sort_check()
            # Reset changes from gipf.
            self.pair_checkers = [solitaire.pair_down]
            if len(self.build_checkers) == 1:
                self.build_checkers.append(solitaire.build_suit)
        return go

    def do_gipf(self, arguments):
        """
        Gipf

        Parameters:
        arguments: The name of the game to gipf to. (str)
        """
        # Run the edge, if possible.
        game, losses = self.gipf_check(arguments, ('bisley', 'freecell'))
        # Winning Bisley gets you an up or down build.
        if game == 'bisley':
            if not losses:
                self.human.tell('\nYour next build may be up or down one rank.')
                self.pair_checkers = [solitaire.pair_up_down]
        # Winning Freecell lets you move a stack ignoring suit.
        elif game == 'freecell':
            if not losses:
                self.human.tell('\nYour next build may move a stack regardless of suit.')
                self.build_checkers = [solitaire.build_down]
        # Otherwise I'm confused.
        else:
            self.human.tell('Only the spider crawls the web.')
        return True

    def do_turn(self, arguments):
        """
        Turn over cards from the stock. (bool)

        Parameters:
        arguments: The (ignored) arguments to the turn command. (str)
        """
        # Check for no stock.
        if not self.stock:
            self.human.error('There are no more cards to turn over.')
        # Check for empty piles (or relaxed-turn option)
        elif not all(self.tableau) and not self.relaxed_turn:
            self.human.error('You cannot turn over cards from the stock if you have empty tableau piles.')
        else:
            # Deal the cards to the tableau.
            for pile_index, pile in enumerate(self.tableau):
                self.transfer([self.stock[-1]], pile, face_up = True, undo_ndx = pile_index)
                if not self.stock:
                    break

    def set_checkers(self):
        """Set the game specific rule checkers. (None)"""
        super(Spider, self).set_checkers()
        # Set the dealers.
        self.dealers = [solitaire.deal_n(54, up = self.open), solitaire.deal_stock_all]
        # Set the rule checkers.
        self.build_checkers = [solitaire.build_suit, solitaire.build_down]
        self.lane_checkers = [solitaire.lane_suit, solitaire.lane_down]
        self.pair_checkers = [solitaire.pair_down]
        self.sort_checkers = [solitaire.sort_none]

    def set_options(self):
        """Set up the game specific options. (None)"""
        # Set the base solitaire options.
        self.options = {'num-foundations': 8, 'num-tableau': 10}
        # Set the deal options.
        self.option_set.add_option('one-suit', ['1s'], action = 'key=deck-specs', target = self.options,
            value = (8, cards.TrackOneSuit), default = None,
            question = 'Should the deck only have one suit? bool')
        self.option_set.add_option('two-suit', ['2s'], action = 'key=deck-specs', target = self.options,
            value = (4, cards.TrackTwoSuit), default = None,
            question = 'Should the deck only have two suits? bool')
        self.option_set.add_option('open', ['o'], question = 'Should the tableau be dealt face up? bool')
        # Set the play options.
        self.option_set.add_option('relaxed-turn', ['relaxed', 'rt'],
            question = 'Should you be able to turn over cards with empty lanes? bool')


if __name__ == '__main__':
    # Play the game without the full interface.
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    spider = Spider(player.Player(name), '')
    spider.play()
