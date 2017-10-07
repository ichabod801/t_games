"""
freecell_game.py

FreeCell and related games.

Constants:
CREDITS: Credits for FreeCell. (str)
CREDITS_BAKER: Credits for Baker's Game. (str)
RULES: Rules for FreeCell. (str)
RULES_BAKER: Rules for Baker's Game. (str)

Classes:
FreeCell: A game of FreeCell. (Solitaire)
BakersGame: A game of Baker's Game. (FreeCell)
"""


import tgames.card_games.solitaire_games.solitaire_game as solitaire
import tgames.utility as utility


# Credits for FreeCell.
CREDITS = """
Game Design/Original Programming: Paul Alfille
Python Implementation: Craig "Ichabod" O'Brien
"""

# Credits for Baker's Game.
CREDITS_BAKER = """
Game Design: Traditional
Python Implementation: Craig "Ichabod" O'Brien
"""

# Rules for FreeCell.
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
cells. So if you have two empty free cells, the game lets you move three cards
as one.

Options:
cells: The number of free cells available. 1-10, defaults to 4.
piles: The number of tableau piles. 4-10, defaults to 8.
"""

# Rules for Baker's Game.
RULES_BAKER = """
Cards on the tableau build down in rank and matching suit. Cards are sorted to
the foundation by suit in ascending rank order. Any card at the top of a 
tableau pile may be moved to one of the free cells. Empty tableau piles may be
filled with any card from the top of another tableau pile or one of the free 
cells.

Technically, cards may only be moved one at a time. However, the computer
keeps track of how large a stack you could move one card at a time, and allows
you to move a stack that size as one move. For example, if you two free cells,
you can move a stack of three cards one at a time: one each to a free cell,
then third to the destination card, then the two cards back off the free
cells. So if you have two empty free cells, the game lets you move three cards
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
    num_options = 2

    def do_gipf(self, arguments):
        """
        Gipf

        Parameters:
        arguments: The name of the game to gipf to. (str)
        """
        game, losses = self.gipf_check(arguments, ('hamurabi',))
        # Hamurabi
        if game == 'hamurabi':
            if not losses:
                self.human.tell(self)
                cell_check = self.cell_text()
                tableau_check = [str(stack[-1]) for stack in self.tableau if stack]
                pair_hold = self.pair_checkers
                self.pair_checkers = []
                while True:
                    cards_raw = self.human.ask('Enter a free cell card and a card to build it on: ')
                    cards = cards_raw.upper().split()
                    if cards[0] not in cell_check:
                        self.human.tell('You must build with a free cell card.')
                    elif cards[1] not in tableau_check:
                        self.human.tell('You must build to the top of a tableau pile.')
                    elif not self.do_build(cards_raw):
                        break
                self.pair_checkers = pair_hold
        else:
            self.human.tell('There are no valid moves for the gipf of spades.')

    def handle_options(self):
        """Process the game options."""
        # Set the defaults.
        self.options = {}
        self.options['num-tableau'] = 8
        self.options['num-cells'] = 4
        # Check provided options.
        self.raw_options = self.raw_options.strip().lower()
        # Check for sticking with the defaults.
        if self.raw_options == 'none':
            pass
        # Check for interface provided options.
        elif self.raw_options:
            self.flags |= 1
            for word in self.raw_options.split():
                if '=' in word:
                    option, value = word.split('=', maxsplit = 1)
                    # Number of free cells.
                    if option == 'cells':
                        if value.isdigit and int(value) in range(1, 11):
                            self.options['num-cells'] = int(value)
                        else:
                            self.human.tell('Invalid cells option value: {}.'.format(value))
                    # Number of tableau piles.
                    elif option == 'piles':
                        if value.isdigit and int(value) in range(4, 11):
                            self.options['num-tableau'] = int(value)
                        else:
                            self.human.tell('Invalid piles option value: {}.'.format(value))
        # Check for manual input of options.
        else:
            change = self.human.ask('Would you like to change the options? ')
            if change.lower() in utility.YES:
                self.flags |= 1
                # Number of free cells.
                prompt = 'How many free cells (1-10, return for 4)? '
                cells = self.human.ask_int(prompt, low = 1, high = 10, default = 4, cmd = False)
                self.options['num-cells'] = cells
                # Number of tableau piles.
                prompt = 'How many tableau piles (4-10, return for 8)? '
                piles = self.human.ask_int(prompt, low = 4, high = 10, default = 8, cmd = False)
                self.options['num-tableau'] = piles

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(FreeCell, self).set_checkers()
        # Set the game specific rules checkers.
        self.build_checkers = [solitaire.build_one]
        self.lane_checkers = [solitaire.lane_one]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_alt_color]
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up]
        # Set the dealers
        self.dealers = [solitaire.deal_free]


class BakersGame(FreeCell):
    """
    A game of Baker's Game. (FreeCell)

    Baker's Game is the game that inspired the creation of FreeCell. It is called
    Baker's Game after C.L. Baker, who described it to Martin Gardner. Baker did
    not claim to have created the game.

    Overridden Methods:
    set_checkers
    """

    aka = ['Brain Jam']
    credits = CREDITS_BAKER
    name = "Baker's Game"
    num_options = 2
    rules = RULES_BAKER

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(BakersGame, self).set_checkers()
        # Set the rules for this variation.
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_suit]


if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    freec = FreeCell(player.Player(name), '')
    freec.play()