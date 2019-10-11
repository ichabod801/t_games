"""
calvin_cards_game.py

A game of Calvin Cards.

To Do:
options (secret)???

Constants:
CREDITS: The credits for Calvin Cards. (str)
RULES: The (lack of) rules for Calvin Cards. (str)

Classes:
CalvinCards: A game of Calvin Cards. (solitaire.Solitaire)
"""


import random

from . import solitaire_game as solitaire
from ... import utility


CREDITS = """
Game Design: Calvin
Game Programming: Craig "Ichabod" O'Brien
"""

OPTION_HELP = """
deal_up= (du=): The probability that cards are dealt face up. Defaults to
    0.667.
down_chance= (do=): The probability that a card will be turned face down.
    Defaults to 0.5.
drop_chance= (dr=): The probability that a cell or pile will be dropped.
    Defaults to 0.33.
flip_half= (fh=): The probability that half the dealt cards are flipped face
    down. Defaults to 0.5
max_cells= (xc=): The maximum number of initial free cells. Defaults to 2.
max_pass= (xp=): The maximum number of initial passes through the deck.
    Defaults to 3.
max_reserve= (xr=): The maximum number of initial reserve piles. Defaults to 3.
max_tableau= (xt=): The maximum number of initial tableau piles. Defaults to
    10.
max_turn= (xu=): The maximum number of initial cards turned over by the turn
    command. Defaults to 4.
min_cells= (nc=): The minimum number of initial free cells. Defaults to 0.
min_pass= (np=): The minimum number of initial passes through the deck.
    Defaults to 0, which converts to -1, which is treated as infinite.
min_reserve= (nr=): The minimum number of initial reserve piles. Defaults to 1.
min_tableau= (nt=): The minimum number of initial tableau piles. Defaults to 5.
min_turn= (nu=): The minimum number of initial cards turned over by the turn
    command. Defaults to 1.
move-chance= (mv=): The probability that two cards will be swapped. Defaults to
    0.33.
up-chance= (up=): The probability that a card will be flipped face up. Defaults
    to 0.33.

Down chance is checked first, if there is no rule change. Then up chance is
checked, and finally move chance.
"""

RULES = """
I'd love to tell you the rules, but I can't, because no one knows what they
are. Except for the rule about masks. That is not to be questioned.
"""


class CalvinCards(solitaire.Solitaire):
    """
    A game of Calvin Cards. (solitaire.Solitaire)

    Attributes:
    deal_up: The probability that the cards will be dealt face up. (float)
    down_chance: The chance that a card move will be a flip face down. (float)
    drop_chance: The probability that a cell or pile will be dropped. (float)
    flip_half: The probability that half the cards will be flipped down. (float)
    keep_rules: A count down timer for changing the rules. (int)
    lane_ranks: The ranks that can be moved into an empty lane. (list of str)
    message: The message to give after a rule change. (str)
    max_cells: The maximum number of initial free cells. (int)
    max_pass: The maximum number of initial passes through the deck. (int)
    max_reserve: The maximum number of initial reserve piles. (int)
    max_tableau: The maximum number of initial tableau piles. (int)
    max_turn: The maximum number of initial cards turned over by turn cmd. (int)
    min_cells: The minimum number of initial free cells. (int)
    min_pass: The minimum number of initial passes through the deck. (int)
    min_reserve: The minimum number of initial reserve piles. (int)
    min_tableau: The minimum number of initial tableau piles. (int)
    min_turn: The minimum number of initial cards turned over by turn cmd. (int)
    move_chance: The chance that cards will move on any given turn. (float)
    up_chance: The chance that a card move will be a flip face up. (float)

    Class Attributes:
    build_types: The available pair rule suffixes. (list of str)
    ofs: What items in the game messages can be 'of'. (tuple of string)
    sort_to_lane: The lane-able rank for each foundation base rank. (dict)

    Methods:
    change_rules: Change the rules of the game randomly. (None)
    move_cards: Randomly flip or swap cards. (None)
    randomize_build: Randomize the building and pairing rules. (None)

    Overridden Methods:
    __str__
    do_undo
    handle_options
    player_action
    set_checkers
    set_solitaire
    set_up
    """

    aka = ['CaCa']
    build_types = ['suit', 'color', 'alt_color', 'not_suit', 'ANY']
    categories = ['Card Games', 'Solitaire Games']
    credits = CREDITS
    help_text = {'options': OPTION_HELP}
    name = 'Calvin Cards'
    ofs = ('wisdom', 'bonuses', 'songs', 'spinning', 'secrets', 'opposites', 'time')
    rules = RULES
    sort_to_lane = dict(zip('A23456789TJQK', 'KA23456789TJQ'))

    def __str__(self):
        """Human readable text representation. (str)"""
        text = super(CalvinCards, self).__str__()
        # Add a message to the standard text, if there is one.
        if self.message:
            text = '{}\n\n{}'.format(text, self.message)
            self.message = ''
        return text

    def change_rules(self):
        """Change the rules of the game randomly. (None)"""
        # !! refactor for size
        # Keep choosing rule categories until a valid change is found.
        while True:
            change = random.choice(('build', 'sort', 'turn', 'free', 'reserve', 'tableau'))
            if change == 'build':
                # Change the build rules.
                self.randomize_build()
                item = 'ball'
            elif change == 'sort':
                # Increase the base foundation rank, if there is still an empty foundation.
                if [] in self.foundations:
                    current = self.deck.ranks.index(self.foundation_rank)
                    self.foundation_rank = self.deck.ranks[(current + 1) % len(self.deck.ranks)]
                    if self.foundation_rank == 'X':
                        self.foundation_rank = 'A'
                    self.lane_ranks.append(self.sort_to_lane[self.foundation_rank])
                    item = 'shuttlecock'
                else:
                    continue
            elif change == 'turn':
                # Change the number of cards turned over, if you can still go through the stock.
                if self.stock_passes != self.max_passes:
                    self.turn_count = random.randint(1, 4)
                else:
                    self.max_passes += 1
                item = 'tree'
            elif change == 'free':
                # Increase the number of free cells.
                self.options['num-cells'] += 1
                self.num_cells += 1
                item = 'flag'
            elif change == 'reserve':
                # Redeal the reserve into a random number of piles, if there are enough reserve cards.
                reserve_cards = sum(self.reserve, [])
                new_count = random.randint(1, 3)
                if len(reserve_cards) >= new_count:
                    # Reset the reserve data.
                    self.options['num-reserve'] = new_count
                    self.reserve = [[] for pile in range(new_count)]
                    # Deal the cards.
                    self.deck.cards = reserve_cards
                    for card_index in range(len(reserve_cards)):
                        self.deck.deal(self.reserve[card_index % len(self.reserve)])
                    self.deck.in_play = self.deck.in_play[:52]  # clean up card tracking.
                    item = 'ring'
                else:
                    continue
            elif change == 'tableau':
                # Increase the number of tableau piles.
                if self.tableau.count([]) < 2:
                    self.options['num-cells'] += 1
                    self.num_cells += 1
                    item = 'flag'
                else:
                    continue
            break
        # Set a message indicating the rules have changed.
        action = random.choice(('been bonked by', 'scored with', 'stumbled into', 'taken', 'lost'))
        of = random.choice(self.ofs)
        self.message = 'You have {} the {} of {}.'.format(action, item, of)

    def do_undo(self):
        """
        You may not undo moves in Calvin Cards.
        """
        self.human.error('No move in Calvin Cards may be made twice.')
        return True

    def handle_options(self):
        """Handle the option settings for this game. (None)"""
        # Confirm the player is wearing a mask.
        mask = self.human.ask('\nAre you wearing a mask? ')
        if mask.lower() not in utility.YES:
            self.option_set.errors.append('No mask.')
            return
        # Do the standard option handling, with no deal number request, and no questions.
        self.silent = True
        if not self.raw_options.strip():
            self.raw_options = 'none'
        super(CalvinCards, self).handle_options()

    def move_cards(self):
        """Randomly flip or swap cards. (None)"""
        # Check for actually moving a card.
        if random.random() < self.move_chance:
            tableau_cards = sum(self.tableau, [])
            # Randomly choose a type of move.
            chance = random.random()
            if chance < self.up_chance:
                # Turn a down card up.
                down_cards = [card for card in tableau_cards if not card.up]
                if down_cards:
                    random.choice(down_cards).up = True
            elif chance < self.up_chance + self.down_chance:
                # Turn an up (and unmovable) card down.
                up_cards = [card for card in tableau_cards if card.up and not self.super_stack(card)]
                if up_cards:
                    random.choice(up_cards).up = False
            else:
                # Swap two cards.
                tableau_cards = [card for card in tableau_cards if not self.super_stack(card)]
                if len(tableau_cards) > 1:
                    card_a, card_b = random.sample(tableau_cards, 2)
                    index_a = card_a.game_location.index(card_a)
                    index_b = card_b.game_location.index(card_b)
                    card_a.game_location, card_b.game_location = card_b.game_location, card_a.game_location
                    card_a.game_location[index_b] = card_a
                    card_b.game_location[index_a] = card_b

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Get and process the move.
        go = super(CalvinCards, self).player_action(player)
        # If there was an actual move, check for chaos.
        if not go:
            old_loc = self.moves[-1][1]
            # Check for rules change
            self.keep_rules -= 1
            if not self.keep_rules:
                self.change_rules()
                self.keep_rules = random.randint(4, 8)
            # If no rule change, check for disappearing cell/pile.
            elif (old_loc == self.cells or not old_loc) and random.random() < self.drop_chance:
                item = ''
                if old_loc is self.cells:
                    # Remove the cell.
                    self.num_cells -= 1
                    self.options['num-cells'] -= 1
                    item = 'flag'
                elif any(old_loc is pile for pile in self.tableau) and len(self.tableau) > 4:
                    # Remove the tableau pile.
                    self.options['num-tableau'] -= 1
                    del self.tableau[[old_loc is pile for pile in self.tableau].index(True)]
                    item = 'ball'
                # Set a message if anything was removed.
                if item:
                    of = random.choice(self.ofs)
                    self.message = 'Whoops! You dropped the {} of {}.'.format(item, of)
            # If no other changes, check for moving cards.
            else:
                self.move_cards()
        return go

    def randomize_build(self):
        """Randomize the building and pairing rules. (None)"""
        # Get a random build type, but let it stay on by_suit if it is already there.
        suit_build = solitaire.pair_suit in self.build_checkers
        while True:
            build_type = random.choice(self.build_types)
            if not (suit_build and build_type == 'suit'):
                break
        # Reset the checkers.
        self.build_checkers = [solitaire.build_down]
        self.pair_checkers = [solitaire.pair_down]
        if build_type != 'ANY':
            self.pair_checkers.append(getattr(solitaire, 'pair_{}'.format(build_type)))

    def set_checkers(self):
        """Randomize the initial rule checkers. (None)"""
        super(CalvinCards, self).set_checkers()
        self.randomize_build()
        # Set up the deal rules.
        # The tableau has at least two rows, and can have up to four with max tableau piles.
        tableau_cards = random.randint(20, 40)
        # The stock has about 2/3 of the remaining cards, but each reserve pile must have at least one card.
        stock_cards = min(52 - tableau_cards - self.options['num-reserve'], random.randint(8, 22))
        # The reserve gets the rest of the cards.
        reserve_cards = 52 - tableau_cards - stock_cards
        # Set the deal functions
        up = random.random() < self.deal_up
        dealer = random.choice((solitaire.deal_n, solitaire.deal_triangle_n, solitaire.deal_random_n))
        self.dealers = [dealer(tableau_cards, up)]
        if up and random.random() < self.flip_half:
            self.dealers.append(solitaire.deal_flip_half)
        self.dealers.extend([solitaire.deal_reserve_n(reserve_cards), solitaire.deal_stock_all])
        # Set the sorting and laning functions.
        self.foundation_rank = 'A'
        self.lane_ranks = ['K']
        self.sort_checkers = [solitaire.sort_rank, solitaire.sort_up]
        self.lane_checkers = [solitaire.lane_ranks]

    def set_options(self):
        """Set the options for the game. (None)"""
        # Set the deal options.
        self.option_set.add_option('deal-up', ['du'], float, 0.667)
        self.option_set.add_option('flip-half', ['fh'], float, 0.5)
        # Set the layout options
        self.option_set.add_option('min-cells', ['nc'], int, 0)
        self.option_set.add_option('max-cells', ['xc'], int, 2)
        self.option_set.add_option('min-pass', ['np'], int, 0)
        self.option_set.add_option('max-pass', ['xp'], int, 3)
        self.option_set.add_option('min-reserve', ['nr'], int, 1)
        self.option_set.add_option('max-reserve', ['xr'], int, 3)
        self.option_set.add_option('min-tableau', ['nt'], int, 5)
        self.option_set.add_option('max-tableau', ['xt'], int, 10)
        self.option_set.add_option('min-turn', ['nu'], int, 1)
        self.option_set.add_option('max-turn', ['xu'], int, 4)
        # Set the card movement options.
        self.option_set.add_option('down-chance', ['do'], float, 0.5)
        self.option_set.add_option('drop-chance', ['dr'], float, 0.33)
        self.option_set.add_option('move-chance', ['mv'], float, 0.33)
        self.option_set.add_option('up-chance', ['up'], float, 0.33)

    def set_solitaire(self):
        """Randomize the beginning of the solitaire game. (None)"""
        # Randomize the options
        self.options = {'deck-spec': [], 'num-foundations': 4, 'wrap-ranks': True}
        self.options['num-tableau'] = random.randint(self.min_tableau, self.max_tableau)
        self.options['num-reserve'] = random.randint(self.min_reserve, self.max_reserve)
        self.options['num-cells'] = random.randint(self.min_cells, self.max_cells)
        self.options['turn-count'] = random.randint(self.min_turn, self.max_turn)
        self.options['max-passes'] = random.randint(self.min_pass, self.max_pass)
        if not self.options['max-passes']:
            self.options['max-passes'] = -1
        super(CalvinCards, self).set_solitaire()

    def set_up(self):
        """Set up the game. (None)"""
        # Do the standard solitaire set up.
        super(CalvinCards, self).set_up()
        # Set up game specific tracking valuesl
        self.keep_rules = random.randint(4, 8)
        self.message = ''
