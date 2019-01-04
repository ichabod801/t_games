"""
solitaire_game.py

Base class for solitaire games.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
HELP_TEXt: General help for solitaire games. (str)
MULTI_DECK_HELP: Help for multi-deck solitaire games. (str)
SCORE_HELP: An explanation of how solitaire game scores are calculated. (str)

Classes:
Solitaire: A generalized solitaire game. (game.Game)
MultiSolitaire: A game of solitaire that uses multiple decks. (Solitaire)
"""


import itertools
import random

import t_games.cards as cards
import t_games.game as game
from t_games.card_games.solitaire_games.rule_checkers import *


HELP_TEXT = """
Help for solitaire games. (?)

Cards are represented by a two character string. The first is the number of
their rank (for 2-9) for the first character of their rank (jokers are rank
X). The second character is the first letter of their suit. So the Two of
Hearts is 2H and Jack of Clubs is JC. ?? representes a face down card, and
-- represents an empty space where a card was or could be.

There are various commands for the standard moves in a solitaire game:

    * build: Build stacks on the tableau.
    * free: Move cards to free cells.
    * lane: Move cards to empty tableau piles.
    * match: Match pairs of cards together.
    * sort: Move cards to the foundations.
    * turn: Turn cards over from the stock.

In addition, the undo command will take back moves and the auto command will
sort multiple cards at a time. Help is available for all of these commands.

You can also just enter one or two cards without a command. The game will try
to look for a move and make one if it can find one. If two cards are given, it
will first try a build move, and if that doesn't work it will try to match the
cards. Otherwise the order of moves the system looks for is:

    1. Try to sort the card to a foundation.
    2. Try to build the card on another card.
    3. Try to match the card with another card.
    4. Try to move the card to a free cell.
    5. Try to move the card to an empty lane.

For games with multiple decks of cards, see also 'help multi-deck'. And be
sure to check the rules for the specific game you are playing.
"""

MULTI_DECK_HELP = """
Solitaire games with multiple decks bring about extra issues for text-based
games. If you want to build the Two of Spades onto the Three of Diamonds,
there may be two Two of Spades available to move and/or two Three of Diamons
to build them on.

The first way to deal with this is to be specific when possible. If you just
type '2S' to move the Two of Spades onto the Three of Diamonds, it might get
moved on to the Three of Hearts. So be clear with '2S 3D'. You can be more
specific with location identifiers. The format for cards with location
identifiers is RS-AN (Rank, Suit, Area, Number). The area can be F (free
cells), R (reserve), T (tableau), or W (waste). The number is only needed for
reserve and tableau piles, and can be from 1 (the first/leftmost) to the number
of piles. It defaults to one, for cases where there is only one reserve pile.
Note that using just a number for a location identifier is assumed to be
refering to a tableau pile.

If the move made is still not the one you intended, you can use the alternate
command (alias alt) to pick an alternate version of the move. This does not
penalize you in terms of the move count. You can add location identifiers as
arguments to the alternate command. The first one refers to the (current)
location of the card you want to move, and the second (if given) indicates
where you want to move it to.
"""

SCORE_HELP = """
Scores are standardized for all solitaire games. You start with zero points,
and lose one point for each card in the deck (not counting decorative cards,
like the Queens in Quadrille). You then lose a further point for every move,
including undos (and when you undo, you don't get the point back for the move
you are undoing). You gain five points every time you sort a card. If you win,
you get a bonus five points for every card that has been sorted. If you win
without undoing you get a further bonus of five points for every card that was
sorted at the end of the game. That is, for every card sorted since the last
move that didn't sort a card to the foundations. For scoring purposes, every
card moved to the foundation counts as sorted, whether it was moved there with
a sort move or a match move.
"""


class Solitaire(game.Game):
    """
    A generalized solitaire game. (game.game)

    As an example of how this generally works: the foo command is handled by
    the do_foo method, which parse the command and uses the foo_check method
    to confirm a valid move. The foo_check method checks basic rules common
    to all games, and then uses the foo_checker attribute (a list of
    functions) to check rules specific to the game.

    Attributes:
    build_checkers: Functions for determining valid builds. (list of callable)
    cells: Holding spaces for manuevering cards. (list of Card)
    dealers: The deal functions for setting up the tableau. (list of callable)
    deck: The deck of cards for the game. (cards.TrackingDeck)
    foundations: The piles to fill to win the game. (list of list of Card)
    free_checkers: Functions for determining valid cell moves. (list of callable)
    lane_checkers: Functions for determining valid lane mvoes. (list of callable)
    match_checkers: Functions for determining valid matches. (list of callable)
    max_passes: The number of allowed passes through the stock. (int)
    moves: The moves taken in the game. (list of list)
    num_cells: The number of cells in the game. (int)
    options: The standard solitaire options for this game. (dict of str: object)
    pair_checkers: Functions for validating pairs in tableau stacks. (list)
    reserve: Piles where building is not permitted. (list of list of Card)
    sort_checkers: Functions for validating foundation moves. (list of callable)
    stock: A face down pile of cards for later play. (list of Card)
    stock_passes: The number of times the waste has been gone through. (int)
    tableau: The main playing area. (list of list of card.TrackingCard)
    turn_count: The number of cards to turn from the stock each time. (int)
    undo_count: The number of undos taken in the game. (int)
    waste: A face up pile of cards that can be played from. (list of Card)
    wrap_ranks: Flag for building by rank wrappng from king to ace. (bool)

    Methods:
    build_check: Check for a valid build. (bool)
    build_pair: Check for a valid pair of building cards. (str)
    cell_text: Generate the text for the cards in cells. (str)
    deal: Deal the initial set up for the game. (None)
    do_auto: Automatically play cards into the foundations. (bool)
    do_build: Build card(s) into stacks on the tableau. (bool)
    do_free: Move a card to one of the free cells. (bool)
    do_lane: Move a card into an empty lane. (None)
    do_match: Match two cards and discard them. (None)
    do_sort: Move a card to the foundation. (bool)
    do_turn: Turn cards from the stock into the waste. (bool)
    do_undo: Undo one or more previous moves. (bool)
    find_foundation: Find the foundation a card should sort to. (list of Card)
    foundation_text: Generate the text for the foundation piles. (str)
    free_check: Check that a card can be moved to a free cell. (bool)
    game_over: Check for the foundations being full. (bool)
    guess: Guess what move to make for a particular card. (None)
    guess_two: Guess what move to make for two given cards. (bool)
    lane_check: Check for a valid move into a lane. (bool)
    match_check: Check for a valid match of two cards. (bool)
    reserve_text: Generate text for the reserve piles. (str)
    set_checkers: Set the game specific rules. (None)
    set_solitaire: Special initialization for solitaire games. (None)
    sort_check: Check for a valid sort. (bool)
    stack_check: Check for a valid stack to move. (bool)
    stock_text: Generate text for the stock and waste. (str)
    super_stack: Find and validate any stack being moved. (list of Card)
    tableau_text: Generate text for the tableau piles. (str)
    transfer: Move a stack of cards from one game location to another. (None)

    Overridden Methods:
    __str__
    default
    player_action
    set_options
    set_up
    """

    aliases = {'a': 'auto', 'b': 'build', 'f': 'free', 'l': 'lane', 'm': 'match', 'otto': 'auto',
        's': 'sort', 't': 'turn', 'u': 'undo'}
    help_text = {'help': HELP_TEXT, 'multi-deck': MULTI_DECK_HELP, 'scores': SCORE_HELP}
    name = 'Solitaire Base'

    def __str__(self):
        """Generate a huuman readable text representation. (str)"""
        # Assume there are foundations and a tableau, add other text as needed.
        lines = []
        lines.append(self.foundation_text())
        if self.num_cells:
            lines.append(self.cell_text())
        lines.append(self.tableau_text())
        if self.reserve:
            lines.append(self.reserve_text())
        if self.stock or self.waste:
            lines.append(self.stock_text())
        return '\n' + '\n\n'.join(lines)

    def build_check(self, mover, target, moving_stack, show_error = True):
        """
        Check for a valid build. (bool)

        Parameters:
        mover: The card to move. (Card)
        target: The destination card. (Card)
        moving_stack: The stack of cards that would move with mover. (Card)
        show_error: A flag for displaying why the build failed. (bool)
        """
        error = ''
        # check for valid destination
        if target.game_location not in self.tableau or target != target.game_location[-1]:
            error = 'The destination (the {:n}) is not on top of a tableau pile.'.format(target)
        # check for moving foundation cards
        elif mover.game_location in self.foundations:
            error = 'Cards may not be moved from the foundation.'
        # check for face down cards
        elif not mover.up:
            error = 'The {:n} is face down and cannot be moved.'.format(mover)
        # check for a valid stack to move
        elif not moving_stack:
            error = 'The {:n} is not the base of a movable stack.'.format(mover)
        # check valid stack
        else:
            error = self.build_pair(mover, target)
            if not error:
                for checker in self.build_checkers:
                    error = checker(self, mover, target, moving_stack)
                    if error:
                        break
        # handle determination
        if error and show_error:
            self.human.error()
            self.human.error(error)
        return not error

    def build_pair(self, mover, target):
        """
        Check for a valid pair of building cards. (str)

        Returns any error resulting from the build.

        Parameters:
        mover: The card to move. (Card)
        target: The destination card. (Card)
        """
        error = ''
        for checker in self.pair_checkers:
            error = checker(self, mover, target)
            if error:
                break
        return error

    def cell_text(self):
        """Generate the text for the cards in cells. (str)"""
        extras = ['--' for cell in range(self.options['num-cells'] - len(self.cells))]
        return ' '.join([str(card) for card in self.cells] + extras)

    def clean_up(self):
        """Handle end of game tasks. (None)"""
        # Set the turn count.
        self.turns = self.move_count + 2 * self.undo_count
        # Give congrats or condolonces.
        if self.win_loss_draw[0]:
            self.human.tell('\nCongratulation! You won!')
            # Add win bonuses to the score.
            self.scores[self.human.name] += sum([len(foundation) for foundation in self.foundations]) * 5
            if not self.undo_count:
                self.scores[self.human.name] += self.last_sort * 5
        else:
            self.human.tell('\nYou lost. Better luck next time.')
        # Give a contrats message.
        message = 'You made {} moves (with {} undos), for a score of {}.'
        self.human.tell(message.format(self.turns, self.undo_count, self.scores[self.human.name]))

    def deal(self):
        """Deal the initial set up for the game. (None)"""
        for dealer in self.dealers:
            dealer(self)

    def default(self, line):
        """
        Handle unrecognized commands. (bool)

        line: The user's input. (str)
        """
        cards = self.deck.card_re.findall(line)
        # No cards is just standard error.
        if not cards:
            self.human.error('\nI do not recognize that command.')
        # One or two cards are guess moves.
        elif len(cards) == 1:
            return self.guess(cards[0])
        elif len(cards) == 2:
            return self.guess_two(*cards)
        # More than two cards is someone being silly.
        else:
            self.human.error("\nI don't know what to do with that many cards.")

    def do_auto(self, max_rank):
        """
        Automatically play cards to the foundations. (a)

        If no argument is given, auto will play cards as long as it can. If a card
        rank is given as an argument, auto will on play cards up to and including that
        rank.
        """
        # Convert max rank to int.
        max_rank = max_rank.upper()
        if max_rank.strip() == '':
            max_rank = len(self.deck.ranks) - 1
        elif max_rank in self.deck.ranks:
            max_rank = self.deck.ranks.index(max_rank)
        else:
            self.human.error('\nThere was an error: the rank specified is not in the deck.')
            return True
        # Loop until there are no sortable cards.
        while True:
            sorts = 0
            # Check free cells.
            for card in self.cells:
                card_foundation = self.find_foundation(card)
                if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                    self.do_sort(str(card))
                    sorts += 1
            # Check tableau.
            for pile in self.tableau:
                if pile:
                    card = pile[-1]
                    card_foundation = self.find_foundation(card)
                    if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                        self.do_sort(str(card))
                        sorts += 1
            # Check the waste.
            if self.waste:
                card = self.waste[-1]
                card_foundation = self.find_foundation(card)
                if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                    self.do_sort(str(card))
                    sorts += 1
            # Check the reserve.
            for pile in self.reserve:
                if pile:
                    card = pile[-1]
                    card_foundation = self.find_foundation(card)
                    if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                        self.do_sort(str(card))
                        sorts += 1
            if not sorts:
                break
        return False

    def do_build(self, arguments):
        """
        Build card(s) into stacks on the tableau. (b)

        Two cards must be given to this command: the card to move and the card to
        build it onto. If you are moving a stack of cards, specify the bottom card of
        the stack as the card to move.
        """
        # Parse the arguments.
        card_arguments = self.deck.card_re.findall(arguments.upper())
        if len(card_arguments) != 2:
            self.human.error('\nInvalid arguments to build command: {!r}.'.format(arguments))
            return True
        mover, target = card_arguments
        # Get the details on all the cards.
        mover = self.deck.find(mover)
        target = self.deck.find(target)
        moving_stack = self.super_stack(mover)
        # Check for a valid move.
        if self.build_check(mover, target, moving_stack):
            self.transfer(moving_stack, target.game_location)
            return False
        else:
            return True

    def do_free(self, card):
        """
        Move a card to one of the free cells. (f)

        This command takes one argument: the card to move.
        """
        # Parse the arguments.
        card_arguments = self.deck.card_re.findall(card.upper())
        if len(card_arguments) != 1:
            self.human.error('\nInvalid arguments to free command: {!r}.'.format(arguments))
            return True
        # Get the details on the card to be freed.
        card = self.deck.find(card_arguments[0])
        # Free the card.
        if self.free_check(card):
            self.transfer([card], self.cells)
            return False
        else:
            return True

    def do_lane(self, card):
        """
        Move a card into an empty lane. (l)

        This command takes one argument: the card to move.
        """
        # Get the card and the cards to be moved.
        if not self.deck.card_re.match(card):
            self.human.error('\nInvalid card passed to lane command: {!r}.'.format(card))
            return True
        card = self.deck.find(card)
        moving_stack = self.super_stack(card)
        # Check for validity and move.
        if self.lane_check(card, moving_stack):
            self.transfer(moving_stack, self.tableau[self.tableau.index([])])
            return False
        else:
            return True

    def do_match(self, cards):
        """
        Match two cards and discard them. (m)

        The two cards specified by the arguments can be listed in any order.
        """
        # Get the card and the card to be matched.
        cards = self.deck.card_re.findall(cards)
        if len(cards) != 2:
            self.human.error('\nYou must provide two valid cards to the match command.')
            return True
        # Check for validity and match.
        cards = [self.deck.find(card) for card in cards]
        if self.match_check(*cards):
            self.transfer([cards[0]], self.foundations[0])
            self.transfer([cards[1]], self.foundations[0], undo_ndx = 1)

    def do_sort(self, card):
        """
        Move a card to the foundation. (s)

        This command takes one argument: the card to move.
        """
        # Get the card to sort.
        if not self.deck.card_re.match(card):
            self.human.error('\nInvalid card passed to sort command: {!r}.'.format(card))
            return True
        card = self.deck.find(card)
        # Check for validity and sort.
        foundation = self.find_foundation(card)
        if self.sort_check(card, foundation):
            self.transfer([card], foundation)
            return False
        else:
            return True

    def do_turn(self, arguments):
        """
        Turn cards from the stock into the waste. (t)

        This command takes no arguments. The number of cards turned over depends on
        the rules of the game you are playing.
        """
        # Check for being able to turn cards.
        if self.stock_passes != self.max_passes and (self.stock or self.waste):
            # Put the waste back in the stock if necessary.
            if not self.stock:
                self.transfer(self.waste[:], self.stock, up = False)
                self.stock.reverse()
            # Flip over turn count cards.
            for card_index in range(self.turn_count):
                self.transfer(self.stock[-1:], self.waste, undo_ndx = card_index)
                # Stop when the stock runs out.
                if not self.stock:
                    break
            if not self.stock:
                self.stock_passes += 1
            return False
        # Warn on invalid turn attempts.
        elif self.stock or self.waste:
            self.human.error('\nYou may not make any more passes through the stock.')
            return True
        else:
            self.human.error('\nThere are no more cards to turn.')
            return True

    def do_undo(self, num_moves):
        """
        Undo one or more previous moves. (u)

        If this command is called with no arguments, one move is undone. If an integer
        argument is given, that many moves are undone.
        """
        # Get the number of moves to undo.
        if not num_moves.strip():
            num_moves = 1
        num_moves = int(num_moves)
        # Loop through that many undos.
        moves_undone = False
        for move_index in range(num_moves):
            # Check for there being a move to undo.
            if self.moves:
                # Update the move tracking.
                move_stack, old_location, new_location, undo_index, flip = self.moves.pop()
                moves_undone = True
                # Check for flipping the undone card(s) back down.
                if old_location:
                    force_down = (old_location == self.stock or old_location in self.reserve)
                    force_down = force_down and not old_location[-1].up
                else:
                    force_down = old_location is self.stock
                # Check for having flipped a revealed card.
                if flip:
                    old_location[-1].up = False
                # Move the cards back.
                self.transfer(move_stack, old_location, track = False, undo_ndx = undo_index)
                # Handle flipping the undone card(s) back down.
                if force_down:
                    for card in move_stack:
                        card.up = False
                # Handle multiple-transfer moves recursively.
                if undo_index:
                    self.do_undo('')
                else:
                    self.undo_count += 1
                    self.move_count -= 1
            # Stop if there's nothing to undo.
            else:
                self.human.error('\nThere are no moves to undo.')
                break
        # End the turn if a move was undone.
        return not moves_undone

    def find_foundation(self, card):
        """
        Determine which foundation a card should sort to. (list of Card)

        Parameters:
        card: The card to be sorted. (cards.TrackingCard)
        """
        return self.foundations[self.deck.suits.index(card.suit)]

    def foundation_text(self):
        """Generate the text for the foundation piles. (str)"""
        return ' '.join([str(pile[-1]) if pile else '--' for pile in self.foundations])

    def free_check(self, card, show_error = True):
        """
        Check that a card can be moved to a free cell. (bool)

        Parameters:
        card: The card to be freed. (Card)
        show_error: A flag for showing why the card can't be freed. (bool)
        """
        error = ''
        # Check for open cells.
        if len(self.cells) == self.num_cells:
            error = 'There are no free cells to place the {:n} into.'.format(card)
        # Check for foundation card.
        elif card.game_location in self.foundations:
            error = 'Cards cannot be freed from the foundation.'
        # Check for blocked card.
        elif card.game_location[-1] != card:
            error = 'The {:n} is not available to be freed.'.format(card)
        # Check for a face down card.
        elif not card.up:
            error = 'The {:n} is face down and cannot be freed.'.format(card)
        # Check game specific rules.
        else:
            for checker in self.free_checkers:
                error = checker(self, card)
                if error:
                    break
        # Handle determination.
        if error and show_error:
            self.human.error()
            self.human.error(error)
        return not error

    def game_over(self):
        """
        Check for the foundations being full. (bool)

        'Full' is defined as containing all cards that are were not discarded.
        """
        # Get the card counts.
        check = sum([len(foundation) for foundation in self.foundations])
        target = len(self.deck.cards) + len(self.deck.in_play)
        # Check for the win.
        if check == target:
            # Update the score.
            self.win_loss_draw[0] = 1
            return True
        else:
            # Carry on.
            return False

    def guess(self, card_text):
        """
        Guess what move to make for a particular card. (bool)

        Parameters:
        card_text: The card to move. (str)
        """
        go = True
        # Get the card.
        card = self.deck.find(card_text)
        # Check sorting the card.
        if self.foundations and self.sort_check(card, self.find_foundation(card), False):
            go = self.do_sort(str(card))
        else:
            moving_stack = self.super_stack(card)
            for pile in self.tableau:
                # Check building the card
                if pile and self.build_check(card, pile[-1], moving_stack, False):
                    go = self.do_build('{:u} {:u}'.format(card, pile[-1]))
                    break
                # Check matching the card.
                elif pile and self.match_check(card, pile[-1], False):
                    go = self.do_match('{:u} {:u}'.format(card, pile[-1]))
                    break
            else:
                # Check non-tableau matching.
                for pile in [self.waste] + self.reserve + [[free] for free in self.cells]:
                    if pile and self.match_check(card, pile[-1], False):
                        go = self.do_match('{:u} {:u}'.format(card, pile[-1]))
                        break
                else:
                    # Check freeing the card.
                    if card.game_location is not self.cells and self.free_check(card, False):
                        go = self.do_free(str(card))
                    # Check laning the card.
                    elif self.lane_check(card, moving_stack, False):
                        go = self.do_lane(str(card))
                    else:
                        # Error out if nothing works.
                        player = self.players[self.player_index]
                        player.error('\nThere are no valid moves for the {:n}.'.format(card))
        return go

    def guess_two(self, card_text, target_text):
        """
        Guess what move to make for two given cards. (bool)

        Parameters:
        card_text: The specification for the first card. (str)
        target_text: The specification for the second card. (str)
        """
        go = True
        # Get the card information.
        card = self.deck.find(card_text)
        target = self.deck.find(target_text)
        moving_stack = self.super_stack(card)
        two_text = '{:u} {:u}'.format(card, target)
        # Check for building the card on the target.
        if self.build_check(card, target, moving_stack, False):
            go = self.do_build(two_text)
        # Check for matching the card with the target.
        elif self.match_check(card, target, False):
            go = self.do_match(two_text)
        # Error out if you can't build or match.
        else:
            player = self.players[self.player_index]
            error = '\nThere are no valid moves for the {:n} and the {:n}.'
            player.error(error.format(card, target))
        return go

    def lane_check(self, card, moving_stack, show_error = True):
        """
        Check for a valid move into a lane. (bool)

        Parameters:
        card: The card to move into the lane. (Card)
        moving_stack: The cards on top of the card moving. (list of Card)
        show_error: A flag for showing why the card can't be moved. (bool)
        """
        error = ''
        # Check for sorted cards.
        if card.game_location in self.foundations:
            error = 'The {:n} is sorted and cannot be moved.'.format(card)
        # Check for face down cards.
        elif not card.up:
            error = 'The {:n} is face down and cannot be moved.'.format(card)
        # Check for open lanes.
        elif not self.tableau.count([]):
            error = 'There are no open lanes.'
        # Check for a valid stack.
        elif not moving_stack:
            error = 'The {:n} is not the base of a valid stack to move.'.format(card)
        # Check game specific rules.
        else:
            for checker in self.lane_checkers:
                error = checker(self, card, moving_stack)
                if error:
                    break
        # Warn the user of any errors.
        if error and show_error:
            self.human.error()
            self.human.error(error)
        return not error

    def match_check(self, card, match, show_error = True):
        """
        Check ofr a valid match of two cards. (bool)

        Parameters:
        card: The card being checked. (card.TrackingCard)
        match: The card it is being matched to. (card.TrackingCard)
        show_error: A flag for showing why the card can't be moved. (bool)
        """
        error = ''
        # Check both cards equally.
        for check_it in [card, match]:
            # Check for sorted cards.
            if check_it.game_location in self.foundations:
                error = 'The {:n} is sorted and cannot be moved.'.format(check_it)
                break
            # Check for face down cards.
            elif not check_it.up:
                error = 'The {:n} is face down and cannot be moved.'.format(check_it)
                break
        # Check game specific rules.
        else:
            for checker in self.match_checkers:
                error = checker(self, card, match)
                if error:
                    break
        # Warn the user of any errors.
        if error and show_error:
            self.human.error()
            self.human.error(error)
        return not error

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        The return value is a flag for the player's turn being done.

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Get the move.
        player.tell(self)
        move = player.ask('\nWhat is your move? ')
        # Make the move.
        keep_playing = self.handle_cmd(move)
        # Score the move.
        sorted_count = sum([len(foundation) for foundation in self.foundations])
        deck_size = len(self.deck.cards) + len(self.deck.in_play)
        self.scores[self.human.name] = sorted_count * 5 - self.move_count - deck_size - self.undo_count * 2
        return keep_playing

    def reserve_text(self):
        """Generate text for the reserve piles. (str)"""
        reserve_text = []
        for pile in self.reserve:
            if pile:
                reserve_text.append(str(pile[-1]))
            else:
                reserve_text.append('--')
        return ' '.join(reserve_text)

    def set_checkers(self):
        """Set the game specific rules. (None)"""
        # Set the default checkers.
        self.build_checkers = []
        self.free_checkers = []
        self.lane_checkers = []
        self.match_checkers = [match_none]
        self.pair_checkers = []
        self.sort_checkers = []
        # Set the default dealers.
        self.dealers = [deal_all]

    def set_options(self):
        """Handle game options and set the player list. (None)"""
        self.options = {}

    def set_solitaire(self):
        """
        Special initialization for solitaire games. (None)

        For an ulimited number of passes through the stock, set max_passes to -1.
        """
        # Update the default solitaire options based on the game.
        options = {'deck-specs': [], 'num-tableau': 7, 'num-foundations': 4, 'num-reserve': 0,
            'num-cells': 0, 'turn-count': 3, 'max-passes': -1, 'wrap-ranks': False}
        options.update(self.options)
        # Initialize the specified attributes.
        self.num_cells = options['num-cells']
        self.wrap_ranks = options['wrap-ranks']
        self.turn_count = options['turn-count']
        self.max_passes = options['max-passes']
        # Initialize the derived attributes.
        # Initialize the deck.
        self.deck = cards.TrackingDeck(self, *options['deck-specs'])
        deal_num = -1
        deal_text_index = self.option_set.settings_text.find('deal-num')
        if deal_text_index != -1:
            self.option_set.settings_text = self.option_set.settings_text[:(deal_text_index - 1)]
        if self.raw_options.lower() != 'none':
            prompt = '\nEnter the deal number, or return for a random deal: '
            deal_num = self.human.ask_int(prompt, low = 0, default = -1, cmd = False)
        if deal_num == -1:
            deal_num = None
        elif deal_num == 0:
            deal_num = random.randint(1, 1000000)
            self.human.tell('The random deal number is {}.'.format(deal_num))
        if deal_num:
            self.option_set.settings_text += ' deal-num={}'.format(deal_num)
        self.deck.shuffle(number = deal_num)
        # Initialize the variable game locations
        self.tableau = [[] for pile in range(options['num-tableau'])]
        self.foundations = [[] for foundation in range(options['num-foundations'])]
        self.reserve = [[] for pile in range(options['num-reserve'])]
        # Initialize the default attributes.
        # Initialize the static game locations.
        self.cells = []
        self.stock = []
        self.stock_passes = 0
        self.waste = []
        # Initialize the undo history.
        self.moves = []
        self.undo_count = 0
        self.move_count = 0
        self.last_sort = 0
        # Initialize the game specific rules.
        self.set_checkers()

    def set_up(self):
        """Set up the game. (None)"""
        self.set_solitaire()
        self.deal()
        self.scores[self.human.name] = -len(self.deck.cards) - len(self.deck.in_play)

    def sort_check(self, card, foundation, show_error = True):
        """
        Check for a valid sort. (bool)

        Parameters:
        card: The card to be sorted. (Card)
        foundation: The target foundation. (list of Card)
        show_error: A flag for showing why the card can't be sorted. (bool)
        """
        error = ''
        # Check for moving foundation cards.
        if card.game_location in self.foundations:
            error = 'The {:n} is already sorted.'.format(card)
        # check for face down cards.
        elif not card.up:
            error = 'The {:n} is face down and cannot be sorted.'.format(card)
        # Check for blocked cards.
        elif (card.game_location in self.tableau + self.reserve + [self.waste] and
            card.game_location[-1] != card):
            error = 'The {:n} is blocked and cannot be sorted.'.format(card)
        # Check game specific rules.
        else:
            for checker in self.sort_checkers:
                error = checker(self, card, foundation)
                if error:
                    break
        # Warn the user of any errors.
        if error and show_error:
            self.human.error()
            self.human.error(error)
        return not error

    def stack_check(self, stack):
        """
        Check for a valid stack to move. (bool)

        Parameters:
        stack: The stack of cards to check. (list of Card)
        """
        valid = True
        if len(stack) > 1:
            for card_index, card in enumerate(stack[:-1]):
                next_card = stack[card_index + 1]
                if self.build_pair(next_card, card):
                    valid = False
                    break
        return valid

    def stock_text(self):
        """Generate text for the stock and waste. (str)"""
        # Generate the stock text.
        if self.stock:
            stock_text = '??'
        else:
            stock_text = '--'
        # Generate the waste text.
        for card in self.waste[-self.turn_count:]:
            stock_text += ' ' + str(card)
        stock_text += ' ' * (3 * self.turn_count + 2 - len(stock_text))
        return stock_text

    def super_stack(self, card):
        """
        Find and validate any stack being moved. (list of Card)

        If the stack is invalid, an empty list is returned.

        Parameters:
        card: The card at the base of the stack to be moved.
        """
        stack = []
        if card.game_location is self.cells:
            # A card in a cell is just the card.
            stack = [card]
        elif card.game_location in self.reserve + [self.waste]:
            # A card in the reserve or waste is a just the card, if it's on top.
            if card == card.game_location[-1]:
                stack = [card]
            else:
                stack = []
        else:
            # Otherwise (it's in the tableau) check the full stack.
            stack = card.game_location[card.game_location.index(card):]
            if not self.stack_check(stack):
                stack = []
        return stack

    def tableau_text(self):
        """Generate text for the tableau piles. (str)"""
        max_tableau = max([len(pile) for pile in self.tableau])
        tableau_lines = [['--' for pile in self.tableau]]
        tableau_lines += [['  ' for pile in self.tableau] for pile_index in range(max_tableau - 1)]
        for pile_index, pile in enumerate(self.tableau):
            for card_index, card in enumerate(pile):
                tableau_lines[card_index][pile_index] = str(card)
        return '\n'.join([' '.join(line) for line in tableau_lines])

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
        # Record the move.
        old_location = move_stack[0].game_location
        if track:
            self.moves.append([move_stack[:], old_location, new_location, undo_ndx])
        # Move the cards.
        for card in move_stack:
            old_location.remove(card)
            card.up = up
        new_location.extend(move_stack)
        # Turn over any revealed cards.
        if old_location and old_location is not self.stock and not old_location[-1].up:
            old_location[-1].up = True
            # Track turning over revealed cards.
            if track:
                self.moves[-1].append(True)
        elif track:
            self.moves[-1].append(False)
        # Reset location tracking.
        for card in move_stack:
            card.game_location = new_location
        # Update the move counts.
        if not undo_ndx and track:
            self.move_count += 1
            if new_location in self.foundations:
                self.last_sort += 1
            else:
                self.last_sort = 0


class MultiSolitaire(Solitaire):
    """
    A game of solitaire that uses multiple decks. (Solitaire)

    You could have one class, and if there is only one deck, return a list of
    one, but you would lose specificity of errors.

    Attributes:
    alt_moves: Alternate possibilities for the last move. (list of tuple)

    Methods:
    do_alternate: Redo the last command with different but matching cards. (bool)
    find_location: Find a location in the game. (list)
    move_error: Warn the user about an invalid move. (None)

    Overridden Methods:
    do_auto
    do_build
    do_free
    do_lane
    do_match
    do_sort
    do_turn
    do_undo
    find_foundation
    guess
    guess_two
    set_solitaire
    transfer
    """

    aliases = {'alt': 'alternate'}
    name = 'MultiSolitaire Base'

    def do_alternate(self, argument):
        """
        Redo the last command with different but matching cards. (alt)

        This is for when there are two cards of the same rank and suit that
        can make the same move, and the game makes the wrong one.
        """
        if self.alt_moves:
            # Find the last move from the user.
            move_index = -1
            while self.moves[move_index][3]:
                move_index -= 1
            base_move = self.moves[move_index]
            # Find the move to make.
            if argument:
                # Get the specifications and possibilities.
                locations = [self.find_location(word) for word in argument.split()]
                valid = self.alt_moves[:]
                # Filter the possibilities by the location specifications.
                if locations:
                    valid = [move for move in valid if move[0][0].game_location == locations[0]]
                if len(locations) > 1:
                    valid = [move for move in valid if move[1] == locations[1]]
                # Make the move if there is one.
                if valid:
                    new_move = valid.pop()
                    self.alt_moves.remove(new_move)
                else:
                    # Warn the user of bad specifications.
                    new_move = None
                    self.human.error('\nThere is no alternate move matching that specification.')
            else:
                new_move = self.alt_moves.pop()
            if new_move:
                # Undo the last move without penalty.
                self.do_undo('1', clear_alt = False)
                self.undo_count -= 1
                # Redo the move with the next move.
                self.transfer(*new_move)
                return False
        else:
            # Warn the user of invalid plays.
            self.human.error('\nThe last move is not alternatable.')
            return True

    def do_auto(self, max_rank):
        """
        Automatically play cards to the foundations. (a)

        If no argument is given, auto will play cards as long as it can. If a card
        rank is given as an argument, auto will on play cards up to and including that
        rank.
        """
        # Convert max rank to int
        max_rank = max_rank.upper()
        if max_rank.strip() == '':
            max_rank = len(self.deck.ranks) - 1
        elif max_rank in self.deck.ranks:
            max_rank = self.deck.ranks.index(max_rank)
        else:
            self.human.error('\nThere was an error: the rank specified is not in the deck.')
            return True
        # Loop until there are no sortable cards
        while True:
            # Reset the loop.
            sorts = 0
            # Check the free cells.
            for card in self.cells:
                foundations = self.find_foundation(card)
                for card_foundation in foundations:
                    if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                        self.do_sort(str(card))
                        sorts += 1
            # Check the tableau piles.
            for pile in self.tableau:
                if pile:
                    card = pile[-1]
                    foundations = self.find_foundation(card)
                    for card_foundation in foundations:
                        if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                            self.do_sort(str(card))
                            sorts += 1
            # Check the waste.
            if self.waste:
                card = self.waste[-1]
                foundations = self.find_foundation(card)
                for card_foundation in foundations:
                    if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                        self.do_sort(str(card))
                        sorts += 1
            # Check the reserve piles.
            for pile in self.reserve:
                if pile:
                    card = pile[-1]
                    foundations = self.find_foundation(card)
                    for card_foundation in foundations:
                        if card.rank_num <= max_rank and self.sort_check(card, card_foundation, False):
                            self.do_sort(str(card))
                            sorts += 1
            if not sorts:
                break
        return False

    def do_build(self, arguments):
        """
        Build card(s) into stacks on the tableau. (b)

        Two cards must be given to this command: the card to move and the card to
        build it onto. If you are moving a stack of cards, specify the bottom card of
        the stack as the card to move.
        """
        # Parse the arguments.
        card_arguments = self.deck.card_re.findall(arguments.upper())
        if len(card_arguments) != 2:
            self.human.error('\nInvalid arguments to build command: {!r}.'.format(arguments))
            return True
        mover, target = card_arguments
        # Get the details on both cards.
        movers = self.deck.find(mover)
        targets = self.deck.find(target)
        self.alt_moves = []
        for mover in movers:
            moving_stack = self.super_stack(mover)
            for target in targets:
                # Check for a valid move.
                if self.build_check(mover, target, moving_stack, show_error = False):
                    self.alt_moves.append((moving_stack, target.game_location))
        # Make the move.
        if self.alt_moves:
            self.transfer(*self.alt_moves.pop())
            return False
        else:
            # Warn the user about invalid moves.
            self.move_error('building', card_arguments, movers, targets)
            return True

    def do_free(self, card):
        """
        Move a card to one of the free cells. (f)

        This command takes one argument: the card to move.
        """
        # Parse the arguments.
        card_arguments = self.deck.card_re.findall(card.upper())
        if len(card_arguments) != 1:
            self.human.error('\nInvalid arguments to free command: {!r}.'.format(arguments))
            return True
        # Get the details on the card to be freed.
        cards = self.deck.find(card_arguments[0])
        # Free the card
        self.alt_moves = []
        for card in cards:
            if self.free_check(card):
                self.alt_moves.append(([card], self.cells))
        if self.alt_moves:
            self.transfer(*self.alt_moves.pop())
            return False
        else:
            # Warn the user about invalid moves.
            self.move_error('freeing', card_arguments, cards)
            return True

    def do_lane(self, card_text):
        """
        Move a card into an empty lane. (l)

        This command takes one argument: the card to move.
        """
        # Get the card and the cards to be moved.
        if not self.deck.card_re.match(card_text):
            self.human.error('\nInvalid card passed to lane command: {!r}.'.format(card))
            return True
        cards = self.deck.find(card_text)
        self.alt_moves = []
        for card in cards:
            moving_stack = self.super_stack(card)
            # Check for validity and add the move the possibles.
            if self.lane_check(card, moving_stack, False):
                self.alt_moves.append((moving_stack, self.tableau[self.tableau.index([])]))
        if self.alt_moves:
            # Make one of the possible moves.
            self.transfer(*self.alt_moves.pop())
            return False
        else:
            # Warn the user about invalid moves.
            self.move_error('laning', [card_text], cards)
            return True

    def do_match(self, card_text):
        """
        Match two cards and discard them. (m)

        The two cards specified by the arguments can be listed in any order.
        """
        # Get the cards to match.
        card_words = self.deck.card_re.findall(card_text)
        # Check for a valid number of cards.
        if len(card_words) != 2:
            self.human.error('\nYou must provide two valid cards to the match command.')
            return True
        # Check the actual cards.
        cards = [self.deck.find(card) for card in card_words]
        # Check all possibled combinations of cards for valid moves.
        for card in cards[0]:
            for match in cards[1]:
                if self.match_check([card, match], False):
                    self.alt_moves.append((card, match))
        if self.alt_moves:
            # If there are valid moves, make one of them.
            cards = self.alt_moves.pop()
            self.transfer([card[0]], self.foundations[0])
            self.transfer([card[1]], self.foundations[0])
            return False
        else:
            # Warn the user about invalid moves.
            self.move_error('matching', card_words, cards[0], cards[1])
            return True

    def do_sort(self, card_text):
        """
        Move a card to the foundation. (s)

        This command takes one argument: the card to move.
        """
        # Get the cards.
        if not self.deck.card_re.match(card_text):
            self.human.error('\nInvalid card passed to sort command: {!r}.'.format(card))
            return True
        cards = self.deck.find(card_text)
        # Check the cards for sortability.
        self.alt_moves = []
        for card in cards:
            foundations = self.find_foundation(card)
            for foundation in foundations:
                if self.sort_check(card, foundation, False):
                    self.alt_moves.append(([card], foundation))
        if self.alt_moves:
            # If there are valid moves, make one of them.
            self.transfer(*self.alt_moves.pop())
            return False
        else:
            # Warn the user about invalid moves.
            self.move_error('sorting', card_text, cards)
            return True

    def do_turn(self, arguments):
        """
        Turn cards from the stock into the waste. (t)

        This command takes no arguments. The number of cards turned over depends on
        the rules of the game you are playing.
        """
        # Remove the previous alternative moves.
        self.alt_moves = []
        return super(MultiSolitaire, self).do_turn(arguments)

    def do_undo(self, num_moves, clear_alt = True):
        """
        Undo one or more previous moves. (u)

        If this command is called with no arguments, one move is undone. If an integer
        argument is given, that many moves are undone.
        """
        # Remove the previous alternative moves if asked to.
        if clear_alt:
            self.alt_moves = []
        return super(MultiSolitaire, self).do_undo(num_moves)

    def find_foundation(self, card):
        """
        Find the foundations a card can be sorted to. (list of list)

        Parameters:
        card: The card to sort. (str)
        """
        first_index = self.deck.suits.index(card.suit)
        foundations = []
        for deck_index in range(self.deck.decks):
            foundations.append(self.foundations[first_index + len(self.deck.suits) * deck_index])
        return foundations

    def find_location(self, location_text):
        """
        Find a location in the game. (list)

        Parameters:
        location_text: Text specifying the location. (str)
        """
        # Parse out the location type and the location count.
        location_text = location_text.upper()
        if location_text.isdigit():
            location_type = 'T'
            location_count = int(location_text) - 1
        elif location_text[-1].isdigit():
            location_type = location_text[0]
            location_count = int(location_text[1:]) - 1
        else:
            location_type = location_text
            location_count = 0
        # Get the location by type.
        if location_type == 'F':
            location = self.cells
        elif location_type == 'R':
            location = self.reserve
        elif location_type == 'T':
            location = self.tableau
        elif location_type == 'W':
            location = self.waste
        else:
            location = []
        # Get the sub-location based on the count.
        if location_type in 'RT':
            try:
                location = location[location_count]
            except IndexError:
                location = []
        return location

    def guess(self, card_text):
        """
        Guess what move to make for a particular card. (None)

        Parameters:
        card_text: The card to move. (str)
        """
        # Loop through the possible cards.
        card_text = card_text.upper()
        cards = self.deck.find(card_text)
        moves = []
        for card in cards:
            # Check sorting the card.
            if self.foundations:
                for foundation in self.find_foundation(card):
                    if self.sort_check(card, foundation, False):
                        moves.append('sort {:u}'.format(card))
            if not moves:
                moving_stack = self.super_stack(card)
                for pile in self.tableau:
                    # Check bulding the card.
                    if pile and self.build_check(card, pile[-1], moving_stack, False):
                        moves.append('build {:u} {:u}'.format(card, pile[-1]))
                        break
                    # Check matching the card.
                    elif pile and self.match_check(card, pile[-1], False):
                        moves.append('match {:u} {:u}'.format(card, pile[-1]))
                        break
                else:
                    # Check non-tableau matching of the card.
                    for pile in [self.waste] + self.reserve + [[free] for free in self.cells]:
                        if pile and self.match_check(card, pile[-1], False):
                            moves.append('match {:u} {:u}'.format(card, pile[-1]))
                            break
                    else:
                        # Check freeing the card.
                        if card.game_location is not self.cells and self.free_check(card, False):
                            moves.append('free {:u}'.format(card))
                        # Check laning the card.
                        elif self.lane_check(card, moving_stack, False):
                            moves.append('lane {:u}'.format(card))
            if moves:
                break
        # Make a move if you have one.
        if moves:
            moves.reverse()
            return self.handle_cmd(moves.pop())
        # If no moves were found, errror out.
        elif cards:
            self.human.error('\nThere is no valid move for {:a}.'.format(card))
            return True
        # If no cards were found, error out.
        else:
            self.human.error('\nNo card was found matching {!r}.'.format(card_text))

    def guess_two(self, card, target):
        """
        Guess what move to make for two given cards. (bool)

        Parameters:
        card: The first card specified. (str)
        target: The second card specified. (str)
        """
        # Get the card information.
        card_text = '{} {}'.format(card, target)
        cards = self.deck.find(card)
        targets = self.deck.find(target)
        moves = []
        # Loop through all combinations of cards.
        for card, target in itertools.product(cards, targets):
            moving_stack = self.super_stack(card)
            # Check for building the card on the target.
            if self.build_check(card, target, moving_stack, False):
                moves.append('build {:u} {:u}'.format(card, target))
            # Check for matching the card with the target.
            elif self.match_check(card, target, False):
                moves.append('match {:u} {:u}'.format(card, target))
        # Make a move if you have one.
        if moves:
            return self.handle_cmd(moves.pop())
        # If no moves were found, errror out.
        else:
            self.move_error('bulding or matching', card_text.split(), cards, targets)
            return True

    def move_error(self, move_type, card_arguments, movers, targets = None):
        """
        Warn the user about an invalid move. (None)

        Parameters:
        move_type: The type of move being made. (str)
        card_arguments: The arguments passed to the do_move method. (str or list of str)
        movers: The possible cards to move. (list of TrackingCard)
        targets: The possible cards to move onto. (list of TrackingCard)
        """
        if movers:
            if targets:
                # Warn the user if there are no valid two-card moves.
                message = '\nThere are no valid moves for {} {:a} onto {:a}.'
                self.human.error(message.format(move_type, movers[0], targets[0]))
            elif targets is None:
                # Warn the user if there are no valid one-card moves.
                self.human.error('\nThere are no valid moves for {} {:a}.'.format(move_type, movers[0]))
            else:
                # Warn the user if the target card can't be found.
                self.human.error('\nThere is no card matching {!r}.'.format(card_arguments[1].upper()))
        else:
            # Warn the user if the moving card can't be found.
            self.human.error('\nThere is no card matching {!r}.'.format(card_arguments[0].upper()))

    def set_solitaire(self):
        """
        Special initialization for solitaire games. (None)

        For an ulimited number of passes through the stock, set max_passes to -1.
        """
        options = {'deck-specs': [], 'num-tableau': 7, 'num-foundations': 4, 'num-reserve': 0,
            'num-cells': 0, 'turn-count': 3, 'max-passes': -1, 'wrap-ranks': False}
        options.update(self.options)
        # Initialize the specified attributes.
        self.num_cells = options['num-cells']
        self.wrap_ranks = options['wrap-ranks']
        self.turn_count = options['turn-count']
        self.max_passes = options['max-passes']
        # Initialize the derived attributes.
        # Initialze the deck.
        self.deck = cards.MultiTrackingDeck(self, *options['deck-specs'])
        deal_num = -1
        deal_text_index = self.option_set.settings_text.find('deal-num')
        if deal_text_index != -1:
            self.option_set.settings_text = self.option_set.settings_text[:(deal_text_index - 1)]
        if self.raw_options.lower() != 'none':
            prompt = '\nEnter the deal number, or return for a random deal: '
            deal_num = self.human.ask_int(prompt, low = 0, default = -1, cmd = False)
        if deal_num == -1:
            deal_num = None
        elif deal_num == 0:
            deal_num = random.randint(1, 1000000)
            self.human.tell('The random deal number is {}.'.format(deal_num))
        if deal_num:
            self.option_set.settings_text += ' deal-num={}'.format(deal_num)
        self.deck.shuffle(number = deal_num)
        # Initialize the piles of piles.
        self.tableau = [[] for pile in range(options['num-tableau'])]
        self.foundations = [[] for foundation in range(options['num-foundations'])]
        self.reserve = [[] for pile in range(options['num-reserve'])]
        # Initialize default attributes.
        # Intialize the simple piles.
        self.cells = []
        self.stock = []
        self.stock_passes = 0
        self.waste = []
        # Initialize the undo history.
        self.moves = []
        self.undo_count = 0
        self.move_count = 0
        self.last_sort = 0
        # Set the game specific rules.
        self.set_checkers()

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
        super(MultiSolitaire, self).transfer(move_stack, new_location, track, up, undo_ndx)
        # Clear the location text for the moving card.
        move_stack[0].loc_txt = ''
        move_stack[0].location_text = ''


if __name__ == '__main__':
    # Play the game without the interface.
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    solo = Solitaire(player.Player(name), '')
    solo.play()
