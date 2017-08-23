"""
freecell_game.py

FreeCell and related games.

Classes:
FreeCell: A game of freecell. (Solitaire)
"""


import tgames.card_games.solitaire_games.solitaire_game as solitaire
import tgames.utility as utility


CREDITS = """
Game Design/Original Programming: Paul Alfille
Python Implementation: Craig "Ichabod" O'Brien
"""

RULES = """
Cards on the tableau build down in rank and alternating in color. Cards are
sorted to the foundation by suit in ascending rank order. Any card at the top
of a tableau pile may be moved to one of the free cells. Empty tableau piles
may be filled with any card from the top of another tableau pile or one of the
free cells.

Technically, cards may only be moved one at a time. However, the computer
keeps track of how large a stack you could move one card at a time, and allows
you to move a stack that size as one move. For example, if you two free cells,
you can move a stack of three cards one at a time: one each to a free cell,
then third to the destination card, then the two cards back off the free
cells. So if you have two empty free cells, the game lets you move two cards
as one.

Options:
cells: The number of free cells available. 1-10, defaults to 4.
piles: The number of tableau piles. 4-10, defaults to 8.
"""


class FreeCell(solitaire.Solitaire):
    """
    A game of FreeCell. (Solitaire)

    Overridden Methods:
    handle_options
    set_up
    """

    categories = ['Card Games', 'Solitaire Games', 'FreeCell Games']
    name = 'FreeCell'

    def handle_options(self):
        """Process the game options."""
        # Set the defaults.
        self.num_tableau = 8
        self.num_cells = 4
        # Check provided options.
        self.raw_options = self.raw_options.strip().lower()
        # Check for sticking with the defaults.
        if self.raw_options == 'none':
            pass
        # Check for interface provided options.
        elif self.raw_options:
            for word in self.raw_options.split():
                if '=' in word:
                    option, value = word.split('=', maxsplit = 1)
                    # Number of free cells.
                    if option == 'cells':
                        if value.isdigit and int(value) in range(1, 11):
                            self.num_cells = int(value)
                        else:
                            self.human.tell('Invalid cells option value: {}.'.format(value))
                    # Number of tableau piles.
                    elif option == 'piles':
                        if value.isdigit and int(value) in range(4, 11):
                            self.num_tableau = int(value)
                        else:
                            self.human.tell('Invalid piles option value: {}.'.format(value))
        # Check for manual input of options.
        else:
            change = self.human.ask('Would you like to change the options? ')
            if change.lower() in utility.YES:
                # Number of free cells.
                while True:
                    cells = self.human.ask('How many free cells (1-10, return for 4)? ')
                    if not cells.strip():
                        self.num_cells = 4
                    elif cells.strip().isdigit() and int(cells) in range(1, 11):
                        self.num_cells = int(cells)
                    else:
                        self.human.tell('That is not a valid number of cells.')
                        continue
                    break
                # Number of tableau piles.
                while True:
                    piles = self.human.ask('How many tableau piles (4-10, return for 8)? ')
                    if not piles.strip():
                        self.num_tableau = 8
                    elif piles.strip().isdigit() and int(piles) in range(1, 11):
                        self.num_tableau = int(piles)
                    else:
                        self.human.tell('That is not a valid number of piles.')
                        continue
                    break


    def set_up(self):
        """Set up the game for play."""
        # Basic solitaire set up.
        self.set_solitaire(num_tableau = 8, num_cells = 4)
        # Set the game specific rules checkers.
        self.build_checkers = [solitaire.build_one]
        self.lane_checkers = [solitaire.lane_one]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_alt_color]
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up]
        # Set the deck and deal the cards.
        self.dealers = [solitaire.deal_free]
        self.deal()


if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    freec = FreeCell(player.Player(name), '')
    freec.play()