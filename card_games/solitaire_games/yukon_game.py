"""
yukon_game.py

A game of Yukon.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: Credits for Yukon. (str)
RULES: Rules for Yukon. (str)

Class:
Yukon: A game of Yukon.
"""


from . import solitaire_game as solitaire


CREDITS = """
Game Design: Traditional.
Game Programming: Craig "Ichabod" O'Brien.
"""

RULES = """
The cards are dealt in a triangle of seven piles, the first pile having one
card, and each pile to the right having one more card. Then the rest of the
cards are deal face up, left to right, on all stacks but the first.

Any stack of cards may be moved, as long as the bottom card in the stack is one
rank below and a different color than the card it is being moved onto. Empty
tableau piles may be filled with a king or any stack starting with a king.

Options:
piles= (p=): How many tableau piles there should be.
suits (s, russian): Cards must be matched by suit, not alternating color.
"""


class Yukon(solitaire.Solitaire):
    """
    A game of Yukon. (Solitaire)

    Overridden Methods:
    set_checkers
    set_options
    """

    aka = []
    categories = ['Card Games', 'Solitaire Games', 'Building Games']
    credits = CREDITS
    name = 'Yukon'
    num_options = 2
    rules = RULES

    def do_gipf(self, arguments):
        """
        That is not one of the eleven words for snow.
        """
        game, losses = self.gipf_check(arguments, ('klondike',))
        # Mate turns all of the aces face up.
        if game == 'klondike':
            if not losses:
                player = self.players[self.player_index]
                player.tell(self)
                player.tell()
                # Get the mover
                while True:
                    mover = player.ask('Pick a tableau card to move, with two cards on top of it: ')
                    mover = self.deck.find(mover)
                    location = mover.game_location
                    if location in self.tableau and mover == location[-3] and mover.up:
                        moving_stack = location[-3:]
                        break
                    error = 'The {} is not on the tableau with two cards on top of it.'
                    player.error(error.format(mover.name))
                # Get the target.
                while True:
                    target = player.ask('Pick a tableau card to move those three cards to: ')
                    target = self.deck.find(target)
                    location = target.game_location
                    if location in self.tableau and target == location[-1]:
                        break
                    player.error('The {} is not on top of a tableau stack.'.format(target.name))
                # Make the move.
                self.transfer(moving_stack, location)
        # Otherwise I'm confused.
        else:
            self.human.tell("That is not one of the eleven words for snow.")
        return True

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(Yukon, self).set_checkers()
        # Set the game specific rules checkers.
        self.lane_checkers = [solitaire.lane_king]
        if self.suits:
            self.build_checkers = [solitaire.build_down_one, solitaire.build_suit_one]
        else:
            self.build_checkers = [solitaire.build_down_one, solitaire.build_alt_color_one]
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up]
        # Set the dealers
        self.dealers = [solitaire.deal_klondike, solitaire.deal_yukon]

    def set_options(self):
        """Define the options for the game. (None)"""
        self.options = {}
        # Set the deal options.
        self.option_set.add_option('piles', ['p'], action = 'key=num-tableau', target = self.options,
            default = 7, converter = int, question = 'How many tableau piles should their be?')
        self.option_set.add_option('suits', ['s', 'russian'],
            question = 'Should building be done by suits instead of alternating colors? bool')
