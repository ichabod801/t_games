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
standard-turn (st): Cards are not sorted from the waste when turning cards
    from the stock.
"""


class Pyramid(solitaire.Solitaire):
    """
    A game of Pyramid (solitaire.Solitaire)

    Overridden Methods:
    find_foundation
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
    num_options = 2
    # The rules of the game.
    rules = RULES

    def do_turn(self, arguments):
        """
        Turn cards from the stock into the waste. (bool)

        Parameters:
        arguments: The (ignored) arguments to the turn command. (str)
        """
        # Move the current waste card to the foundation.
        if self.stock_passes != self.max_passes and self.waste:
            self.transfer(self.waste[-1:], self.foundations[0])
        # Do the turn as normal.
        super(Pyramid, self).do_turn(arguments)
        # Update the undo count for the turned cards.
        for card_index in range(self.options['turn-count']):
            self.moves[-card_index][-1] += 1

    def find_foundation(self, card):
        """
        Find the foundation a card can be sorted to. (list of TrackingCard)

        Parameters:
        card: The card to sort. (str)
        """
        return self.foundations[0]

    def handle_options(self):
        """Handle the particular option settings. (None)"""
        super(Pyramid, self).handle_options()
        if self.standard_turn:
            self.do_turn = super(Pyramid, self).do_turn

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(Pyramid, self).set_checkers()
        self.dealers = [solitaire.deal_pyramid, solitaire.deal_stock_all]
        self.build_checkers = [solitaire.build_none]
        self.lane_checkers = [solitaire.lane_none]
        self.match_checkers = [solitaire.match_top, solitaire.match_pyramid, solitaire.match_thirteen]
        self.sort_checkers = [solitaire.sort_kings]

    def set_options(self):
        """Set up the game specific options. (None)"""
        self.options = {'max-passes': 1, 'num-foundations': 1, 'num-tableau': 7, 'turn-count': 1}
        self.option_set.add_option('cells', ['c'], int, action = "key=num-cells", default = 0, 
            valid = range(11), target = self.options,
            question = 'How many free cells should be available (0-10, return for 0)? ')
        self.option_set.add_option('standard-turn', ['st'],
            question = 'Should cards stay in the waste when new ones are turned from the stock? bool')

    def tableau_text(self):
        """Generate the text representation of the tableau piles. (str)"""
        lines = ['']
        for pile_count in range(len(self.tableau)):
            lines.append('  ' * (6 - pile_count))
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