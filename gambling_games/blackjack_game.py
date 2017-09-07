"""
blackjack_game.py

Blackjack.

to-do:
do_quit
clean up comments
flesh out rules
flesh out the options

Classes:
Blackjack: A game of Blackjack. (game.Game)
BlackjackHand: A hand of Blackjack. (cards.Hand)
"""


import tgames.cards as cards
import tgames.game as game


class Blackjack(game.Game):
    """
    A game of Blackjack. (game.Game)
    """

    aliases = {'b': 'bet', 'h': 'hit', 's': 'stand'}
    ordinals = ('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth')

    def deal(self):
        """Deal the hands. (None)"""
        self.dealer_hand = BlackjackHand(self.deck)
        self.dealer_hand.draw(False)
        self.dealer_hand.draw()
        self.player_hands = [BlackjackHand(self.deck)]
        self.player_hands[0].draw()
        self.player_hands[0].draw()
        self.player_hands[0].status = 'open'

    def do_bet(self, arguments):
        """
        Record the player's bet. (bool)

        Parameters:
        arguments: The amount bet. (str)
        """
        if self.phase != 'bet':
            self.human.tell('You have already bet this hand.')
            return False
        int_args = self.parse_arguments('bet', arguments, max_args = 2)
        if not int_args:
            return False
        bet, hand_index = int_args
        if self.limit and bet > self.limit:
            self.human.tell('The betting limit is {} bucks.'.format(self.limit))
        elif bet > self.scores[self.human.name]:
            self.human.tell('You only have {} bucks left to bet.'.format(self.scores[self.human.name]))
        else:
            self.bets[hand_index] = bet
            self.scores[self.human.name] -= self.bets[hand_index]
            if min(self.bets) > 0:
                self.deal()
                self.phase = 'play'

    def do_hit(self, arguments):
        """
        Deal a card to the player. (bool)

        Parameters:
        arguments: The number of the hand to hit. (str)
        """
        if self.phase != 'play':
            self.human.tell('No hands have been dealt yet.')
            return False
        int_args = self.parse_arguments('hit', arguments)
        if not int_args:
            return False
        hand_index = int_args[0]
        hand = self.player_hands[hand_index]
        if hand.status != 'open':
            self.human.tell('That hand is {}, you cannot hit it.'.format(hand.status))
        else:
            hand.draw()
            score = hand.score()
            if score > 21:
                self.human.tell('You busted with {}.'.format(score))
                hand.status = 'busted'
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

    def do_stand(self, arguments):
        """
        Set a hand as done. (bool)

        Parameters:
        arguments: The number of the hand to hit. (str)
        """
        if self.phase != 'play':
            self.human.tell('No hands have been dealt yet.')
            return False
        int_args = self.parse_arguments('hit', arguments)
        if not int_args:
            return False
        hand_index = int_args[0]
        hand = self.player_hands[hand_index]
        if hand.status != 'open':
            self.human.tell('That hand is {}, you cannot stand with it.'.format(hand.status))
        else:
            hand.status = 'standing'

    def game_over(self):
        """Determine the end of game."""
        return self.scores[self.human.name] == 0

    def handle_options(self):
        """Handle the game options. (None)"""
        self.stake = 100
        self.limit = 5
        self.decks = 4
        self.bets = [0]

    def parse_arguments(self, command, arguments, max_args = 1):
        try:
            int_args = [int(arg) for arg in arguments.split()]
        except ValueError:
            message = 'Invalid argument to {} ({}): must be no more than {} integers.'
            self.human.tell(message.format(command, arguments, max_args))
            return []
        if max_args - len(int_args) == 1:
            int_args.append(1)
        if len(int_args) != max_args:
            self.human.tell('Need more arguments to the {0} command. See help {0}.'.format(command))
            return []
        if int_args[-1] > len(self.player_hands):
            self.human.tell('Invalid hand index ({}).'.format(int_args[-1]))
            return []
        int_args[-1] -= 1
        return int_args

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        self.show_status()
        move = self.human.ask("What's your play? ")
        hand_done = self.handle_cmd(move)
        statuses = [hand.status for hand in self.player_hands]
        if 'open' not in statuses:
            if 'standing' in statuses:
                self.showdown()
            self.phase = 'bet'
            self.bets = [0]
            return False
        else:
            return hand_done

    def set_up(self):
        """Set up the game. (None)"""
        self.scores = {self.human.name: self.stake}
        self.deck = cards.Deck(decks = self.decks)
        self.deck.shuffle()
        self.dealer_hand = BlackjackHand(self.deck)
        self.player_hands = [BlackjackHand(self.deck)]
        self.phase = 'bet'

    def show_status(self):
        """Show the current game situation to the player. (None)"""
        text = "\nYou have {} bucks.".format(self.scores[self.human.name])
        if self.phase == 'bet':
            text += '\nThe dealer is waiting for your bet.'
        elif self.phase == 'play':
            text += "\nThe dealer's hand is {}.".format(self.dealer_hand)
            text += '\nYour hand is {} ({}).'.format(self.player_hands[0], self.player_hands[0].score())
            for hand_index, hand in self.player_hands[1:]:
                text += '\nYour {} hand is {}.'.format(self.ordinals[hand_index + 1], hand)
        self.human.tell(text)

    def showdown(self):
        """Show and hit the dealer's hand and resolve the round. (None)"""
        self.dealer_hand.cards[0].up = True
        self.human.tell('The dealer has {}.'.format(self.dealer_hand))
        while self.dealer_hand.score() < 17:
            self.dealer_hand.draw()
            self.human.tell('The dealer draws the {}.'.format(self.dealer_hand.cards[-1].name))
        dealer_value = self.dealer_hand.score()
        self.human.tell("The dealer's hand is {}.".format(dealer_value))
        if dealer_value > 21:
            self.human.tell('The dealer busted.')
        for hand_index, hand in enumerate(self.player_hands):
            payout = self.wins(hand)
            if payout > 1:
                self.human.tell('You won with {}.'.format(hand))
            elif payout == 1:
                self.human.tell('You pushed with {}.'.format(hand))
            else:
                self.human.tell('You lost with {}.'.format(hand))
            self.scores[self.human.name] += int(self.bets[hand_index] * payout)
        self.dealer_hand.discard()
        for hand in self.player_hands:
            hand.discard()
            hand.status = 'open'

    def wins(self, hand):
        hand_value = hand.score()
        hand_bj = hand_value == 21 and len(hand.cards) == 2
        dealer_value = self.dealer_hand.score()
        dealer_bj = dealer_value == 21 and len(self.dealer_hand.cards) == 2
        if hand_value > dealer_value or dealer_value > 21:
            if hand_bj:
                payout = 2.5
            else:
                payout = 2
        elif hand_value == dealer_value:
            if hand_bj and dealer_bj:
                payout = 1
            elif hand_bj:
                payout = 2.5
            elif dealer_bj:
                payout = 0
            else:
                payout = 1
        else:
            payout = 0
        return payout


class BlackjackHand(cards.Hand):
    """
    A hand of Blackjack. (cards.Hand)

    Class Attributes:
    card_values: A mapping of card ranks to score values. (dict of str: int)

    Attributes:
    soft: A flag for the hand being soft (ace = 11).

    Overridden Methods:
    score
    """

    card_values = dict(zip('23456789TAJQK', list(range(2, 12)) + [10] * 3))

    def __init__(self, deck):
        super(BlackjackHand, self).__init__(deck)
        self.status = 'open'

    def score(self):
        """Score the hand. (int)"""
        score = sum([self.card_values[card.rank] for card in self.cards])
        if score > 21:
            ace_count = len([card for card in self.cards if card.rank == 'A'])
            while score > 21 and ace_count:
                score -= 10
                ace_count -= 1
                self.soft = False
        else:
            self.soft = True
        return score


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