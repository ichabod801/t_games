"""
canfield_game.py

A game of Canfield.
"""


import tgames.card_games.solitaire_games.solitaire_game as solitaire


CREDITS = """
Game Design: Richard A. Canfield
Game Programming: Craig "Ichabod" O'Brien
"""


class Canfield(solitaire.Solitaire):
    """
    A game of Canfield. (Solitaire)
    """

    aka = ['Demon']
    credits = CREDITS
    name = 'Canfield'

    def handle_options(self):
        """Set up the game options. (None)"""
        # Set the default options.
        self.options = {'num-tableau': 4, 'num-reserve': 1, 'wrap-ranks': True}

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        # Set the default checkers.
        super(Canfield, self).set_checkers()
        # Set the rules.
        self.lane_checkers = [lane_reserve]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_alt_color]
        self.sort_checkers = [solitaire.sort_rank, solitaire.sort_up]
        # Set the dealers.
        self.dealers = [deal_reserve13, solitaire.deal_start_foundation, deal_tableau1, 
            solitaire.deal_stock_all]


def deal_reserve13(game):
    """
    Deal 13 cards to the reserve. (None)

    Parameters:
    game: The game to deal cards for. (Solitaire)
    """
    for card_index in range(13):
        game.deck.deal(game.reserve[0], card_index == 12)

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
    Check only laning cards from the reserve. (bool)

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