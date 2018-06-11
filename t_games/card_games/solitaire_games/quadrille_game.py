"""
quadrille_game.py

A game of Quadrille.

Classes:
Quadrille: A game of Quadrille. (solitaire.Solitaire)
"""


import t_games.card_games.solitaire_games.solitaire_game as solitaire


class Quadrille(solitaire.Solitaire):
    """
    A game of Quadrille. (solitaire.Solitaire)
    """

    # The menu categories for the game.
    categories = ['Card Games', 'Solitaire Games', 'Closed Games']
    # The name of the game.
    name = 'Quadrille'

    def __str__(self):
        """Human readable text representation. (str)"""
        piles = self.foundations
        lines = ['      {}'.format(piles[2][-1])]
        lines.append('  {}      {}'.format(piles[5][-1], piles[6][-1]))
        lines.append('      QH')
        lines.append('{}  QD  QS  {}'.format(piles[1][-1], piles[3][-1]))
        lines.append('      QC')
        lines.append('  {}      {}'.format(piles[4][-1], piles[7][-1]))
        lines.append('      {}'.format(piles[0][-1]))
        lines.append('')
        lines.append(self.stock_text())
        lines.append('')
        return '\n'.join(lines)
    
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

    def set_checkers(self):
        """Set the game specific rule checking functions. (None)"""
        super(Quadrille, self).set_checkers()
        # Set the rule checking functions.
        self.build_checkers = [solitaire.build_none]
        self.lane_checkers = [solitaire.lane_none]
        self.sort_checkers = [solitaire.sort_up_down]
        # Set the dealers
        self.dealers = [solitaire.deal_reserve_queens, solitaire.deal_five_six, solitaire.deal_stock_all]

    def set_options(self):
        """Set the available game options."""
        self.options = {'num-foundations': 8, 'num-reserve': 4, 'turn-count': 1, 'max-passes': 3}


if __name__ == '__main__':
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    quad = Quadrille(player.Player(name), '')
    quad.play()
