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

Functions:
_move_one_size: Calculate maximum stack under "move one" rules. (int)
------------------------------------------
build_none: No building is allowed. (bool)
build_one: Build moving one card at a time. (bool)
build_reserve: Build only from the reserve. (bool)
build_whole: Check that only complete tableau stacks are moved. (str)
-------------------------------------------------
deal_aces: Deal the aces onto the tableau. (None)
deal_aces_multi: Deal the aces to the foundations in a multi-deck game. (None)
deal_all: Deal all the cards out onto the tableau. (None)
deal_free: Fill the free cells with the last cards dealt. (None)
deal_klondike: Deal deal a triangle in the tableau. (None)
deal_reserve_n: Create a dealer that deals n cards to the reserve (None)
deal_n: Create a dealer that deals n cards onto the tableau. (function)
deal_one_row: Deal one card face up to each tableau pile. (None)
deal_selective: Deal tableau cards with selection of foundation rank. (None)
deal_start_foundation: Deal an initial foundation card. (None)
deal_twos: Deal the twos onto the tableau. (None)
deal_twos_foundation: Deal the twos to the foundations. (None)
deal_stock_all: Move the rest of the deck into the stock. (None)
flip_random: Flip random tableau cards face down. (None)
------------------------------------------------------
lane_king: Check moving only kings into a lane. (bool)
lane_none: Cards may not be moved to empty lanes. (bool)
lane_reserve: Lane only from the reserve (bool)
lane_reserve_waste: Check only laning cards from the reserve. (str)
lane_one: Check moving one card at a time into a lane. (bool)
-------------------------------------------------------------
match_adjacent: Allow matching of cards are in adjacent tableau piles. (str)
match_none: Disallow any match moves. (bool)
match_pairs: Allow matching cards of the same rank. (str)
match_tableau: Allow matching if the cards are in the tableau. (str)
match_thirteen: Allow matching cards that sum to 13. (str)
--------------------------------------------
pair_alt_color: Build in alternating colors. (str)
pair_down: Build sequentially down in rank. (str)
pair_suit: Build in suits. (str)
pair_not_suit: Build in anything but suits. (str)
--------------------------------------------
sort_ace: Sort starting with the ace. (bool)
sort_kinds: Only kings may be sorted. (str)
sort_no_reserve: Sort non-starters only when the reserve is empty. (bool)
sort_none: No sorting is allowed. (str)
sort_rank: Sort starting with a specific rank. (bool)
sort_up: Sort sequentially up in rank. (bool)
"""


import itertools
import random


# Define helper functions for the dealers and checkers.

def _move_one_size(game, to_lane = False):
    """
    Calculate maximum stack under "move one" rules. (int)

    In other words, how big a stack could you move by moving one card at a time.
    
    Parameters:
    game: The game being played. (Solitaire)
    to_lane: A flag for the moving going to an open lane. (bool)
    """
    free = game.num_cells - len(game.cells)
    if lane_king in game.lane_checkers:
        lanes = 0
    else:
        lanes = game.tableau.count([]) - to_lane
    return (1 + free) * 2 ** lanes

# Define build checkers.

def build_none(game, mover, target, moving_stack):
    """
    No building is allowed. (bool)
    
    Parameters:
    game: The game being played. (Solitaire)
    mover: The card to move. (TrackingCard)
    target: The destination card. (TrackingCard)
    moving_stack: The stack of cards that would move. (list of TrackingCard)
    """
    return 'Building is not allowed in this game.'
    
def build_one(game, mover, target, moving_stack):
    """
    Build moving one card at a time. (bool)
    
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
    Build only from the reserve. (bool)
    
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

def build_whole(game, mover, target, moving_stack):
    """
    Check that only complete tableau stacks are moved. (str)

    Parameters:
    mover: The card being moved. (TrackingCard)
    target: The card being moved to. (TrackingCard)
    moving_stack: The stack the mover is the base of. (list of TrackingCard)
    """
    error = ''
    if mover.game_location in game.tableau and mover != mover.game_location[0]:
        mover_index = mover.game_location.index(mover)
        if mover.game_location[mover_index - 1].up:
            error = 'Only complete stacks may be moved on the tableau.'
    return error

# Define dealers.

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
    for suit in game.deck.suits:
        ace_text = 'A' + suit
        ace = game.deck.find(ace_text)[0]
        for foundation in game.find_foundation(ace):
            game.deck.force(ace_text, foundation)

def deal_all(game):
    """
    Deal all the cards out onto the tableau. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    for card_ndx in range(len(game.deck.cards)):
        game.deck.deal(game.tableau[card_ndx % len(game.tableau)])

def deal_free(game):
    """
    Fill the free cells with the last cards dealt. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    # Find the last card dealt.
    max_tableau = max([len(pile) for pile in game.tableau])
    last_index = [index for index, pile in enumerate(game.tableau) if len(pile) == max_tableau][-1]
    # Move them to the free cells.
    unfilled = game.num_cells - len(game.cells)
    for card in range(unfilled):
        game.cells.append(game.tableau[last_index].pop())
        game.cells[-1].game_location = game.cells
        last_index = (last_index - 1) % len(game.tableau)

def deal_klondike(game):
    """
    Deal deal a triangle in the tableau. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    # Deal out the triangle of cards.
    for card_ndx in range(len(game.tableau)):
        for tableau_ndx in range(card_ndx, len(game.tableau)):
            game.deck.deal(game.tableau[tableau_ndx], card_ndx == tableau_ndx)

def deal_reserve_n(n, up = False):
    """
    Create a dealer that deals n cards to the reserve (function)

    The top card is always dealt face up.

    Parameters:
    n: The number of cards to deal to the reserve. (int)
    up: A flag for dealing the cards face up. (bool)
    """
    def dealer(game):
        for card_index in range(n):
            game.deck.deal(game.reserve[0], up)
        game.reserve[0][-1].up = True
    return dealer

def deal_n(n, up = True):
    """
    Create a dealer that deals n cards onto the tableau. (function)

    The top card is always dealt face up.

    Parameters:
    n: The number of cards to deal to the reserve. (int)
    up: A flag for dealing the cards face up. (bool)
    """
    def dealer(game):
        for card_index in range(n):
            game.deck.deal(game.tableau[card_index % len(game.tableau)], face_up = up)
    return dealer

def deal_one_row(game):
    """
    Deal one card face up to each tableau pile. (None)

    Parameters:
    game: The game to deal cards for. (Solitaire)
    """
    for stack in game.tableau:
        game.deck.deal(stack, True)

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
    card = game.deck.cards[-1]
    foundation = game.find_foundation(card)
    game.deck.deal(foundation, True)
    game.foundation_rank = card.rank

def deal_stock_all(game):
    """
    Move the rest of the deck into the stock, in the same order. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    while game.deck.cards:
        game.deck.deal(game.stock, face_up = False)
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

def deal_twos_foundations(game):
    """
    Deal the twos to the foundations. (None)

    Parameters:
    game: The game to deal cards for. (Solitaire)
    """
    for suit in game.deck.suits:
        deuce = game.deck.find('2' + suit)
        target = game.find_foundation(deuce)
        game.deck.force(deuce, target)

def flip_random(game):
    """
    Flip random tableau cards face down. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    for pile in game.tableau:
        random.choice(pile[:-1]).up = False

# Define lane checkers.

def lane_king(game, card, moving_stack):
    """
    Check moving only kings into a lane. (bool)
    
    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The cards on top of the card moving. (list of TrackingCard)
    """
    error = ''
    # check for the moving card being a king.
    if card.rank != 'K':
        error = 'You can only move kings into an empty lane.'
    return error
        
def lane_none(game, card, moving_stack):
    """
    Cards may not be moved to empty lanes. (bool)
    
    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The cards on top of the card moving. (list of TrackingCard)
    """
    return 'Cards may not be moved to empty lanes.'
        
def lane_one(game, card, moving_stack):
    """
    Check moving one card at a time into a lane. (bool)
    
    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The cards on top of the card moving. (list of TrackingCard)
    """
    error = ''
    # check for open space to move the stack
    max_lane = _move_one_size(game, to_lane = True)
    if len(moving_stack) > max_lane:
        error = 'You can only move {} cards to a lane at the moment.'.format(max_lane)
    return error

def lane_reserve(game, card, moving_stack):
    """
    Lane only from the reserve (bool)
    
    Parameters:
    game: The game being played. (Solitaire)
    card: The card to move into the lane. (TrackingCard)
    moving_stack: The cards on top of the card moving. (list of TrackingCard)
    """
    error = ''
    # check for the moving card being a king.
    if (not game.reserve[0]) or card !=  game.reserve[0][-1]:
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
    # check for the moving card being on top of a reserve pile.
    if not any(game.reserve) and card != game.waste[-1]:
        error = 'If the reserve is empty, you can only lane cards from the waste.'
    elif any(game.reserve) and card not in [stack[-1] for stack in game.reserve]:
        error = 'You can only move cards from the reserve into an empty lane.'
    return error

# Define match checkers.

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
    start, end = [game.tableau.index([card]) for card in cards]
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
        error = '{} and {} are not adjacent to each other on the tableau.'.format(*cards)
    return error

def match_none(game, card, match):
    """
    Disallow any matchest. (bool)

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
    if cards[0].rank != cards[1].rank:
        error = '{} and {} are not the same rank.'.format(*cards)
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
    for card in cards:
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
    total = sum(game.deck.ranks.index(card.rank) for card in cards)
    if total != 13:
        error = 'The ranks of {} and {} do not sum to thirteen.'.format(*cards)
    return error

# Define pair checkers.
    
def pair_alt_color(self, mover, target):
    """
    Build in alternating colors. (str)
    
    Parameters:
    game: The game buing played. (Solitaire)
    mover: The card to move. (TrackingCard)
    target: The destination card. (TrackingCard)
    """
    error = ''
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
    if mover.suit != target.suit:
        error = 'The {} is not the same suit as the {}'
        error = error.format(mover.name, target.name)
    return error

# Define sort checkers.

def sort_ace(game, card, foundation):
    """
    Sort starting with the ace. (bool)
    
    Parameters:
    game: The game being played. (Solitiaire)
    card: The card to be sorted. (TrackingCard)
    foundation: The target foundation. (list of TrackingCard)
    """
    error = ''
    # check for match to foundation pile
    if not foundation and card.rank_num != 1:
        error = 'Only aces can be sorted to empty foundations.'
    return error

def sort_kings(game, card, foundation):
    """
    Only allow kings to be sorted. (str)

    Parameters:
    game: The game being played. (solitaire.Solitaire)
    card: The card to be sorted. (cards.TrackingCard)
    foundation: The foundation to sort to. (list of cards.TrackingCard)
    """
    error = ''
    if card.rank != 'K':
        error = 'Only kings may be sorted.'
    return error

def sort_no_reserve(game, card, foundation):
    """
    Sort non-starters only when the reserve is empty. (bool)
    
    Parameters:
    game: The game being played. (Solitiaire)
    card: The card to be sorted. (TrackingCard)
    foundation: The target foundation. (list of TrackingCard)
    """
    error = ''
    # check for match to foundation pile
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

def sort_rank(game, card, foundation):
    """
    Sort starting with a specific rank. (bool)
    
    Parameters:
    game: The game being played. (Solitiaire)
    card: The card to be sorted. (TrackingCard)
    foundation: The target foundation. (list of TrackingCard)
    """
    error = ''
    # check for match to foundation pile
    if not foundation and card.rank != game.foundation_rank:
        rank_name = card.rank_names[card.rank_num].lower()
        error = 'Only {}s can be sorted to empty foundations.'.format(rank_name)
    return error

def sort_up(game, card, foundation):
    """
    Sort sequentially up in rank. (bool)
    
    Parameters:
    game: The game being played. (Solitiaire)
    card: The card to be sorted. (TrackingCard)
    foundation: The target foundation. (list of TrackingCard)
    """
    error = ''
    # check for match to foundation pile
    if foundation and not card.above(foundation[-1]):
        error = '{} is not one rank higher than {}.'.format(card, foundation[-1])
    return error
