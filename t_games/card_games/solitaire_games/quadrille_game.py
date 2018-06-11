"""
quadrille_game.py

A game of Quadrille.

Classes:
Quadrille: A game of Quadrille. (solitaire.Solitaire)
"""


import time

import t_games.card_games.solitaire_games.solitaire_game as solitaire


class Quadrille(solitaire.Solitaire):
    """
    A game of Quadrille. (solitaire.Solitaire)
    """

    # The menu categories for the game.
    categories = ['Card Games', 'Solitaire Games', 'Closed Games']
    # The name of the game.
    name = 'Quadrille'

    def do_auto(self, arguments):
        """
        Automatically play cards into the foundations. (bool)
        
        Parameters:
        arguments: The arguments to the sort command. (str)
        """
        # Check for full auto.
        if arguments.lower().startswith('f'):
            self.full_auto(arguments)
            return False
        # Otherwise handle normally.
        else:
            return super(Quadrille, self).do_auto(arguments)

    def __str__(self):
        """Human readable text representation. (str)"""
        piles = self.foundations
        lines = ['', '      {}'.format(piles[2][-1])]
        lines.append('  {}      {}'.format(piles[5][-1], piles[6][-1]))
        lines.append('      QH')
        lines.append('{}  QD  QS  {}'.format(piles[1][-1], piles[3][-1]))
        lines.append('      QC')
        lines.append('  {}      {}'.format(piles[4][-1], piles[7][-1]))
        lines.append('      {}'.format(piles[0][-1]))
        lines.extend(('', self.stock_text(), ''))
        return '\n'.join(lines)

    def find_foundation(self, card):
        """
        Determine which foudations a card could be sorted to. (list of list)

        Parameters:
        card: The card to find foundations for. (card.TrackingCard)
        """
        foundation_index = self.deck.suits.index(card.suit)
        if card.rank in '789TJ':
            foundation_index += 4
        return self.foundations[foundation_index]

    def full_auto(self, arguments):
        """
        Automatically play the game. (bool)
        
        Parameters:
        arguments: The arguments to the sort command. (str)
        """
        # Strip out non-digits from the front of the argument.
        while arguments and not arguments.isdigit():
            arguments = arguments[1:]
        # Convert the arguments to a 0-10 digit.
        if arguments:
            speed = 10 - min(10, max(0, int(arguments)))
        else:
            speed = 5
        # Make moves while there are cards to move.
        passes = self.stock_passes
        while self.stock or self.waste:
            # Get a card to sort.
            if not self.waste:
                self.do_turn('')
            else:
                # Check the card for sorting.
                foundation = self.find_foundation(self.waste[-1])
                if self.sort_check(self.waste[-1], foundation, False):
                    self.do_sort(str(self.waste[-1]))
                # If you cant sort, get another card.
                elif self.stock:
                    self.do_turn('')
                else:
                    # Keep track of passes through the deck, and exit when limit reached.
                    passes += 1
                    if passes == self.options['max-passes']:
                        break
                    else:
                        self.do_turn('')
            # Update tracking and pause.
            print(self)
            self.turns += 1
            time.sleep(0.1 * speed)

    def set_checkers(self):
        """Set the game specific rule checking functions. (None)"""
        super(Quadrille, self).set_checkers()
        # Set the rule checking functions.
        self.build_checkers = [solitaire.build_none]
        self.lane_checkers = [solitaire.lane_none]
        self.sort_checkers = [solitaire.sort_up_down]
        # Set the dealers
        self.dealers = [solitaire.deal_queens_out, solitaire.deal_five_six, solitaire.deal_stock_all]

    def set_options(self):
        """Set the available game options."""
        self.options = {'num-foundations': 8, 'num-reserve': 4, 'turn-count': 1, 'max-passes': 3,
            'wrap-ranks': True}


if __name__ == '__main__':
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    quad = Quadrille(player.Player(name), '')
    quad.play()
