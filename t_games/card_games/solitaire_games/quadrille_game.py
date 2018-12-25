"""
quadrille_game.py

A game of Quadrille.

Constants:
CREDITS: The credits for Qualdrille. (str)
RULES: The rules for Quadrille. (str)

Classes:
Quadrille: A game of Quadrille. (solitaire.Solitaire)
"""


import time

import t_games.card_games.solitaire_games.solitaire_game as solitaire


# The credits for Quadrille.
CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

# The rules for Quadrille.
RULES = """
The queens are layed out in the center. The fives and sixes are dealt around
them as foundations. The fives build down to the kings, and the sixes build up
to the jacks.

You can flip cards from the stock one at a time into the waste, and sort the
top card of the waste. You get three passes through the deck.

You may use the command 'auto full' (or just 'auto f') to have the computer
play the game for you. You can add a number from 0 to 10 to adjust the speed
at which it plays.
"""


class Quadrille(solitaire.Solitaire):
    """
    A game of Quadrille. (solitaire.Solitaire)

    Methods:
    full_auto: Automatically play the game for the user. (bool)

    Overridden Methods:
    __str__
    do_auto
    find_foundation
    set_checkers
    set_options
    """

    aka = ['Captive Queens', 'La Francaise', 'Partners', 'Quad']
    categories = ['Card Games', 'Solitaire Games', 'Revealing Games']
    credits = CREDITS
    name = 'Quadrille'
    rules = RULES

    def __str__(self):
        """Generate a human readable text representation. (str)"""
        piles = self.foundations
        lines = ['', '      {}'.format(piles[2][-1])]
        lines.append('  {}      {}'.format(piles[5][-1], piles[6][-1]))
        lines.append('      QH')
        lines.append('{}  QD  QS  {}'.format(piles[1][-1], piles[3][-1]))
        lines.append('      QC')
        lines.append('  {}      {}'.format(piles[4][-1], piles[7][-1]))
        lines.append('      {}'.format(piles[0][-1]))
        lines.extend(('', self.stock_text()))
        return '\n'.join(lines)

    def do_auto(self, arguments):
        """
        Automatically play cards into the foundations. (a)

        If full (or f) is passed as the first argument to the auto command (in
        Quadrille), the game is played for you by the computer. If a number from zero
        to ten is passed as a second argument, it controls the speed at which the
        computer plays from 0 (one move per second) to 10 (as fast as possible).
        """
        # Check for full auto.
        if arguments and arguments.lower().split()[0] in ('f', 'full'):
            self.full_auto(arguments)
            return False
        # Otherwise handle normally.
        else:
            return super(Quadrille, self).do_auto(arguments)

    def do_gipf(self, arguments):
        """
        I don't know that dance.
        """
        # Run the edge, if possible.
        game, losses = self.gipf_check(arguments, ('yacht',))
        # Winning Yacht gives you an extra pass through the deck.
        if game == 'yacht':
            if not losses:
                self.max_passes += 1
                self.human.tell('\nYou have gained an extra pass through the deck.')
        # Otherwise I'm confused.
        else:
            self.human.tell("I don't know that dance.")
        return True

    def find_foundation(self, card):
        """
        Determine which foudations a card could be sorted to. (list of list)

        Parameters:
        card: The card to find foundations for. (card.TrackingCard)
        """
        # Find the base foundation.
        foundation_index = self.deck.suits.index(card.suit)
        # Switch foundations for cards building up.
        if card.rank in '789TJ':
            foundation_index += 4
        return self.foundations[foundation_index]

    def full_auto(self, arguments):
        """
        Automatically play the game for the user. (bool)

        Parameters:
        arguments: The arguments to the sort command. (str)
        """
        # Strip out non-digits from the front of the argument.
        arguments = ''.join([char for char in arguments if char.isdigit()])
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
        # Set the dealers.
        self.dealers = [solitaire.deal_queens_out, solitaire.deal_five_six, solitaire.deal_stock_all]

    def set_options(self):
        """Set the available game options."""
        self.options = {'num-foundations': 8, 'num-reserve': 4, 'turn-count': 1, 'max-passes': 3,
            'wrap-ranks': True}


if __name__ == '__main__':
    # Play the game without the full interface.
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    quad = Quadrille(player.Humanoid(name), '')
    quad.play()
