"""
klondike_game.py

Klondike solitaire and variants.

Constants:
CREDITS: Credits for Klondike. (str)
RULES: Rules for Klondike. (str)

Classes:
Klondike: A game of Klondike. (Solitaire)

Functions:
deal_klondike: Deal deal a triangle in the tableau. (None)
"""


import tgames.card_games.solitaire_games.solitaire_game as solitaire
import tgames.utility as utility


CREDITS = """
Game Design: Traditional (maybe prospectors in the Klondike)
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
Cards on the tableau are built down in rank and alternating in color. Cards
are sorted to the foundations up in suit from the ace. Empty tableau piles may
be filled with a king or a stack starting with a king.

Cards from the stock are turned over three at a time. The stock may be gone
through as many times as you wish.

Options:
switch-one: You can switch to turning over one card at a time, but only for
    one last pass through the deck. (use the switch command)
turn-one: Cards from the stock are turned over one at a time.
"""


class Klondike(solitaire.Solitaire):
    """
    A game of Klondike. (Solitaire)

    Overridden Methods:
    set_checkers
    """

    aka = ['Seven Up', 'Sevens']
    categories = ['Card Games', 'Solitaire Games', 'Klondike Games']
    credits = CREDITS
    name = 'Klondike'
    rules = RULES

    def do_switch(self, arguments):
        """
        Switch from three cards at a time to one card at a time. (bool)

        Parameters:
        arguments. The (ignored) arguments to the command. (str)
        """
        if self.switched:
            self.human.tell('You may not switch to one card at a time.')
        else:
            # Reset the options
            self.switched = True
            self.turn_count = 1
            # Reset the stock
            self.transfer(self.waste[:], self.stock, face_up = False)
            self.stock.reverse()
            # Reset the stock tracking
            self.stock_passes += 1
            self.max_passes = self.stock_passes + 1
        return False

    def handle_options(self):
        """Set the game options. (None)"""
        # Set the defaults.
        self.switched = True
        self.options = {}
        # Check for options
        if self.raw_options.lower() == 'none':
            pass
        elif self.raw_options:
            self.flags |= 1
            for word in self.raw_options.lower().split():
                if word == 'turn-one':
                    self.options['turn-count'] = 1
                elif word == 'switch-one':
                    self.switched = False
        else:
            if self.human.ask('Would you like to change the options? ') in utility.YES:
                self.flags |= 1
                turn_one = self.human.ask('Would you like to go through the stock one card at a time? ')
                if turn_one in utility.YES:
                    self.options['turn-count'] = 1
                switch_msg = 'Should you be able to switch to one card at a time for one last pass? '
                if self.human.ask(switch_msg) in utility.YES:
                    self.switched = False

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(Klondike, self).set_checkers()
        # Set the game specific rules checkers.
        self.lane_checkers = [solitaire.lane_king]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_alt_color]
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up]
        # Set the dealers
        self.dealers = [deal_klondike]


def deal_klondike(game):
    """
    Deal deal a triangle in the tableau. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    # Deal out the triangle of cards.
    for card_ndx in range(len(game.tableau)):
        for tableau_ndx in range(card_ndx, len(game.tableau)):
            game.deck.deal(game.tableau[tableau_ndx], card_ndx == tableau_ndx)
    # Move the rest of the deck into the stock, in the same order.
    while game.deck.cards:
        game.deck.deal(game.stock)
    game.stock.reverse()


if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    klondike = Klondike(player.Player(name), '')
    klondike.play()