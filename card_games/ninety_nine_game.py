"""
ninety_nine_game.py

This is the accumulating game, not the trick taking game.

Constants:
CREDITS: The credits for Ninety-Nine. (str)
RULES: The rules of Ninety-Nine.

Classes:
NinetyNine: A game of Ninety-Nine. (game.Game)
Bot99: A bot for Ninety-Nine. (player.Bot)
"""


import random
import re

import tgames.cards as cards
import tgames.game as game
import tgames.player as player
import tgames.utility as utility


CREDITS = """
Game Design: Traditional (Romani)
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
Each turn you play a card, adding it's value to the running total. You must 
correctly state the new total when you play a card. For example, if the total 
to you is 81, and you wanted to play the five of diamonds, you would enter 
'5d 86' If you can't play a card without taking the total over 99, you must 
pass, and lose one of your three tokens. At that point the hands are redealt 
and the total is reset to zero. If you lose all of your tokens, you are out 
of the game. The last player with tokens wins.

Cards are face value with face cards being 10, with the following exceptions:
    A: 1 or 11
    4: 0
    10: -10 or 10
    K: 0

In addition, a 4 reverses the order of play and a 3 skips the next player's 
turn. Nines take the total to 99, no matter what the previous total was.

The tokens command will show you how many tokens each player has left.

Options:
99=: The ranks that take the total to 99. It can be one rank or multiple ranks
    separated by slashes.
chicago: Equivalent to zero=9 skip=9 99=K minus=10.
face=: The ranks that have their face value. This is used to reset default
    non-face values. Face cards will have a value of 10.
jokers=: The number of jokers added to the deck. Their default value is 99.
joker-rules: Equivalent to zero=9 reverse=k face=4 jokers=2.
minus=: The ranks that have their value negated. It can be one rank or 
    multiple ranks separated by slashes.
plus-minus=: The ranks that can be positive or negative. It can be one rank or
    multiple ranks separated by slashes.
reverse=: The rank that reverses the order of play.
skip=: The rank that skips the next player.
zero=: The ranks valued at 0. It can be one rank or multiple ranks separated 
    by slashes.
"""


class NinetyNine(game.Game):
    """
    A game of Ninety-Nine. (game.Game)

    Class Attributes:
    nn_re: A regular expression for Ninety-Nine moves. (re.SRE_Expression)

    Attributes:
    card_values: The possible values for each rank. (dict of str: tuple)
    deck: The deck of cards for the game. (cards.Deck)
    hands: The players hands of cards, keyed by name. (dict of str:cards.Hand)
    reverse_rank: The rank that reverses the order of play. (str)
    skip_rank: The rank that skips over a player. (str)
    total: The current total rank count. (int)

    Methods:
    deal: Deal a new hand of cards. (None)
    do_pass: Pass the turn, lose a token. (bool)
    do_tokens: Show how many tokens are left. (bool)

    Overridden Methods:
    clean_up
    do_quit
    game_over
    handle_options
    player_turn
    set_up
    """

    aka = ['99']
    aliases = {'p': 'pass'}
    credits = CREDITS
    name = 'Ninety-Nine'
    nn_re = re.compile('([1-9atjqkx][cdhs]).*?(-?\d\d?)', re.I)
    num_options = 7
    rules = RULES

    def clean_up(self):
        """Clean up the game. (None)"""
        self.players.extend(self.out_of_the_game)
        self.out_of_the_game = []

    def deal(self):
        """Deal a new hand of cards. (None)"""
        # Shuffle all the cards back into the deck.
        for hand in self.hands.values():
            hand.discard()
        self.deck.shuffle()
        # Deal three cards to each player.
        for card in range(3):
            for hand in self.hands.values():
                hand.draw()

    def do_pass(self, arguments):
        """
        Pass the turn and lose a token. (bool)

        Parameters:
        arguments: The ignored arguments to the command. (None)
        """
        # Remove a token.
        player = self.players[self.player_index]
        self.scores[player.name] -= 1
        message = '{} loses a token. They now have {} tokens.'
        self.human.tell(message.format(player.name, self.scores[player.name]))
        # Check for removing the player from the game..
        if not self.scores[player.name]:
            # Adjust scoring (last player out should score higher).
            for name, value in self.scores.items():
                if value < 1:
                    self.scores[name] = value - 1
            # Remove the player without messing up player tracking.
            next_player = self.players[(self.player_index + 1) % len(self.players)]
            self.players.remove(player)
            self.out_of_the_game.append(player)
            self.player_index = self.players.index(next_player) - 1
            self.human.tell('{} is out of the game.'.format(player.name))
        # Reset the game.
        self.deal()
        self.total = 0

    def do_tokens(self, arguments):
        """
        Show how many tokens are left. (bool)

        Parameters:
        arguments: The ignored arguments to the command. (None)
        """
        self.human.tell()
        for player in self.players:
            self.human.tell('{} has {} tokens left.'.format(player.name, self.scores[player.name]))
        return True

    def do_quit(self, arguments):
        """
        Quit the game, which counts as a loss. (bool)

        Overridden due to changing self.players over course of the game.

        Parameters:
        arguments: The modifiers to the quit. (str)
        """
        self.flags |= 4
        self.force_end = 'loss'
        self.win_loss_draw = [0, max(len(self.scores) - 1, 1), 0]
        if arguments.lower() in ('!', 'quit', 'q'):
            self.human.held_inputs = ['!']
        return False

    def game_over(self):
        """Check for the game being over. (bool)"""
        # Play until only one player is in the game.
        if len(self.players) == 1:
            # Set the win-loss-draw.
            human_score = self.scores[self.human.name]
            for score in self.scores.values():
                if score < human_score:
                    self.win_loss_draw[0] += 1
                elif score > human_score:
                    self.win_loss_draw[1] += 1
            return True
        else:
            return False

    def handle_options(self):
        """Handle the game options(None)"""
        # !! needs options for the number of bots.
        # Set default options.
        self.card_values = {rank: (rank_index,) for rank_index, rank in enumerate(cards.Card.ranks)}
        self.card_values['A'] = (1, 11)
        self.card_values['4'] = (0,)
        self.card_values['9'] = (99,) # go to 99
        self.card_values['T'] = (-10, 10)
        self.card_values['J'] = (10,)
        self.card_values['Q'] = (10,)
        self.card_values['K'] = (0,)
        self.card_values['X'] = (99,)
        self.reverse_rank = '4'
        self.skip_rank = '3'
        self.jokers = 0
        self.players = [self.human]
        for bot in range(2):
            self.players.append(Bot99([player.name for player in self.players]))
        self.players.append(Bot99Medium([player.name for player in self.players]))
        # Handle no options.
        if self.raw_options.lower() == 'none':
            pass
        # Handle passed options.
        elif self.raw_options:
            self.flags |= 1
            self.raw_options = self.raw_options.lower()
            self.raw_options = self.raw_options.replace('joker-rules', 'zero=9 reverse=k face=4/T jokers=2')
            self.raw_options = self.raw_options.replace('chicago', 'zero=9 skip=9 99=K minus=T')
            for word in self.raw_options.lower().split():
                if '=' in word:
                    option, value = word.split('=', 1)
                    if option == '99':
                        for rank in value.split('/'):
                            if rank.upper() in cards.Card.ranks:
                                self.card_values[rank.upper()] = (99,)
                            else:
                                self.human.tell('Invalid value for 99 option: {!r}'.format(rank))
                    elif option == 'face':
                        for rank in value.split('/'):
                            if rank.upper() in cards.Card.ranks:
                                card_value = min(cards.Card.ranks.index(rank.upper()), 10)
                                self.card_values[rank.upper()] = (card_value,)
                            else:
                                self.human.tell('Invalid value for minus option: {!r}'.format(rank))
                    elif option == 'jokers':
                        if value.isdigit():
                            self.jokers = int(value)
                        else:
                            self.human.tell('Invalid value for jokers option: {!r}.'.format(value))
                    elif option == 'minus':
                        for rank in value.split('/'):
                            if rank.upper() in cards.Card.ranks:
                                card_value = min(cards.Card.ranks.index(rank.upper()), 10)
                                self.card_values[rank.upper()] = (-card_value,)
                            else:
                                self.human.tell('Invalid value for minus option: {!r}'.format(rank))
                    elif option == 'plus-minus':
                        for rank in value.split('/'):
                            if rank.upper() in cards.Card.ranks:
                                card_value = min(cards.Card.ranks.index(rank.upper()), 10)
                                self.card_values[rank.upper()] = (-card_value, card_value)
                            else:
                                self.human.tell('Invalid value for plus-minus option: {!r}'.format(rank))
                    elif option == 'reverse':
                        if value.upper() in cards.Card.ranks:
                            self.reverse_rank = value.upper()
                        else:
                            self.human.tell('Invalid value for reverse option: {!r}'.format(value))
                    elif option == 'skip':
                        if value.upper() in cards.Card.ranks:
                            self.skip_rank = value.upper()
                        else:
                            self.human.tell('Invalid value for skip option: {!r}'.format(value))
                    elif option == 'zero':
                        for rank in value.split('/'):
                            if rank.upper() in cards.Card.ranks:
                                self.card_values[rank.upper()] = (0,)
                            else:
                                self.human.tell('Invalid value for zero option: {!r}'.format(rank))
                    else:
                        self.human.tell('Invalid option to Ninety-Nine: {}=.'.format(option))
                else:
                    self.human.tell('Invalid option to Ninety-Nine: {}.'.format(option))
        # Handle asked options.
        else:
            self.flags |= 1
            if self.human.ask('Would you like to change the options? ') in utility.YES:
                query = 'What cards should have a 99 value (slash-separated, return for 9)? '
                while True:
                    nn =self.human.ask(query)
                    if not nn.strip():
                        nn = '9'
                    ranks = nn.upper().split('/')
                    for rank in ranks:
                        if rank not in cards.Card.ranks:
                            self.human.tell('{} is not a valid rank.'.foramt(rank))
                            break
                    else:
                        for rank in ranks:
                            self.card_values[rank] = (99,)
                        break
                query = 'What cards should have their face value (slash-separated, return for all but '
                query += 'A/4/9/10/K)? '
                while True:
                    face =self.human.ask(query)
                    if not face.strip():
                        break
                    ranks = face.upper().split('/')
                    for rank in ranks:
                        if rank not in cards.Card.ranks:
                            self.human.tell('{} is not a valid rank.'.foramt(rank))
                            break
                    else:
                        for rank in ranks:
                            card_value = min(cards.Card.ranks.index(rank), 10)
                            self.card_values[rank] = (card_value,)
                        break
                while True:
                    jokers = self.human.ask('How many jokers would you like in the deck (return for 0)? ')
                    if jokers.isdigit():
                        self.jokers = int(jokers)
                        break
                    else:
                        self.human.tell('Non-negative integers only, please.')
                query = 'What cards should have minus their face value (slash-separated, enter for none)? '
                while True:
                    minus =self.human.ask(query)
                    if not minus.strip():
                        break
                    ranks = minus.upper().split('/')
                    for rank in ranks:
                        if rank not in cards.Card.ranks:
                            self.human.tell('{} is not a valid rank.'.foramt(rank))
                            break
                    else:
                        for rank in ranks:
                            card_value = min(cards.Card.ranks.index(rank), 10)
                            self.card_values[rank] = (-card_value,)
                        break
                query = 'What cards should have +/- their face value (slash-separated, enter for T)? '
                while True:
                    plus_minus =self.human.ask(query)
                    if not plus_minus.strip():
                        plus_minus = 'T'
                    ranks = plus_minus.upper().split('/')
                    for rank in ranks:
                        if rank not in cards.Card.ranks:
                            self.human.tell('{} is not a valid rank.'.foramt(rank))
                            break
                    else:
                        for rank in ranks:
                            card_value = min(cards.Card.ranks.index(rank), 10)
                            self.card_values[rank] = (-card_value, card_value)
                        break
                query - 'What rank should reverse the order of play (return for 4)? '
                while True:
                    reverse = self.human.ask(query).upper()
                    if not reverse.strip():
                        reverse = '4'
                    if reverse in cards.Card.ranks:
                        self.reverse_rank = reverse
                        break
                    else:
                        self.human.tell('{} is not a valid card rank.'.format(reverse))
                query - 'What rank should skip the next player (return for 3)? '
                while True:
                    skip = self.human.ask(query).upper()
                    if not skip.strip():
                        skip = '3'
                    if skip in cards.Card.ranks:
                        self.skip_rank = skip
                        break
                    else:
                        self.human.tell('{} is not a valid card rank.'.format(skip))
                query = 'What cards should have zero value (slash-separated, return for 4/K)? '
                while True:
                    zero =self.human.ask(query)
                    if not zero.strip():
                        zero = '4/K'
                    ranks = zero.upper().split('/')
                    for rank in ranks:
                        if rank not in cards.Card.ranks:
                            self.human.tell('{} is not a valid rank.'.foramt(rank))
                            break
                    else:
                        for rank in ranks:
                            self.card_values[rank] = (0,)
                        break

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Get the relevant hand of cards.
        hand = self.hands[player.name]
        # Display the current game status.
        self.human.tell()
        player.tell('The total to you is {}.'.format(self.total))
        player.tell('Your hand is: {}'.format(hand))
        # Get the players move.
        move = player.ask('What is your move? ')
        parsed = self.nn_re.search(move)
        if parsed:
            # Handle standard moves
            card, new_total = parsed.groups()
            card = card.upper()
            new_total = int(new_total)
            # Check for a valid card.
            if card in hand.cards:
                # Check for a valid total
                values = self.card_values[card[0]]
                valid_add = (new_total < 100) and (new_total - self.total in values)
                if valid_add or (new_total == 99 and 99 in values): 
                    # Play the card.
                    hand.discard(card)
                    self.total = new_total
                    message = '{} played the {}, the total is {}.'
                    self.human.tell(message.format(player.name, card, self.total))
                    # Handle reversing the order of play.
                    if card[0] == self.reverse_rank:
                        self.players.reverse()
                        self.player_index = self.players.index(player)
                        self.human.tell('The order of play is reversed.')
                    # Handle skipping a player's turn.
                    if card[0] == self.skip_rank:
                        self.player_index = (self.player_index + 1) % len(self.players)
                        name = self.players[self.player_index].name
                        self.human.tell("{}'s turn is skipped.".format(name))
                    # Draw a card.
                    hand.draw()
                    return False
                else:
                    # Warn on bad total.
                    player.tell('Incorrect or invalid total provided.')
            else:
                # Warn if the player doesn't have the card.
                player.tell('You do not have that card.')
        else:
            # Handle other commands.
            return self.handle_cmd(move)
        return True

    def set_up(self):
        """Set up the game. (None)"""
        random.shuffle(self.players)
        self.out_of_the_game = []
        # Hand out tokens.
        self.scores = {player.name: 3 for player in self.players}
        # Set up deck and hands.
        self.deck = cards.Deck(jokers = self.jokers)
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        # Deal three cards to each player.
        self.deal()
        # Set the tracking variables
        self.total = 0


class Bot99(player.Bot):
    """
    A bot for Ninety-Nine. (player.Bot)

    Methods:
    get_possibles: Get the possible plays. (list of tuple)

    Overridden Methods:
    ask
    tell
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The information to get from the player. (str)
        """
        # Figure out which cards can be played and how.
        possibles = self.get_possibles()
        if possibles:
            # Play the highest possible total, if you can play.
            possibles.sort()
            return '{1} {0}'.format(*possibles[-1])
        else:
            # Pass if you can't play.
            return 'pass'

    def get_possibles(self):
        """Get the possible plays. (list of tuple)"""
        # Get the game state.
        total = self.game.total
        hand = self.game.hands[self.name]
        # Figure out which cards can be played and how.
        possibles = []
        for card in hand.cards:
            for value in self.game.card_values[card.rank]:
                if total + value < 100:
                    possibles.append((total + value, card))
                elif value == 99:
                    possibles.append((99, card))
        return possibles

    def tell(self, text):
        """
        Give information to the player. (None)

        Parameters:
        text: The inforamtion to give to the player. (str)
        """
        pass


class Bot99Medium(Bot99):
    """
    A better bot for Ninety-Nine. (player.Bot)

    Overridden Methods:
    ask
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The information to get from the player. (str)
        """
        # Get the game state.
        hand = self.game.hands[self.name]
        total = self.game.total
        # Figure out which cards can be played and how.
        possibles = self.get_possibles()
        # Get the cards to keep
        keepers, players = [], []
        for value, card in possibles:
            card_value = self.game.card_values[card.rank]
            if min(card_value) < 1 or max(card_value) == 99:
                keepers.append((value, card))
            else:
                players.append((value, card))
        # Play the highest possible total, if you can play.
        if players:
            players.sort()
            return '{1} {0}'.format(*players[-1])
        elif keepers:
            keepers.sort()
            return '{1} {0}'.format(*keepers[-1])
        else:
            # Pass if you can't play.
            return 'pass'