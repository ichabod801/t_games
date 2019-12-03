"""
pyramid_game.py

A game of Pyramid.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Pyramid. (str)
RULES: The rules for Pyramid. (str)

Classes:
Pyramid: A game of Pyramid. (solitaire.Solitaire)
"""


from . import solitaire_game as solitaire


# The credits for Pyramid.
CREDITS = """
Game Design: Traditional
    Giza option designed by Michael Keller
Game Programming: Craig "Ichabod" O'Brien
"""

# The rules for Pyramid.
RULES = """
A pyramid of cards is dealt out with one card on the top row, two cards on the
second row, and so on for seven rows. Cards are open on the tableau if both of
the card under that card have been removed. For example, in this layout:

    AC
  JD  KD
5S

The five of spades and the king of diamonds are available for play, but the
jack of diamonds is blocked by the five of spades, and the ace of clubs is
blocked by the jack and king of diamonds.

Any pair that totals thirteen may be matched to the foundation. Jacks count as
11, queens as 12, and kings as 13 (kings may just be sorted to the
foundation). The stock may be turned over one at a time to be matched with
cards on the tableau. However, any unused waste cards are sorted to the
foundation.

Options:
cells= (c): The number of free cells available. 0 to 10, defaults to 0.
giza: Fully open game with 8 reserve piles. Equivalent to 'reserve=8
    reserve-rows=3'.
klondike: Klondike style stock and waste. Equivalent to 'passes=-1
    turn-count=3'.
passes= (p): The number of passes through the stock you get. -1 gives
    unlimited passes. If this is not one, the standard-turn option is in
    effect. Defaults to 1.
relaxed-match (rm): You may match cards even if one is blocking the other.
relaxed-win (rw): If the pyramid is clear, you can win even if there are
    cards in the stock or waste.
reserve= (r): The number of reserve piles. 0 to 8, defaults to 0.
reserve-rows= (rr): The number of reserve rows. 0 to 3, defaults to 1.
standard-turn (st): Cards are not sorted from the waste when turning cards
    from the stock.
turn-count= (tc): How many cards are turned over from the stock at a time.
    Defaults to 1.
"""


class Pyramid(solitaire.Solitaire):
    """
    A game of Pyramid (solitaire.Solitaire)

    Attributes:
    relaxed_match: A flag for relaxing the matching rules. (bool)
    relaxed_wins: A flag for winning just by clearing the pyramid. (bool)
    reserve_rows: The number of cards in each reserve pile. (int)
    standard_turn: A flag for using the default turning rules. (bool)

    Methods:
    is_empty: Check that there are no face up cards not in the foundation. (bool)

    Overridden Methods:
    do_turn
    find_foundation
    game_over
    handle_options
    reserve_text
    set_checkers
    set_options
    tableau_text
    """

    aka = ['Pyra']
    categories = ['Card Games', 'Solitaire Games', 'Matching Games']
    credits = CREDITS
    name = 'Pyramid'
    num_options = 8
    rules = RULES

    def do_auto(self, max_rank):
        """
        Automatically play cards to the foundations. (a)

        If no argument is given, auto will play cards as long as it can. If a card
        rank is given as an argument, auto will on play cards up to and including that
        rank. If the pyramid and waste are cleared (and any reserve or free cells),
        auto will sort all of the cards in the stock (except with the standard-turn
        option).
        """
        # Do the normal auto sort.
        super(Pyramid, self).do_auto(max_rank)
        # Check for sorting the stock.
        if not self.standard_turn and self.is_empty():
            self.sort_stock()
        return False

    def do_gipf(self, arguments):
        """
        Monte Carlo slides all the cards to the left to fill in any gaps. Spider (hah!)
        sorts any unblocked cards.
        """
        # Run the edge, if possible.
        game, losses = self.gipf_check(arguments, ('monte carlo', 'spider'))
        # Winning Monte Carlo slides all cards to the left.
        if game == 'monte carlo':
            if not losses:
                # Move cards over repeatedly.
                while True:
                    undo_index = 0
                    # Loop  through pairs of tabelau piles.
                    for left, right in zip(self.tableau, self.tableau[1:]):
                        # Move the appropriate cards if there are any.
                        stack = right[(len(left) - 1):]
                        if stack:
                            self.transfer(stack, left, undo_ndx = undo_index)
                            undo_index += 1
                    # If no cards were moved, stop trying to move cards.
                    if not undo_index:
                        break
        # Winning Spider (hah!) sorts any unblocked cards.
        elif game == 'spider':
            if not losses and self.stock:
                # Sort all of the unblocked cards.
                for pile_index, pile in enumerate(self.tableau):
                    if pile and not solitaire.sort_pyramid(self, pile[-1], self.foundations[0]):
                        self.transfer(pile[-1:], self.foundations[0], undo_ndx = pile_index)
        # Otherwise I'm confused.
        else:
            self.human.tell("No, it's Giza. Gee-zah.")
        return True

    def do_turn(self, arguments):
        """
        Turn cards from the stock into the waste. (t)

        In Pyramid, cards in the waste are sorted to the foundation before the next
        card is turned over from the stock. If the only cards left are in the stock,
        they will all be sorted instead of turned over into the waste (except with
        the standard-turn option).
        """
        # Store current move tracking.
        count_hold = self.move_count
        # Move the current waste card to the foundation.
        if self.waste:
            self.transfer(self.waste[:], self.foundations[0])
        # Check for autosorting the stock.
        if not self.standard_turn and self.is_empty():
            self.sort_stock()
        # Otherwise, do the turn as normal.
        else:
            super(Pyramid, self).do_turn(arguments)
            # Update the undo and move tracking.
            for move in self.moves[-self.options['turn-count']:]:
                move[-2] += 1
            self.move_count = count_hold + 1

    def find_foundation(self, card):
        """
        Find the foundation a card can be sorted to. (list of TrackingCard)

        Parameters:
        card: The card to sort. (str)
        """
        return self.foundations[0]

    def game_over(self):
        """Check for the end of the game."""
        # Check for relaxed win and empty pyramid.
        if self.relaxed_win and not self.tableau[0] and not self.cells and not any(self.reserve):
            # Transfer the stock and the waste to the foundation for a win.
            if self.waste:
                self.transfer(self.waste[:], self.foundations[0])
            if self.stock:
                self.transfer(self.stock[:], self.foundations[0])
        # Return the normal check.
        return super(Pyramid, self).game_over()

    def handle_options(self):
        """Handle the particular option settings. (None)"""
        super(Pyramid, self).handle_options()
        # Multiple passes through the stock requires standard turn rules.
        if self.options['max-passes'] > 1 or self.options['max-passes'] == -1:
            self.standard_turn = True
        # Apply the standard turn rules.
        if self.standard_turn:
            self.do_turn = super(Pyramid, self).do_turn

    def is_empty(self):
        """Check that there are no face up cards not in the foundation. (bool)"""
        return not any(self.tableau) and not any(self.reserve) and not self.cells and not self.waste

    def reserve_text(self):
        """Generate text for the reserve piles. (str)"""
        # Set up a blank reserve.
        max_reserve = max([len(pile) for pile in self.reserve])
        reserve_lines = [['  ' for pile in self.reserve] for row in range(max_reserve)]
        # Fill in the cards.
        for pile_index, pile in enumerate(self.reserve):
            for card_index, card in enumerate(pile):
                reserve_lines[card_index][pile_index] = str(card)
        # Format and return as a string.
        padding = '  ' * (7 - self.options['num-reserve'])
        return '\n'.join(['{}{}'.format(padding, '  '.join(line)) for line in reserve_lines])

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(Pyramid, self).set_checkers()
        # Set the dealers.
        self.dealers = [solitaire.deal_pyramid]
        if self.options['num-reserve']:
            reserve_cards = self.options['num-reserve'] * self.reserve_rows
            self.dealers.append(solitaire.deal_reserve_n(reserve_cards, up = True))
        self.dealers.append(solitaire.deal_stock_all)
        # Set the rule checkers.
        self.build_checkers = [solitaire.build_none]
        self.lane_checkers = [solitaire.lane_none]
        if self.relaxed_match:
            self.match_checkers = [solitaire.match_top_two, solitaire.match_pyramid_relax]
        else:
            self.match_checkers = [solitaire.match_top, solitaire.match_pyramid]
        self.match_checkers.append(solitaire.match_thirteen)
        self.sort_checkers = [solitaire.sort_kings_only, solitaire.sort_pyramid]
        # Add free cell rules.
        if self.options['num-cells']:
            self.free_checkers = [solitaire.free_pyramid]

    def set_options(self):
        """Set up the game specific options. (None)"""
        # Set the solitaire options.
        self.options = {'max-passes': 1, 'num-foundations': 1, 'num-tableau': 7, 'turn-count': 1}
        # Set the option groups.
        self.option_set.add_group('giza', 'reserve=8 reserve-rows=3')
        self.option_set.add_group('klondike', 'passes=-1 turn-count=3')
        # Set the game options.
        # Set the stock and waste options.
        self.option_set.add_option('passes', ['p'], int, action = "key=max-passes", default = 1,
            check = lambda passes: passes > 1 or passes == -1, target = self.options,
            question = 'How many passes through the stock (-1 for infinite, return for 1)? ')
        self.option_set.add_option('standard-turn', ['st'],
            question = 'Should cards stay in the waste when new ones are turned from the stock? bool')
        self.option_set.add_option('turn-count', ['tc'], int, action = "key=turn-count", default = 1,
            valid = (1, 2, 3), target = self.options,
            question = 'How many cards turned from the stock at a time (1-3, return for 1)? ')
        # Set the relaxed rules options.
        self.option_set.add_option('relaxed-match', ['rm'],
            question = 'Should you be able to match cards that are blocking each other? bool')
        self.option_set.add_option('relaxed-win', ['rw'],
            question = 'Should you be able to win just by clearing the pyramid? bool')
        # Set options for additional piles.
        self.option_set.add_option('cells', ['c'], int, action = "key=num-cells", default = 0,
            valid = range(11), target = self.options,
            question = 'How many free cells should be available (0-10, return for 0)? ')
        self.option_set.add_option('reserve', ['r'], int, action = "key=num-reserve", default = 0,
            valid = range(9), target = self.options,
            question = 'How reserve piles should there be (0-8, return for 0)? ')
        self.option_set.add_option('reserve-rows', ['rr'], int, default = 1, valid = range(4),
            question = 'How many reserve rows should there be (0-3, return for 1)? ')

    def sort_stock(self):
        """Sort the stock. (self)"""
        for card in self.stock[:]:
            self.transfer([card], self.foundations[0])

    def tableau_text(self):
        """Generate the text representation of the tableau piles. (str)"""
        lines = []
        for pile_count in range(len(self.tableau)):
            # Pad each row to make a triantle shape.
            lines.append('  ' * (6 - pile_count + (self.options['num-reserve'] == 8)))
            for pile_index in range(pile_count + 1):
                # Show each row diagonally (down to the left) in the triangle shape.
                if len(self.tableau[pile_index]) > (pile_count - pile_index):
                    card_text = str(self.tableau[pile_index][pile_count - pile_index])
                else:
                    card_text = '  '
                lines[-1] = '{}{}  '.format(lines[-1], card_text)
        lines = filter(lambda text: text.strip(), lines)
        return '\n'.join(lines)
