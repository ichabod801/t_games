"""
forty_thieves_game.py

A game of Forty Thieves.

Classes:
FortyThieves: A game of Forty Thieves. (solitaire.Solitaire)
"""


import tgames.card_games.solitaire_games.solitaire_game as solitaire


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
This is a two deck solitaire game. Ten columns of four cards each are dealt 
for the tableau. There are eight foundations to be built up, ace to king in
suit. You may only move one card at a time. Building on the tableau is down
in rank by suit. You may turn over one card from the stock at a time, and 
place it in a waste pile. The top card of the waste pile is available for
building or sorting. You may only go through the stock once.

OPTIONS:
alt-color (streets): The tableau is built down in rank by alternating color.
columns (c): The number of tableau columns (stacks) dealt.
down-rows: The number of tabelau rows that are dealt face down.
dress-parade (rank-and-file) Equivalent to 'alt-color down-rows=3 move-seq'.
emporer (deauville): Equivalent to 'alt-color down-rows=3'.
found-aces: Start the game with the aces on the foundations.
indian: Equivalent to 'down-rows=1 c=10 r=3 not-suit'.
limited: Equivalent to 'c=12 r=3'.
lucas: Equivalent to 'found-aces c=13 r=3'.
maria: Equivalent to 'alt-color c=9 r=4'.
move-seq: Move any built sequence on the tableau.
not-suit: The tableau is built down in rank by anything but suit.
number-ten: Equivalent to 'down-rows=2 c=10 r=4 alt-color move-seq'.
rows (r): The number of tableau rows (cards per stack) dealt.
"""


class FortyThieves(solitaire.MultiSolitaire):
    """
    A game of Forty Thieves. (solitaire.Solitaire)
    """

    aka = ['Big Forty', 'Le Cadran', 'Napoleon at St Helena', 'Roosevelt at San Juan']
    categories = ['Card Games', 'Solitaire Games', 'Forty Thieves']
    name = 'Forty Thieves'
    num_options = 7

    def do_gipf(self, arguments):
        """
        Gipf

        Parameters:
        arguments: The name of the game to gipf to. (str)
        """
        game, losses = self.gipf_check(arguments, ('freecell',))
        # Freecell
        if game == 'freecell':
            if not losses:
                self.human.tell(self)
                tableau_check = [stack[-1] for stack in self.tableau if stack]
                while True:
                    cards_raw = self.human.ask('Enter a waste card and a card to build it on: ')
                    cards = cards_raw.upper().split()
                    if cards[0] not in self.waste:
                        self.human.tell('You must build with a face up waste card.')
                    elif cards[1] not in tableau_check:
                        self.human.tell('You must build to the top of a tableau pile.')
                    else:
                        break
                waste_ndx = self.waste.index(cards[0])
                waste_card = self.waste[waste_ndx]
                tableau_stack = [stack for stack in self.tableau if stack[-1] == cards[1]][0]
                self.transfer([waste_card], tableau_stack)
            pass
        else:
            self.human.tell("I'm sorry, I quit gipfing for Lent.")

    def handle_options(self):
        """Handle the game options. (None)"""
        super(FortyThieves, self).handle_options()
        self.options['num-tableau'] = self.columns

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(FortyThieves, self).set_checkers()
        # Set game specific rules.
        if not self.move_seq:
            self.build_checkers = [solitaire.build_one]
            self.lane_checkers = [solitaire.lane_one]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_suit]
        if self.streets:
            self.pair_checkers[-1] = solitaire.pair_alt_color
        elif self.not_suit:
            self.pair_checkers[-1] = pair_not_suit
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up]
        # Set the dealers.
        self.dealers = []
        if self.found_aces:
            self.dealers.append(deal_aces_multi)
        if self.down_rows:
            self.down_rows = min(self.down_rows, self.rows - 1)
            self.dealers.append(solitaire.deal_n(self.columns * self.down_rows, False))
        self.dealers.append(solitaire.deal_n(self.columns * (self.rows - self.down_rows)))
        self.dealers.append(solitaire.deal_stock_all)

    def set_options(self):
        self.options = {'max-passes': 1, 'num-foundations': 8, 'num-tableau': 10, 'turn-count': 1}
        self.option_set.add_group('emperor', 'streets down-rows=3')
        self.option_set.add_group('deauville', 'streets down-rows=3')
        self.option_set.add_group('dress-parade', 'streets down-rows=3 move-seq')
        self.option_set.add_group('rank-and-file', 'streets down-rows=3 move-seq')
        self.option_set.add_group('lucas', 'found-aces c=13 r=3')
        self.option_set.add_group('maria', 'alt-color c=9 r=4')
        self.option_set.add_group('limited', 'c=12 r=3')
        self.option_set.add_group('indian', 'down-rows=1 c=10 r=3 not-suit')
        self.option_set.add_group('number-ten', 'down-rows=2 c=10 r=4 alt-color move-seq')
        self.option_set.add_option('streets', ['alt-color'],
            question = 'Should tableau building be down by alternating color (return for by suit)? bool')
        self.option_set.add_option('not-suit',
            question = 'Should tableau building be down by anything but suit? bool')
        self.option_set.add_option('columns', ['c'], int, default = 10, 
            question = 'How many tableau columns (stacks) should be dealt (return for 10)? ')
        self.option_set.add_option('rows', ['r'], int, default = 4, 
            question = 'How many tableau rows should be dealt (return for 4)? ')
        self.option_set.add_option('down-rows', ['d'], int, default = 0,
            question = 'How many rows of the tableau should be dealt face down (return for none)? ')
        self.option_set.add_option('found-aces',
            question = 'Should the aces be dealt to start the foundations? bool')
        self.option_set.add_option('move-seq', ['josephine'],
            question = 'Should you be able to move any sequence on the tableau (return for one card at a time)? bool')
    
    def stock_text(self):
        """Generate text for the stock and waste. (str)"""
        # stock
        if self.stock:
            stock_text = '?? '
        else:
            stock_text = '   '
        # waste
        stock_text += ' '.join(str(card) for card in self.waste)
        return stock_text


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


if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    forty = FortyThieves(player.Player(name), '')
    forty.play()