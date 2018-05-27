"""
klondike_game.py

Klondike solitaire and variants.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: Credits for Klondike. (str)
RULES: Rules for Klondike. (str)

Classes:
Klonbot: A bot to play Klondike stupidly. (Bot)
Klondike: A game of Klondike. (Solitaire)

Functions:
deal_klondike: Deal deal a triangle in the tableau. (None)
"""


import t_games.player as player
import t_games.card_games.solitaire_games.solitaire_game as solitaire
import t_games.utility as utility


CREDITS = """
Game Design: Traditional (maybe prospectors in the Klondike)
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
Cards on the tableau are built down in rank and alternating in color. Cards
are sorted to the foundations up in suit from the ace. Empty tableau piles may
be filled with a king or a stack starting with a king.

Cards from the stock are turned over three at a time. The stock may be gone
through as many times as you wish.

Options:
piles=: How many tableau piles there should be.
switch-one: You can switch to turning over one card at a time, but only for
    one last pass through the deck. (use the switch command)
turn-one: Cards from the stock are turned over one at a time.
"""


class Klonbot(player.Bot):
    """
    A bot to play Klondike stupidly. (Bot)

    In college I knew people who played Klondike by playing every card they could
    as soon as they could. But you can have better outcomes by delaying some 
    moves, especially when managing the stock. So I used to say, "I could not only
    write a program to play Solitaire, I could write a program to play Solitaire
    for you." Here it is.

    The bot is designed to run several games by deal number and record the wins. 
    To play one random game, set the start parameter to -1.

    !! Add a final check to see if cards can be moved around to sort out cards.

    Attributes:
    last_num: The last deal number to be played. (int)
    made_moves: The moves made this game, to prevent loops. (set of str)
    next_num: The next deal number to be played. (int)
    turn_count: The number of consecutive turns of the stock. (int)
    wins: The deal numbers for games that were won. (list of int)

    Methods:
    move_check: Check a given card for possible moves. (str, str)
    next_move: Get the next move to make. (str)

    Overridden Methods:
    __init__
    ask
    tell
    """

    def __init__(self, start = 1, end = 10):
        """
        Set up the bot. (None)

        To play one random deal, set start to -1.

        Parameters:
        start: The first deal number to play. (int)
        end: The last deal number to play. (int)
        """
        super(Klonbot, self).__init__()
        # Set up tracking variables
        self.turn_count = 0
        self.made_moves = set()
        self.next_num = start
        self.last_num = end
        self.wins = []

    def ask(self, prompt):
        """
        Answer questions from the game. (str)

        Parameters:
        prompt: The question from the game. (str)
        """
        # Do not set options. !! I could add an options attribute to allow this.
        if 'options' in prompt:
            response = 'nope'
        # Provide the next deal number unless set for random game.
        elif 'deal number' in prompt:
            if self.next_num == -1:
                response = ''
            else:
                response = str(self.next_num)
                self.next_num += 1
                self.made_moves = set()
        # Check that all specified deals have been played.
        elif 'play again' in prompt:
            if self.next_num > self.last_num or self.next_num == -1:
                reponse = 'no way'
            else:
                response = 'y'
        # Get the next move.
        elif 'move' in prompt:
            response = self.next_move()
        # Raise error on unrecognized prompt.
        else:
            raise RuntimeError('Unrecognized prompt to Klonbot: {}'.format(prompt))
        #print('Klonbot:', response)
        return response

    def move_check(self, card, targets, foundations):
        """
        Check a given card for possible moves. (str, str)

        The return value is the move name and the target card, if any. If the move
        returned is empty, no valid move was found.

        Parameters:
        card: The card to check for moves. (Card)
        targets: The cards you can build on. (list of Card)
        foundations: The cards you can sort to. (list of Card)
        """
        # Sort aces.
        if card.rank == 'A':
            return 'sort', ''
        # Check for other sorts.
        for target in foundations:
            if card.above(target) and card.suit == target.suit and card == card.game_location[-1]:
                return 'sort', ''
        # Fill empty lanes with kings.
        if card.rank == 'K' and len(targets) < 7:
            return 'lane', ''
        # Check for building on the tableau.
        for target in targets:
            if card.below(target) and card.color != target.color:
                return 'build', target
        # Return empty strings if no move found.
        return '', ''

    def next_move(self):
        """Get the next move to make. (str)"""
        # Get places to move to.
        foundations = [stack[-1] for stack in self.game.foundations if stack]
        targets = [stack[-1] for stack in self.game.tableau if stack]
        # Get the cards that can move.
        movers = []
        for stack in self.game.tableau:
            if stack:
                for card in stack:
                    if card.up and not (card.rank == 'K' and stack[0] == card):
                        movers.append(card)
                        break
        possibles = movers + targets
        if self.game.waste:
            possibles.append(self.game.waste[-1])
        # Check each card for possible moves.
        for card in possibles:
            move, target = self.move_check(card, targets, foundations)
            full_move = '{} {} {}'.format(move, card, target)
            if move and full_move not in self.made_moves:
                self.made_moves.add(full_move)
                self.turn_count = 0
                return full_move
        # If you can't move turn the stock, but give up if you've done it too much.
        if self.turn_count > 8:
            print('Lost')
            return 'quit'
        else:
            self.turn_count += 1
            return 'turn'

    def tell(self, *args, **kwargs):
        """Echo the game output to the user. (None)"""
        #super(Klonbot, self).tell(*args, **kwargs)
        text = str(args[0])
        # Watch for mistakes.
        if 'is not' in text or 'cannot' in text:
            raise RuntimeError('Apparentl illegal move by Klonbot.')
        # Record winning games.
        elif 'You won' in text:
            self.wins.append(self.next_num - 1)
            print(text)


class Klondike(solitaire.Solitaire):
    """
    A game of Klondike. (Solitaire)

    Overridden Methods:
    set_checkers
    """

    aka = ['Seven Up', 'Sevens']
    categories = ['Card Games', 'Solitaire Games', 'Closed Games', 'Builders']
    credits = CREDITS
    name = 'Klondike'
    num_options = 3
    rules = RULES

    def do_gipf(self, arguments):
        """
        Gipf

        Parameters:
        arguments: The name of the game to gipf to. (str)
        """
        game, losses = self.gipf_check(arguments, ('battleships', 'hangman', 'solitaire dice'))
        go = True
        card = None
        # Battleships
        if game == 'battleships':
            if not losses:
                # Remind the human.
                self.human.tell(self)
                # Get a pile with down cards.
                while True:
                    top_card = self.human.ask('\nPick the top card of a tableau pile that has down cards: ')
                    pile = [pile for pile in self.tableau if pile[-1] == top_card]
                    if not pile:
                        self.human.tell('That is not the top card of a tableau pile.')
                    else:
                        pile = pile[0]
                        down = [card for card in pile if not card.up]
                        if not down:
                            self.human.tell('That pile has no down cards in it.')
                        else:
                            break
                # Get a down card from that pile.
                query = 'Which down card do you want to see (1 = bottom, {} = top)? '.format(len(down))
                card_index = self.human.ask_int(query, low = 1, high = len(down), cmd = False) - 1
                card = down[card_index]
                # Reveal the card.
                self.human.tell('The card you chose is the {}.'.format(card.name))
        # Hangman
        elif game == 'hangman':
            if not losses:
                # Remind the human.
                self.human.tell(self)
                # Get the suit.
                while True:
                    suit = self.human.ask('\nSelect the suit of a jack to move to the top of the waste: ')
                    if suit.upper() not in self.deck.suits:
                        self.human.tell('That suit is not in the deck.')
                    else:
                        break
                card = self.deck.find('J' + suit)
        elif game == 'solitaire dice':
            if not losses:
                # Remind the human.
                self.human.tell(self)
                # Get the card.
                while True:
                    card_text = self.human.ask('\nSelect a card in the waste to move to the top of the waste: ')
                    if card_text not in self.waste:
                        self.human.tell('That card is not in the waste.')
                    else:
                        break
                card = self.deck.find(card_text)
        # No matching game.
        else:
            self.human.tell('My hovercraft is full of eels.')
        if card is not None:
            # Move the card to the end of the waste.
            card.game_location.remove(card)
            self.waste.append(card)
            card.up = True
            card.game_location = self.waste
            go = False
        return go

    def do_switch(self, arguments):
        """
        Switch from three cards at a time to one card at a time. (bool)

        Parameters:
        arguments. The (ignored) arguments to the command. (str)
        """
        if self.switched:
            self.human.error('You may not switch to one card at a time.')
        else:
            # Reset the options
            self.switched = True
            self.turn_count = 1
            # Reset the stock
            self.transfer(self.waste[:], self.stock, face_up = False)
            self.stock.reverse()
            # Reset the stock tracking
            self.stock_passes += 1
            self.max_passes = self.stock_passes + 1
        return False

    def set_checkers(self):
        """Set up the game specific rules. (None)"""
        super(Klondike, self).set_checkers()
        # Set the game specific rules checkers.
        self.lane_checkers = [solitaire.lane_king]
        self.pair_checkers = [solitaire.pair_down, solitaire.pair_alt_color]
        self.sort_checkers = [solitaire.sort_ace, solitaire.sort_up]
        # Set the dealers
        self.dealers = [deal_klondike, solitaire.deal_stock_all]

    def set_options(self):
        """Define the options for the game. (None)"""
        self.options = {}
        self.option_set.add_option('piles', action = 'key=num-tableau', target = self.options,
            default = 7, converter = int, question = 'How many tableau piles should their be?')
        self.option_set.add_option('switch-one', target = 'switched', value = False, default = True,
            question = 'Should you be able to switch to one card at a time for one last pass? bool')
        self.option_set.add_option('turn-one', action = 'key=turn-count', target = self.options,
            value = 1, default = 3,
            question = 'Would you like to go through the stock one card at a time? bool')


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

def sim_test(start = 1, end = 10):
    bot = Klonbot()
    sim = Klondike(bot, 'none')
    for game_num in range(1, end + 1):
        bot.next_num = game_num
        results = sim.play()
        print(results)
    #print([card.rank + card.suit for card in sim.waste + sim.stock[::-1]])
    return bot, sim


if __name__ == '__main__':
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    if name.lower() == 'sim':
        bot, sim = sim_test()
    else:
        klondike = Klondike(player.Player(name), '')
        klondike.play()