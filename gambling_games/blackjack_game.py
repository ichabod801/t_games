"""
blackjack_game.py

Blackjack.

!! Side bets would be nice, but I'm not implementing them now. I need to 
    reckon how to do it first. It needs to have pre/post deal bets with
    varied payouts. Or is it just pre? That would simplify a litte.
    So: dictionary of side bets made, names match methods, check after
    deal. Some you check later, like Bust It! Maybe check at showdown too.

Constants:
CREDITS: Credits for Blackjack. (str)
HINT_KEYS: The meanings of the entries in the hint tables. (dict of str:str)
HINTS: Condensed tables of hints. (str)
RULES: Rules for Blackjack. (str)

Classes:
Blackjack: A game of Blackjack. (game.Game)
BlackjackHand: A hand of Blackjack. (cards.Hand)
"""


import tgames.cards as cards
import tgames.game as game
import tgames.utility as utility


# Credits for Blackjack.
CREDITS = """
Game Design: Traditional (U.S. Casinos)
Game Programming: Craig "Ichabod" O'Brien
The hints were taken from a table on Wikipedia.
"""

# The meanings of the entries in the hint tables.
HINT_KEYS = {'Dh': 'Double (else Hit)', 'Ds': 'Double (else Stand)', 'H': 'Hit', 'S': 'Stand', 
    'Sp': 'Split', 'Su': 'Surrender (else Hit)'}

# Condensed tables of hints.
HINTS = """S45H2Su3S5H3Su1H1S5H5S5H7S3H5Dh18H3Dh4H45
S14Ds1S5Ds5S2H4Dh4H7Dh3H7Dh3H8Dh2H8Dh2H5
Sp10S10Sp5S1Sp2S2Sp16H4Sp5H5Dh8H5Sp2H5Sp6H4Sp6H4"""

# Rules for Blackjack.
RULES = """
The goal is to get a higher total than the dealer, without going over 21. Face
cards count as 10, aces can be 1 or 11, and all other cards are face value. A
two card hand worth 21 is called "blackjack," and beats all other hands. 
Winning with blackjack pays out at 3:2.

After you bet, you get two cards up, and the dealer gets one card up and one 
card down. If either you or the dealer has blackjack, that is dealt with right
away. Otherwise you can continue to get hit (get another card) until you are
ready to stand (stay with the cards you have). If you go over 21 you lose.

You may increase your bet up to double at any point, on the condition that you
get one and only more card. If you have a pair, you may split it into two 
hands, and get another card for each hand (you must bet the same amount for
the second hand). As the first action of your hand, you may surrender to get
half of your bet back.

If you stand, the dealer reveals their hole card, and draws cards until they
get 17 or higher. If they bust (go over 21) or get a lower value than you, you
win.

COMMANDS:
Double (d): Increse your bet up to double and get one more card. If you are 
    not doubling the bet, specify the bet after the command.
Hit (h): Get annother card.
Split (sp): Split a pair to create two hands. 
Stand (s): Stick with the cards you have.
Surrender (su): Give up your hand in exchange for half your bet back.

Any command may take a hand number from 1 to n, for times when you have more
than one hand. If no hand number is given, the first hand is assumed.

OPTIONS:
decks=: The number of decks shuffled together. (defaults to 4)
hands=: The number hands simultaneously played. (defaults to 1, can be 2 or 3)
hit-split-ace: You can hit a split ace.
limit=: The maximum bet. (defaults to 8)
no-double-split: You cannot double split hands.
no-resplit: You cannot split hands that were already split.
s17: The dealer stands on a soft 17.
split-rank: You can only split cards of the same rank.
stake=: The number of bucks the player starts with. (defaults to 100)
surrender: You may surrender (as first action, get back half bet).
true-double: You cannot double less than the original bet.
"""


class Blackjack(game.Game):
    """
    A game of Blackjack. (game.Game)

    Class Attributes:
    ordinals: Ordinal words for displaying multiple hands. (tuple of str)

    Attributes:
    dealer_hand: The dealer's cards. (BlackjackHand)
    phase: The current point in the game turn, betting or getting cards. (str)
    player_hands: The player's cards, in one more hands. (list of BlackjackHand)

    Methods:
    deal: Deal the hands. (None)
    do_hit: Deal a card to the player. (bool)
    do_hint: Get a suggested play for your position. (bool)
    do_split: Split a pair into two hands. (bool)
    do_stand: Set a hand as done. (bool)
    do_surrender: Concede the hand for half the bet back. (bool)
    get_bet: Record the player's bet. (None)
    load_hints: Parse the hint table from the condensed string. (None)
    load_table: Load a condensed table. (list of list of str)
    parse_arguments: Parse integer arguments to command. (list of int)
    reset: Reset the game for the next deal. (None)
    show_status: Show the current game situation to the player. (None)
    showdown: Show and hit the dealer's hand and resolve the round. (None)
    wins: Determine if a hand wins and it's payout. (float)

    Overridden Methods:
    do_quit
    game_over
    player_action
    set_options
    set_up
    """

    # Alternate names for the game.
    aka = ['Twenty-One', '21']
    # Alternate words for commands
    aliases = {'b': 'bet', 'd': 'double', 'h': 'hit', 'q': 'quit', 's': 'stand', 'sp': 'split',
        'su': 'surrender'}
    # Interface categories for the game.
    categories = ['Gambling Games', 'Card Games']
    # Credits for the game.
    credits = CREDITS
    # The name of the game.
    name = 'Blackjack'
    # The number of settable options.
    num_options = 11
    # Ordinal words for displaying multiple hands.
    ordinals = ('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth')
    # The rules of the game.
    rules = RULES

    def deal(self):
        """Deal the hands. (None)"""
        # Deal the dealer's cards.
        self.dealer_hand = BlackjackHand(self.deck)
        self.dealer_hand.draw(False)
        self.dealer_hand.draw()
        # Deal the player's cards.
        self.player_hands = [BlackjackHand(self.deck) for hand in range(self.hand_count)]
        for hand in self.player_hands:
            hand.draw()
            hand.draw()
            hand.status = 'open'
            hand.was_split = False
        # Check for insurance.
        if self.dealer_hand.cards[-1].rank == 'A':
            self.human.tell('The dealer is showing an ace.')
            self.human.tell('Your hand is {}.'.format(self.player_hands[0]))
            for hand_index, hand in enumerate(self.player_hands[1:]):
                self.human.tell('Your {} hand is {}.'.format(self.ordinals[hand_index + 1], hand))
            while True:
                prompt = 'How much insurance would you like? '
                insure = self.human.ask_int(prompt, low = 0, high = min(self.bets) / 2, default = 0)
                if isinstance(insure, int):
                    self.insurance = insure
                    self.scores[self.human.name] -= self.insurance
                    break
                else:
                    self.handle_cmd(insure)
        else:
            self.insurance = 0
        # Check for dealer blackjack.
        if self.dealer_hand.blackjack():
            self.human.tell('The dealer has blackjack.')
            # Check for insurance.
            if self.insurance:
                self.human.tell('You won {} bucks from your insurance.'.format(self.insurance * 2))
                self.scores[self.human.name] += self.insurance * 2
            for hand in self.player_hands:
                hand.status = 'standing'
            self.showdown()
        else:
            # Check for player blackjack.
            for hand_index, hand in enumerate(self.player_hands):
                if hand.blackjack():
                    self.human.tell('The dealer is showing {}.'.format(self.dealer_hand.cards[-1]))
                    self.human.tell('You won with blackjack ({}).'.format(hand))
                    self.scores[self.human.name] += int(self.bets[hand_index] * 2.5)
                    hand.status = 'paid'
            self.phase = 'play'

    def do_double(self, arguments):
        """
        Double your bet for one last card. (bool)

        Parameters:
        arguments: The bet increase and the hand. (str)
        """
        # Check for proper timing.
        if self.phase != 'play':
            self.human.tell('No hands have been dealt yet.')
            return False
        # Parse the arguments.
        if not arguments.strip():
            int_args = [self.bets[0], 0]
        else:
            int_args = self.parse_arguments('double', arguments, max_args = 2)
            if not int_args:
                return False
        bet, hand_index = int_args
        hand = self.player_hands[hand_index]
        # Check for valid bet amount.
        if bet > self.scores[self.human.name]:
            self.human.tell('You only have {} bucks to bet.'.format(self.scores[self.human.name]))
        elif self.true_double and bet != self.bets[hand_index]:
            self.human.tell('You can only double the original bet ({})'.format(self.bets[hand_index]))
        elif bet > self.bets[hand_index]:
            self.human.tell('You can only double up to your original bet ({}).'.format(self.bets[hand_index]))
        # Make sure the hand can receive cards.
        elif hand.status != 'open':
            self.human.tell('That hand is {}, you cannot double it.'.format(hand.status))
        elif not self.double_split and hand.was_split:
            self.human.tell('You cannot double a split hand.')
        else:
            # Increase the bet
            self.bets[hand_index] += bet
            self.scores[self.human.name] -= bet
            # Deal the card.
            hand.draw()
            score = hand.score()
            self.human.tell('You draw the {}.'.format(hand.cards[-1].name))
            # Check for a busted hand.
            if score > 21:
                self.human.tell('You busted with {} ({}).'.format(score, hand))
                hand.status = 'busted'
            else:
                hand.status = 'standing'

    def do_gipf(self, arguments):
        """
        Gipf

        Parameters:
        arguments: The name of the game to gipf to. (str)
        """
        game, losses = self.gipf_check(arguments, ('ninety-nine',)) # bacarat when it's done.
        if game == 'ninety-nine':
            if not losses:
                self.dealer_skip = True
        else:
            self.human.tell('ValueError: gipf')
        return True

    def do_hit(self, arguments):
        """
        Deal a card to the player. (bool)

        Parameters:
        arguments: The number of the hand to hit. (str)
        """
        # Check for proper timing.
        if self.phase != 'play':
            self.human.tell('No hands have been dealt yet.')
            return False
        # Parse the arguments.
        int_args = self.parse_arguments('hit', arguments)
        if not int_args:
            return False
        hand_index = int_args[0]
        # Make sure hand can receive cards.
        hand = self.player_hands[hand_index]
        if hand.status != 'open':
            self.human.tell('That hand is {}, you cannot hit it.'.format(hand.status))
        else:
            # Draw the card.
            hand.draw()
            score = hand.score()
            # Check for busted hand.
            if score > 21:
                self.human.tell('You busted with {} ({}).'.format(score, hand))
                hand.status = 'busted'
            # Check for forced stand.
            elif score == 21:
                hand.status = 'standing'
                self.human.tell('You now have 21 with {}.'.format(hand))

    def do_hint(self, arguments):
        """
        Get a suggested play for your position. (bool)

        Parameters:
        arguments: The number of the hand to hit. (str)
        """
        # Check for proper timing.
        if self.phase != 'play':
            self.human.tell('No hands have been dealt yet.')
            return False
        # Parse the arguments.
        int_args = self.parse_arguments('hint', arguments)
        if not int_args:
            return False
        hand_index = int_args[0]
        hand = self.player_hands[hand_index]
        # Determine which column to use.
        column = BlackjackHand.card_values[self.dealer_hand.cards[-1].rank] - 2
        # Determine the table and row to use.
        values = [BlackjackHand.card_values[card.rank] for card in hand.cards]
        if hand.score() == 21:
            self.human.tell('Stand, you idiot.')
            return False
        elif len(values) == 2 and values[0] == values[1]:
            table = self.hints['pair']
            row = values[0] - 2
        elif hand.soft:
            table = self.hints['ace']
            row = hand.score() - 13
        else:
            table = self.hints['base']
            row = hand.score() - 5
        # Display the hint.
        self.human.tell(HINT_KEYS[table[row][column]])
        if self.flags & 1:
            self.human.tell('Hints may not be valid with the current options.')

    def do_quit(self, arguments):
        """
        Stop playing before losing all your money. (bool)

        Parameters:
        arguments: The number of the hand to hit. (str)
        """
        self.flags |= 4
        if self.scores[self.human.name] > self.stake:
            self.win_loss_draw[0] = 1
            self.force_end = 'win'
        elif self.scores[self.human.name] < self.stake:
            self.win_loss_draw[1] = 1
            self.force_end = 'draw'
        else:
            self.win_loss_draw[2] = 1
            self.force_end = 'loss'
        return False

    def do_split(self, arguments):
        """
        Split a pair into two hands. (bool)

        Parameters:
        arguments: The number of the hand to hit. (str)
        """
        # Check timing.
        if self.phase != 'play':
            self.human.tell('No hands have been dealt yet.')
            return False
        # Parse arguments.
        int_args = self.parse_arguments('split', arguments)
        if not int_args:
            return False
        hand_index = int_args[0]
        hand = self.player_hands[hand_index]
        # Check for valid split.
        if len(hand.cards) != 2:
            self.human.tell('You can only split a hand of two cards.')
        elif self.split_rank and hand.cards[0].rank != hand.cards[1].rank:
            self.human.tell('You may only split cards of the same rank.')
        elif hand.card_values[hand.cards[0].rank] != hand.card_values[hand.cards[1].rank]:
            self.human.tell('You may only split cards of the same value.')
        elif not self.resplit and hand.was_split:
            self.human.tell('You may not split a hand that was already split.')
        else:
            # Split the hands.
            new_hand = hand.split()
            self.player_hands.append(new_hand)
            self.bets.append(self.bets[hand_index])
            self.scores[self.human.name] -= self.bets[-1]
            # Draw new cards.
            hand.draw()
            self.human.tell('The original hand drew the {}.'.format(hand.cards[-1].name))
            new_hand.draw()
            self.human.tell('The new hand drew the {}.'.format(new_hand.cards[-1].name))
            # Stop hitting spit aces, if thems the rules.
            if not self.hit_split_ace and hand.cards[0].rank == 'A':
                hand.status = 'standing'
                new_hand.status = 'standing'

    def do_stand(self, arguments):
        """
        Set a hand as done. (bool)

        Parameters:
        arguments: The number of the hand to hit. (str)
        """
        # Check timing.
        if self.phase != 'play':
            self.human.tell('No hands have been dealt yet.')
            return False
        # Parse arguments.
        int_args = self.parse_arguments('hit', arguments)
        if not int_args:
            return False
        hand_index = int_args[0]
        # Check that the hand is not arleady standing or busted.
        hand = self.player_hands[hand_index]
        if hand.status != 'open':
            self.human.tell('That hand is {}, you cannot stand with it.'.format(hand.status))
        else:
            # Set the hand to standing.
            hand.status = 'standing'

    def do_surrender(self, arguments):
        """
        Concede the hand for half the bet back. (bool)

        Parameters:
        arguments: The number of the hand to hit. (str)
        """
        # Check for proper timing.
        if not self.surrender:
            self.human.tell('Surrender is not allowed in this game.')
            return False
        if self.phase != 'play':
            self.human.tell('No hands have been dealt yet.')
            return False
        # Parse the arguments.
        int_args = self.parse_arguments('surrender', arguments)
        if not int_args:
            return False
        hand_index = int_args[0]
        # Make sure hand has no actions taken on it.
        hand = self.player_hands[hand_index]
        if hand.status != 'open':
            self.human.tell('That hand is {}, you cannot hit it.'.format(hand.status))
        elif hand.was_split:
            self.human.tell('You cannot surrender a split hand.')
        elif len(hand.cards) > 2:
            self.human.tell('You cannot surrender a hand that has been hit.')
        else:
            hand.status = 'surrendered'
            self.scores[self.human.name] += int(self.bets[hand_index] / 2)

    def game_over(self):
        """Determine the end of game. (bool)"""
        loss = self.scores[self.human.name] == 0 and self.phase == 'bet'
        if loss:
            self.win_loss_draw[1] = 1
        return loss

    def get_bet(self):
        """Get the bet from the user. (None)"""
        self.human.tell('\nYou have {} bucks.'.format(self.scores[self.human.name]))
        prompt = 'How much would you like to bet this round (return for max): '
        max_bet = min(self.limit, self.scores[self.human.name])
        if self.hand_count == 1:
            num_bets = [1]
        else:
            num_bets = [1, self.hand_count]
        bets = self.human.ask_int_list(prompt, low = 1, high = max_bet, default = [max_bet],
            valid_lens = num_bets)
        if isinstance(bets, list):
            # Handle single bets.
            if len(bets) == 1:
                bets = bets * self.hand_count
            self.bets = bets
            self.scores[self.human.name] -= sum(bets)
            self.status = 'play'
            return True
        else:
            return self.handle_cmd(bets)

    def load_hints(self):
        """Parse the hint table from the condensed string. (None)"""
        # Split out the condensed tables.
        base_text, ace_text, pair_text = HINTS.split('\n')
        # Parse and save the tables.
        self.hints = {'base': list(reversed(self.load_table(base_text)))}
        self.hints['ace'] = list(reversed(self.load_table(ace_text)))
        self.hints['pair'] = list(reversed(self.load_table(pair_text)))

    def load_table(self, text, columns = 10):
        """
        Load a condensed table. (list of list of str)

        Parameters:
        text: The table condensed to a string. (str)
        """
        # Set up the parsing loop.
        table = [[]]
        key = ''
        count = 0
        # Loop through the characters.
        for char in text + 'x':
            # Pull out the repetitions.
            if char.isdigit():
                count = count * 10 + int(char)
            # Fill in the table when you find a new key.
            elif count:
                for key_index in range(count):
                    table[-1].append(key)
                    if len(table[-1]) == columns:
                        table.append([])
                key = char
                count = 0
            # Pull out the keys
            else:
                key += char
        # Trim empty rows.
        if not table[-1]:
            table.pop()
        # Return the table.
        return table

    def parse_arguments(self, command, arguments, max_args = 1):
        """
        Parse integer arguments to command. (list of int)

        This function assumes that the last argument is an optional hand indicator.

        Parameters:
        command: The command used. (str)
        arguments: The arguments passed to the command. (str)
        max_args: The maximum number of arguments allowed. (int)
        """
        # Check for integer arguments.
        try:
            int_args = [int(arg) for arg in arguments.split()]
        except ValueError:
            message = 'Invalid argument to {} ({}): must be no more than {} integers.'
            self.human.tell(message.format(command, arguments, max_args))
            return []
        # Check for correct number of arguments.
        if max_args - len(int_args) == 1:
            # Add default hand index if necessary.
            int_args.append(1)
        if len(int_args) != max_args:
            self.human.tell('Need more arguments to the {0} command. See help {0}.'.format(command))
            return []
        # Check for a valid hand index.
        if int_args[-1] > len(self.player_hands):
            self.human.tell('Invalid hand index ({}).'.format(int_args[-1]))
            return []
        # Adjust hand index to 0 indexing
        int_args[-1] -= 1
        # Return integer arguments.
        return int_args

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Make sure the bet has been recorded.
        if self.phase == 'bet':
            go = self.get_bet()
            if not go:
                return False
            self.deal()
        # Check for active hands
        statuses = [hand.status for hand in self.player_hands]
        if 'open' in statuses:
            # Show the current game state.
            self.show_status()
            # Get and handle the user input.
            move = self.human.ask("What's your play? ")
            self.human.tell()
            return self.handle_cmd(move)
        # Check for showdown
        elif 'standing' in statuses:
            self.showdown()
            return False
        else:
            self.reset()
            return False

    def reset(self):
        """Reset the game for the next deal. (None)"""
        # Reset tracking variables.
        self.bets = [0] * self.hand_count
        self.insurance = 0
        self.phase = 'bet'
        # Discard all cards.
        self.dealer_hand.discard()
        for hand in self.player_hands:
            hand.discard()
        self.player_hands = [BlackjackHand(self.deck) for hand in range(self.hand_count)]

    def set_options(self):
        """Define the game options. (None)"""
        # Betting options.
        self.option_set.add_option('stake', [], int, 100, check = lambda bucks: bucks > 0,
            question = 'How much money would you like to start with (return for 100)? ')
        self.option_set.add_option('limit', [], int, 8, check = lambda bucks: 0 < bucks,
            question = 'What should the maximum bet be (return for 8)? ')
        # Deal options.
        self.option_set.add_option('decks', [], int, 4, valid = (1, 2, 4, 6, 8),
            question = 'How many decks should be in the shoe (return for 4)? ')
        self.option_set.add_option('hands', [], int, 1, check = lambda hands: 0 < hands < 4,
            question = 'How hands would you like to play (return for 1)? ', target = 'hand_count')
        # Doubling options
        self.option_set.add_option('true-double', 
            question = 'Should a double have to be a true double? bool')
        self.option_set.add_option('no-double-split', value = False, default = True, 
            target = 'double_split', question = 'Should doubling a split hand be banned? bool')
        # Splitting options.
        self.option_set.add_option('split-rank',
            question = 'Should you only be able to split hands of equal rank? bool')
        self.option_set.add_option('no-resplit', value = False, default = True, target = 'resplit',
            question = 'Should you be blocked from splitting a split hand? bool')
        self.option_set.add_option('hit-split-ace',
            question = 'Should you be able to hit split aces? bool')
        # Showdown options.
        self.option_set.add_option('surrender',
            question = 'Should you be able to surrender hands? bool')
        self.option_set.add_option('s17', value = False, default = True, target = 'hit_soft_17',
            question = 'Should the dealer be able to stand on a soft 17? bool')

    def set_up(self):
        """Set up the game. (None)"""
        # Set up tracking variables.
        self.scores = {self.human.name: self.stake}
        self.bets = [0] * self.hand_count
        self.insurance = 0
        self.phase = 'bet'
        self.dealer_skip = False
        # Set up the deck.
        self.deck = cards.Deck(decks = self.decks, shuffle_size = 17 * self.decks)
        self.deck.shuffle()
        # Set up default hands.
        self.dealer_hand = BlackjackHand(self.deck)
        self.player_hands = [BlackjackHand(self.deck)]
        # Load hints.
        self.load_hints()

    def show_status(self):
        """Show the current game situation to the player. (None)"""
        # Show the stake left.
        text = "\nYou have {} bucks.".format(self.scores[self.human.name])
        # Show all of the hands.
        text += "\nThe dealer's hand is {}.".format(self.dealer_hand)
        text += '\nYour hand is {} ({}).'.format(self.player_hands[0], self.player_hands[0].score())
        hand_text = '\nYour {} hand is {} ({}).'
        for hand_index, hand in enumerate(self.player_hands[1:]):
            text += hand_text.format(self.ordinals[hand_index + 1], hand, hand.score())
        # Send the information to the human.
        self.human.tell(text)

    def showdown(self):
        """Show and hit the dealer's hand and resolve the round. (None)"""
        # Reveal the dealer's hole card.
        self.dealer_hand.cards[0].up = True
        self.human.tell('The dealer has {}.'.format(self.dealer_hand))
        if self.dealer_skip:
            self.dealer_skip = False
        else:
            # Draw up to 17.
            while self.dealer_hand.score() < 17:
                self.dealer_hand.draw()
                self.human.tell('The dealer draws the {}.'.format(self.dealer_hand.cards[-1].name))
            # Hit on soft 17.
            if self.hit_soft_17 and self.dealer_hand.score() == 17 and self.dealer_hand.soft:
                self.dealer_hand.draw()
                self.human.tell('The dealer draws the {}.'.format(self.dealer_hand.cards[-1].name))
        # Get and show the dealer's final hand value.
        dealer_value = self.dealer_hand.score()
        self.human.tell("The dealer's hand is {}.".format(dealer_value))
        # Check for dealer bust.
        if dealer_value > 21:
            self.human.tell('The dealer busted.')
        # Pay out winning hands
        for hand_index, hand in enumerate(self.player_hands):
            if hand.status == 'standing':
                payout = self.wins(hand)
                if payout > 1:
                    self.human.tell('You won with {}.'.format(hand))
                elif payout == 1:
                    self.human.tell('You pushed with {}.'.format(hand))
                else:
                    self.human.tell('You lost with {}.'.format(hand))
                self.scores[self.human.name] += int(self.bets[hand_index] * payout)
        self.reset()

    def wins(self, hand):
        """
        Determine if a hand wins and it's payout. (float)

        Parameters:
        hand: The hand to check for a win. (BlackjackHand)
        """
        # Get the hand value
        hand_value = hand.score()
        hand_bj = hand.blackjack()
        # Get the dealer's value
        dealer_value = self.dealer_hand.score()
        dealer_bj = self.dealer_hand.blackjack()
        # Check for a win.
        if hand_value > dealer_value or dealer_value > 21:
            if hand_bj:
                payout = 2.5
            else:
                payout = 2
        # Check for a push
        elif hand_value == dealer_value:
            if hand_bj and dealer_bj:
                payout = 1
            # Blackjack beats 21
            elif hand_bj:
                payout = 2.5
            elif dealer_bj:
                payout = 0
            else:
                payout = 1
        # Otherwise it's a loss
        else:
            payout = 0
        return payout


class BlackjackHand(cards.Hand):
    """
    A hand of Blackjack. (cards.Hand)

    Class Attributes:
    card_values: A mapping of card ranks to score values. (dict of str: int)

    Attributes:
    soft: A flag for the hand being soft (ace = 11). (bool)
    status: Is the hand open, standing, or busted. (str)
    was_split: A flag indicating the hand comes from a split. (bool)

    Overridden Methods:
    score
    """

    # A mapping of card ranks to score values.
    card_values = dict(zip('23456789TAJQK', list(range(2, 12)) + [10] * 3))

    def __init__(self, deck):
        """
        Set up the hand. (None)

        Parameters:
        deck: The deck the hand's cards come from. (Deck)
        """
        super(BlackjackHand, self).__init__(deck)
        self.status = 'empty'
        self.was_split = False
        self.soft = False

    def blackjack(self):
        """Check the hand for a blackjack. (bool)"""
        return self.score() == 21 and len(self.cards) == 2 and not self.was_split

    def score(self):
        """Score the hand. (int)"""
        score = sum([self.card_values[card.rank] for card in self.cards])
        # check for hard hand and adjust ace values.
        ace_count = len([card for card in self.cards if card.rank == 'A'])
        while score > 21 and ace_count:
            score -= 10
            ace_count -= 1
        self.soft = bool(ace_count)
        return score

    def split(self):
        """Split the hand. (int)"""
        new_hand = BlackjackHand(self.deck)
        new_hand.cards.append(self.cards.pop())
        self.was_split = True
        new_hand.was_split = True
        new_hand.status = 'open'
        return new_hand


if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    if name.lower() == 'sim':
        bot, sim = sim_test()
    else:
        blackjack = Blackjack(player.Player(name), '')
        print(blackjack.play())