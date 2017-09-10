"""
blackjack_game.py

Blackjack.

to-do:
redo bet
write some rules
detect player blackjack
hints
flesh out the options

!! Side bets would be nice, but I'm not implementing them now.

Constants:
CREDITS: Credits for Blackjack.

Classes:
Blackjack: A game of Blackjack. (game.Game)
BlackjackHand: A hand of Blackjack. (cards.Hand)
"""


import tgames.cards as cards
import tgames.game as game


# Credits for Blackjack.
CREDITS = """
Game Design: Traditional (U.S. Casinos)
Game Programming: Craig "Ichabod" O'Brien
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
    do_split: Split a pair into two hands. (bool)
    do_stand: Set a hand as done. (bool)
    do_surrender: Concede the hand for half the bet back. (bool)
    get_bet: Record the player's bet. (None)
    parse_arguments: Parse integer arguments to command. (list of int)
    show_status: Show the current game situation to the player. (None)
    showdown: Show and hit the dealer's hand and resolve the round. (None)
    wins: Determine if a hand wins and it's payout. (float)

    Overridden Methods:
    do_quit
    game_over
    handle_options
    """

    # Alternate names for the game.
    aka = ['twenty-one', '21']
    # Alternate words for commands
    aliases = {'b': 'bet', 'd': 'double', 'h': 'hit', 'q': 'quit', 's': 'stand', 'sp': 'split',
        'su': 'surrender'}
    # Interface categories for the game.
    categories = ['Gambling Games', 'Card Games']
    # Credits for the game.
    credits = CREDITS
    # The name of the game.
    name = 'Blackjack'
    # Ordinal words for displaying multiple hands.
    ordinals = ('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth')

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
            for hand_index, hand in self.player_hands[1:]:
                self.human.tell('Your {} hand is {}.'.format(self.ordinals[hand_index + 1], hand))
            while True:
                insure = self.human.ask('How much insurance would you like? ')
                if not insure.strip():
                    insure = '0'
                if insure.strip().isdigit() and int(insure) <= min(self.bets) / 2:
                    self.insurance = int(insure)
                    self.scores[self.human.name] -= self.insurance
                    break
                else:
                    self.human.tell('That is not a valid insurance ammount.')
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
        elif not self.double_split and hand.split:
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
        while True:
            bet_text = self.human.ask('How much would you like to bet this round (return for max): ')
            try:
                bets = [int(x) for x in bet_text.split()]
            except ValueError:
                self.human.tell('Integers only, please.')
                continue
            if len(best) == 1:
                bets = bets * len(self.player_hands)
            # Check for valid number of bets.
            if len(bets) != len(self.player_hands):
                self.human.tell('Enter one bet per hand, or one bet to bet the same for all hands.')
            # Check for valid bet ammount.
            elif self.limit and max(bets) > self.limit:
                self.human.tell('The betting limit is {} bucks.'.format(self.limit))
            elif min(bets) < 1:
                self.human.tell('All bets must be positive.')
            elif sum(bets) > self.scores[self.human.name]:
                self.human.tell('You only have {} bucks left to bet.'.format(self.scores[self.human.name]))
            else:
                self.bets = bets
                break

    def handle_options(self):
        """Handle the game options. (None)"""
        # Set the default options.
        self.stake = 100
        self.limit = 8
        self.decks = 4
        self.hand_count = 1
        self.true_double = False
        self.split_rank = False
        self.resplit = True
        self.double_split = True
        self.hit_split_ace = False
        self.surrender = True # for testing, should be false.

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

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Make sure the bet has been recorded.
        if self.phase == 'bet':
            self.get_bet()
            self.deal()
            self.phase = 'play'
        # Show the current game state.
        self.show_status()
        # Get and handle the user input.
        move = self.human.ask("What's your play? ")
        hand_done = self.handle_cmd(move)
        # Check for the end of the turn.
        statuses = [hand.status for hand in self.player_hands]
        if 'open' not in statuses:
            # Check for show down with dealer (unless already done for dealer blackjack).
            if 'standing' in statuses and self.phase != 'bet':
                self.showdown()
            # Reset game tracking.
            self.phase = 'bet'
            self.bets = [0] * self.hand_count
            return False
        else:
            return hand_done

    def set_up(self):
        """Set up the game. (None)"""
        # Set up tracking variables.
        self.scores = {self.human.name: self.stake}
        self.bets = [0] * self.hand_count
        self.insurance = 0
        self.phase = 'bet'
        # Set up the deck.
        self.deck = cards.Deck(decks = self.decks)
        self.deck.shuffle()
        # Set up default hands.
        self.dealer_hand = BlackjackHand(self.deck)
        self.player_hands = [BlackjackHand(self.deck)]

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
        # Draw up to 17.
        while self.dealer_hand.score() < 17:
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
        # Discard all hands.
        self.dealer_hand.discard()
        for hand in self.player_hands:
            hand.discard()

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
        self.status = 'open'
        self.was_split = False

    def blackjack(self):
        """Check the hand for a blackjack. (bool)"""
        return self.score() == 21 and len(self.cards) == 2 and not self.was_split

    def score(self):
        """Score the hand. (int)"""
        score = sum([self.card_values[card.rank] for card in self.cards])
        # check for hard hand and adjust ace values.
        if score > 21:
            ace_count = len([card for card in self.cards if card.rank == 'A'])
            while score > 21 and ace_count:
                score -= 10
                ace_count -= 1
                self.soft = False
        else:
            self.soft = True
        return score

    def split(self):
        """Split the hand. (int)"""
        new_hand = BlackjackHand(self.deck)
        new_hand.cards.append(self.cards.pop())
        self.was_split = True
        new_hand.was_split = True
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