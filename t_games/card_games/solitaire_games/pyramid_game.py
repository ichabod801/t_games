"""
pyramid_game.py

A game of Pyramid.

Constants:
CREDITS: The credits for Pyramid. (str)
RULES: The rules for Pyramid. (str)

Classes:
Pyramid: A game of Pyramid. (solitaire.Solitaire)
"""


import t_games.card_games.solitaire_games.solitaire_game as solitaire

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
klondike: Klondike style stock and waste. Equivalent to 'passes = -1 
    turn-count = 3'.
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
    standard_turn: A flag for using the default turning rules. (bool)

    Overridden Methods:
    do_turn
    find_foundation
    game_over
    handle_options
    set_checkers
    set_options
    tableau_text
    """

    # The categories the game is in.
    categories = ['Card Games', 'Solitaire Games', 'Closed Games']
    # The credits for the game.
    credits = CREDITS
    # The name of the game.
    name = 'Pyramid'
    # The number of settable options.
    num_options = 8
    # The rules of the game.
    rules = RULES

    def do_turn(self, arguments):
        """
        Turn cards from the stock into the waste. (bool)

        Parameters:
        arguments: The (ignored) arguments to the turn command. (str)
        """
        # Move the current waste card to the foundation.
        if self.waste:
            self.transfer(self.waste[:], self.foundations[0])
        # Do the turn as normal.
        super(Pyramid, self).do_turn(arguments)
        # Update the undo count for the turned cards.
        for move in self.moves[-self.options['turn-count']:]:
            move[-2] += 1

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
        if self.options['max-passes'] > 1 or self.options['max-passes'] == -1:
            self.standard_turn = True
        if self.standard_turn:
            self.do_turn = super(Pyramid, self).do_turn

    def reserve_text(self):
        """Generate text for the reserve piles. (str)"""
        max_reserve = max([len(pile) for pile in self.reserve])
        reserve_lines = [['  ' for pile in self.reserve] for row in range(max_reserve)]
        for pile_index, pile in enumerate(self.reserve):
            for card_index, card in enumerate(pile):
                reserve_lines[card_index][pile_index] = str(card)
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
        self.sort_checkers = [solitaire.sort_kings]

    def set_options(self):
        """Set up the game specific options. (None)"""
        # Set the solitaire options.
        self.options = {'max-passes': 1, 'num-foundations': 1, 'num-tableau': 7, 'turn-count': 1}
        # Set the option groups.
        self.option_set.add_group('giza', 'reserve=8 reserve-rows=3')
        self.option_set.add_group('klondike', 'passes=-1 turn-count=3')
        # Set the game options.
        self.option_set.add_option('cells', ['c'], int, action = "key=num-cells", default = 0, 
            valid = range(11), target = self.options,
            question = 'How many free cells should be available (0-10, return for 0)? ')
        self.option_set.add_option('passes', ['p'], int, action = "key=max-passes", default = 1, 
            check = lambda passes: passes > 1 or passes == -1, target = self.options,
            question = 'How many passes through the stock (-1 for infinite, return for 1)? ')
        self.option_set.add_option('relaxed-match', ['rm'],
            question = 'Should you be able to match cards that are blocking each other? bool')
        self.option_set.add_option('relaxed-win', ['rw'],
            question = 'Should you be able to win just by clearing the pyramid? bool')
        self.option_set.add_option('reserve', ['r'], int, action = "key=num-reserve", default = 0, 
            valid = range(9), target = self.options,
            question = 'How reserve piles should there be (0-8, return for 0)? ')
        self.option_set.add_option('reserve-rows', ['rr'], int, default = 1, valid = range(4),
            question = 'How many reserve rows should there be (0-3, return for 1)? ')
        self.option_set.add_option('standard-turn', ['st'],
            question = 'Should cards stay in the waste when new ones are turned from the stock? bool')
        self.option_set.add_option('turn-count', ['tc'], int, action = "key=turn-count", default = 1, 
            valid = (1, 2, 3), target = self.options,
            question = 'How many cards turned from the stock at a time (1-3, return for 1)? ')

    def tableau_text(self):
        """Generate the text representation of the tableau piles. (str)"""
        lines = []
        for pile_count in range(len(self.tableau)):
            lines.append('  ' * (6 - pile_count + (self.options['num-reserve'] == 8)))
            for pile_index in range(pile_count + 1):
                if len(self.tableau[pile_index]) > (pile_count - pile_index):
                    card_text = str(self.tableau[pile_index][pile_count - pile_index])
                else:
                    card_text = '  '
                lines[-1] = '{}{}  '.format(lines[-1], card_text)
        return '\n'.join(lines)


if __name__ == '__main__':
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    pyramid = Pyramid(player.Player(name), '')
    pyramid.play()