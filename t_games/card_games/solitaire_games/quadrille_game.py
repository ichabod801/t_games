"""
quadrille_game.py

A game of Quadrille.

       5H
  6D
       QH
5D  QD    QS
       QC

Classes:
Quadrille: A game of Quadrille. (solitaire.Solitaire)
"""


import t_games.card_games.solitaire_games as solitaire


class Quadrille(solitaire.Solitaire):
    """
    A game of Quadrille. (solitaire.Solitaire)
    """

    # The menu categories for the game.
    categories = ['Card Games', 'Solitaire Games', 'Closed Games']
    # The name of the game.
    name = 'Quadrille'
    
    def do_sort(self, card):
        """
        Move a card to the foundation. (bool)
        
        Parameters:
        card: The card being moved. (str)
        """
        # get the card
        if not self.deck.card_re.match(card):
            self.human.error('Invalid card passed to sort command: {!r}.'.format(card))
            return True
        card = self.deck.find(card)
        for foundation in self.find_foundation(card):
            if self.sort_check(card, foundation, False):
                self.transfer([card], foundation)
                return False
        message = 'The {} cannot be sorted to either the up or down foundation at the moment.'
        self.human.error(message.format(card))
        return True

    def find_foundation(self, card):
        """
        Determine which foudations a card could be sorted to. (list of list)

        Parameters:
        card: The card to find foundations for. (card.TrackingCard)
        """
        foundation_index = self.deck.suits.index(card.suit)
        return self.foundations[foundation_index], self.foundations[foundation_index + 4]

    def set_options(self):
        """Set the available game options."""
        self.options = {'num-foundations': 8, 'num-reserve': 4, 'turn-count': 1, 'max-passes': 3}


def sort_up_down(game, card, foundation):
    """
    Sort a card up or down, depending on the foundation. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card to sort. (card.TrackingCard)
    foundation: The foundation to sort it to. (list of card.TrackingCard)
    """
    error = ''
    if game.foundations.index(foundation) < 4:
        if not card.below(foundation[-1]):
            error = 'The {} is not one rank below the {}.'.format(card, foundation[-1])
    elif not card.above(foundation[-1]):
        error = 'The {} is not one rank above the {}.'.format(card, foundation[-1])


if __name__ == '__main__':
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    quad = Quadrille(player.Player(name), '')
    quad.play()
