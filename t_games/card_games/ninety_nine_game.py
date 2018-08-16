"""
ninety_nine_game.py

This is the accumulating game, not the trick taking game.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Ninety-Nine. (str)
RULES: The rules of Ninety-Nine.

Classes:
NinetyNine: A game of Ninety-Nine. (game.Game)
Bot99: A bot for Ninety-Nine. (player.Bot)
Bot99Medium: A better bot for Ninety-Nine. (Bot99)
"""


import random
import re

import t_games.cards as cards
import t_games.game as game
import t_games.options as options
import t_games.player as player
import t_games.utility as utility


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
    separated by slashes. (default is 9)
chicago: Equivalent to zero=4/9 skip=9 99=K minus=10 plus-minus=.
easy= (e=): How many easy bots you will play against. (default = 2)
face=: The ranks that have their face value. This is used to reset default
    non-face values. Face cards will have a value of 10.
jokers= (j=): The number of jokers in the deck. Their default value is 99.
joker-rules: Equivalent to zero=9/k reverse=k jokers=2 99=x skip=.
medium= (m=): How many medium bots you will play against. (default = 2)
minus= (-=): The ranks that have their value negated. It can be one rank or
    multiple ranks separated by slashes.
plus-minus= (+-=): The ranks that can be positive or negative. It can be one
    rank or multiple ranks separated by slashes.
reverse= (r=): The rank that reverses the order of play.
skip= (s=): The rank that skips the next player.
zero= (0=): The ranks valued at 0. It can be one rank or multiple ranks separated
    by slashes.
"""


class NinetyNine(game.Game):
    """
    A game of Ninety-Nine. (game.Game)

    Class Attributes:
    ninety_nine_re: A regular expression for Ninety-Nine moves. (SRE_Expression)

    Attributes:
    card_values: The possible values for each rank. (dict of str: tuple)
    deck: The deck of cards for the game. (cards.Deck)
    easy: The number of easy bots in the game. (int)
    eight_nine: A flag for reversing eights and nines. (bool)
    face: The ranks that score face value rather than a special value. (list)
    free_pass: A flag for passing without a token. (bool)
    hands: The players hands of cards, keyed by name. (dict of str:cards.Hand)
    minus: The ranks that have their value negated. (list of str)
    out_of_the_game: Players who have dropeed out of the game. (list of Player)
    plus_minus: The ranks of cards with face and negative face value. (list)
    rank99: The ranks that set the value to 99. (list of str)
    reverse_rank: The rank that reverses the order of play. (str)
    skip_rank: The rank that skips over a player. (str)
    total: The current total rank count. (int)
    zero: The ranks valued at zero. (list of str)

    Methods:
    deal: Deal a new hand of cards. (None)
    do_pass: Pass the turn, lose a token. (bool)
    do_tokens: Show how many tokens are left. (bool)
    help_ranks: Show the current special ranks in the game. (None)

    Overridden Methods:
    clean_up
    do_quit
    game_over
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['99']
    aliases = {'p': 'pass'}
    categories = ['Card Games']
    credits = CREDITS
    name = 'Ninety-Nine'
    ninety_nine_re = re.compile('([1-9atjqkx][cdhs]).*?(-?\d\d?)', re.I)
    num_options = 7
    rules = RULES

    def clean_up(self):
        """Clean up the game for the next game. (None)"""
        self.players.extend(self.out_of_the_game)
        self.out_of_the_game = []

    def deal(self):
        """Deal a new hand of cards. (None)"""
        # Shuffle all the cards back into the deck.
        for hand in self.hands.values():
            hand.discard()
        self.deck.shuffle()
        # Deal three cards to each player still in the game.
        for card in range(3):
            for player in self.players:
                self.hands[player.name].draw()

    def do_gipf(self, arguments):
        """
        Girls in pillow fights? Come on, this is a family game.
        """
        game, losses = self.gipf_check(arguments, ('blackjack', 'crazy eights', 'yacht'))
        go = True
        # Blackjack allows passing without losing a token.
        if game == 'blackjack':
            if not losses:
                self.human.tell('\nYou can pass without losing a token.')
                self.free_pass = True
        # Crazy Eights reverses eights and nines for one play.
        elif game == 'crazy eights':
            if not losses:
                self.human.tell('\nEights and nines are reversed for this play.')
                self.eight_nine = True
        # Yacht gives you a free token..
        elif game == 'yacht':
            if not losses:
                self.scores[self.human.name] += 1
                message = 'You got a free token. You now have {} tokens.'
                self.human.tell(message.format(self.scores[self.human.name]))
        # Otherwise, I'm confused.
        else:
            self.human.tell('Girls in pillow fights? Come on, this is a family game.')
        return go

    def do_pass(self, arguments):
        """
        Pass the turn and lose a token. (p)
        """
        # Handel free passes.
        if self.free_pass:
            self.free_pass = False
        else:
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
                self.hands[player.name].discard()
                self.player_index = self.players.index(next_player) - 1
                self.human.tell('{} is out of the game.'.format(player.name))
            # Reset the game.
            self.deal()
            self.total = 0

    def do_tokens(self, arguments):
        """
        Show how many tokens each player has left.
        """
        self.human.tell()
        for player in self.players:
            self.human.tell('{} has {} tokens left.'.format(player.name, self.scores[player.name]))
        return True

    def do_quit(self, arguments):
        """
        Quit the game, which counts as a loss. (!)

        If you pass quit (or q or !) as an argument to the quit command, it quits the
        game and the entire t_games interface.
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
                else:
                    self.win_loss_draw[2] += 1
            self.win_loss_draw[2] -= 1
            return True
        else:
            return False

    def handle_options(self):
        """Handle the game options(None)"""
        super(NinetyNine, self).handle_options()
        # Set the special rank values.
        for rank in cards.Card.ranks:
            if rank in self.rank99:
                self.card_values[rank] = (99,)
            elif rank in self.minus:
                self.card_values[rank] = (-cards.Card.ranks.index(rank),)
            elif rank in self.plus_minus:
                self.card_values[rank] += (-cards.Card.ranks.index(rank),)
            elif rank in self.zero:
                self.card_values[rank] = (0,)
        # Set the paleyrs.
        self.players = [self.human]
        for bot in range(self.easy):
            self.players.append(Bot99([player.name for player in self.players]))
        for bot in range(self.medium):
            self.players.append(Bot99Medium([player.name for player in self.players]))

    def help_ranks(self):
        """Show the current special ranks in the game. (None)"""
        self.human.tell('\nThe current values of the ranks are:\n')
        # Get the card class.
        if self.deck.discards:
            card_class = self.deck.discards[0].__class__
        elif self.deck.cards:
            card_class = self.deck.cards[0].__class__
        else:
            card_class = self.hands[self.human.name].cards[0]
        # Show the rank values.
        for rank, rank_name in zip(card_class.ranks[1:], card_class.rank_names[1:]):
            value_text = ' or '.join([str(value) for value in self.card_values[rank]])
            self.human.tell('{}: {}'.format(rank_name, value_text))
        # Show the special ranks.
        if self.skip_rank or self.reverse_rank:
            self.human.tell('\nRanks with special abilities include:\n')
        if self.reverse_rank:
            rank_name = card_class.rank_names[card_class.ranks.index(self.reverse_rank)]
            self.human.tell('The rank to reverse the order of play is {}.'.format(rank_name))
        if self.skip_rank:
            rank_name = card_class.rank_names[card_class.ranks.index(self.skip_rank)]
            self.human.tell('The rank to skip the next player is {}.'.format(rank_name))

    def player_action(self, player):
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
        parsed = self.ninety_nine_re.search(move)
        if parsed:
            # Handle standard moves
            card, new_total = parsed.groups()
            card = card.upper()
            new_total = int(new_total)
            # Check for a valid card.
            if card in hand.cards:
                # Get the rank of the card.
                if self.eight_nine and card[0] in '89':
                    # Handle swapping eights and nines.
                    rank = {'8': '9', '9': '8'}[card[0]]
                else:
                    rank = card[0]
                # Check for a valid total
                values = self.card_values[rank]
                valid_add = (new_total < 100) and (new_total - self.total in values)
                if valid_add or (new_total == 99 and 99 in values):
                    # Play the card.
                    hand.discard(card)
                    self.total = new_total
                    self.eight_nine = False
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
                    player.error('Incorrect or invalid total provided.')
            else:
                # Warn if the player doesn't have the card.
                player.error('You do not have that card.')
        else:
            # Handle other commands.
            return self.handle_cmd(move)
        return True

    def set_options(self):
        """Define the options for the game. (None)"""
        # Set the standard card values.
        self.card_values = {rank: (min(10, index),) for index, rank in enumerate(cards.Card.ranks)}
        self.card_values['A'] = (1, 11)
        self.free_pass = False
        # Get check function for rank lists.
        def is_rank_list(ranks):
            return all(rank in cards.Card.ranks for rank in ranks)
        # Set the groups.
        self.option_set.add_group('joker-rules', 'zero=9/k reverse=k jokers=2 99=x skip=')
        self.option_set.add_group('chicago', 'zero=4/9 skip=9 99=K minus=10 plus-minus=')
        # Set the bot options.
        self.option_set.add_option('easy', ['e'], converter = int, default = 2, valid = range(1, 11),
            question = 'How many easy bots do you want to play against (return for 2)? ')
        self.option_set.add_option('medium', ['m'], converter = int, default = 2, valid = range(1, 11),
            question = 'How many medium bots do you want to play against (return for 2)? ')
        # Set the rank value options.
        self.option_set.add_option('99', target = 'rank99', default = ['9', 'X'],
            check = is_rank_list, converter = options.upper,
            question = 'What ranks should be worth 99 points (slash separated, return for 9 and joker)? ')
        self.option_set.add_option('minus', ['-'], default = [''], check = is_rank_list,
            converter = options.upper,
            question = 'What ranks should be worth minus face value (slash separated, return for none)? ')
        self.option_set.add_option('plus-minus', ['+-'], default = ['T'], check = is_rank_list,
            converter = options.upper,
            question = 'What ranks should be worth +/- face value (slash separated, return for tens)? ')
        self.option_set.add_option('zero', ['0'], default = ['4', 'K'], check = is_rank_list,
            converter = options.upper,
            question = 'What ranks should be worth zero (slash separated, return for 4 and king)? ')
        # Set the special rank options.
        self.option_set.add_option('jokers', ['j'], converter = int, default = 0, valid = range(5),
            question = 'How many jokers should there be in the deck (return for 0)? ')
        self.option_set.add_option('reverse', ['r'], target = 'reverse_rank', valid = cards.Card.ranks,
            default = '4', converter = options.upper,
            question = 'What rank should reverse the order of play? ')
        self.option_set.add_option('skip', ['s'], target = 'skip_rank', valid = cards.Card.ranks,
            default = '3', converter = options.upper, question = 'What rank should skip the next player? ')

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
        self.eight_nine = False


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
    A better bot for Ninety-Nine. (Bot99)

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
        # Play the highest possible total, excluding keepers, if you can play.
        if players:
            players.sort()
            return '{1} {0}'.format(*players[-1])
        # Otherwise, play the highest keept you can.
        elif keepers:
            keepers.sort()
            return '{1} {0}'.format(*keepers[-1])
        # Pass if you can't play.
        else:
            return 'pass'


if __name__ == '__main__':
    # Play the game without the interface.
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    ninety_nine = NinetyNine(player.Humanoid(name), '')
    ninety_nine.play()
