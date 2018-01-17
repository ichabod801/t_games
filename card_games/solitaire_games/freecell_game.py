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


import random

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
    credits = CREDITS
    name = 'FreeCell'
    num_options = 7
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
                        self.human.tell('You must build with a free cell card.')
                    elif cards[1] not in tableau_check:
                        self.human.tell('You must build to the top of a tableau pile.')
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
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up]
        # Set the dealers
        if self.challenge == '2A':
            self.dealers = [deal_twos, deal_aces, solitaire.deal_free]
        elif self.challenge == 'A2':
            self.dealers = [deal_aces, deal_twos, solitaire.deal_free]
        else:
            self.dealers = [solitaire.deal_free]
        if self.fill_free:
            self.dealers.append(fill_free)
        if self.supercell:
            self.dealers.append(flip_random)

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
        self.option_set.add_option(name = 'challenge', value = '2A', default = '',
            question = 'Should the twos and aces be dealt first? bool')
        self.option_set.add_option(name = 'egnellahc', value = 'A2', default = '', target = 'challenge',
            question = 'Should the aces and twos be dealt first? bool')
        self.option_set.add_option(name = 'supercell',
            question = 'Should random cards be flipped face down? bool')


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
    num_options = 7
    rules = RULES_BAKER

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(BakersGame, self).set_checkers()
        # Set the rules for this variation.
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_suit]


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

def deal_twos(game):
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
        if card.rank == '2':
            game.deck.force(card, game.tableau[next_index])
            next_index = (next_index + 1) % len(game.tableau)

def fill_free(game):
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

def flip_random(game):
    """
    Flip random tableau cards face down. (None)

    Parameters:
    game: The game to deal the cards for. (Solitaire)
    """
    for pile in game.tableau:
        random.choice(pile[:-1]).up = False


if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    freec = FreeCell(player.Player(name), '')
    freec.play()