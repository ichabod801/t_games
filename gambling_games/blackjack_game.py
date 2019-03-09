"""
blackjack_game.py

Blackjack.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Blackjack. (str)
HINT_KEYS: The meanings of the entries in the hint tables. (dict of str:str)
HINTS: A condensed tables of hints. (str)
RULES: The rules for Blackjack. (str)

Classes:
Blackjack: A game of Blackjack. (game.Game)
BlackjackHand: A hand of Blackjack. (cards.Hand)
"""


from .. import cards
from .. import game
from .. import utility


CREDITS = """
Game Design: Traditional (U.S. Casinos)
Game Programming: Craig "Ichabod" O'Brien
The hints were taken from a table on Wikipedia.
"""

HINT_KEYS = {'Dh': 'Double (else Hit)', 'Ds': 'Double (else Stand)', 'H': 'Hit', 'S': 'Stand',
    'Sp': 'Split', 'Su': 'Surrender (else Hit)'}

HINTS = """S45H2Su3S5H3Su1H1S5H5S5H7S3H5Dh18H3Dh4H45
S14Ds1S5Ds5S2H4Dh4H7Dh3H7Dh3H8Dh2H8Dh2H5
Sp10S10Sp5S1Sp2S2Sp16H4Sp5H5Dh8H5Sp2H5Sp6H4Sp6H4"""

RULES = """
The goal is to get a higher total than the dealer, without going over 21. Face
cards count as 10, aces can be 1 or 11, and all other cards are face value. A
two card hand worth 21 is called "blackjack," and beats all other hands.
Winning with blackjack pays out at 3:2.

After you bet, you get two cards up, and the dealer gets one card up and one
card down. If either you or the dealer has blackjack, that is dealt with right
away. Otherwise you can continue to get hit (get another card) until you are
ready to stand (stay with the cards you have). If you go over 21 you lose.

If you are betting on multiple hands (send the hands= option), you can enter
one bet and it will be applied to all of the hands. If you are playing
multiple hands, you can specify which hand you want to act on with a number.
For example, 'hit 2' will hit your second hand. If you do not specify a hand
number, the command will apply to the lowest numbered open hand.

You may increase your bet up to double at any point, on the condition that you
get one and only more card. If you have a pair, you may split it into two
hands, and get another card for each hand (you must bet the same amount for
the second hand). As the first action of your hand, you may surrender to get
half of your bet back.

If you stand, the dealer reveals their hole card, and draws cards until they
get 17 or higher. If they bust (go over 21) or get a lower value than you, you
win.

Your score in the results and statistics will be how much money you won
(positive) or lost (negative). This means you can calcuate your total winnings
or losses by multiplying you average score times the number of games you have
played.

COMMANDS:
Double (d): Increse your bet up to double and get one more card. If you are
    not doubling the bet, specify the bet after the command.
Hands: Change the number of hands you are playing.
Hint: Get a hint about how to play a hand.
Hit (h): Get annother card.
Split (sp): Split a pair to create two hands.
Stand (s): Stick with the cards you have.
Surrender (su): Give up your hand in exchange for half your bet back.

Any command may take a hand number from 1 to n, for times when you have more
than one hand. If no hand number is given, the first open hand is assumed.

OPTIONS:
decks= (d=): The number of decks in the shoe. (1, 2, 4 (default), 6 or 8)
hands= (h=): The number hands simultaneously played. (1 (default), 2, or 3)
hit-split-ace (hsa): You can hit a split ace.
limit= (l=): The maximum bet. (defaults to 8)
no-double-split (nds): You cannot double split hands.
no-resplit (nr): You cannot split hands that were already split.
s17: The dealer stands on a soft 17.
split-rank (sr): You can only split cards of the same rank.
stake= (s=): The number of bucks the player starts with. (defaults to 100)
surrender (su): You may surrender (as first action, get back half bet).
true-double (td): You cannot double less than the original bet.
"""


class Blackjack(game.Game):
    """
    A game of Blackjack. (game.Game)

    Attributes:
    bets: The bets for each hand. (list of int)
    dealer_hand: The dealer's cards. (BlackjackHand)
    dealer_skip: A flag for not allowing the dealer to draw. (bool)
    deck: The deck of cards used in the game. (cards.Deck)
    decks: How many decks are in the shoe/self.deck. (int)
    double_split: A flag for being able to double after a split. (bool)
    hands: The hands currently being played. (list of Hand)
    hand_count: The number of starting hands the player is dealt. (int)
    hints: The best play for various hand totals. (dict of str: list of list)
    hit_soft_17: A flag for the dealer having to hit a soft 17. (bool)
    hit_split_ace: A flag for being able to hit a split ace. (bool)
    insurance: The amount of insurace on the current deal. (int)
    limit: The maximum allowed bet. (int)
    phase: The current point in the game turn, betting or getting cards. (str)
    player_hands: The player's cards, in one more hands. (list of BlackjackHand)
    resplit: A flag for being able to resplit a split hand. (bool)
    split_rank: A flag for only being able to split the same rank. (bool)
    stake: The number of bucks the player starts with. (bool)
    surrender: A flag for surrender being allowed. (su)
    true_double: A flag for doubles having to be at least the original bet. (bool)

    Methods:
    deal: Deal the hands. (None)
    do_double: Double your bet for one last card. (bool)
    do_hands: Change the number of hands being played. (bool)
    do_hint: Get a suggested play for your position. (bool)
    do_hit: Deal a card to the player. (bool)
    do_split: Split a pair into two hands. (bool)
    do_stand: Set a hand as done. (bool)
    do_surrender: Concede the hand for half the bet back. (bool)
    get_bet: Record the player's bet. (None)
    load_hints: Parse the hint table from the condensed string. (None)
    load_table: Load a condensed table. (list of list of str)
    parse_arguments: Parse integer arguments to command. (list of int)
    phase_check: Check that the phase is appropriate for hand actions. (bool)
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

    aka = ['Twenty-One', '21']
    aliases = {'b': 'bet', 'd': 'double', 'h': 'hit', 'q': 'quit', 's': 'stand', 'sp': 'split',
        'su': 'surrender'}
    categories = ['Gambling Games']
    credits = CREDITS
    name = 'Blackjack'
    num_options = 11
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
            # Update the user on the situation.
            self.human.tell('The dealer is showing an ace.')
            self.human.tell('Your hand is {}.'.format(self.player_hands[0]))
            for hand_index, hand in enumerate(self.player_hands[1:]):
                hand_ordinal = utility.number_word(hand_index + 2, ordinal = True)
                self.human.tell('Your {} hand is {}.'.format(hand_ordinal, hand))
            # Ask until you get a valid insurance amount, blocking other blackjack moves until done.
            self.phase = 'insurance'
            while True:
                prompt = 'How much insurance would you like? '
                insure = self.human.ask_int(prompt, low = 0, high = min(self.bets) / 2, default = 0)
                if isinstance(insure, int):
                    self.insurance = insure
                    self.scores[self.human.name] -= self.insurance
                    break
                else:
                    self.handle_cmd(insure)
            self.phase = 'play'
        else:
            self.insurance = 0
        # Check for dealer blackjack.
        if self.dealer_hand.blackjack():
            self.human.tell('\nThe dealer has blackjack.')
            # Check for insurance.
            if self.insurance:
                self.human.tell('You won {} bucks from your insurance.'.format(self.insurance * 2))
                self.scores[self.human.name] += self.insurance * 2
            # Resolve the hand.
            for hand in self.player_hands:
                hand.status = 'standing'
            self.showdown()
        else:
            # Check for player blackjack.
            for hand_index, hand in enumerate(self.player_hands):
                if hand.blackjack():
                    self.human.tell('The dealer is showing {}.'.format(self.dealer_hand.cards[-1]))
                    self.human.tell('\nYou won with blackjack ({}).'.format(hand))
                    self.scores[self.human.name] += int(self.bets[hand_index] * 2.5)
                    hand.status = 'paid'
                    self.bets[hand_index] = 0
            self.phase = 'play'

    def do_double(self, arguments):
        """
        Double your bet for one last card. (d)

        If you have multiple hands, you should indicate which hand you are doubling
        with an integer argument to the double command (1 for the first hand listed,
        two for the second hand, and so on.)

        If the true-double option has not been selected, you can also enter a bet up
        to the ammount bet on the original hand. If you don't enter a bet, the bet is
        set to the amount bet on the original hand.
        """
        # Check for proper timing.
        if not self.phase_check('double'):
            return True
        # Parse the arguments.
        if not arguments.strip():
            # Find the default hand.
            for hand_index, hand in enumerate(self.player_hands):
                if hand.status == 'open':
                    break
            int_args = [hand_index, self.bets[hand_index]]
        else:
            int_args = self.parse_arguments('double', arguments, max_args = 2)
            if not int_args:
                return True
        hand_index, bet = int_args
        hand = self.player_hands[hand_index]
        # Check for valid bet amount.
        if bet > self.scores[self.human.name]:
            self.human.error('You only have {} bucks to bet.'.format(self.scores[self.human.name]))
        elif self.true_double and bet != self.bets[hand_index]:
            self.human.tell('You can only double the original bet ({})'.format(self.bets[hand_index]))
        elif bet > self.bets[hand_index]:
            error_text = 'You can only double up to your original bet ({}).'
            self.human.error(error_text.format(self.bets[hand_index]))
        # Make sure the hand can receive cards.
        elif hand.status != 'open':
            self.human.error('That hand is {}, you cannot double it.'.format(hand.status))
        elif not self.double_split and hand.was_split:
            self.human.error('You cannot double a split hand.')
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
                self.bets[hand_index] = 0
            else:
                hand.status = 'standing'
        return True

    def do_gipf(self, arguments):
        """
        Ninety-Nine stops the dealer from drawing this round.
        """
        game, losses = self.gipf_check(arguments, ('ninety-nine',))
        # A Ninety-Nine win stops the dealer from drawing this round.
        if game == 'ninety-nine':
            if not losses:
                self.dealer_skip = True
        # Otherwise, I'm confused.
        else:
            self.human.tell('ValueError: gipf')
        return True

    def do_hands(self, arguments):
        """
        Change the number of hands being played.

        The argument should be the number of hands to play, from 1 to 4.
        """
        # Check for integer input.
        try:
            new_count = int(arguments)
        except ValueError:
            self.human.error('\nInvalid arguments to hands command: {!r}.'.format(arguments))
            return True
        # Check for valid input.
        if 1 <= new_count <= 4:
            # Confirm the change to the user.
            if self.phase == 'bet':
                message = '\nYou are now playing {}.'
            else:
                message = '\nNext round you will play {}.'
            self.human.tell(message.format(utility.number_plural(new_count, 'hand')))
            # Make the change.
            self.hand_count = new_count
        else:
            # Warn on invalid input.
            self.human.error('\nYou can only play one to four hands.')
        return True

    def do_hint(self, arguments):
        """
        Get a suggested play for your position.

        If you have multiple hands, you should indicate which hand you are asking for
        with an integer argument to the hint command (1 for the first hand listed,
        two for the second hand, and so on.)
        """
        # Check for proper timing.
        if not self.phase_check('get a hint'):
            return True
        # Parse the arguments.
        int_args = self.parse_arguments('hint', arguments)
        if not int_args:
            return True
        hand_index = int_args[0]
        hand = self.player_hands[hand_index]
        # Determine which column to use.
        column = BlackjackHand.card_values[self.dealer_hand.cards[-1].rank] - 2
        # Determine the table and row to use.
        values = [BlackjackHand.card_values[card.rank] for card in hand.cards]
        if hand.score() == 21:
            self.human.tell('Stand, you idiot.')
            return True
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
        return True

    def do_hit(self, arguments):
        """
        Get another card dealt to your hand. (h)

        If you have multiple hands, you should indicate which hand you are hitting
        with an integer argument to the hit command (1 for the first hand listed,
        two for the second hand, and so on.)
        """
        # Check for proper timing.
        if not self.phase_check('get hit'):
            return True
        # Parse the arguments.
        int_args = self.parse_arguments('hit', arguments)
        if not int_args:
            return True
        hand_index = int_args[0]
        # Make sure hand can receive cards.
        hand = self.player_hands[hand_index]
        if hand.status != 'open':
            self.human.error('That hand is {}, you cannot hit it.'.format(hand.status))
        else:
            # Draw the card.
            hand.draw()
            score = hand.score()
            # Check for busted hand.
            if score > 21:
                self.human.tell('You busted with {} ({}).'.format(score, hand))
                hand.status = 'busted'
                self.bets[hand_index] = 0
            # Check for forced stand.
            elif score == 21:
                hand.status = 'standing'
                self.human.tell('You now have 21 with {}.'.format(hand))
        return True

    def do_quit(self, argument):
        """
        Stop playing Blackjack. (!)
        """
        # Determine overall winnings or losses.
        self.scores[self.human.name] -= self.stake
        # Determine if the game is a win or a loss.
        result = 'won'
        if self.scores[self.human.name] > 0:
            self.win_loss_draw[0] = 1
        elif self.scores[self.human.name] < 0:
            result = 'lost'
            self.win_loss_draw[1] = 1
        else:
            self.win_loss_draw[2] = 1
        # Inform the user.
        plural = utility.plural(abs(self.scores[self.human.name]), 'buck')
        self.human.tell('\nYou {} {} {}.'.format(result, abs(self.scores[self.human.name]), plural))
        # Keeps turns as number of (dealer) hands.
        if self.phase == 'bet':
            self.turns -= 1
        # Quit the game.
        self.flags |= 4
        self.force_end = True

    def do_split(self, arguments):
        """
        Split a pair into two hands. (sp)

        If you have multiple hands, you should indicate which hand you are splitting
        with an integer argument to the split command (1 for the first hand listed,
        two for the second hand, and so on.)
        """
        # Check timing.
        if not self.phase_check('split a hand'):
            return True
        # Parse arguments.
        int_args = self.parse_arguments('split', arguments)
        if not int_args:
            return True
        hand_index = int_args[0]
        hand = self.player_hands[hand_index]
        # Check for valid split.
        if len(hand.cards) != 2:
            self.human.error('You can only split a hand of two cards.')
        elif self.split_rank and hand.cards[0].rank != hand.cards[1].rank:
            self.human.error('You may only split cards of the same rank.')
        elif hand.card_values[hand.cards[0].rank] != hand.card_values[hand.cards[1].rank]:
            self.human.error('You may only split cards of the same value.')
        elif not self.resplit and hand.was_split:
            self.human.error('You may not split a hand that was already split.')
        elif self.bets[hand_index] > self.scores[self.human.name]:
            self.human.error('You do not have enough money to split that hand.')
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
        return True

    def do_stand(self, arguments):
        """
        Set a hand as done. (s)

        If you have multiple hands, you should indicate which hand you are doubling
        with an integer argument to the double command (1 for the first hand listed,
        two for the second hand, and so on.)
        """
        # Check timing.
        if not self.phase_check('stand'):
            return True
        # Parse arguments.
        int_args = self.parse_arguments('hit', arguments)
        if not int_args:
            return True
        hand_index = int_args[0]
        # Check that the hand is not arleady standing or busted.
        hand = self.player_hands[hand_index]
        if hand.status != 'open':
            self.human.error('That hand is {}, you cannot stand with it.'.format(hand.status))
        else:
            # Set the hand to standing.
            hand.status = 'standing'
        return True

    def do_surrender(self, arguments):
        """
        Concede the hand for half the bet back. (su)

        If you have multiple hands, you should indicate which hand you are doubling
        with an integer argument to the double command (1 for the first hand listed,
        two for the second hand, and so on.)
        """
        # Check for proper timing.
        if not self.surrender:
            self.human.error('Surrender is not allowed in this game.')
            return True
        if not self.phase_check('surrender'):
            return True
        # Parse the arguments.
        int_args = self.parse_arguments('surrender', arguments)
        if not int_args:
            return True
        hand_index = int_args[0]
        # Make sure hand has no actions taken on it.
        hand = self.player_hands[hand_index]
        if hand.status != 'open':
            self.human.error('That hand is {}, you cannot surrender it.'.format(hand.status))
        elif hand.was_split:
            self.human.error('You cannot surrender a split hand.')
        elif len(hand.cards) > 2:
            self.human.error('You cannot surrender a hand that has been hit.')
        else:
            # Surrender the hand.
            hand.status = 'surrendered'
            self.scores[self.human.name] += int(self.bets[hand_index] / 2)
            self.bets[hand_index] = 0
        return True

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # The game is over when the human is out of money (and live bets).
        if self.scores[self.human.name] == 0 and self.phase == 'bet':
            # Set the results.
            self.win_loss_draw[1] = 1
            self.human.tell('\nYou lost all of your money.')
            self.scores[self.human.name] -= self.stake
            return True
        else:
            return False

    def get_bet(self):
        """Get the bet from the user. (None)"""
        # Prepare the query.
        prompt = 'How much would you like to bet this round (return for max): '
        max_bet = min(self.limit, self.scores[self.human.name])
        # Check for enough to bet one buck for each hand.
        if self.scores[self.human.name] < self.hand_count:
            # Get rid of unbettable hands.
            plural = utility.number_plural(self.hand_count, 'hand')
            self.human.tell('You do not have enough money to play {}.'.format(plural))
            self.do_hands(self.scores[self.human.name])
        # Check for multiple bets.
        if self.hand_count == 1:
            num_bets = [1]
        else:
            num_bets = [1, self.hand_count]
        # Loop until you have a bet or no-go command (like quit).
        while True:
            # Query the user.
            self.human.tell('\nYou have {} bucks.'.format(self.scores[self.human.name]))
            bets = self.human.ask_int_list(prompt, low = 1, high = max_bet, default = [max_bet],
                valid_lens = num_bets)
            # Handle bets.
            if isinstance(bets, list):
                # Single bets are assumed to be for all hands.
                if len(bets) == 1:
                    bets = bets * self.hand_count
                # Check for a valid total.
                if sum(bets) > self.scores[self.human.name]:
                    self.human.error('You do not have that much money ({} bucks needed).'.format(sum(bets)))
                    continue
                # Record the bets.
                self.bets = bets
                self.scores[self.human.name] -= sum(bets)
                # Continue the game.
                self.phase = 'play'
                return True
            else:
                # Handle other commands, looping unless they call for end of turn.
                if not self.handle_cmd(bets):
                    return False

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
        columns: The expected number of columns in the table. (int)
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
            # Pull out the keys.
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

        This function assumes that the first argument is an optional hand indicator.

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
            self.human.error(message.format(command, arguments, max_args))
            return []
        # Check for correct number of arguments.
        if max_args - len(int_args) == 1:
            # Add the bet if necessary.
            if len(self.player_hands) > 1 and command == 'double':
                # Make sure the hand index is valid.
                if int_args[0] <= len(self.player_hands):
                    int_args.append(self.bets[int_args[0] - 1])
                else:
                    self.human.error('Invalid hand index ({}).'.format(int_args[-1]))
                    return []
            # Add default hand index if necessary.
            else:
                # Default hand is the next open hand.
                for hand_index, hand in enumerate(self.player_hands):
                    if hand.status == 'open':
                        break
                int_args.append(hand_index + 1)
        if len(int_args) != max_args:
            self.human.error('Need more arguments to the {0} command. See help {0}.'.format(command))
            return []
        # Check for a valid hand index.
        if int_args[0] > len(self.player_hands):
            self.human.error('Invalid hand index ({}).'.format(int_args[-1]))
            return []
        # Adjust hand index to 0 indexing.
        int_args[0] -= 1
        # Return integer arguments.
        return int_args

    def phase_check(self, task):
        """
        Check that the phase is appropriate for actions on hands. (bool)

        Parameters:
        task: The hand action being tried. (str)
        """
        if self.phase == 'bet':
            self.human.error('No hands have been dealt yet.')
        elif self.phase == 'insurance':
            self.human.error('You must decide on insurance before you can {}.'.format(task))
        else:
            return True
        return False

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
            move = self.human.ask("\nWhat's your play? ")
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
        # Set the betting options.
        self.option_set.add_option('stake', ['s'], int, 100, check = lambda bucks: bucks > 0,
            question = 'How much money would you like to start with (return for 100)? ')
        self.option_set.add_option('limit', ['l'], int, 8, check = lambda bucks: 0 < bucks,
            question = 'What should the maximum bet be (return for 8)? ')
        # Set the deal options.
        self.option_set.add_option('decks', ['d'], int, 4, valid = (1, 2, 4, 6, 8),
            question = 'How many decks should be in the shoe (return for 4)? ')
        self.option_set.add_option('hands', ['h'], int, 1, check = lambda hands: 0 < hands < 4,
            question = 'How hands would you like to play (return for 1)? ', target = 'hand_count')
        # Set the doubling options
        self.option_set.add_option('true-double', ['td'],
            question = 'Should a double have to be a true double? bool')
        self.option_set.add_option('no-double-split', ['nds'], value = False, default = True,
            target = 'double_split', question = 'Should doubling a split hand be banned? bool')
        # Set the splitting options.
        self.option_set.add_option('split-rank', ['sr'],
            question = 'Should you only be able to split hands of equal rank? bool')
        self.option_set.add_option('no-resplit', ['nr'], value = False, default = True, target = 'resplit',
            question = 'Should you be blocked from splitting a split hand? bool')
        self.option_set.add_option('hit-split-ace', ['hsa'],
            question = 'Should you be able to hit split aces? bool')
        # Set the showdown options.
        self.option_set.add_option('surrender', ['su'],
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
        # Load the hints.
        self.load_hints()

    def show_status(self):
        """Show the current game situation to the player. (None)"""
        # Show the stake left.
        text = "\nYou have {} bucks in hand and {} bucks in play."
        text = text.format(self.scores[self.human.name], sum(self.bets))
        # Show all of the hands.
        text += "\nThe dealer's hand is {}.".format(self.dealer_hand)
        text += '\nYour hand is {} ({}) [{}].'
        text = text.format(self.player_hands[0], self.player_hands[0].score(), self.player_hands[0].status)
        hand_text = '\nYour {} hand is {} ({}) [{}].'
        for hand_index, hand in enumerate(self.player_hands[1:]):
            ordinal = utility.number_word(hand_index + 2, True)
            text += hand_text.format(ordinal, hand, hand.score(), hand.status)
        # Send the information to the human.
        self.human.tell(text)

    def showdown(self):
        """Show and hit the dealer's hand and resolve the round. (None)"""
        # Reveal the dealer's hole card.
        self.dealer_hand.cards[0].up = True
        self.human.tell('\nThe dealer has {}.'.format(self.dealer_hand))
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
        # Get the hand value.
        hand_value = hand.score()
        hand_bj = hand.blackjack()
        # Get the dealer's value.
        dealer_value = self.dealer_hand.score()
        dealer_bj = self.dealer_hand.blackjack()
        # Check for a win.
        if hand_value > dealer_value or dealer_value > 21:
            if hand_bj:
                payout = 2.5
            else:
                payout = 2
        # Check for a push.
        elif hand_value == dealer_value:
            if hand_bj and dealer_bj:
                payout = 1
            # Blackjack beats 21.
            elif hand_bj:
                payout = 2.5
            elif dealer_bj:
                payout = 0
            else:
                payout = 1
        # Otherwise it's a loss.
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
    __init__
    score
    """

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
        # Create the new hand.
        new_hand = BlackjackHand(self.deck)
        new_hand.cards.append(self.cards.pop())
        new_hand.status = 'open'
        # Mark both hands as having been split.
        self.was_split = True
        new_hand.was_split = True
        # Return the new hand.
        return new_hand
