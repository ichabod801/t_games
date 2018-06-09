"""
strategy_game.py

Classes:
Strategy: A game of Strategy. (solitaire.Solitaire)

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Functions:
build_reserve: Build only from the reserve. (bool)
lane_reserve: Lane only from the reserve (bool)
sort_no_reserve: Sort non-aces only when the reserve is empty. (bool)
"""


import t_games.card_games.solitaire_games.solitaire_game as solitaire


CREDITS = """
Game Design: Albert Morehead and Geoffrey Mott-Smith
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
All of the cards are dealt to the reserve. You may move the top card of the 
reserve onto any of the eight tableau piles. Aces may be sorted as they 
appear, but no other card may be sorted until the reserve is empty.

Parlett suggests that each time you win, play again with one less tableau
pile.

Options:
piles: The number of tableau piles (1-8).
"""


class Strategy(solitaire.Solitaire):
    """
    A game of Strategy. (solitaire.Solitaire)

    Overridden Methods:
    set_checkers
    set_options
    """

    credits = CREDITS
    # Interface categories for the game.
    categories = ['Card Games', 'Solitaire Games', 'Closed Games']
    name = 'Strategy'
    num_options = 1
    rules = RULES

    def do_gipf(self, arguments):
        """
        Gipf

        Parameters:
        arguments: The name of the game to gipf to. (str)
        """
        # Check and possibly play the game.
        game, losses = self.gipf_check(arguments, ('roulette',))
        go = True
        # A Roulette win lets you swap (spin) two adjacent cards.
        if game == 'roulette':
            if not losses:
                # Remind the human.
                self.human.tell(self)
                while True:
                    # Get two cards from the human.
                    card_text = self.human.ask('\nWhich two adjacent cards would you like to spin? ')
                    cards = self.deck.card_re.findall(card_text)
                    cards = [self.deck.find(card) for card in cards]
                    # Check that they are next to each other.
                    if len(cards) != 2:
                        self.human.tell('Please pick two cards.')
                    elif cards[0].game_location != cards[1].game_location:
                        self.human.tell('The two cards must be in the same tableau pile.')
                    else:
                        pile = cards[0].game_location
                        indexes = [pile.index(card) for card in cards]
                        if abs(indexes[0] - indexes[1]) == 1:
                            # Swap (spin) the two cards.
                            pile[indexes[0]], pile[indexes[1]] = pile[indexes[1]], pile[indexes[0]]
                            break
                        else:
                            self.human.tell('Those cards are not next to each other.')
                go = False
        # Handle other games or arguments.
        else:
            self.human.tell('That does not compute.')
        return go

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(Strategy, self).set_checkers()
        # Cards only move from the reserve (at first).
        self.build_checkers = [solitaire.build_reserve]
        self.lane_checkers = [solitaire.lane_reserve]
        # There are no stacks of cards to move.
        self.pair_checkers = []
        # Sort aces. Up from aces after the reserve is empty.
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up, solitaire.sort_no_reserve]
        # All cards start in the reserve.
        self.dealers = [solitaire.deal_reserve_n(52)]

    def set_options(self):
        """Set the game options. (None)"""
        self.options = {'num-tableau': 8, 'num-reserve': 1}
        self.option_set.add_option(name = 'piles', action = 'key=num-tableau', converter = int, 
            default = 8, valid = range(1, 9), target = self.options,
            question = 'How many tableau piles (1-8, return for 8)? ')


if __name__ == '__main__':
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    strat = Strategy(player.Player(name), '')
    strat.play()