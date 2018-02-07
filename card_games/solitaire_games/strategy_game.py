"""
strategy_game.py

Classes:
Strategy: A game of Strategy. (solitaire.Solitaire)
"""


import tgames.card_games.solitaire_games.solitaire_game as solitaire


CREDITS = """
Game Design: Albert Morehead and Geoffrey Mott-Smith
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
All of the cards are dealt to the reserve. You may move the top card of the 
reserve onto any of the eight tableau piles. Aces may be sorted as they 
appear, but no other card may be sorted until the reserve is empty.

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
    categories = ['Card Games', 'Solitaire Games', 'Closed Games', 'Sorters']
    name = 'Strategy'
    num_options = 1
    rules = RULES

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        self.build_checkers = [build_reserve]
        self.lane_checkers = [lane_reserve]
        self.pair_checkers = []
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up, sort_no_reserve]
        self.dealers = [solitaire.deal_reserve_n(52)]

    def set_options(self):
        """Set the game options. (None)"""
        self.options = {'num-tableau': 8, 'num-reserve': 1}
        self.option_set.add_option(name = 'piles', action = 'key=num-tableau', converter = int, 
            default = 8, valid = range(1, 9), target = self.options,
            question = 'How many tableau piles (1-8, return for 8)? ')


def build_reserve(game, mover, target, moving_stack):
    """
    Build from the reserve. (bool)
    
    Parameters:
    game: The game being played. (Solitaire)
    mover: The card to move. (TrackingCard)
    target: The destination card. (TrackingCard)
    moving_stack: The stack of cards that would move. (list of TrackingCard)
    """
    error = ''
    # check that mover is the top card of the waste.
    if (not game.reserve[0]) or mover != game.reserve[0][-1]:
        error = 'You may only build the top card from the reserve.'
    return error

def lane_reserve(game, card, moving_stack):
    """
    Check moving the top reserve card to a lane. (bool)
    
    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The cards on top of the card moving. (list of TrackingCard)
    """
    error = ''
    # check for the moving card being a king.
    if (not game.reserve[0]) or card !=  game.reserve[0][-1]:
        error = 'You can only lane the top card from the reserve.'
    return error

def sort_no_reserve(game, card, foundation):
    """
    Sort non-aces only when the reserve is empty. (bool)
    
    Parameters:
    game: The game being played. (Solitiaire)
    card: The card to be sorted. (TrackingCard)
    foundation: The target foundation. (list of TrackingCard)
    """
    error = ''
    # check for match to foundation pile
    if game.reserve[0] and card.rank != 'A':
        error = 'Only aces can be sorted before the reserve is emptied.'
    return error


if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    strat = Strategy(player.Player(name), '')
    strat.play()