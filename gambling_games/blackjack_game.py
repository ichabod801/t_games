"""
blackjack_game.py

Blackjack.

to-do:
write some rules
flesh out rules
    surrender: must be first decision. half-bet back. allowing it is an option. not if dealer bj
    multiple starting hands (1-3)
    note: dealer check's black jack. If they've got it, game ends. Either you have bj and push, or you lose.
    insurance: If dealer has an ace, side bet they have bj. 2:1. If you have bj, pays out even. up to half bet.
    no negative bets.
hints
flesh out the options
side bets

Classes:
Blackjack: A game of Blackjack. (game.Game)
BlackjackHand: A hand of Blackjack. (cards.Hand)
"""


import tgames.cards as cards
import tgames.game as game


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
    do_bet: Record the player's bet. (bool)
    do_hit: Deal a card to the player. (bool)
    do_stand: Set a hand as done. (bool)

    Overridden Methods:
    do_quit
    game_over
    handle_options
    """

    # Alternate words for commands
    aliases = {'b': 'bet', 'd': 'double', 'h': 'hit', 'q': 'quit', 's': 'stand', 'sp': 'split',
        'su': 'surrender'}
    # Interface categories for the game.
    categories = ['Gambling Games', 'Card Games']
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
        self.player_hands = [BlackjackHand(self.deck)]
        self.player_hands[0].draw()
        self.player_hands[0].draw()
        self.player_hands[0].status = 'open'

    def do_bet(self, arguments):
        """
        Record the player's bet. (bool)

        !! I will want a way for them to place one bet for all hands (default? -1?)
        !! also set a default bet.

        Parameters:
        arguments: The amount bet. (str)
        """
        # Check for proper timing.
        if self.phase != 'bet':
            self.human.tell('You have already bet this hand.')
            return False
        # Parse the arguments.
        int_args = self.parse_arguments('bet', arguments, max_args = 2)
        if not int_args:
            return False
        bet, hand_index = int_args
        # Check for valid bet ammount.
        if self.limit and bet > self.limit:
            self.human.tell('The betting limit is {} bucks.'.format(self.limit))
        elif bet > self.scores[self.human.name]:
            self.human.tell('You only have {} bucks left to bet.'.format(self.scores[self.human.name]))
        else:
            # Record the bet.
            self.bets[hand_index] = bet
            self.scores[self.human.name] -= self.bets[hand_index]
            # Check for all bets in.
            if min(self.bets) > 0:
                self.deal()
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

    def do_surrender(self, arguments):
        """
        Deal a card to the player. (bool)

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
        elif hand.split:
            self.human.tell('You cannot surrender a split hand.')
        elif len(hand.cards) > 2:
            self.human.tell('You cannot surrender a hand that has been hit.')
        else:
            hand.status = 'surrendered'
            self.scores[self.human.name] += int(self.bet[hand_index] / 2)

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
        Set a hand as done. (bool)

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
            self.human.tell('The new hand dred the {}.'.format(new_hand.cards[-1].name))
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

    def game_over(self):
        """Determine the end of game. (bool)"""
        return self.scores[self.human.name] == 0

    def handle_options(self):
        """Handle the game options. (None)"""
        # Set the default options.
        self.stake = 100
        self.limit = 8
        self.decks = 4
        self.bets = [0]
        self.true_double = False
        self.split_rank = False
        self.resplit = True
        self.double_split = True
        self.hit_split_ace = False
        self.surrender = False

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
        # Show the current game state.
        self.show_status()
        # Get and handle the user input.
        move = self.human.ask("What's your play? ")
        hand_done = self.handle_cmd(move)
        # Check for the end of the turn.
        statuses = [hand.status for hand in self.player_hands]
        if 'open' not in statuses:
            # Check for show down with dealer.
            if 'standing' in statuses:
                self.showdown()
            # Reset game tracking.
            self.phase = 'bet'
            self.bets = [0]
            return False
        else:
            return hand_done

    def set_up(self):
        """Set up the game. (None)"""
        # Set up tracking variables.
        self.scores = {self.human.name: self.stake}
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
        # Show the right stuff for the current phase.
        if self.phase == 'bet':
            # Show that bets are still pending.
            text += '\nThe dealer is waiting for your bet.'
        elif self.phase == 'play':
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
            hand.status = 'open'

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