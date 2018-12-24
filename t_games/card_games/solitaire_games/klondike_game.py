"""
klondike_game.py

Klondike solitaire and variants.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: Credits for Klondike. (str)
EASY_FREE: Easy FreeCell deals for testing Klonbot. (list of it)
RULES: Rules for Klondike. (str)

Classes:
Klonbot: A bot to play Klondike stupidly. (player.Bot)
Klondike: A game of Klondike. (solitaire.Solitaire)

Functions:
sim_test: Run a simulation with the Klonbot. (Klonbot, Klondike)
"""


import t_games.player as player
import t_games.card_games.solitaire_games.solitaire_game as solitaire
import t_games.utility as utility


CREDITS = """
Game Design: Traditional (maybe prospectors in the Klondike)
Game Programming: Craig "Ichabod" O'Brien
"""

# From http://freecellgamesolutions.com/stats.html.
EASY_FREE = [164, 892, 1012, 1081, 1150, 1529, 2508, 2514, 3178, 3225, 3250, 4929, 5055, 5152, 5213, 5300,
    5814, 5877, 5907, 6749, 6893, 7018, 7058, 7167, 7807, 8355, 8471, 8961, 9998, 10772, 11863, 11987,
    12392, 12411, 12676, 13214, 13464, 13532, 14014, 14624, 14826, 15140, 15196, 17772, 17871, 18026,
    18150, 18427, 19951, 20533, 21657, 21900, 22663, 23328, 24176, 24919, 25001, 25904, 26719, 27121,
    27853, 28856, 30329, 30418, 30584, 30755, 30849, 31185, 31316, 32016, 33624, 33710, 33949, 34898,
    37509, 37913, 38066, 38168, 38770, 40041, 40441, 40616, 41293, 41426, 41747, 41993, 42094, 43073,
    43196, 43306, 45580, 46561, 47774, 47824, 47917, 48675, 48689, 48800, 48995, 49487, 49676, 49923,
    50203, 50534, 51232, 52255, 52331, 52573, 53488, 54477, 56070, 57035, 57355, 57435, 58441, 58573,
    59641, 59974, 60306, 61047, 61206, 61556, 62090, 62487, 62799, 63249, 63675, 63880]

RULES = """
The cards are dealt in a triangle of seven piles, the first pile having one
card, and each pile to the right having one more card.

Cards on the tableau are built down in rank and alternating in color. Cards
are sorted to the foundations up in suit from the ace. Empty tableau piles may
be filled with a king or a stack starting with a king.

Cards from the stock are turned over three at a time. The stock may be gone
through as many times as you wish.

Options:
piles= (p=): How many tableau piles there should be.
switch-one (s1): You can switch to turning over one card at a time, but only for
    one last pass through the deck. (use the switch command)
turn-one (t1): Cards from the stock are turned over one at a time.
"""


class Klonbot(player.Bot):
    """
    A bot to play Klondike stupidly. (player.Bot)

    In college I knew people who played Klondike by playing every card they could
    as soon as they could. But you can have better outcomes by delaying some
    moves, especially when managing the stock. So I used to say, "I could not only
    write a program to play Solitaire, I could write a program to play Solitaire
    for you." Here it is.

    The bot is designed to run several games by deal number and record the wins.
    To play one random game, set the start parameter to -1.

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
        # Do not set options.
        if 'options' in prompt:
            response = 'nope'
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
        return response

    def ask_int(self, prompt, low = None, high = None, valid = [], default = None, cmd = True):
        """
        Get an integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (int or None)
        high: The highest acceptable value for the integer. (int or None)
        valid: The valid values for the integer. (container of int)
        default: The default choice. (int or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        # Provide the next deal number unless set for random game.
        if 'deal number' in prompt:
            if self.next_num == -1:
                response = ''
            else:
                response = self.next_num
                self.next_num += 1
                self.made_moves = set()
                self.turn_count = 0
        else:
            return super(Klonbot, self).ask_int(prompt, low, high, valid, default, cmd)
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
        possibles = movers + [card for card in targets if card not in movers]
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
        turnable_cards = len(self.game.stock) + len(self.game.waste)
        if self.turn_count < (turnable_cards / 3.0):
            self.turn_count += 1
            return 'turn'
        else:
            return 'quit'

    def tell(self, *args, **kwargs):
        """Echo the game output to the user. (None)"""
        text = str(args[0])
        # Watch for mistakes.
        if 'is not' in text or 'cannot' in text:
            raise RuntimeError('Apparently illegal move by Klonbot.')
        # Record winning games.
        elif 'You won' in text:
            self.wins.append(self.next_num - 1)
            print('Won, deal number =', self.next_num - 1)


class Klondike(solitaire.Solitaire):
    """
    A game of Klondike. (Solitaire)

    Attributes:
    switched: A flag for switching to one card at a time. (bool)

    Methods:
    do_switch: Switch from three cards at a time to one card at a time. (bool)

    Overridden Methods:
    set_checkers
    """

    aka = ['Seven Up', 'Sevens', 'Klon']
    categories = ['Card Games', 'Solitaire Games', 'Closed Games']
    credits = CREDITS
    name = 'Klondike'
    num_options = 3
    rules = RULES

    def do_gipf(self, arguments):
        """
        My hovercraft is full of eels.
        """
        game, losses = self.gipf_check(arguments, ('battleships', 'hangman', 'solitaire dice'))
        go = True
        card = None
        # Battleships lets you see one down card.
        if game == 'battleships':
            if not losses:
                # Remind the human.
                self.human.tell(self)
                # Get a pile with down cards.
                while True:
                    top_card = self.human.ask('\nPick the top card of a tableau pile that has down cards: ')
                    pile = [pile for pile in self.tableau if pile and pile[-1] == top_card]
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
                self.human.tell('\nThe card you chose is the {}.'.format(card.name))
        # Hangman lets you move one jack to the top of the waste.
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
        # Solitaire lets you move any waste card to the top of the waste.
        elif game == 'solitaire dice':
            if not losses:
                # Remind the human.
                self.human.tell(self)
                # Get the card.
                while True:
                    card_text = self.human.ask('\nSelect a card in the waste to move to the top: ')
                    if card_text not in self.waste:
                        self.human.tell('That card is not in the waste.')
                    else:
                        break
                card = self.deck.find(card_text)
        # Otherwise I'm confused.
        else:
            self.human.tell('My hovercraft is full of eels.')
        # Move any selected card to the end of the waste.
        if card is not None:
            card.game_location.remove(card)
            self.waste.append(card)
            card.up = True
            card.game_location = self.waste
            go = False
        return go

    def do_switch(self, arguments):
        """
        Switch from three cards at a time to one card at a time.

        This move is only available if the the switch-one option has been
        chosen. Making the switch leaves you with only one more pass through
        the deck.
        """
        if self.switched:
            # Warn the user if switching is not allowed.
            self.human.error('You may not switch to one card at a time.')
        else:
            # Reset the options
            self.switched = True
            self.turn_count = 1
            # Reset the stock
            self.transfer(self.waste[:], self.stock, up = False)
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
        self.dealers = [solitaire.deal_klondike, solitaire.deal_stock_all]

    def set_options(self):
        """Define the options for the game. (None)"""
        self.options = {}
        # Set the deal option.
        self.option_set.add_option('piles', ['p'], action = 'key=num-tableau', target = self.options,
            default = 7, converter = int, question = 'How many tableau piles should their be? ')
        # Set the play options.
        self.option_set.add_option('switch-one', ['s1'], target = 'switched', value = False, default = True,
            question = 'Should you be able to switch to one card at a time for one last pass? bool')
        self.option_set.add_option('turn-one', ['t1'], action = 'key=turn-count', target = self.options,
            value = 1, default = 3,
            question = 'Would you like to go through the stock one card at a time? bool')


def sim_test(start = 1, end = 100):
    """
    Run a simulation with the Klonbot. (Klonbot, Klondike)

    Parameters:
    start: The first deal to play. (int)
    last: The last deal to play. (int)
    """
    # Set up the bot and the game.
    bot = Klonbot()
    sim = Klondike(bot, '')
    # Play through the games.
    for game_num in EASY_FREE:
        print('Playing game #{}.'.format(game_num))
        bot.next_num = game_num
        results = sim.play()
    # Return the bot and the game.
    return bot, sim


if __name__ == '__main__':
    # Play the game without the full interface.
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    # Check for Klonbot play.
    if name.lower() == 'sim':
        bot, sim = sim_test()
    else:
        # Otherwise let the human play.
        klondike = Klondike(player.Humanoid(name), '')
        klondike.play()
