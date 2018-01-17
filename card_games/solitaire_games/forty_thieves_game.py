"""
forty_thieves_game.py

A game of Forty Thieves.

Classes:
FortyThieves: A game of Forty Thieves. (solitaire.Solitaire)
"""


import tgames.card_games.solitaire_games.solitaire_game as solitaire


class FortyThieves(solitaire.MultiSolitaire):
    """
    A game of Forty Thieves. (solitaire.Solitaire)
    """

    aka = ['Big Forty', 'Cadran', 'Napoleon at St Helena', 'Roosevelt at San Juan']
    categories = ['Card Games', 'Solitaire Games', 'Forty Thieves']
    name = 'Forty Thieves'
    num_options = 2

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

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(FortyThieves, self).set_checkers()
        # Set game specific rules.
        self.build_checkers = [solitaire.build_one]
        self.lane_checkers = [solitaire.lane_one]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_suit]
        if self.streets:
            self.pair_checkers[-1] = solitaire.pair_alt_color
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up]
        # Set the dealers.
        self.dealers = [solitaire.deal_n(40), solitaire.deal_stock_all]
        if self.down_rows:
            self.pair_checkers[:1] = [solitaire.deal_n(30, False), solitaire.deal_n(10)]

    def set_options(self):
        self.options = {'max-passes': 1, 'num-foundations': 8, 'num-tableau': 10, 'turn-count': 1}
        for alias in ('emperor', 'deauville', 'dress-parade', 'rank-and-file'):
            self.option_set.add_group(alias, 'streets down-rows')
        self.option_set.add_option('streets', ['alt-color'])
        self.option_set.add_option('down-rows')
    
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


if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    forty = FortyThieves(player.Player(name), '')
    forty.play()