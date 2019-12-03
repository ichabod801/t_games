"""
thoughtful_game.py

A game of Thoughtful Solitaire (open Klondike).

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Thoughtful Solitaire. (str)
RULES: The rules of Thoughtful Solitaire. (str)

Classes:
Thoughtful: A game of Thoughtful Solitaire. (solitaire.Solitaire)
"""


import random

from . import solitaire_game as solitaire


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
Thoughtful Solitaire is an open version of Klondike, so all card are dealt face
up. As in Klondike, you can build any card on the top of a tableau pile onto
another tableau card this the opposite color and one rank higher. You can move
complete stacks built in that way as well. The top card of any tableau pile may
also sorted to the foundations going up and in suit. Empty lanes may be filled
with a king.

In addition there are eight reserve piles. The top card from any reserve pile
may be built to the tableau or sorted to the foundations as stated above.
However, once you pull a card from a reserve pile, all the reserve piles to the
left of that reserve pile will be blocked (as indicated by an XX at the bottom
of the pile). They can be unblocked with the turn command. This simulates going
through the stock three cards at a time as in normal Klondike.

Options:
unblocked (u): There are no blocked reserve piles.
"""


class Thoughtful(solitaire.Solitaire):
    """
    A game of Thoughtful Solitaire. (Solitaire)

    Attributes:
    blocked_history: The value of blocked_index after each move. (list of int)
    blocked_index: The index of the rightmost blocked reserve pile. (int)

    Methods:
    card_shift: Shift a card to the top of it's pile. (None)
    turn_transfer: Move a card while undoing a turn move. (None)

    Overridden Methods:
    do_turn
    do_undo
    reserve_text
    set_checkers
    set_options
    set_up
    transfer
    """

    aka = ['Thoughtful', 'ThSo']
    categories = ['Card Games', 'Solitaire Games', 'Open Games']
    credits = CREDITS
    name = 'Thoughtful Solitaire'
    num_options = 1
    rules = RULES

    def card_shift(self, piles, pile_type):
        """
        Shift a card to the top of it's pile. (None)

        Parameters:
        piles: The list of piles the card must be in. (list of list)
        pile_type: The name of the piles being searched. (str)
        """
        # Get the card from the user.
        print(self)
        query = '\nWhich {} card would you like to move to the top of its stack? '.format(pile_type)
        while True:
            card = self.human.ask(query)
            for pile in piles:
                if card in pile:
                    break
            else:
                # Warn the user if you can't find the card.
                self.human.error('That card is not in the {}.'.format(pile_type))
                continue
            break
        # Move the card to the top of the pile.
        pile.append(pile.pop(pile.index(card)))
        # Block undo past this point.
        self.moves = []

    def do_gipf(self, arguments):
        """
        Chess lets you move a tableau card to the top of its pile.

        Klondike lets you move a reserve card to the top of its pile.
        """
        game, losses = self.gipf_check(arguments, ('chess', 'klondike'))
        go = True
        if game == 'chess':
            if not losses:
                self.card_shift(self.tableau, 'tableau')
        elif game == 'klondike':
            if not losses:
                self.card_shift(self.reserve, 'reserve')
        else:
            self.human.tell("That's exactly what I was thinking!")
        return go

    def do_turn(self, arguments):
        """
        Turn cards from the stock into the waste. (t)

        This command takes no arguments. The cards in the reserve are moved left from
        the bottom up until all piles (except maybe the last one) have three cards.
        """
        # Track if any moves are actually made.
        start_moves = len(self.moves)
        # Get the first pile needing cards.
        for pile_index, pile in enumerate(self.reserve):
            if len(pile) < 3:
                start_pile = pile_index
                break
        else:
            start_pile = len(self.reserve) - 1
        # Get the first pile to the right with cards.
        end_pile = start_pile + 1
        for pile_index, pile in enumerate(self.reserve[end_pile:], start = end_pile):
            if pile:
                end_pile = pile_index
                break
        else:
            # Catch no cards to move.
            end_pile = 0
        # Loop through the remaining cards.
        undo = 0
        while end_pile and end_pile < self.options['num-reserve']:
            # Move the next card to the stack needing one.
            self.transfer([self.reserve[end_pile][0]], self.reserve[start_pile], undo_ndx = undo)
            # Update the undo count so it's treated as one move.
            undo += 1
            # Update the end pile.
            while end_pile < self.options['num-reserve'] and not self.reserve[end_pile]:
                end_pile += 1
            # Update the start pile if necessary.
            if len(self.reserve[start_pile]) == 3:
                start_pile += 1
                # Start pile and end pile can't be the same pile, it will reverse itself infinitely.
                if start_pile == end_pile:
                    end_pile += 1
                    while end_pile < self.options['num-reserve'] and not self.reserve[end_pile]:
                        end_pile += 1
        # Check for no cards to move.
        if start_moves == len(self.moves):
            # Find the rightmost pile.
            pile_index = -1
            try:
                while not self.reserve[pile_index]:
                    pile_index -= 1
            # Watch out for an empty reserve.
            except IndexError:
                self.human.error('There is nothing to turn.')
                return True
            # Move that card onto itself (it goes to turn_transfer, so gets put on the bottom).
            #self.transfer([self.reserve[pile_index][0]], self.reserve[pile_index])
        # Reset to no blocked piles.
        if self.blocked and self.blocked_history:
            self.blocked_index = -1
            self.blocked_history[-1] = -1

    def do_undo(self, arguments):
        """
        Undo one or more previous moves. (u)

        If this command is called with no arguments, one move is undone. If an integer
        argument is given, that many moves are undone.
        """
        super(Thoughtful, self).do_undo(arguments)
        if self.blocked:
            # Reset the blocked history and the blocked pile.
            self.blocked_history = self.blocked_history[:len(self.moves)]
            if self.blocked_history:
                self.blocked_index = self.blocked_history[-1]
            else:
                self.blocked_index = -1

    def reserve_text(self):
        """Generate text for the reserve piles. (str)"""
        # Set up a blank reserve.
        max_reserve = max([len(pile) for pile in self.reserve])
        reserve_lines = [['  ' for pile in self.reserve] for row in range(max_reserve)]
        # Fill in the cards.
        for pile_index, pile in enumerate(self.reserve):
            for card_index, card in enumerate(pile):
                reserve_lines[card_index][pile_index] = str(card)
        if self.blocked and self.blocked_index != -1:
            reserve_lines.append(['XX'] * (self.blocked_index + 1))
        # Format and return as a string.
        return '\n'.join(['{}'.format(' '.join(line)) for line in reserve_lines])

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(Thoughtful, self).set_checkers()
        # Set the game specific rules checkers.
        self.build_checkers = [solitaire.build_unblocked]
        self.lane_checkers = [solitaire.lane_king, solitaire.lane_unblocked]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_alt_color]
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up, solitaire.sort_unblocked]
        # Set the dealers.
        self.dealers = [solitaire.deal_klondike, solitaire.deal_reserve_n(24, True), solitaire.deal_open]

    def set_options(self):
        """Define the options for the game. (None)"""
        self.options = {'num-reserve': 8}
        self.option_set.add_option('unblocked', ['u'], default = True, value = False, target = 'blocked',
            question = 'Should indexes to the left of that reserve pile used be blocked? bool')

    def set_up(self):
        """Set up the game. (None)"""
        super(Thoughtful, self).set_up()
        # Set up tracking for the blocked pile.
        self.blocked_index = -1
        self.blocked_history = []

    def transfer(self, move_stack, new_location, track = True, up = True, undo_ndx = 0):
        """
        Move a stack of cards from one game location to another. (None)

        This handles the card's knowledge of where it is and tracking game moves.

        Parameters:
        move_stack: The stack of cards to move. (list of Card)
        new_location: The new game location for the cards. (list of Card)
        track: A flag for tracking the move. (bool)
        up: A flag for the cards being face up. (bool)
        undo_ndx: Nominally how many undos there are to do. (int)
        """
        # Check for undoing turns.
        old_location = move_stack[0].game_location
        if new_location in self.reserve and old_location in self.reserve and not track:
            self.turn_transfer(move_stack, new_location)
        else:
            super(Thoughtful, self).transfer(move_stack, new_location, track, up, undo_ndx)
            # Update and record the blocked pile for this turn.
            if track and self.blocked:
                # Check by id() to avoid matching empty lists that aren't the same pile.
                pile_ids = [id(pile) for pile in self.reserve]
                if not undo_ndx and id(old_location) in pile_ids:
                    self.blocked_index = pile_ids.index(id(old_location)) - 1
                # Move the block back after emptying a reserve pile.
                while self.blocked_index > -1 and not self.reserve[self.blocked_index + 1]:
                    self.blocked_index -= 1
                self.blocked_history.append(self.blocked_index)

    def turn_transfer(self, move_stack, new_location):
        """
        Move a card while undoing a turn move. (None)

        This version prepends the card to the new_location rather than appending it.

        Parameters:
        move_stack: The stack of cards to move. (list of Card)
        new_location: The new game location for the cards. (list of Card)
        """
        # Record the move.
        old_location = move_stack[0].game_location
        # Move the cards.
        for card in move_stack:
            old_location.remove(card)
            new_location.insert(0, card)
        # Reset location tracking.
        for card in move_stack:
            card.game_location = new_location
