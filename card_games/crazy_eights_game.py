"""
crazy_eights_game.py

A game of Crazy Eights.

Classes:
C8Bot: A basic Crazy Eights bot. (player.Bot)
CrazyEights: A game of Crazy Eights (game.Game)
"""


import tgames.cards as cards
import tgames.game as game
import tgames.player as player


class C8Bot(player.Bot):
    """
    A basic Crazy Eights bot. (player.Bot)

    Attributes:
    held_suit: The suit to switch to after playing an 8. (str)

    Overridden Methods:
    ask
    tell
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        # Playing a card.
        if prompt == 'What is your play? ':
            # Get the relevant cards.
            discard = self.game.deck.discards[-1]
            hand = self.game.hands[self.name]
            # Get the current suit.
            if self.game.suit:
                suit = self.game.suit
            else:
                suit = discard.suit
            # Calculate the legal plays.
            suit_matches = [card for card in hand.cards if card.suit == suit and card.rank != '8']
            rank_matches = [card for card in hand.cards if card.rank == discard.rank and card.rank != '8']
            eights = [card for card in hand.cards if card.rank == '8']
            # Calculate the frequencies of suits in hand.
            suits = [(len([card for card in hand.cards if card.suit == suit]), suit) for suit in 'CDHS']
            suits.sort(reverse = True)
            # Play a suit match if possible.
            if suit_matches:
                suit_matches.sort()
                card = str(suit_matches[-1])
            # Otherwise play a rank match.
            elif rank_matches:
                rank_suits = [card.suit for card in rank_matches]
                for count, suit in suits:
                    if suit in rank_suits:
                        card = discard.rank + suit
                        break
            # Play eights as a last resort.
            elif eights:
                card = str(eights[0])
                self.held_suit = suits[0][1]
            # Draw if you can't play anything.
            else:
                card = 'draw'
                self.game.human.tell('{} drew a card.'.format(self.name))
            if card != 'draw':
                self.game.human.tell('{} played the {}.'.format(self.name, card))
            return card
        # Choosing a suit.
        elif prompt == 'What suit do you choose? ':
            suit, self.held_suit = self.held_suit, None
            self.game.human.tell('The new suit to match is {}.'.format(suit)) 
            return suit
        # Raise an error if you weren't programmed to handle the question.
        else:
            raise ValueError('Invalid prompt to C8Bot: {!r}'.format(prompt))

    def tell(self, text):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
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
    game_over
    handle_options
    player_turn
    set_up
    """

    categories = ['Card Games', 'Shedding Games']
    name = 'Crazy Eights'

    def deal(self):
        """Deal the cards to the players. (None)"""
        # Empty the current hands.
        for hand in self.hands.values():
            hand.discard()
        # Reset the hands and the deck.
        self.deck.shuffle()
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        # Determine the number of cards to deal.
        if len(self.players) == 2:
            hand_size = 7
        else:
            hand_size = 8
        # Deal the cards.
        for card in range(hand_size):
            for player in self.players:
                self.hands[player.name].draw()
        # Sort the human's hand for readability.
        self.hands[self.human.name].cards.sort()
        self.hands[self.human.name].cards.sort(key = lambda card: card.suit)
        # Discard the starting card.
        self.deck.discard(self.deck.deal())

    def game_over(self):
        """Check for the game being over. (bool)"""
        # Win if someone scored enough points.
        if max(self.scores.values()) > self.goal:
            # Find the winner.
            scores = [(score, name) for name, score in self.scores.items()]
            scores.sort(reverse = True)
            self.human.tell('{1} won the game with {0} points.'.format(*scores[0]))
            # Calculate the win/loss/draw.
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
        # Set the winning score.
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
        # Draw cards.
        if move.lower() in ('d', 'draw'):
            hand.draw()
            # Sort the human's cards.
            if player.name == self.human.name:
                hand.cards.sort()
                hand.cards.sort(key = lambda card: card.suit)
            # Check for empty deck.
            if not self.deck.discards:
                player.tell('You drew the last card.')
                self.score()
                self.deal()
                return False
            else:
                return True
        # Play cards.
        elif move in hand.cards:
            # Check for valid play.
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
                # Check for playing their last card.
                if not hand.cards:
                    self.human.tell('{} played their last card.'.format(player.name))
                    self.score()
                    self.deal()
            # Warn for invalid plays.
            else:
                player.tell('That is not a valid play.')
                return True
            return False
        # Handle other commands.
        else:
            return self.handle_cmd(move)

    def score(self):
        """Score the round's winner. (None)"""
        # Set up the loop.
        round_scores = {player.name: 0 for player in self.players}
        winner = ''
        low_score = 10000
        # Score each hand.
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
            # Track the lowest hand to find the winner.
            if round_scores[name] < low_score:
                # !! does not track tied winners well.
                winner = name
                low_score = round_scores[name]
            self.human.tell('{} had {} points in their hand.'.format(name, round_scores[name]))
        # Get score relative to lowest score and total it.
        winner_bump = 0
        for name in round_scores:
            round_scores[name] -= low_score
            winner_bump += round_scores[name]
        # Lowest score scores the relative total.
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
        # Set up the tracking variable.
        self.suit = ''
