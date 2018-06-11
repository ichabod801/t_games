"""
freecell_game.py

FreeCell and related games.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: Credits for FreeCell. (str)
CREDITS_BAKER: Credits for Baker's Game. (str)
RULES: Rules for FreeCell. (str)
RULES_BAKER: Rules for Baker's Game. (str)

Classes:
FreeCell: A game of FreeCell. (Solitaire)
BakersGame: A game of Baker's Game. (FreeCell)
"""


import random

import t_games.card_games.solitaire_games.solitaire_game as solitaire
import t_games.utility as utility


# Credits for FreeCell.
CREDITS = """
Game Design/Original Programming: Paul Alfille
Python Implementation: Craig "Ichabod" O'Brien
"""

# Credits for Baker's Game.
CREDITS_BAKER = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
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
you to move a stack that size as one move. For example, if you have two free 
cells, you can move a stack of three cards one at a time: one each to a free 
cell, then third to the destination card, then the two cards back off the free
cells. So if you have two empty free cells, the game lets you move three cards
as one.

Options:
cells: The number of free cells available. 1-10, defaults to 4.
piles: The number of tableau piles. 4-10, defaults to 8.
"""


class FreeCell(solitaire.Solitaire):
    """
    A game of FreeCell. (Solitaire)

    Attributes:
    challenge: A flag for dealing the twos and aces first. (bool)
    egnellahc: A flag for dealing the aces and twos first. (bool)
    fill_free: A flag for filling the free cells with the last four cards. (bool)
    kings_only: A flag for only allowing kings in empty lanes. (bool)
    supercell: A flag for flipping tableau cards over randomly. (bool)

    Overridden Methods:
    handle_options
    set_up
    """

    # Interface categories for the game.
    categories = ['Card Games', 'Solitaire Games', 'Open Games']
    credits = CREDITS
    name = 'FreeCell'
    num_options = 8
    rules = RULES

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
                        self.human.error('You must build with a free cell card.')
                    elif cards[1] not in tableau_check:
                        self.human.error('You must build to the top of a tableau pile.')
                    elif not self.do_build(cards_raw):
                        break
                self.pair_checkers = pair_hold
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
        self.option_set.add_option(name = 'cells', action = 'key=num-cells', converter = int, default = 4,
            valid = range(1, 15), target = self.options, 
            question = 'How many free cells (1-10, return for 4)? ')
        self.option_set.add_option(name = 'piles', action = 'key=num-tableau', converter = int, 
            default = 8, valid = range(4, 14), target = self.options,
            question = 'How many tableau piles (4-10, return for 8)? ')
        self.option_set.add_option(name = 'fill-free',
            question = 'Should the free cells be filled with the last four cards dealt? bool')
        self.option_set.add_option(name = 'kings-only',
            question = 'Should the kings be the only card playable to empty lanes? bool')
        self.option_set.add_option(name = 'challenge',
            question = 'Should the twos and aces be dealt first? bool')
        self.option_set.add_option(name = 'egnellahc', 
            question = 'Should the aces and twos be dealt first? bool')
        self.option_set.add_option(name = 'supercell',
            question = 'Should random cards be flipped face down? bool')
        self.option_set.add_option(name = 'baker',
            question = "Should tableau cards be built by suit (Baker's Game)? bool")


if __name__ == '__main__':
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    freec = FreeCell(player.Player(name), '')
    freec.play()