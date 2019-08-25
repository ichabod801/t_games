"""
rule_checkers.py

These are rule checking and dealing functions for the Solitaire and
MultiSolitaire classes in solitaire_game.py. They are in their own file for
greater readability.

The parameter list for each type of function:
    * build checkers: game, mover, target, moving_stack
    * dealers: game
    * lane checkers: game, mover, moving_stack
    * match checkers: game, card, match
    * pair checkers: game, mover, target
    * sort checkers: game, card, foundation

Each rule checker returns a string containing a message clarifying any error
found. If that string is empty, the move is valid (as far as that rule is
concerned).

For the reasoning behind the existence of this file, see the wiki.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Functions:
_move_one_size: Calculate maximum stack under "move one" rules. (int)
---------------------------------------------------------------------
build_alt_color_one: Movers must be a different color than the targets. (str)
build_down: Check that only stacks of descending ranks are moved. (str)
build_down_one: Check that the moving card is one less than the target. (str)
build_none: No building is allowed. (str)
build_one: Build moving one card at a time. (str)
build_reserve: Build only from the reserve. (str)
build_suit: Check that only stacks of the same suit are moved. (str)
build_suit_one: You can only build on cards of the same suit. (str)
build_whole: Check that only complete tableau stacks are moved. (str)
-------------------------------------------------
deal_aces: Deal the aces onto the tableau. (None)
deal_aces_multi: Deal the aces to the foundations in a multi-deck game. (None)
deal_aces_up: Deal the aces onto the foundations. (None)
deal_all: Deal all the cards out onto the tableau. (None)
deal_bisley: Deal cards to the tableau with the first four piles short. (None)
deal_five_six: Deal the fives and sixes as foundations. (None)
deal_free: Fill the free cells with the last cards dealt. (None)
deal_klondike: Deal deal a triangle in the tableau. (None)
deal_n: Create a dealer that deals n cards onto the tableau. (function)
deal_one_row: Deal one card face up to each tableau pile. (None)
deal_open: Turn all of the tableau cards face up. (None)
deal_pyramid: Deal a pyramid of cards. (None)
deal_queens_out: Discard the queensl (None)
deal_rank_foundations: Deal a specific rank to the foundations. (None)
deal_reserve_n: Create a dealer that deals n cards to the reserve (None)
deal_selective: Deal tableau cards with selection of foundation rank. (None)
deal_start_foundation: Deal an initial foundation card. (None)
deal_stock_all: Move the rest of the deck into the stock. (None)
deal_twos: Deal the twos onto the tableau. (None)
deal_yukon: Deal the cards face up on the tableau, except the first pile. (None)
flip_random: Flip random tableau cards face down. (None)
--------------------------------------------------------
free_pyramid: Allow freeing cards open below and to the right. (str)
--------------------------------------------------------------------
lane_down: Check moving only stacks of descending ranks into a lane. (str)
lane_king: Check moving only kings into a lane. (str)
lane_none: Cards may not be moved to empty lanes. (str)
lane_one: Check moving one card at a time into a lane. (str)
lane_reserve: Lane only from the reserve (str)
lane_reserve_waste: Check only laning cards from the reserve. (str)
lane_suit: Check moving only stacks of the same suit to empty lanes. (str)
lane_unblocked: Cards may not be moved from blocked reserve piles. (str)
------------------------------------------------------------------------
match_adjacent: Allow matching of cards are in adjacent tableau piles. (str)
match_none: Disallow any match moves. (str)
match_pairs: Allow matching cards of the same rank. (str)
match_pyramid: Allow matching cards open below and to the right. (str)
match_pyramid_relax: Match cards open below and right, or adjacent. (str)
match_tableau: Allow matching if the cards are in the tableau. (str)
match_thirteen: Allow matching cards that sum to 13. (str)
match_top: Allow matching cards on the top of a pile. (str)
match_top_two: Match cards on top of pile, even on top of each other. (str)
--------------------------------------------------
pair_alt_color: Build in alternating colors. (str)
pair_down: Build sequentially down in rank. (str)
pair_not_suit: Build in anything but suits. (str)
pair_suit: Build in suits. (str)
pair_up_down: Build sequentially up or down in rank. (str)
-------------------------------------------
sort_ace: Sort starting with the ace. (str)
sort_kings: Sort starting with a king. (str)
sort_kings_only: Only kings may be sorted. (str)
sort_no_reserve: Sort non-starters only when the reserve is empty. (str)
sort_none: No sorting is allowed. (str)
sort_pyramid: Sorting of blocked cards in a pyramid layout is banned. (str)
sort_rank: Sort starting with a specific rank. (str)
sort_unblocked: Do not sort cards from blocked reserve piles. (str)
sort_up: Sort sequentially up in rank. (str)
sort_up_down: Sort a card up or down, depending on the foundation. (str)
"""


import itertools
import random


################## Define helper functions for the dealers and checkers. ##################


def _move_one_size(game, to_lane = False):
    """
    Calculate maximum stack under "move one" rules. (int)

    In other words, how big a stack could you move by moving one card at a time.

    Parameters:
    game: The game being played. (Solitaire)
    to_lane: A flag for the moving going to an open lane. (str)
    """
    # Get the free cell count.
    free = game.num_cells - len(game.cells)
    # Get the lane count, account for lane king.
    if lane_king in game.lane_checkers:
        lanes = 0
    else:
        lanes = game.tableau.count([]) - to_lane
    # Return the number movable.
    return (1 + free) * 2 ** lanes


################## Define build checkers. ##################


def build_alt_color_one(self, mover, target, moving_stack):
    """
    Movers must be a different color than the targets. (str)

    Parameters:
    game: The game buing played. (Solitaire)
    mover: The card to move. (TrackingCard)
    target: The destination card. (TrackingCard)
    moving_stack: The stack the mover is the base of. (list of TrackingCard)
    """
    error = ''
    # Check for different colors.
    if mover.color == target.color:
        error = 'The {} is not the opposite color of the {}'
        error = error.format(mover.name, target.name)
    return error


def build_down(game, mover, target, moving_stack):
    """
    Check that only stacks of descending ranks are moved. (str)

    Parameters:
    game: The game being played. (Solitaire)
    mover: The card being moved. (TrackingCard)
    target: The card being moved to. (TrackingCard)
    moving_stack: The stack the mover is the base of. (list of TrackingCard)
    """
    error = ''
    # Check that each pair is descending.
    for card, next_card in zip(moving_stack, moving_stack[1:]):
        if not next_card.below(card):
            error = 'Only stacks of descending rank may be moved together.'
            break
    return error


def build_down_one(game, mover, target, moving_stack):
    """
    Check that the moving card is one less than the target card. (str)

    Parameters:
    game: The game being played. (Solitaire)
    mover: The card being moved. (TrackingCard)
    target: The card being moved to. (TrackingCard)
    moving_stack: The stack the mover is the base of. (list of TrackingCard)
    """
    error = ''
    # Check the mover being one less than the target.
    if not mover.below(target):
        error = 'The {} is not one lower than the {}.'.format(mover.name, target.name)
    return error


def build_none(game, mover, target, moving_stack):
    """
    No building is allowed. (str)

    Parameters:
    game: The game being played. (Solitaire)
    mover: The card to move. (TrackingCard)
    target: The destination card. (TrackingCard)
    moving_stack: The stack of cards that would move. (list of TrackingCard)
    """
    return 'Building is not allowed in this game.'


def build_one(game, mover, target, moving_stack):
    """
    Build moving one card at a time. (str)

    Parameters:
    game: The game being played. (Solitaire)
    mover: The card to move. (TrackingCard)
    target: The destination card. (TrackingCard)
    moving_stack: The stack of cards that would move. (list of TrackingCard)
    """
    error = ''
    # Check for enough space to move the cards
    if len(moving_stack) > _move_one_size(game):
        error = 'You may only move {} cards at this time.'.format(_move_one_size(game))
    return error


def build_reserve(game, mover, target, moving_stack):
    """
    Build only from the reserve. (str)

    Parameters:
    game: The game being played. (Solitaire)
    mover: The card to move. (TrackingCard)
    target: The destination card. (TrackingCard)
    moving_stack: The stack of cards that would move. (list of TrackingCard)
    """
    error = ''
    # check that mover is the top card of the waste.
    if (not game.reserve[0]) or mover != game.reserve[0][-1]:
        error = 'You may only build the top card from the reserve.'
    return error


def build_suit(game, mover, target, moving_stack):
    """
    You can only build on cards of the same suit. (str)

    Parameters:
    game: The game being played. (Solitaire)
    mover: The card being moved. (TrackingCard)
    target: The card being moved to. (TrackingCard)
    moving_stack: The stack the mover is the base of. (list of TrackingCard)
    """
    error = ''
    # Check that all cards match the first card's suit.
    suit = mover.suit
    for card in moving_stack[1:]:
        if card.suit != suit:
            error = 'Only stacks of the same suit may be moved together.'
            break
    return error


def build_suit_one(game, mover, target, moving_stack):
    """
    Check that the moving card is the same suit as the target card. (str)

    Parameters:
    game: The game being played. (Solitaire)
    mover: The card being moved. (TrackingCard)
    target: The card being moved to. (TrackingCard)
    moving_stack: The stack the mover is the base of. (list of TrackingCard)
    """
    error = ''
    # Check the mover being the same suit as the target.
    if mover.suit != target.suit:
        error = 'The {} is not the same suit as the {}.'.format(mover.name, target.name)
    return error


def build_unblocked(game, mover, target, moving_stack):
    """
    Do not build from blocked reserve piles. (str)

    Parameters:
    game: The game being played. (Solitaire)
    mover: The card being moved. (TrackingCard)
    target: The card being moved to. (TrackingCard)
    moving_stack: The stack the mover is the base of. (list of TrackingCard)
    """
    error = ''
    # Check that the card isn't in a blocked reserve pile.
    pile = mover.game_location
    if pile in game.reserve and game.reserve.index(pile) <= game.blocked_index:
        error = 'You cannot build cards from blocked reserve piles.'
    return error


def build_whole(game, mover, target, moving_stack):
    """
    Check that only complete tableau stacks are moved. (str)

    Parameters:
    game: The game being played. (Solitaire)
    mover: The card being moved. (TrackingCard)
    target: The card being moved to. (TrackingCard)
    moving_stack: The stack the mover is the base of. (list of TrackingCard)
    """
    error = ''
    # If it's in the tableau and not at the bottom of a pile ...
    if mover.game_location in game.tableau and mover != mover.game_location[0]:
        # ... make sure the card below it is face down.
        mover_index = mover.game_location.index(mover)
        if mover.game_location[mover_index - 1].up:
            error = 'Only complete stacks may be moved on the tableau.'
    return error


################## Define dealers. ##################


def deal_aces(game):
    """
    Deal the aces onto the tableau. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    # Find the next pile to deal to.
    min_tableau = min([len(pile) for pile in game.tableau])
    next_index = [index for index, pile in enumerate(game.tableau) if len(pile) == min_tableau][0]
    # Deal the aces.
    for card in game.deck.cards[::-1]:
        if card.rank == 'A':
            game.deck.force(card, game.tableau[next_index])
            next_index = (next_index + 1) % len(game.tableau)


def deal_aces_multi(game):
    """
    Deal the aces to the foundations in a multi-deck game.

    Parameters:
    game: A multi-deck game of solitaire. (MultiSolitaire)
    """
    # Loop through the suits.
    for suit in game.deck.suits:
        # Loop through the aces.
        ace_text = 'A' + suit
        ace = game.deck.find(ace_text)[0]
        for foundation in game.find_foundation(ace):
            game.deck.force(ace_text, foundation)


def deal_aces_up(game):
    """
    Deal the aces onto the foundations. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    for suit in game.deck.suits:
        card = game.deck.find('A{}'.format(suit))
        foundation = game.find_foundation(card)
        game.deck.force(card, foundation)


def deal_all(game):
    """
    Deal all the cards out onto the tableau. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    for card_index in range(len(game.deck.cards)):
        game.deck.deal(game.tableau[card_index % len(game.tableau)])


def deal_bisley(game):
    """
    Deal all the cards out onto the tableau with the first four piles short. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    for card_index in range(len(game.deck.cards)):
        game.deck.deal(game.tableau[(card_index + 4) % len(game.tableau)])


def deal_five_six(game):
    """
    Deal the fives and sixes as foundations. (None)

    Parameters:
    game: The game to deal cards for. (solitaire.Solitaire)
    """
    for foundation_index, suit in enumerate(game.deck.suits):
        five = game.deck.find('5' + suit)
        game.deck.force(five, game.foundations[foundation_index])
        six = game.deck.find('6' + suit)
        game.deck.force(six, game.foundations[foundation_index + 4])


def deal_free(game):
    """
    Fill the free cells. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    for cell_index in range(game.num_cells):
        game.deck.deal(game.cells, up = True)


def deal_klondike(game):
    """
    Deal deal a triangle in the tableau. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    for card_index in range(len(game.tableau)):
        for pile_index, pile in enumerate(game.tableau[card_index:], card_index):
            game.deck.deal(pile, up = card_index == pile_index)


def deal_n(n, up = True):
    """
    Create a dealer that deals n cards onto the tableau. (function)

    The top card is always dealt face up.

    Parameters:
    n: The number of cards to deal to the reserve. (int)
    up: A flag for dealing the cards face up. (str)
    """
    def dealer(game):
        # Deal the cards.
        for card_index in range(n):
            game.deck.deal(game.tableau[card_index % len(game.tableau)], up = up)
        # Turn the top cards face up.
        for pile in game.tableau:
            pile[-1].up = True
    return dealer


def deal_one_row(game):
    """
    Deal one card face up to each tableau pile. (None)

    Parameters:
    game: The game to deal cards for. (Solitaire)
    """
    for stack in game.tableau:
        game.deck.deal(stack, True)


def deal_open(game):
    """
    Turn all of the tableau cards face up. (None)

    Parameters:
    game: The game to deal cards for. (Solitaire)
    """
    for stack in game.tableau:
        for card in stack:
            card.up = True


def deal_pyramid(game):
    """
    Deal a pyramid of cards. (None)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    """
    num_piles = game.options['num-tableau']
    for pile_count in range(num_piles):
        for pile_index in range(pile_count + 1):
            game.deck.deal(game.tableau[pile_index])


def deal_queens_out(game):
    """
    Discard the queens. (None)

    Parameters:
    game: The game to deal cards for. (solitaire.Solitaire)
    """
    for reserve_index, suit in enumerate(game.deck.suits):
        queen = game.deck.find('Q' + suit)
        # Put the queen in play so it can be discarded.
        game.deck.force(queen, game.reserve[reserve_index])
        game.deck.discard(queen)


def deal_rank_foundations(rank):
    """
    Create a dealer to deal a specific rank to the foundations. (None)

    Parameters:
    rank: The rank to deal to the foundations. (str)
    """
    def deal_foundations(game):
        for suit in game.deck.suits:
            card = game.deck.find(rank + suit)
            target = game.find_foundation(card)
            game.deck.force(card, target)
    return deal_foundations


def deal_reserve_n(n, up = False):
    """
    Create a dealer that deals n cards to the reserve (function)

    The top card is always dealt face up.

    Parameters:
    n: The number of cards to deal to the reserve. (int)
    up: A flag for dealing the cards face up. (str)
    """
    def dealer(game):
        reserve_index = 0
        for card_index in range(n):
            game.deck.deal(game.reserve[reserve_index], up)
            reserve_index = (reserve_index + 1) % game.options['num-reserve']
        for pile in game.reserve:
            pile[-1].up = True
    return dealer


def deal_selective(game):
    """
    Deal tableau cards with selection of the starting foundation card. (None)

    Parameters:
    game: The game to deal cards for. (Solitaire)
    """
    # Get the possible foundation cards.
    starters = game.deck.cards[-len(game.tableau) - 1:]
    starter_text = ', '.join([card.rank + card.suit for card in starters])
    # Get the player's choice for a foundation card.
    message = 'Which of these cards would you like on the foundation: {}? '.format(starter_text)
    while True:
        founder = game.human.ask(message).strip()
        if founder in starters:
            break
        game.human.error('That is not one of the available cards.')
    # Deal the foundation card chosen.
    founder = game.deck.find(founder)
    target = game.find_foundation(founder)
    game.deck.force(founder, target)
    game.foundation_rank = founder.rank
    # Deal the rest of the cards.
    deal_one_row(game)


def deal_start_foundation(game):
    """
    Deal an initial foundation card. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    # Find where the card needs to be dealt.
    card = game.deck.cards[-1]
    foundation = game.find_foundation(card)
    # Deal the card and update the game.
    game.deck.deal(foundation, True)
    game.foundation_rank = card.rank


def deal_stock_all(game):
    """
    Move the rest of the deck into the stock, in the same order. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    # Deal the cards individually to update game_location attribute.
    while game.deck.cards:
        game.deck.deal(game.stock, up = False)
    # Reverse the cards after being dealt.
    game.stock.reverse()


def deal_twos(game):
    """
    Deal the twos onto the tableau. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    # Find the next pile to deal to.
    min_tableau = min([len(pile) for pile in game.tableau])
    next_index = [index for index, pile in enumerate(game.tableau) if len(pile) == min_tableau][0]
    # Deal the aces.
    for card in game.deck.cards[::-1]:
        if card.rank == '2':
            game.deck.force(card, game.tableau[next_index])
            next_index = (next_index + 1) % len(game.tableau)


def deal_yukon(game):
    """
    Deal the cards face up on the tableau, except the first pile. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    while game.deck.cards:
        for pile in game.tableau[1:]:
            game.deck.deal(pile)
            if not game.deck.cards:
                break


def flip_random(game):
    """
    Flip random tableau cards face down. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    for pile in game.tableau:
        random.choice(pile[:-1]).up = False


################## Define free checkers. ##################


def free_pyramid(game, card):
    """
    Allow freeing cards open below and to the right. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card being moved. (TrackingCard)
    """
    error = ''
    if card.game_location in game.tableau:
        pile_index = game.tableau.index(card.game_location)
        if pile_index < 6 and len(card.game_location) <= len(game.tableau[pile_index + 1]):
            error = 'The {} is blocked by the {}.'.format(card, game.tableau[pile_index + 1][-1])
    return error


################## Define lane checkers. ##################


def lane_down(game, card, moving_stack):
    """
    Check moving only stacks of descending ranks into a lane. (str)

    Parameters:
    game: The game being played. (Solitaire)
    card: The card being moved. (TrackingCard)
    moving_stack: The stack the mover is the base of. (list of TrackingCard)
    """
    error = ''
    suit = card.suit
    # Check that each card is below the previous one in rank.
    for this_card, next_card in zip(moving_stack, moving_stack[1:]):
        if not next_card.below(this_card):
            error = 'Only stacks of descending rank may be moved into an empty lane.'
            break
    return error


def lane_king(game, card, moving_stack):
    """
    Check moving only kings into a lane. (str)

    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The cards on top of the card moving. (list of TrackingCard)
    """
    error = ''
    # Check for the moving card being a king.
    if card.rank != 'K':
        error = 'You can only move kings into an empty lane.'
    return error


def lane_none(game, card, moving_stack):
    """
    Cards may not be moved to empty lanes. (str)

    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The cards on top of the card moving. (list of TrackingCard)
    """
    return 'Cards may not be moved to empty lanes.'


def lane_one(game, card, moving_stack):
    """
    Check moving one card at a time into a lane. (str)

    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The cards on top of the card moving. (list of TrackingCard)
    """
    error = ''
    # Check for open space to move the stack.
    max_lane = _move_one_size(game, to_lane = True)
    if len(moving_stack) > max_lane:
        error = 'You can only move {} cards to a lane at the moment.'.format(max_lane)
    return error


def lane_reserve(game, card, moving_stack):
    """
    Lane only from the reserve (str)

    This function assumes one and only one reserve pile.

    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The cards on top of the card moving. (list of TrackingCard)
    """
    error = ''
    # Check for the moving card being in the reserve.
    if (not game.reserve[0]) or card != game.reserve[0][-1]:
        error = 'You can only lane the top card from the reserve.'
    return error


def lane_reserve_waste(game, card, moving_stack):
    """
    Check only laning cards from the reserve. (str)

    If nothing is in the reserve, the waste pile may be used.

    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The cards on top of the card moving. (list of TrackingCard)
    """
    error = ''
    # Check for an emmpty reserve.
    if not any(game.reserve) and card != game.waste[-1]:
        error = 'If the reserve is empty, you can only lane cards from the waste.'
    # Check for the moving card being on top of a reserve pile.
    elif any(game.reserve) and card not in [stack[-1] for stack in game.reserve]:
        error = 'You can only move cards from the reserve into an empty lane.'
    return error


def lane_suit(game, card, moving_stack):
    """
    Check moving only stacks of the same suit to empty lanes. (str)

    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The stack the mover is the base of. (list of TrackingCard)
    """
    error = ''
    # Check that all cards are the same suit.
    suit = card.suit
    for other_card in moving_stack[1:]:
        if other_card.suit != suit:
            error = 'Only stacks of the same suit may be moved to empty lanes.'
            break
    return error


def lane_unblocked(game, card, moving_stack):
    """
    Cards may not be moved from blocked reserve piles. (str)

    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The stack the mover is the base of. (list of TrackingCard)
    """
    error = ''
    # Check that the card isn't in a blocked reserve pile.
    pile = moving_stack[0].game_location
    if pile in game.reserve and game.reserve.index(pile) <= game.blocked_index:
        error = 'You cannot lane cards from blocked reserve piles.'
    return error


################## Define match checkers. ##################


def match_adjacent(game, card, match):
    """
    Allow matching of cards are in adjacent tableau piles. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card to match. (TrackingCard)
    match: The card to match it to. (TrackingCard)
    """
    error = ''
    # Get the distance between the cards.
    start = game.tableau.index([card])
    end = game.tableau.index([match])
    distance = end - start
    # Get the valid distances.
    valid_distances = []
    # Get the valid orthogonal distances.
    if start % 5:
        valid_distances.append(-1)
    if start % 5 != 4:
        valid_distances.append(1)
    if start < game.options['num-tableau'] - 5:
        valid_distances.append(5)
    if start > 4:
        valid_distances.append(-5)
    # Use the orthogonal distances to get the valid diagonal distances.
    for x, y in itertools.combinations(valid_distances, 2):
        if x + y != 0:
            valid_distances.append(x + y)
    # Check that the distance is valid.
    if distance not in valid_distances:
        error = '{} and {} are not adjacent to each other on the tableau.'.format(card, match)
    return error


def match_none(game, card, match):
    """
    Disallow any matches. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card to match. (TrackingCard)
    match: The card to match it to. (TrackingCard)
    """
    return 'Matching cards is not allowed in this game.'


def match_pairs(game, card, match):
    """
    Allow matching cards of the same rank. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card to match. (TrackingCard)
    match: The card to match it to. (TrackingCard)
    """
    error = ''
    # Check for cards of the same rank.
    if card.rank != match.rank:
        error = '{} and {} are not the same rank.'.format(card, match)
    return error


def match_pyramid(game, target, match):
    """
    Allow matching cards open below and to the right. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    target: The card to match. (TrackingCard)
    match: The card to match it to. (TrackingCard)
    """
    error = ''
    # Check that each card is free.
    for card in (target, match):
        if card.game_location in game.tableau:
            pile_index = game.tableau.index(card.game_location)
            if pile_index < 6 and len(card.game_location) <= len(game.tableau[pile_index + 1]):
                error = '{} is blocked by the {}.'.format(card, game.tableau[pile_index + 1][-1])
        if error:
            break
    return error


def match_pyramid_relax(game, target, match):
    """
    Match cards open below and right, even right of each other. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    target: The card to match. (TrackingCard)
    match: The card to match it to. (TrackingCard)
    """
    error = ''
    # Check that each card is free.
    for card in (target, match):
        if card.game_location in game.tableau:
            pile_index = game.tableau.index(card.game_location)
            if pile_index < 6 and len(card.game_location) <= len(game.tableau[pile_index + 1]):
                # Allow the match if the cards block each other.
                if game.tableau[pile_index + 1][-1] not in (target, match):
                    error = '{} is blocked by the {}.'.format(card, game.tableau[pile_index + 1][-1])
        if error:
            break
    return error


def match_tableau(game, card, match):
    """
    Allow matching if the cards are in the tableau. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card to match. (TrackingCard)
    match: The card to match it to. (TrackingCard)
    """
    error = ''
    # Check that both cards are in the reserve.
    for card in [card, match]:
        if card.game_location not in game.tableau:
            error = '{} is not in the tableau'.format(card)
            break
    return error


def match_thirteen(game, card, match):
    """
    Allow matching cards that sum to 13. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card to match. (TrackingCard)
    match: The card to match it to. (TrackingCard)
    """
    error = ''
    # Check for a total of 13.
    total = card.rank_num + match.rank_num
    if total != 13:
        error = 'The ranks of {} and {} do not sum to thirteen.'.format(card, match)
    return error


def match_top(game, target, match):
    """
    Allow matching cards on the top of a pile. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    target: The card to match. (TrackingCard)
    match: The card to match it to. (TrackingCard)
    """
    error = ''
    # Check that the cards are both on top of piles.
    for card in (target, match):
        if card != card.game_location[-1] and card.game_location != game.cells:
            error = '{} is not on the top of a pile.'.format(card)
        if error:
            break
    return error


def match_top_two(game, target, match):
    """
    Allow matching cards on the top of a pile, even if on top of each other. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    target: The card to match. (TrackingCard)
    match: The card to match it to. (TrackingCard)
    """
    error = ''
    # Check for both cards on top of a pile.
    if target.game_location[-2:] in [[target, match], [match, target]]:
        return error
    # Check that the cards are both on top of piles.
    for card in (target, match):
        if card != card.game_location[-1] and card.game_location != game.cells:
            error = '{} is not on the top of a pile.'.format(card)
        if error:
            break
    return error


################## Define pair checkers. ##################


def pair_alt_color(self, mover, target):
    """
    Build in alternating colors. (str)

    Parameters:
    game: The game buing played. (Solitaire)
    mover: The card to move. (TrackingCard)
    target: The destination card. (TrackingCard)
    """
    error = ''
    # Check for different colors.
    if mover.color == target.color:
        error = 'The {} is not the opposite color of the {}'
        error = error.format(mover.name, target.name)
    return error


def pair_down(self, mover, target):
    """
    Build sequentially down in rank. (str)

    Parameters:
    game: The game being played. (Solitaire)
    mover: The card to move. (TrackingCard)
    target: The destination card. (TrackingCard)
    """
    error = ''
    # Check for descending ranks.
    if not mover.below(target):
        error = 'The {} is not one rank lower than the {}'
        error = error.format(mover.name, target.name)
    return error


def pair_not_suit(game, mover, target):
    """
    Build in anything but suits. (str)

    Parameters:
    game: The game buing played. (Solitaire)
    mover: The card to move. (TrackingCard)
    target: The destination card. (TrackingCard)
    """
    error = ''
    # Check for different suits.
    if mover.suit == target.suit:
        error = 'The {} is the same suit as the {}'
        error = error.format(mover.name, target.name)
    return error


def pair_suit(self, mover, target):
    """
    Build in suits. (str)

    Parameters:
    game: The game buing played. (Solitaire)
    mover: The card to move. (TrackingCard)
    target: The destination card. (TrackingCard)
    """
    error = ''
    # Check for the same suit.
    if mover.suit != target.suit:
        error = 'The {} is not the same suit as the {}'
        error = error.format(mover.name, target.name)
    return error


def pair_up_down(self, mover, target):
    """
    Build sequentially up or down in rank. (str)

    Parameters:
    game: The game being played. (Solitaire)
    mover: The card to move. (TrackingCard)
    target: The destination card. (TrackingCard)
    """
    error = ''
    # Check for descending ranks.
    if not mover.below(target) and not mover.above(target):
        error = 'The {} is not one rank higher or lower than the {}'
        error = error.format(mover.name, target.name)
    return error


################## Define sort checkers. ##################


def sort_ace(game, card, foundation):
    """
    Sort starting with the ace. (str)

    Parameters:
    game: The game being played. (Solitiaire)
    card: The card to be sorted. (TrackingCard)
    foundation: The target foundation. (list of TrackingCard)
    """
    error = ''
    # Check for match to foundation pile.
    if not foundation and card.rank_num != 1:
        error = 'Only aces can be sorted to empty foundations.'
    return error


def sort_kings(game, card, foundation):
    """
    Sort starting with the king. (str)

    Parameters:
    game: The game being played. (Solitiaire)
    card: The card to be sorted. (TrackingCard)
    foundation: The target foundation. (list of TrackingCard)
    """
    error = ''
    # Check for match to foundation pile.
    if not foundation and card.rank_num != 13:
        error = 'Only kings can be sorted to empty foundations.'
    return error


def sort_kings_only(game, card, foundation):
    """
    Only allow kings to be sorted. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card to be sorted. (cards.TrackingCard)
    foundation: The foundation to sort to. (list of cards.TrackingCard)
    """
    error = ''
    # Check for a king.
    if card.rank != 'K':
        error = 'Only kings may be sorted.'
    return error


def sort_no_reserve(game, card, foundation):
    """
    Sort non-starters only when the reserve is empty. (str)

    Parameters:
    game: The game being played. (Solitiaire)
    card: The card to be sorted. (TrackingCard)
    foundation: The target foundation. (list of TrackingCard)
    """
    error = ''
    # Check for an empty reserve or foundation.
    if game.reserve[0] and foundation:
        error = 'Only base cards can be sorted before the reserve is emptied.'
    return error


def sort_none(game, card, foundation):
    """
    No sorting is allowed. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card to be sorted. (cards.TrackingCard)
    foundation: The foundation to sort to. (list of cards.TrackingCard)
    """
    return 'Sorting is not allowed in this game.'


def sort_pyramid(game, card, foundation):
    """
    Sorting of blocked cards in a pyramid layout is banned. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card to be sorted. (cards.TrackingCard)
    foundation: The foundation to sort to. (list of cards.TrackingCard)
    """
    error = ''
    # Check that the card is open on both sides.
    if card.game_location in game.tableau:
        pile_index = game.tableau.index(card.game_location)
        if pile_index < 6 and len(card.game_location) <= len(game.tableau[pile_index + 1]):
            error = 'The {} is blocked by the {}.'.format(card, game.tableau[pile_index + 1][-1])
    return error


def sort_rank(game, card, foundation):
    """
    Sort starting with a specific rank. (str)

    Parameters:
    game: The game being played. (Solitiaire)
    card: The card to be sorted. (TrackingCard)
    foundation: The target foundation. (list of TrackingCard)
    """
    error = ''
    # Check for match to foundation pile.
    if not foundation and card.rank != game.foundation_rank:
        rank_name = card.rank_names[card.rank_num].lower()
        error = 'Only {}s can be sorted to empty foundations.'.format(rank_name)
    return error


def sort_unblocked(game, card, foundation):
    """
    Do not sort cards from blocked reserve piles. (str)

    Parameters:
    game: The game being played. (Solitiaire)
    card: The card to be sorted. (TrackingCard)
    foundation: The target foundation. (list of TrackingCard)
    """
    error = ''
    # Check that the card isn't in a blocked reserve pile.
    pile = card.game_location
    if pile in game.reserve and game.reserve.index(pile) <= game.blocked_index:
        error = 'You cannot sort cards from blocked reserve piles.'
    return error


def sort_up(game, card, foundation):
    """
    Sort sequentially up in rank. (str)

    Parameters:
    game: The game being played. (Solitiaire)
    card: The card to be sorted. (TrackingCard)
    foundation: The target foundation. (list of TrackingCard)
    """
    error = ''
    # Check for match to foundation pile.
    if foundation and not card.above(foundation[-1]):
        error = '{} is not one rank higher than {}.'.format(card, foundation[-1])
    return error


def sort_up_down(game, card, foundation):
    """
    Sort a card up or down, depending on the foundation. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card to sort. (card.TrackingCard)
    foundation: The foundation to sort it to. (list of card.TrackingCard)
    """
    error = ''
    # Check for the card being abover or below, based on the foundation.
    if game.foundations.index(foundation) < 4:
        if foundation and not card.below(foundation[-1]):
            error = 'The {} is not one rank below the {}.'.format(card, foundation[-1])
    elif foundation and not card.above(foundation[-1]):
        error = 'The {} is not one rank above the {}.'.format(card, foundation[-1])
    return error
