"""
bisley_game.py

A game of Bisley.

Constants:
CREDITS: The credits for Bisley. (str)
RULES: The rules for Bisley. (str)

Classes:
Bisley: A game of Bisley. (solitaire.Solitaire)
"""


import t_games.card_games.solitaire_games.solitaire_game as solitaire


# The credits for Bisley.
CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

# The rules for Bisley.
RULES = """
Four aces are dealt as four of the eight foundations. Thirteen columns of
cards are dealt as the tableau: four columns of three cards under the ace
foundations, and nine columns of four card to the right of the ace 
foundations.

Cards may be built on the tableau one at time by suit, in either ascending or
descending rank. Kings may be sorted to foundations above the ace foundations.
Cards may be sorted down in suit from the kings, or up in suit from the aces.
Empty foundation columns may not be filled with any card.
"""


class Bisley(solitaire.Solitaire):
    """
    A game of Bisley. (solitaire.Solitaire)

    Overridden Methods:
    __str__
    find_foundation
    foundation_text
    set_checkers
    set_options
    tableau_text
    """

    # The menu categories for the game.
    categories = ['Card Games', 'Solitaire Games', 'Open Games']
    # The credits for Bisley.
    credits = CREDITS
    # The name of the game.
    name = 'Bisley'
    # The rules for Bisley.
    rules = RULES

    def __str__(self):
        """Human readable text representation. (str)"""
        # Mix the foundation text in with the tableau text.
        return '\n{}{}\n'.format(self.foundation_text(), self.tableau_text())

    def find_foundation(self, card):
        """
        Determine which foundation a card should sort to. (list of TrackingCard)
        
        Parameters:
        card: The card to sort to a foundation. (cards.TrackingCard)
        """
        # Start with the king foundation.
        sort_index = self.deck.suits.index(card.suit)
        possible = self.foundations[sort_index + 4]
        # Switch to the ace foundation if possible.
        if (possible and card.above(possible[-1])) or card.rank == 'A':
            sort_index += 4
        return self.foundations[sort_index]

    def foundation_text(self):
        """Generate the text representation of the foundations."""
        # Put the foundations in two rows, kings over aces.
        words = []
        for index, foundation in enumerate(self.foundations):
            # Get the text for the foundation card (or not).
            if foundation:
                words.append(str(foundation[-1]))
            else:
                words.append('  ')
            # Get the text between the foundation cards.
            if index == 3:
                words.append('\n')
            else:
                words.append(' ')
        return ''.join(words)

    def set_checkers(self):
        """Set the game specific rules. (None)"""
        super(Bisley, self).set_checkers()
        # Set up the dealers.
        self.dealers = [solitaire.deal_aces_up, solitaire.deal_bisley]
        # Set up the rule checkers.
        self.build_checkers = [solitaire.build_one]
        self.lane_checkers = [solitaire.lane_none]
        self.pair_checkers = [solitaire.pair_suit, solitaire.pair_up_down]
        self.sort_checkers = [solitaire.sort_up_down, solitaire.sort_kings]

    def set_options(self):
        """Set up the possible options for the game. (None)"""
        self.options = {'num-foundations': 8, 'num-tableau': 13}

    def tableau_text(self):
        """Generate the text representation of the foundations."""
        # Get the tallest row, account for the ace foundations.
        row_heights = [len(pile) for pile in self.tableau]
        for pushed in range(4):
            row_heights[pushed] += 1
        row_max = max(row_heights)
        # Loop through the rows.
        rows = []
        for row_index in range(row_max):
            # Add a row and loop through the columns.
            rows.append([])
            for column_index in range(13):
                # Shift the first four columns under the ace foundations
                if row_index == 0 and column_index < 4:
                    continue
                if column_index < 4:
                    card_index = row_index - 1
                else:
                    card_index = row_index
                # Add a card or a blank spot to the row as neccessary.
                if card_index < len(self.tableau[column_index]):
                    rows[-1].append(str(self.tableau[column_index][card_index]))
                else:
                    rows[-1].append('  ')
        # Return the text generated from the rows.
        return '\n'.join([' '.join(row) for row in rows])


if __name__ == '__main__':
    # Play the game without the full interface.
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    bisley = Bisley(player.Player(name), '')
    bisley.play()

