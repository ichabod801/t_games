"""
hearts_game.py

A game of Hearts.

Classes:
HeartBot: A simple bot for Hearts. (player.Bot)
Hearts: A game of Hearts. (game.Game)
"""


import re

from .. import cards
from .. import game
from .. import player
from .. import utility


class HeartBot(player.Bot):
    """
    A simple bot for Hearts. (player.Bot)

    Attribute:
    hand: The player's cards in the game. (cards.Hand)

    Methods:
    pass_cards: Determine which cards to pass. (list of cards.Card)
    play: Play a card to start or add to a trick. (card.Card)

    Overridden Methods:
    ask
    set_up
    tell
    """

    def ask(self, prompt):
        """
        Get a response from the bot. (str)

        Parameters:
        prompt: The question to ask the bot. (str)
        """
        if prompt.startswith('\nWhich three'):
            return ' '.join(str(card) for card in self.pass_cards())
        elif prompt.startswith('\nWhat is'):
            card = str(self.play())
            self.game.human.tell('{} plays the {}.'.format(self.name, card))
            return card
        else:
            return super(HeartBot, self).ask(prompt)

    def pass_cards(self):
        """Determine which cards to pass. (list of card.Card)"""
        # Get rid of high spades, high hearts, and high other cards, in that order
        to_pass = [card for card in self.hand if card in ('KS', 'AS')]
        hearts = [card for card in self.hand if card.suit == 'H']
        hearts.sort(key = lambda card: card.rank_num, reverse = True)
        to_pass.extend(hearts)
        if len(to_pass) < 3:
            other = [card for card in self.hand if card not in to_pass]
            other.sort(key = lambda card: card.rank_num, reverse = True)
            to_pass.extend(other)
        return to_pass[:3]

    def play(self):
        """Play a card to start or add to a trick. (card.Card)"""
        if self.game.trick:
            trick_starter = self.game.trick.cards[0]
            playable = [card for card in self.hand if card.suit == trick_starter.suit]
            if playable:
                playable.sort(key = lambda card: card.rank_num)
                losers = [card for card in playable if card.rank_num < trick_starter.rank_num]
                if losers:
                    return losers[-1]
                else:
                    return playable[0]
            else:
                if 'QS' in self.hand:
                    return 'QS'
                hearts = [card for card in self.hand if card.suit == 'H']
                hearts.sort(key = lambda card: card.rank_num)
                if hearts:
                    return hearts[-1]
                else:
                    return sorted(self.hand.cards, key = lambda card: card.rank_num)[-1]
        else:
            self.hand.cards.sort(key = lambda card: card.rank_num)
            return self.hand.cards[0]

    def set_up(self):
        """Set up the bot. (None)"""
        self.hand = self.game.hands[self.name]

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        pass


class Hearts(game.Game):
    """
    A game of Hearts. (game.Game)

    Attributes:
    deck: The deck of cards used in the game. (cards.Deck)
    hands: The players' hands of cards. (dict of str: cards.Hand)
    passes: The cards passed by each player. (dict of str: cards.Hand)
    trick: The cards in the current trick. (cards.Hand)

    Methods:
    deal: Deal the cards to the players. (None)
    do_play: Play a card, to either start or contribute to a trick. (bool)
    set_dealer: Determine the first dealer for the game. (None)
    trick_winner: Determine who won the trick. (None)

    Overridden Methods:
    game_over
    handle_options
    player_action
    set_up
    """

    aliases = {'p': 'play'}
    card_re = re.compile(r'\s*[x123456789tjqka][cdhs]\s*', re.IGNORECASE)
    categories = ['Card Games']
    name = 'Hearts'

    def deal(self):
        """Deal the cards to the players. (None)"""
        # Deal the cards out equally, leaving any extras aside.
        self.deck.shuffle()
        player_index = self.players.index(self.dealer)
        while True:
            player_index = (player_index + 1) % len(self.players)
            self.hands[self.players[player_index].name].draw()
            if self.players[player_index] == self.dealer and len(self.deck.cards) < len(self.players):
                break
        self.human.tell('{} deals.'.format(self.players[player_index]))
        # Eldest hand starts, and is the next dealer.
        self.dealer = self.players[(player_index + 1) % len(self.players)]
        #print('dealer set to {}.'.format(self.dealer))

    def do_play(self, arguments):
        """
        Play a card, to either start or contribute to a trick.  (p)
        """
        player = self.players[self.player_index]
        hand = self.hands[player.name]
        #print(player.name, hand)
        if self.card_re.match(arguments):
            card_text = arguments.upper()
        else:
            player.error('{!r} is not a card in the deck.'.format(arguments))
            return True
        if self.phase != 'trick':
            player.error('This is not the right time to play cards.')
            return True
        elif card_text not in hand:
            player.error('You do not have the {} to play.'.format(card_text))
            return True
        if self.trick:
            card = hand.cards[hand.cards.index(card_text)]
            trick_suit = self.trick.cards[0].suit
            if card.suit != trick_suit and filter(lambda card: card.suit == trick_suit, hand):
                player.error('You must play a card of the suit led.')
                return True
            hand.shift(card, self.trick)
        else:
            hand.shift(card_text, self.trick)

    def game_over(self):
        """Determine if the game is over. (bool)"""
        if max(self.scores.values()) > self.win:
            human_score = self.scores[self.human.name]
            winning_score = min(self.scores.values())
            for name, score in self.scores.items():
                if score > human_score:
                    self.win_loss_draw[0] += 1
                elif score < human_score:
                    self.win_loss_draw[1] += 1
                elif name != human_score:
                    self.win_loss_draw[2] += 1
                if score == winning_score:
                    self.human.tell('{} wins with {} points.'.format(name, score))
            self.turns = self.tricks
            return True
        else:
            return False

    def handle_options(self):
        """Handle the option settings for this game. (None)"""
        self.win = 100
        self.players = [self.human]
        for bot in range(3):
            self.players.append(HeartBot(taken_names = [player.name for player in self.players]))
        self.max_score = 26

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        if self.phase == 'pass':
            player.tell('\nYour hand is: {}.'.format(self.hands[player.name]))
            move = player.ask('\nWhich three cards do you wish to pass? ')
            cards = self.card_re.findall(move)
            if len(cards) == 3:
                #print('{} passes.'.format(player))
                cards = [card.strip().upper() for card in cards]
                hand = self.hands[player.name]
                if all(card in hand for card in cards):
                    for card in cards:
                        hand.shift(card, self.passes[player.name])
                    if all(self.passes.values()):
                        #print('passing cards...')
                        #print([len(hand) for hand in self.hands.values()])
                        for pass_from, pass_to in zip(self.players[1:] + self.players[:1], self.players):
                            #print('passing from {} to {}'.format(pass_from, pass_to))
                            self.hands[pass_to.name].cards.extend(self.passes[pass_from.name].cards)
                            self.passes[pass_from.name].cards = []
                        #print([len(hand) for hand in self.hands.values()])
                        self.phase = 'trick'
                        self.player_index = self.players.index(self.dealer) - 1
            else:
                return self.handle_cmd(move)
        elif self.phase == 'trick':
            if self.trick:
                player.tell('\nThe trick to you is: {}.'.format(self.trick))
            else:
                player.tell('\nYou lead the trick.')
            player.tell('Your hand is: {}.'.format(self.hands[player.name]))
            move = player.ask('\nWhat is your play? ')
            if self.card_re.match(move):
                go = self.do_play(move)
                if len(self.trick) == len(self.players):
                    self.tricks += 1
                    self.trick_winner()
                return go
            else:
                return self.handle_cmd(move)

    def score_round(self):
        """Score one deck's worth of tricks. (None)"""
        self.human.tell('')
        # Calculate the points this round for each player.
        round_points = {}
        shooter = ''
        for player in self.players:
            # Count the scoring cards.
            hearts, lady = 0, 0
            for card in self.taken[player.name]:
                if card.suit == 'H':
                    hearts += 1
                elif card == 'QS':
                    lady += 1
            # Calculate and store the unadjusted points.
            player_points = hearts + 13 * lady
            round_points[player.name] = player_points
            # Display the card counts and points.
            score_text = '{} had {} {}'.format(player.name, hearts, utility.plural(hearts, 'heart'))
            lady_text = ' and the Queen of Spades' if lady else ''
            score_text = '{}{}, for {} points this round.'.format(score_text, lady_text, player_points) # !! plural points
            self.human.tell(score_text)
            # Inform and record any sucessful shooter.
            if player_points == self.max_score:
                self.human.tell('{} shot the moon!'.format(player.name))
                shooter = player.name
        # Adjust the round points if anyone shot the moon.
        if shooter:
            for player in round_points:
                if player == shooter:
                    round_points[player] = 0
                else:
                    round_points[player] = self.max_score
        # Adjust and display the overall points.
        self.human.tell('\nOverall Scores:')
        for player in self.players:
            self.scores[player.name] += round_points[player.name]
            self.human.tell('{}: {}'.format(player, self.scores[player.name]))

    def set_dealer(self):
        """Determine the first dealer for the game. (None)"""
        # Deal a card to each player, keeping track of the max rank and who was dealt it.
        self.deck.shuffle()
        max_rank = -1
        players = self.players[:]
        max_players = []
        player_index = 0
        self.human.tell('')
        while True:
            # Deal the card.
            card = self.deck.deal(up = True)
            self.deck.discards.append(card)
            self.human.tell('{} was dealt the {}.'.format(players[player_index], card))
            # Track the max rank.
            if card.rank_num == max_rank:
                max_players.append(players[player_index])
            elif card.rank_num > max_rank:
                max_rank = card.rank_num
                max_players = [players[player_index]]
            player_index += 1
            # Check for unique winner.
            if player_index == len(players):
                if len(max_players) == 1:
                    self.dealer = max_players[0]
                    break
                else:
                    # Redeal to any tied players.
                    self.human.tell("\nThere was a tie with two {}'s.".format(self.deck.ranks[max_rank]))
                    max_rank = -1
                    players = max_players
                    max_players = []
                    player_index = 0

    def set_up(self):
        """Set up the game. (None)"""
        self.deck = cards.Deck(ace_high = True)
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        self.passes = {player.name: cards.Hand(self.deck) for player in self.players}
        self.taken = {player.name: cards.Hand(self.deck) for player in self.players}
        self.trick = cards.Hand(self.deck)
        self.set_dealer()
        self.deal()
        self.phase = 'pass'
        self.tricks = 0

    def trick_winner(self):
        """Determine who won the trick. (None)"""
        # Find the winning card.
        trick_suit = self.trick.cards[0].suit
        suit_cards = [card for card in self.trick if card.suit == trick_suit]
        winning_card = sorted(suit_cards, key = lambda card: card.rank_num)[-1]
        card_index = self.trick.cards.index(winning_card)
        # Find the winning player.
        winner_index = (self.player_index + 1 + card_index) % len(self.players)
        winner = self.players[winner_index]
        # Handle the win.
        self.human.tell('\n{} won the trick with the {}.'.format(winner, winning_card))
        self.taken[winner.name].cards.extend(self.trick.cards)
        self.trick.cards = []
        # Check for the end of the round.
        if not self.hands[self.human.name]:
            self.score_round()
            if max(self.scores.values()) < self.win:
                for hand in self.taken.values():
                    hand.discard()
                self.deal()
                self.phase = 'pass'
        else:
            self.player_index = winner_index - 1
