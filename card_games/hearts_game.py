"""
hearts_game.py

A game of Hearts.

Classes:
Hearts: A game of Hearts. (game.Game)
"""


import re

from .. import cards
from .. import game
from .. import player


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

    Overridden Methods:
    player_action
    set_up
    """

    aliases = {'p': 'play'}
    card_re = re.compile(r'^\s*[x123456789tjqk][cdhs]\s*$', re.IGNORECASE)
    categories = ['Card Games']
    name = 'Hearts'

    def deal(self):
        """Deal the cards to the players. (None)"""
        # Deal the cards out equally, leaving any extras aside.
        self.deck.shuffle()
        player_index = self.players.index(self.dealer)
        while self.deck.cards:
            player_index = (player_index + 1) % len(self.players)
            if self.players[player_index] == self.dealer and len(self.deck.cards) < len(self.players):
                break
            self.hands[self.players[player_index]].draw()
        # Eldest hand starts, and is the next dealer.
        self.player_index = (player_index + 1) % len(self.players)
        self.dealer = self.players[self.player_index]

    def do_play(self, arguments):
        """
        Play a card, to either start or contribute to a trick.  (p)
        """
        player = self.players[self.player_index]
        hand = self.hands[player.name]
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
            hand.shift(card_text, self.trick)
        else:
            card = hand.cards[hand.cards.index(card_text)]
            trick_suit = self.trick.cards[0].suit
            if card.suit != trick_suit and filter(lambda card: card.suit == trick_suit, hand):
                player.error('You must play a card of the suit led.')
                return True
            hand.shift(card, self.trick)

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        if self.phase == 'pass':
            player.tell('Your hand is: {}.'.format(self.hands[player.name]))
            move = player.ask('\nWhich three cards do you wish to pass? ')
            cards = self.card_re.findall(move)
            if len(cards) == 3:
                cards = [card.strip().upper() for card in cards]
                hand = self.hands[player.name]
                if all(card in hand for card in cards):
                    for card in cards:
                        hand.shift(card, self.passes[player.name])
                    if player == self.dealer:
                        for pass_from, pass_to in zip(self.players[1:] + self.players[:1], self.players):
                            pass_hand = self.hands[pass_from.name]
                            for card in pass_hand:
                                pass_hand.shift(card, self.hands[pass_to.name])
                        self.phase == 'trick'
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
                return self.do_play(move)
                # !! handle end of trick
            else:
                return self.handle_cmd(move)

    def set_dealer(self):
        """Determine the first dealer for the game. (None)"""
        # Deal a card to each player, keeping track of the max rank and who was dealt it.
        self.deck.shuffle()
        max_rank = -1
        players = self.players[:]
        max_players = []
        player_index = 0
        while True:
            # Deal the card.
            card = self.deck.deal()
            self.deck.discard.append(hand)
            self.human.tell('{} was dealt the {}.'.format(players[player_index], card))
            card_rank = self.deck.cards.index(card.rank)
            # Track the max rank.
            if card_rank == max_rank:
                max_players.append(player)
            elif card_rank > max_rank:
                max_rank = card_rank
                max_players = [player]
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
        self.deck = cards.Deck()
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        self.passes = {player.name: cards.Hand(self.deck) for player in self.players}
        self.trick = cards.Hand(self.deck)
        self.set_dealer()
        self.deal()
        self.phase = 'pass'