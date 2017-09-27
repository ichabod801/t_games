"""
crazy_eights_game.py

A game of Crazy Eights.

Classes:
CrazyEights: A game of Crazy Eights (game.Game)
C8Bot: A basic Crazy Eights bot. (player.Bot)
"""


import tgames.cards as cards
import tgames.game as game
import tgames.player as player


class C8Bot(player.Bot):
    """
    A basic Crazy Eights bot. (player.Bot)
    """

    def ask(self, prompt):
        if prompt == 'What is your play? ':
            discard = self.game.deck.discards[-1]
            hand = self.game.hands[self.name]
            if self.game.suit:
                suit = self.game.suit
            else:
                suit = discard.suit
            suit_matches = [card for card in hand.cards if card.suit == suit and card.rank != '8']
            rank_matches = [card for card in hand.cards if card.rank == discard.rank and card.rank != '8']
            eights = [card for card in hand.cards if card.rank == '8']
            suits = [(len([card for card in hand.cards if card.suit == suit]), suit) for suit in 'CDHS']
            suits.sort(reverse = True)
            if suit_matches:
                suit_matches.sort()
                card = str(suit_matches[-1])
            elif rank_matches:
                rank_suits = [card.suit for card in rank_matches]
                for count, suit in suits:
                    if suit in rank_suits:
                        card = discard.rank + suit
                        break
            elif eights:
                card = str(eights[0])
                self.held_suit = suits[0][1]
            else:
                card = 'draw'
                self.game.human.tell('{} drew a card.'.format(self.name))
            if card != 'draw':
                self.game.human.tell('{} played the {}.'.format(self.name, card))
            return card
        elif prompt == 'What suit do you choose? ':
            suit, self.held_suit = self.held_suit, None
            self.game.human.tell('The new suit to match is {}.'.format(suit)) 
            return suit
        else:
            raise ValueError('Invalid prompt to C8Bot: {!r}'.format(prompt))

    def tell(self, text):
        pass


class CrazyEights(game.Game):
    """
    A game of Crazy Eights. (game.Game)

    Attributes:
    deck: The deck of cards used in the game. (cards.Deck)
    goal: The number of points needed to win the game. (int)
    hands: The player's hands. (dict of str: cards.Hand)
    suit: The suit called with the last eight. (str)

    Methods:
    deal: Deal the cards to the players. (None)
    score: Score the round's winner. (None)

    Overridden Methods:
    handle_options
    player_turn
    set_up
    """

    categories = ['Card Games', 'Shedding Games']
    name = 'Crazy Eights'

    def deal(self):
        """Deal the cards to the players. (None)"""
        for hand in self.hands.values():
            hand.discard()
        self.deck.shuffle()
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        if len(self.players) == 2:
            hand_size = 7
        else:
            hand_size = 8
        for card in range(hand_size):
            for player in self.players:
                self.hands[player.name].draw()
        self.hands[self.human.name].cards.sort()
        self.hands[self.human.name].cards.sort(key = lambda card: card.suit)
        self.deck.discard(self.deck.deal())

    def game_over(self):
        """Check for the game being over. (bool)"""
        if max(self.scores.values()) > self.goal:
            scores = [(score, name) for name, score in self.scores.items()]
            scores.sort(reverse = True)
            self.human.tell('{1} won the game with {0} points.'.format(*scores[0]))
            human_score = self.scores[self.human.name]
            for name, score in self.scores.items():
                if name != self.human.name:
                    if score < human_score:
                        self.win_loss_draw[0] += 1
                    elif score > human_score:
                        self.win_loss_draw[1] += 1
                    else:
                        self.win_loss_draw[2] += 1
            return True
        else:
            return False

    def handle_options(self):
        """Handle the game options. (None)"""
        # Set the default options.
        num_players = 3
        num_smart = 0
        # Set up the players.
        self.players = [self.human]
        taken_names = [self.human.name]
        for bot in range(num_smart):
            self.players.append(C8BotSmart(taken_names))
            taken_names.append(self.players[-1].name)
        for bot in range(num_players - len(self.players)):
            self.players.append(C8Bot(taken_names))
            taken_names.append(self.players[-1].name)
        self.goal = 50 * num_players

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Get the relevant cards.
        hand = self.hands[player.name]
        discard = self.deck.discards[-1]
        # Show the game status.
        player.tell('The card to you is {}.'.format(discard.rank + discard.suit))
        if self.deck.discards[-1].rank == '8' and self.suit:
            player.tell('The suit to you is {}.'.format(self.suit))
        player.tell('Your hand is {}.'.format(hand))
        # Get and process the move.
        move = player.ask('What is your play? ')
        if move.lower() in ('d', 'draw'):
            hand.draw()
            if not self.deck.discards:
                player.tell('You drew the last card.')
                self.score()
                self.deal()
                return False
            else:
                return True
        elif move in hand.cards:
            if move[0].upper() in (discard.rank, '8') or move[1].upper() in (discard.suit, self.suit):
                hand.discard(move)
                # Handle crazy eights.
                if '8' in move:
                    while True:
                        suit = player.ask('What suit do you choose? ').upper()
                        if suit and suit[0] in 'CDHS':
                            self.suit = suit[0]
                            break
                        player.tell('Please enter a valid suit (C, D, H, or S).')
                else:
                    self.suit = ''
                if not hand.cards:
                    self.human.tell('{} played their last card.'.format(player.name))
                    self.score()
                    self.deal()
            else:
                player.tell('That is not a valid play.')
                return True
            return False
        else:
            return self.handle_cmd(move)

    def score(self):
        """Score the round's winner. (None)"""
        round_scores = {player.name: 0 for player in self.players}
        winner = ''
        low_score = 10000
        for name, hand in self.hands.items():
            for card in hand.cards:
                if card.rank == '8':
                    round_scores[name] += 50
                elif card.rank in 'TJQK':
                    round_scores[name] += 10
                elif card.rank == 'A':
                    round_scores[name] += 1
                else:
                    round_scores[name] += int(card.rank)
            if round_scores[name] < low_score:
                # !! does not track tied winners well.
                winner = name
                low_score = round_scores[name]
            self.human.tell('{} had {} points in their hand.'.format(name, round_scores[name]))
        winner_bump = 0
        for name in round_scores:
            round_scores[name] -= low_score
            winner_bump += round_scores[name]
        self.human.tell('{} scores {} points.'.format(winner, winner_bump))
        self.scores[winner] += winner_bump

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the deck.
        if len(self.players) < 6:
            self.deck = cards.Deck()
        else:
            self.deck = cards.Deck(decks = 2)
        # Deal the hands.
        self.hands = {}
        self.deal()
        # Set up the tracking variables.
        self.suit = ''
