"""
crazy_eights_game.py

A game of Crazy Eights.

Constants:
CREDITS: The credits for Crazy Eights. (str)
RULES: The rules for Crazy Eights. (str)

Classes:
C8Bot: A basic Crazy Eights bot. (player.Bot)
C8SmartBot: A smarter bot for Crazy Eights. (C8Bot)
CrazyEights: A game of Crazy Eights (game.Game)
"""


import random

import tgames.cards as cards
import tgames.game as game
import tgames.player as player
import tgames.utility as utility


# The credits for Crazy Eights.
CREDITS = """
Game Design: Traditional (Venezuela)
Game Programming: Craig "Ichabod" O'Brien
"""

# The rules for Crazy Eights.
RULES = """
Each player is dealt 8 cards, 7 in a two player game. The top card of the deck
is discarded face up. Each player in turn must discard a card face up that
matches the suit or rank of the top card on the discard pile. Any 8 may always
be played, and allows the player to pick a new suit to match. If a player 
can't (or doesn't want to) play any cards, they may draw from the deck until 
they can (or choose to) play a card.

When a player runs out of cards, the cards in all the other hands are added up
(face cards are 10, eights are 50, all other cards are face value), and the
player who ran out of cards wins. If the deck runs out of cards, the player 
with the least points in their hand scores the difference between their points
and the points in each hand. After scoring, all cards are shuffled into the
deck and the game is started again. 

The first player to get 50 points times the number of players wins the game.

Options:
one-alert: A warning is given when a player has one card.
pass: When the deck runs out players who can't play just pass their turn.
players=: The number of players in the game, counting the human. (default = 5)
reshuffle: Reshuffle the discards when the deck runs out instead of scoring.
smart=: The number of smart bots in the game. (default = 2)
"""

class C8Bot(player.Bot):
    """
    A basic Crazy Eights bot. (player.Bot)

    Attributes:
    discard: The card that was discarded. (cards.Card)
    eights: The eights that the bot has in hand. (list of cards.Card)
    hand: The bot's hand of cards. (cards.Hand)
    held_suit: The suit to switch to after playing an 8. (str)
    rank_matches: The bot's cards that match the rank to play. (list of Card)
    suit: The suit for the bot to match. (str)
    suits: The suits in hand and their counts. (list of (int, str))
    suit_matches: The bot's cards that match the suit to play. (list of Card)

    Methods:
    get_status

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
        self.get_status()
        # Playing a card.
        if prompt == 'What is your play? ':
            # Play a suit match if possible.
            if self.suit_matches:
                self.suit_matches.sort()
                card = str(self.suit_matches[-1])
            # Otherwise play a rank match.
            elif self.rank_matches:
                self.rank_suits = [card.suit for card in self.rank_matches]
                for count, suit in self.suits:
                    if suit in self.rank_suits:
                        card = self.discard.rank + suit
                        break
            # Play eights as a last resort.
            elif self.eights:
                card = str(self.eights[0])
                self.held_suit = self.suits[0][1]
            # Draw if you can't play anything.
            elif self.game.deck.cards:
                card = 'draw'
                self.game.human.tell('{} drew a card.'.format(self.name))
            else:
                card = 'pass'
            if card in self.hand.cards:
                #self.game.human.tell(self.discard, self.suit, self.hand)
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

    def get_status(self):
        """Calculate the status of the game. (None)"""
        # Get the relevant cards.
        self.discard = self.game.deck.discards[-1]
        self.hand = self.game.hands[self.name]
        # Get the current suit.
        if self.game.suit:
            self.suit = self.game.suit
        else:
            self.suit = self.discard.suit
        # Calculate the legal plays.
        self.suit_matches = [c for c in self.hand.cards if c.suit == self.suit and c.rank != '8']
        self.rank_matches = [c for c in self.hand.cards if c.rank == self.discard.rank and c.rank != '8']
        self.eights = [card for card in self.hand.cards if card.rank == '8']
        # Calculate the frequencies of suits in hand.
        self.suits = [(len([c for c in self.hand.cards if c.suit == suit]), suit) for suit in 'CDHS']
        self.suits.sort(reverse = True)
        # Get the recent plays.
        self.plays = self.game.history[-len(self.game.players):]

    def tell(self, text):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        pass


class C8SmartBot(C8Bot):
    """
    A smarter bot for Crazy Eights. (C8Bot)

    Overridden Methods:
    ask
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        self.get_status()
        # Playing a card.
        if prompt == 'What is your play? ':
            # Check for suit having been switched.
            suit_switch = self.plays[0].suit != self.suit or '8' in [card.rank for card in self.plays]
            # Get playable cards.
            maybes = [c for c in self.hand.cards if c.suit == self.suit or c.rank in (self.discard.rank, '8')]
            maybes = {card: 0 for card in maybes}
            # Calculate the value of each card (cards left in that suit + 2 if switching after another switch)
            final_card = None
            best_count = -5
            for card in maybes:
                if card.rank == '8':
                    # Penalize eights by one point to hold them until needed.
                    maybes[card] = self.suits[0][0] - 1
                    if card.suit == self.suits[0][1]:
                        maybes[card] -= 1
                    if suit_switch and self.suits[0][1] != self.suits:
                        maybes[card] += 2
                else:
                    maybes[card] = len([c for c in self.hand.cards if c.suit == card.suit]) - 1
                    if suit_switch and card.suit != self.suits:
                        maybes[card] += 2
                if maybes[card] > best_count:
                    best_count = maybes[card]
                    final_card = card
            # Make the move
            if final_card is None:
                if self.game.deck.cards:
                    self.game.human.tell('{} drew a card.'.format(self.name))
                    return 'draw'
                else:
                    return 'pass'
            else:
                self.game.human.tell('{} played the {}.'.format(self.name, final_card))
                return str(final_card)
        # Choosing a suit.
        elif prompt == 'What suit do you choose? ':
            suit = self.suits[0][1]
            self.game.human.tell('The new suit to match is {}.'.format(suit)) 
            return suit
        # Raise an error if you weren't programmed to handle the question.
        else:
            raise ValueError('Invalid prompt to C8SmartBot: {!r}'.format(prompt))


class CrazyEights(game.Game):
    """
    A game of Crazy Eights. (game.Game)

    Attributes:
    deck: The deck of cards used in the game. (cards.Deck)
    goal: The number of points needed to win the game. (int)
    hands: The player's hands. (dict of str: cards.Hand)
    history: The cards played so far. (list of cards.Card)
    one_alert: A flag for alerts when a player has one card. (bool)
    pass_count: How many players have passed in a row. (bool)
    suit: The suit called with the last eight. (str)

    Methods:
    ask_options: Get game options from the user. (None)
    deal: Deal the cards to the players. (None)
    draw: Draw a card. (bool)
    parse_options: Parse the options passed from the interface. (None)
    pass_turn: Pass the turn. (bool)
    play_card: Play a card. (bool)
    score: Score the round's winner. (None)

    Overridden Methods:
    game_over
    handle_options
    player_turn
    set_up
    """

    categories = ['Card Games', 'Shedding Games']
    credits = CREDITS
    name = 'Crazy Eights'
    rules = RULES

    def ask_options(self):
        """Get game options from the user. (None)"""
        options = self.human.ask('Would you like to change the options? ')
        if options in utility.YES:
            self.flags |= 1
            query = 'How many players should there be, including you (return for 5)? '
            num_players = self.human.ask_int(query, low = 2, default = 5, cmd = False)
            query = 'How many smart bots should there be (return for 2)? '
            max_smart = num_players - 1
            default = min(2, max_smart)
            num_smart = self.human.ask_int(query, low = 0, high = max_smart, default = default,
                cmd = False)
            answer = self.human.ask('Should there be an alert when a player is down to one card? ')
            self.one_alert = answer in utility.YES
            query = 'What should be done with an empty deck: reshuffle, score, or pass? '
            while True:
                answer = self.human.ask(query).lower()
                if not answer.strip():
                    answer = 'score'
                if answer in ('reshuffle', 'score', 'pass'):
                    self.empty_deck = answer
                    break
                self.human.tell('That is not a valid answer.')

    def deal(self, keep_one = False):
        """
        Deal the cards to the players. (None)

        Parameters:
        keep_one: A flag for keeping the top card of the discard pile. (bool)
        """
        # Keep the discard if requested.
        if keep_one:
            self.human.tell('Reshuffling the deck.')
            keeper = self.deck.discards[-1]
        else:
            # Empty the current hands.
            for hand in self.hands.values():
                hand.discard()
        # Reset and the deck.
        self.deck.shuffle()
        # Set the discard pile.
        if keep_one:
            self.deck.discards = [keeper]
            self.deck.cards.remove(keeper)
        else:
            self.deck.discard(self.deck.deal(), up = True)
            self.history.append(self.deck.discards[-1])
            self.human.tell('The starting card is the {}.'.format(self.deck.discards[-1]))
            # Determine the number of cards to deal.
            if len(self.players) == 2:
                hand_size = 7
            else:
                hand_size = 5
            # Deal the cards.
            for card in range(hand_size):
                for player in self.players:
                    self.hands[player.name].draw()
            # Sort the human's hand for readability.
            self.hands[self.human.name].cards.sort()
            self.hands[self.human.name].cards.sort(key = lambda card: card.suit)

    def draw(self, player):
        """
        Draw a card. (bool)

        Parameters:
        player: The player to draw a card for. (player.Player)
        """
        # Check for a forced pass.
        if self.empty_deck == 'pass' and not self.deck.cards:
            player.tell('You cannot draw, you must pass.')
            self.human.tell('{} passes.'.format(player.name))
            self.pass_count += 1
            if self.pass_count >= len(self.players):
                self.score()
                self.deal()
            return False
        # Draw the card.
        hand = self.hands[player.name]
        hand.draw()
        player.tell('You drew the {}.'.format(hand.cards[-1]))
        # Sort the human's cards.
        if player.name == self.human.name:
            hand.cards.sort()
            hand.cards.sort(key = lambda card: card.suit)
        # Check for empty deck.
        if not self.deck.cards:
            self.human.tell('The deck is empty.')
            if self.empty_deck == 'score':
                self.score()
            if self.empty_deck != 'pass':
                self.deal(self.empty_deck == 'reshuffle')
            return self.empty_deck != 'score'
        else:
            return True

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
        # !! refactor due to size
        # Set the default options.
        num_players = 5
        num_smart = 2
        self.one_alert = False
        self.empty_deck = 'score'
        # Check for no options.
        if self.raw_options.lower() == 'none':
            pass
        # Check for passed options.
        elif self.raw_options:
            self.flags |= 1
            self.parse_options()
        # Ask for options:
        else:
            self.ask_options()
        # Set up the players.
        self.players = [self.human]
        taken_names = [self.human.name]
        for bot in range(num_smart):
            self.players.append(C8SmartBot(taken_names))
            taken_names.append(self.players[-1].name)
        for bot in range(num_players - len(self.players)):
            self.players.append(C8Bot(taken_names))
            taken_names.append(self.players[-1].name)
        # Catch invalid num_smart.
        self.players = self.players[:num_players]
        # Set the winning score.
        self.goal = 50 * num_players

    def parse_options(self):
        """Parse the options passed from the interface. (None)"""
        for word in self.raw_options.lower().split():
            if word == 'one-alert':
                self.one_alert = True
            elif word == 'pass':
                self.empty_deck = 'pass'
            elif word == 'reshuffle':
                self.empty_deck = 'reshuffle'
            elif '=' in word:
                option, value = word.split('=')
                if option == 'players':
                    if value.isdigit():
                        num_players = max(int(value), 2)
                    else:
                        self.human.tell('Invalid value for players option: {!r}'.format(value))
                elif option == 'smart':
                    if value.isdigit():
                        num_smart = int(value)
                    else:
                        self.human.tell('Invalid value for smart option: {!r}'.format(value))
                else:
                    self.human.tell('Invalid option for Crazy Eights: {}=.'.format(option))
            else:
                self.human.tell('Invalid option for Crazy Eights: {}.'.format(word))

    def pass_turn(self, player):
        """
        Pass the turn. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Check for a valid pass.
        if not self.deck.cards and self.empty_deck == 'pass':
            self.human.tell('{} passes.'.format(player.name))
            self.pass_count += 1
            if self.pass_count >= len(self.players):
                self.score()
                self.deal()
            return False
        # Give appropriate error for invalid pass.
        elif self.empty_deck == 'pass':
            player.tell('You may not pass until the deck is empty.')
        else:
            player.tell('None shall pass.')
        return True

    def play_card(self, player, card_text):
        """
        Play a card. (bool)

        Parameters:
        player: The player playing the card. (Player)
        card_text: The card the player entered. (str)
        """
        # Get the relevant cards.
        hand = self.hands[player.name]
        discard = self.deck.discards[-1]
        # Check for valid play.
        if card_text[0].upper() in (discard.rank, '8') or card_text[1].upper() in (discard.suit, self.suit):
            hand.discard(card_text)
            self.history.append(self.deck.discards[-1])
            self.pass_count = 0
            # Handle crazy eights.
            if '8' in card_text:
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
            # Check for one card warning.
            elif self.one_alert and len(hand.cards) == 1:
                self.human.tell('{} has one card left.'.format(player.name))
        # Warn for invalid plays.
        else:
            player.tell('That is not a valid play.')
            return True
        return False

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        self.human.tell()
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
            return self.draw(player)
        # Pass
        if move.lower() in ('p', 'pass'):
            return self.pass_turn(player)
        # Play cards.
        elif move in hand.cards:
            return self.play_card(player, move)
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
        self.human.tell()
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
                # !! does not track tied winners well (that is, at all).
                winner = name
                low_score = round_scores[name]
            self.human.tell('{} had {} points in their hand.'.format(name, round_scores[name]))
        # Get score relative to lowest score and total it.
        winner_bump = 0
        for name in round_scores:
            round_scores[name] -= low_score
            winner_bump += round_scores[name]
        # Lowest score scores the relative total.
        self.human.tell('\n{} scores {} points.\n'.format(winner, winner_bump))
        self.scores[winner] += winner_bump
        for player in self.players:
            self.human.tell('{} has {} points.'.format(player.name, self.scores[player.name]))

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the deck.
        if len(self.players) < 6:
            self.deck = cards.Deck(shuffle_size = -1)
        else:
            self.deck = cards.Deck(decks = 2, shuffle_size = -1)
        # Set up the tracking variables.
        self.history = []
        self.suit = ''
        self.pass_count = 0
        # Deal the hands.
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        self.deal()
        # Randomize the players.
        random.shuffle(self.players)
