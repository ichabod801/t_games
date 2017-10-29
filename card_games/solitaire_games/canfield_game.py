"""
canfield_game.py

game of Canfield.

Classes:
Canfield: A game of Canfield. (Solitaire)

Functions:
build_whole: Check that only complete tableau stacks are moved. (str)
deal_tableau1: Deal one card face up to each tableau pile. (None)
deal_twos_foundations: Deal the twos to the foundations. (None)
deal_selective: Deal tableau cards with selection of a foundation card. (None)
lane_reserve: Check only laning cards from the reserve. (str)
"""


import tgames.options as options
import tgames.card_games.solitaire_games.solitaire_game as solitaire


CREDITS = """
Game Design: Richard A. Canfield
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
The deal is four cards to four tableau piles, one card to start one of the 
foundations, thirteen cards to a reserve, and the rest of the cards to the 
stock.

Foundation piles are built up in rank by suit from whatever rank was put in 
the first foundation pile, going from king to ace if necessary. Tableau piles 
are build down in rank by alternating color. The top card of the reserve is
available for building, and you may turn over the stock to the waste three 
cards at a time and use the top card of the waste. Empty piles on the 
tableau may only be filled from the reserve. If the reserve is empty, cards
from the waste may be used to fill empty spots on the tableau.

Stacks on the tableau may be moved, but only if the whole stack is moved.

Options:
variant=: Play one of the variants from the list below.

Variants:
Chameleon: A 12 card reserve and three foundation piles. Tableau building is
    down regarless of suit, and partial stacks may be moved. The stock is
    turned one card at a time, but with only one pass through the stock.
Rainbow: Tableau building is down regardless of suit.
Rainbow-One: As Rainbow, but cards from the stock are dealt one card at a
    time, with two passes through the stock allowed.
Selective: You are given five cards. You get to choose one to go on the
    foundations. The rest start the tableau piles.
Storehouse: The foundations start filled with twos. The stock is turned up one
    card at a time, with two passes through the stock allowed. The tableau is
    build down by suit.
Superior: The reserve is visible and empty tableau piles may be filled with 
    cards from the waste or reserve.
"""


class Canfield(solitaire.Solitaire):
    """
    A game of Canfield. (Solitaire)

    Class Attributes:
    variants: The recognized variants of Canfield. (tuple of str)

    Methods:
    superior_text: Generate text for the reserve in the superior variant. (str)

    Overridden Methods:
    handle_options
    set_checkers
    """

    aka = ['Demon']
    categories = categories = ['Card Games', 'Solitaire Games', 'Canfield Games']
    credits = CREDITS
    name = 'Canfield'
    num_options = 7 # There are basically seven things the options modify.
    rules = RULES
    variants = ('chameleon', 'rainbow', 'rainbow-one', 'selective', 'storehouse', 'superior')

    def do_gipf(self, arguments):
        """
        Gipf

        Parameters:
        arguments: The name of the game to gipf to. (str)
        """
        game, losses = self.gipf_check(arguments, ("baker's game", 'blackjack'))
        if game == "baker's game":
            if not losses:
                pair_hold = self.pair_checkers
                self.pair_checkers = [solitaire.pair_down, solitaire.pair_suit]
                go = True
                while go:
                    cards = self.human.ask('Enter two cards of the same suit to build: ')
                    go = self.do_build(cards)
                self.pair_checkers = pair_hold
        elif game == 'blackjack':
            if not losses:
                pair_hold = self.pair_checkers
                self.pair_checkers = []
                go = True
                while go:
                    cards = self.human.ask('Enter a jack and anything to build it on: ')
                    if cards.strip().upper()[0] != 'J':
                        self.human.tell('The first card must be a jack.')
                        continue
                    go = self.do_build(cards)
                self.pair_checkers = pair_hold
        else:
            self.human.tell("I'm sorry, I don't speak Flemish.")
        return True

    def handle_options(self):
        """Set up the game options. (None)"""
        super(Canfield, self).handle_options()
        # Set the default options.
        self.options = {'num-tableau': 4, 'num-reserve': 1, 'wrap-ranks': True}
        # Set options based on variant (see also set_checkers).
        if self.option_set.settings_text:
            if self.option_set.settings_text == 'chameleon':
                self.options['num-tableau'] = 3
                self.options['turn-count'] = 1
                self.options['max-passes'] = 1
            elif self.option_set.settings_text in ('rainbow-one', 'storehouse'):
                self.options['turn-count'] = 1
                self.options['max-passes'] = 2

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        # Set the default checkers.
        super(Canfield, self).set_checkers()
        # Set the rules.
        self.build_checkers = [build_whole]
        self.lane_checkers = [lane_reserve]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_alt_color]
        self.sort_checkers = [solitaire.sort_rank, solitaire.sort_up]
        # Set the dealers.
        self.dealers = [solitaire.deal_reserve_n(13), solitaire.deal_start_foundation, deal_tableau1, 
            solitaire.deal_stock_all]
        # Check for variant rules.
        if self.option_set.settings_text == 'chameleon':
            self.build_checkers = []
            self.lane_checkers = []
            self.pair_checkers = [solitaire.pair_down]
        elif self.option_set.settings_text.startswith('rainbow'):
            self.pair_checkers = [solitaire.pair_down]
        elif self.option_set.settings_text == 'selective':
            self.dealers = [solitaire.deal_reserve_n(13), deal_selective, solitaire.deal_stock_all]
        elif self.option_set.settings_text == 'storehouse':
            self.pair_checkers[1] = solitaire.pair_suit
            self.dealers = [deal_twos_foundations, solitaire.deal_reserve_n(13), deal_tableau1,
                solitaire.deal_stock_all]
        elif self.option_set.settings_text == 'superior':
            self.lane_checkers = []
            self.dealers[0] = solitaire.deal_reserve_n(13, True)
            self.reserve_text = self.superior_text

    def set_options(self):
        """Define the game options. (None)"""
        self.option_set.add_option('variant', [], options.lower, default = None, valid = self.variants,
            question = 'Which variant would you like to play? ',
            error_text = 'The valid variants are: {}.'.format(', '.join(self.variants)))

    def superior_text(self):
        """Generate text for the reserve in the superior variant. (str)"""
        return ' '.join([str(card) for card in self.reserve[0]])


def build_whole(game, mover, target, moving_stack):
    """
    Check that only complete tableau stacks are moved. (str)

    Parameters:
    mover: The card being moved. (TrackingCard)
    target: The card being moved to. (TrackingCard)
    moving_stack: The stack the mover is the base of. (list of TrackingCard)
    """
    error = ''
    if mover.game_location in game.tableau and mover != mover.game_location[0]:
        mover_index = mover.game_location.index(mover)
        if mover.game_location[mover_index - 1].up:
            error = 'Only complete stacks may be moved on the tableau.'
    return error

def deal_selective(game):
    """
    Deal tableau cards with selection of the starting foundation card. (None)

    Parameters:
    game: The game to deal cards for. (Solitaire)
    """
    # Get the possible foundation cards.
    starters = game.deck.cards[-len(game.tableau) - 1:]
    starter_text = ', '.join([card.rank + card.suit for card in starters])
    # Get the player's choice for a foundation card.
    message = 'Which of these cards would you like on the foundation: {}? '.format(starter_text)
    while True:
        founder = game.human.ask(message).strip()
        if founder in starters:
            break
        game.human.tell('That is not one of the available cards.')
    # Deal the foundation card chosen.
    founder = game.deck.find(founder)
    target = game.find_foundation(founder)
    game.deck.force(founder, target)
    game.foundation_rank = founder.rank
    # Deal the rest of the cards.
    deal_tableau1(game)

def deal_tableau1(game):
    """
    Deal one card face up to each tableau pile. (None)

    Parameters:
    game: The game to deal cards for. (Solitaire)
    """
    for stack in game.tableau:
        game.deck.deal(stack, True)

def deal_twos_foundations(game):
    """
    Deal the twos to the foundations. (None)

    Parameters:
    game: The game to deal cards for. (Solitaire)
    """
    for suit in game.deck.suits:
        deuce = game.deck.find('2' + suit)
        target = game.find_foundation(deuce)
        game.deck.force(deuce, target)

def lane_reserve(game, card, moving_stack):
    """
    Check only laning cards from the reserve. (str)

    If nothing is in the reserve, the waste pile may be used.
    
    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The cards on top of the card moving. (list of TrackingCard)
    """
    error = ''
    # check for the moving card being on top of a reserve pile.
    if not any(game.reserve) and card != game.waste[-1]:
        error = 'If the reserve is empty, you can only lane cards from the waste.'
    elif any(game.reserve) and card not in [stack[-1] for stack in game.reserve]:
        error = 'You can only move cards from the reserve into an empty lane.'
    return error


if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    canfield = Canfield(player.Player(name), '')
    canfield.play()