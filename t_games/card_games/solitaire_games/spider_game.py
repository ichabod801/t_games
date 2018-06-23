"""
spider_game.py

A game of Spider.

Classes:
Spider: A game of Spider. (solitaire.MultiSolitaire)
"""


import t_games.card_games.solitaire_games.solitaire_game as solitaire


class Spider(solitaire.MultiSolitaire):
    """
    A game of Spider. (solitaire.MultiSolitaire)

    Overridden Methods:
    do_turn
    set_checkers
    set_options
    """

    # The menu categories for the game.
    categories = ['Card Games', 'Solitaire Games', 'Hybrid Games']
    # The name of the game.
    name = 'Spider'

    def do_build(self, arguments):
        """
        Build card(s) into stacks on the tableau. (bool)
        
        Parameters:
        arguments: The card to move and the card to move it onto. (str)
        """
        # Do the building
        go = super(Spider, self).do_build(arguments)
        # If there was building, check for a sortable stack.
        if not go:
            moving_stack, old_location, new_location, undo_index, turn = self.moves[-1]
            for checker in self.build_checkers:
                if len(moving_stack) != 13:
                    break
                if not checker(self, moving_stack[0], new_location[-len(moving_stack)], moving_stack):
                    break
            else:
                # Sort any valid stacks as a whole.
                foundations = self.find_foundation(moving_stack[0])
                foundation = [foundation for foundation in foundations if not foundnation][0]
                self.transfer(moving_stack, foundation, undo_index = 1)
        return go

    def do_turn(self, arguments):
        """
        Turn over cards from the stock. (bool)

        Parameters:
        arguments: The (ignored) arguments to the turn command. (str)
        """
        if not self.stock:
            self.human.error('There are no more cards to turn over.')
        elif not all(self.tableau):
            self.human.error('You cannot turn over cards from the stock if you have empty tableau piles.')
        else:
            for pile_index, pile in enumerate(self.tableau):
                self.transfer([self.stock[-1]], pile, face_up = True, undo_ndx = pile_index)
                if not self.stock:
                    break

    def set_checkers(self):
        """Set the game specific rule checkers. (None)"""
        super(Spider, self).set_checkers()
        self.dealers = [solitaire.deal_n(54), solitaire.deal_stock_all]
        self.build_checkers = [solitaire.build_suit, solitaire.build_down]
        self.lane_checkers = [solitaire.lane_suit, solitaire.lane_down]
        self.pair_checkers = [solitaire.pair_down]
        self.sort_checkers = [solitaire.sort_none]

    def set_options(self):
        """Set up the game specific options. (None)"""
        self.options = {'num-foundations': 8, 'num-tableau': 10}