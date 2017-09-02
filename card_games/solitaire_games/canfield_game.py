"""
canfield_game.py

game of Canfield.

Classes:
Canfield: A game of Canfield. (Solitaire)

Functions:
build_whole: Check that only complete tableau stacks are moved. (str)
deal_tableau1: Deal one card face up to each tableau pile. (None)
lane_reserve: Check only laning cards from the reserve. (str)
"""


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

The options indicate which variant you want to play. Only the first option
is recognized, all other options are ignored.

Options:
Chameleon: A 12 card reserve and three foundation piles. Tableau building is
    down regarless of suit, and partial stacks may be moved. The stock is
    turned one card at a time, but with only one pass through the stock.
"""


class Canfield(solitaire.Solitaire):
    """
    A game of Canfield. (Solitaire)

    Class Attributes:
    variants: The recognized variants of Canfield. (tuple of str)

    Overridden Methods:
    handle_options
    set_checkers
    """

    aka = ['Demon']
    credits = CREDITS
    name = 'Canfield'
    rules = RULES
    variants = ('chameleon')

    def handle_options(self):
        """Set up the game options. (None)"""
        # Set the default options.
        self.options = {'num-tableau': 4, 'num-reserve': 1, 'wrap-ranks': True}
        if self.raw_options.lower() == 'none':
            return None
        if not self.raw_options:
            question = 'Which variant would you like to play (return for standard rules)? '
            while True:
                varaint = self.human.ask(question).strip().lower()
                if not variant:
                    break
                elif variant in self.variants:
                    self.raw_options = variant
                    break
                else:
                    message = 'I do not recognize that variant. The variants I know are:'
                    self.human.tell(message, ', '.join(self.variants))
        if self.raw_options:
            if self.raw_options.lower() == 'chameleon':
                print('chameleon detected')
                self.options['num-tableau'] = 3
                self.options['turn-count'] = 1
                self.options['max-passes'] = 1
            else:
                self.huma.tell('Unrecognized Canfield variant: {}.'.format(self.raw_options))

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        # Set the default checkers.
        super(Canfield, self).set_checkers()
        # Set the rules.
        self.build_checkers = [build_whole]
        self.lane_checkers = [lane_reserve]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_alt_color]
        self.sort_checkers = [solitaire.sort_rank, solitaire.sort_up]
        # Check for variant rules.
        if self.raw_options == 'chameleon':
            self.build_checkers = []
            self.lane_checkers = []
            self.pair_checkers = [solitaire.pair_down]
        # Set the dealers.
        self.dealers = [solitaire.deal_reserve_n(13), solitaire.deal_start_foundation, deal_tableau1, 
            solitaire.deal_stock_all]


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

def deal_tableau1(game):
    """
    Deal one card face up to each tableau pile. (None)

    Parameters:
    game: The game to deal cards for. (Solitaire)
    """
    for stack in game.tableau:
        game.deck.deal(stack, True)

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
    elif card not in [stack[-1] for stack in game.reserve]:
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