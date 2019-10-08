"""
calvin_cards_game.py

A game of Calvin Cards.

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

RULES = """
I'd love to tell you the rules, but I can't, because no one knows what they
are. Except for the rule about masks. That is not to be questioned.
"""


class CalvinCards(solitaire.Solitaire):
    """
    A game of Calvin Cards. (solitaire.Solitaire)
    """

    aka = ['CaCa']
    build_types = ['suit', 'color', 'alt_color', 'not_suit', 'ANY']
    categories = ['Card Games', 'Solitaire Games']
    credits = CREDITS
    name = 'Calvin Cards'
    rules = RULES
    sort_to_lane = dict(zip('A23456789TJQK', 'KA23456789TJQ'))

    def change_rules(self):
        """Change the rules of the game randomly. (None)"""
        while True:
            change = random.choice(('build', 'sort', 'turn', 'free', 'reserve'))
            if change == 'build':
                self.randomize_build()
                item = 'ball'
            elif change == 'sort':
                if [] in self.foundations:
                    current = self.deck.ranks.index(self.foundation_rank)
                    self.foundation_rank = self.deck.ranks[(current + 1) % len(self.deck.ranks)]
                    if self.foundation_rank == 'X':
                        self.foundation_rank = 'A'
                    self.lane_rank = self.sort_to_lane[self.foundation_rank]
                    item = 'shuttlecock'
                else:
                    continue
            elif change == 'turn':
                if self.stock_passes != self.max_passes:
                    self.turn_count = random.randint(1, 4)
                    item = 'tree'
                else:
                    continue
            elif change == 'free':
                self.free_cells.append([])
                self.options['num-cells'] += 1
                item = 'flag'
            elif change == 'reserve':
                reserve_cards = sum(self.reserve, [])
                new_count = random.randint(1, 3)
                if len(reserve_cards) >= new_count:
                    self.options['num-reserve'] = new_count
                    self.reserve = [[] for pile in range(new_count)]
                    self.deck.cards = reserve_cards
                    for card_index in range(len(reserve_cards)):
                        self.deck.deal(self.reserve[card_index % len(self.reserve)])
                    item = 'ring'
                else:
                    continue
            break
        action = random.choice(('been bonked by', 'scored with', 'stumbled into', 'taken', 'lost'))
        of = random.choice(('wisdom', 'bonuses', 'songs', 'spinning', 'secrets', 'opposites', 'time'))
        self.human.tell('You have {} the {} of {}.'.format(item, action, of))

    def do_undo(self):
        """
        You may not undo moves in Calvin Cards.
        """
        self.human.error('No move in Calvin Cards may be made twice.')
        return True

    def handle_options(self):
        """Handle the option settings for this game. (None)"""
        mask = self.human.ask('Are you wearing a mask? ')
        if mask.lower() not in utility.YES:
            self.option_set.errors.append('No mask.')
            return
        self.move_chance = 0.33
        self.up_chance = 0.33
        self.down_chance = 0.5
        super(CalvinCards, self).handle_options()

    def move_cards(self):
        """Randomly flip cards."""
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
                tableau_cards = [card for card in tableau_cards if card.game_location[-1] != card]
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
        # If there was an actual move, check for changing rules.
        if not go:
            self.keep_rules -= 1
            if not self.keep_rules:
                self.change_rules()
                self.keep_rules = random.randint(4, 8)
        self.move_cards()
        return go

    def randomize_build(self):
        """Randomize the building and pairing rules. (None)"""
        self.build_checkers = [solitaire.build_down]
        self.pair_checkers = [solitaire.pair_down]
        build_type = random.choice(self.build_types)
        if build_type != 'ANY':
            #self.build_checkers.append(getattr(solitaire, 'build_{}'.format(build_type)))
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
        print(tableau_cards, stock_cards, reserve_cards)
        # Set the deal functions
        up = random.random() < 0.667
        dealer = random.choice((solitaire.deal_n, solitaire.deal_triangle_n, solitaire.deal_random_n))
        self.dealers = [dealer(tableau_cards, up)]
        if up and random.random() < 0.5:
            self.dealers.append(solitaire.deal_flip_half)
        self.dealers.extend([solitaire.deal_reserve_n(reserve_cards), solitaire.deal_stock_all])
        # Set the sorting and laning functions.
        self.foundation_rank = 'A'
        self.lane_rank = 'K'
        self.sort_checkers = [solitaire.sort_rank, solitaire.sort_up]
        self.lane_checkers = [solitaire.lane_rank]

    def set_solitaire(self):
        """Randomize the beginning of the solitaire game. (None)"""
        # Randomize the options
        self.options = {'deck-spec': [], 'num-foundations': 4, 'wrap-ranks': True}
        self.options['num-tableau'] = random.randint(5, 10)
        self.options['num-reserve'] = random.randint(1, 3)
        self.options['num-cells'] = random.randint(0, 2)
        self.options['turn-count'] = random.randint(1, 4)
        self.options['max-passes'] = random.randint(1, 3)
        super(CalvinCards, self).set_solitaire()

    def set_up(self):
        """Set up the game. (None)"""
        # Do the standard solitaire set up.
        super(CalvinCards, self).set_up()
        # Set up game specific tracking valuesl
        self.keep_rules = random.randint(4, 8)
