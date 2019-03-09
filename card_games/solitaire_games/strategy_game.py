"""
strategy_game.py

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Strategy. (str)
RULES: The rules for Strategy. (str)

Classes:
Strategy: A game of Strategy. (solitaire.Solitaire)
"""


from . import solitaire_game as solitaire


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
piles= (p=): The number of tableau piles (1-8).
"""


class Strategy(solitaire.Solitaire):
    """
    A game of Strategy. (solitaire.Solitaire)

    Overridden Methods:
    set_checkers
    set_options
    """

    aka = ['Stra']
    credits = CREDITS
    categories = ['Card Games', 'Solitaire Games', 'Revealing Games']
    name = 'Strategy'
    num_options = 1
    rules = RULES

    def do_gipf(self, arguments):
        """
        Monte Carlo allows reverses one pile. Roulette lets you swap two adjacent
        cards.
        """
        game, losses = self.gipf_check(arguments, ('monte carlo', 'roulette'))
        go = True
        # A Monte Carlo win lets you reverse one pile.
        if game == 'monte carlo':
            if not losses:
                # Remind the human.
                self.human.tell(self)
                # Get a foundation pile.
                while True:
                    card_text = self.human.ask('Pick a card on the tableau: ')
                    if self.deck.card_re.match(card_text):
                        card = self.deck.find(card_text)
                        if card.game_location in self.tableau:
                            break
                        else:
                            self.human.error('That card is not in the tableau.')
                    else:
                        self.human.error('I do not recognize that card.')
                # Reverse the pile.
                card.game_location.reverse()
                go = False
        # A Roulette win lets you swap (spin) two adjacent cards.
        elif game == 'roulette':
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
        # Otherwise I'm confused.
        else:
            self.human.tell('That does not compute.')
        return go

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(Strategy, self).set_checkers()
        # Set the rule checkers.
        self.build_checkers = [solitaire.build_reserve]
        self.lane_checkers = [solitaire.lane_reserve]
        self.pair_checkers = []
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up, solitaire.sort_no_reserve]
        # Set the dealer.
        self.dealers = [solitaire.deal_reserve_n(52)]

    def set_options(self):
        """Set the game options. (None)"""
        self.options = {'num-tableau': 8, 'num-reserve': 1}
        self.option_set.add_option('piles', ['p'], action = 'key=num-tableau', converter = int,
            default = 8, valid = range(1, 9), target = self.options,
            question = 'How many tableau piles (1-8, return for 8)? ')
