"""
freecell_game.py

FreeCell and related games.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: Credits for FreeCell. (str)
RULES: Rules for FreeCell. (str)
STACK_HELP: Help on how many cards can be moved at one time. (str)

Classes:
FreeCell: A game of FreeCell. (Solitaire)
"""


import random

import t_games.card_games.solitaire_games.solitaire_game as solitaire
import t_games.utility as utility


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
you to move a stack that size as one move. For example, if you have two free
cells, you can move a stack of three cards one at a time: one each to a free
cell, then third to the destination card, then the two cards back off the free
cells. So if you have two empty free cells, the game lets you move three cards
as one.

Options:
baker: Building is done by suit (Baker's Game).
cells: The number of free cells available. 1-10, defaults to 4.
challenge: The twos then the aces are dealt on the bottom row.
egnellahc: The aces then the twos are dealt on the bottom row.
fill-free: The free cells are filled with the last four card from the deck.
kings-only: Only kings can be used to fill free cells.
piles: The number of tableau piles. 4-10, defaults to 8.
supercell: One random card in each pile is turned face down.
"""

STACK_HELP = """
The number of cards you can move at one time depends on the number of empty
free cells and the number of empty lanes. The formula for how many you can
move is (1 + C) * 2 ^ L, where C is the number of empty cells and L is the
number of empty lanes*.

For the mathphobic:

          Cells
Lanes 0  1  2  3  4
  0   1  2  3  4  5
  1   2  4  6  8 10
  2   4  8 12 16 20
  3   8 16 24 32 40

If you are moving the cards to a lane, don't count that lane.

* The formula using the rpn command would be: 1 C + 2 L ^ *
"""


class FreeCell(solitaire.Solitaire):
    """
    A game of FreeCell. (Solitaire)

    Attributes:
    baker: A flag for building being by suit. (bool)
    challenge: A flag for dealing the twos and aces first. (bool)
    egnellahc: A flag for dealing the aces and twos first. (bool)
    fill_free: A flag for filling the free cells with the last four cards. (bool)
    kings_only: A flag for only allowing kings in empty lanes. (bool)
    supercell: A flag for flipping tableau cards over randomly. (bool)

    Overridden Methods:
    set_checkers
    set_options
    """

    aka = ['Free']
    categories = ['Card Games', 'Solitaire Games', 'Open Games']
    credits = CREDITS
    help_text = {'moving-stacks': STACK_HELP}
    name = 'FreeCell'
    num_options = 8
    rules = RULES

    def do_gipf(self, arguments):
        """
        There are no valid moves for the gipf of spades.
        """
        game, losses = self.gipf_check(arguments, ('hamurabi',))
        # Hamurabi allows building a free cell card on any tableau pile.
        if game == 'hamurabi':
            if not losses:
                # Get the state of the game.
                self.human.tell(self)
                cell_check = self.cell_text()
                tableau_check = [str(stack[-1]) for stack in self.tableau if stack]
                # Relax the rules.
                pair_hold = self.pair_checkers
                self.pair_checkers = []
                # Get the cards to move.
                while True:
                    cards_raw = self.human.ask('Enter a free cell card and a card to build it on: ')
                    cards = cards_raw.upper().split()
                    if cards[0] not in cell_check:
                        self.human.error('You must build with a free cell card.')
                    elif cards[1] not in tableau_check:
                        self.human.error('You must build to the top of a tableau pile.')
                    # Stop asking for cards when there's a valid move.
                    elif not self.do_build(cards_raw):
                        break
                # Reset the rules.
                self.pair_checkers = pair_hold
        # Otherwise I'm confused.
        else:
            self.human.tell('There are no valid moves for the gipf of spades.')

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(FreeCell, self).set_checkers()
        # Set the game specific rules checkers.
        self.build_checkers = [solitaire.build_one]
        self.lane_checkers = [solitaire.lane_one]
        if self.kings_only:
            self.lane_checkers.append(solitaire.lane_king)
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_alt_color]
        if self.baker:
            self.pair_checkers[1] = solitaire.pair_suit
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up]
        # Set the dealers
        if self.challenge:
            self.dealers = [solitaire.deal_twos, solitaire.deal_aces, solitaire.deal_all]
        elif self.egnellahc:
            self.dealers = [solitaire.deal_aces, solitaire.deal_twos, solitaire.deal_all]
        else:
            self.dealers = [solitaire.deal_all]
        if self.fill_free:
            self.dealers.append(solitaire.deal_free)
        if self.supercell:
            self.dealers.append(solitaire.flip_random)

    def set_options(self):
        """Set the game options. (None)"""
        self.options = {}
        # Set the tableau dimensions.
        self.option_set.add_option('cells', ['c'], action = 'key=num-cells', converter = int,
            default = 4, valid = range(1, 15), target = self.options,
            question = 'How many free cells (1-10, return for 4)? ')
        self.option_set.add_option('piles', ['p'], action = 'key=num-tableau', converter = int,
            default = 8, valid = range(4, 14), target = self.options,
            question = 'How many tableau piles (4-10, return for 8)? ')
        # Set the deal options.
        self.option_set.add_option('challenge', ['ch'],
            question = 'Should the twos and aces be dealt first? bool')
        self.option_set.add_option('egnellahc', ['eg'],
            question = 'Should the aces and twos be dealt first? bool')
        self.option_set.add_option('supercell', ['sc'],
            question = 'Should random cards be flipped face down? bool')
        self.option_set.add_option('fill-free', ['ff'],
            question = 'Should the free cells be filled with the last four cards dealt? bool')
        # Set the play options.
        self.option_set.add_option('kings-only', ['ko'],
            question = 'Should the kings be the only card playable to empty lanes? bool')
        self.option_set.add_option('baker', ['b'],
            question = "Should tableau cards be built by suit (Baker's Game)? bool")


if __name__ == '__main__':
    # Play the game without the full interface.
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    freec = FreeCell(player.Humanoid(name), '')
    freec.play()
