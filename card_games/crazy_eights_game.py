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
import tgames.options as options
import tgames.player as player
import tgames.utility as utility


# The credits for Crazy Eights.
CREDITS = """
Game Design: Traditional (Venezuela)
Game Programming: Craig "Ichabod" O'Brien
"""

# The rules for Crazy Eights.
RULES = """
Each player is dealt 5 cards, 7 in a two player game. The top card of the deck
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
change=: The rank that allows you to change suits. (default = 8)
change-match: The change suit card must match the discard's suit or rank.
change-set: The change suit card only changes to it's own suit.
draw=: The rank, typically 2, that forces the next player to draw that many 
    cards without playing any.
draw-one: A player who can't play only has to draw one card.
easy=: The number of easy bots in the game. (default = 2)
empty-deck: What to do when the deck is empty: pass (players can pass instead
    of drawing), reshuffle, or score. (default = score)
medium=: The number of medium bots in the game. (default = 2)
multi-score: Each players scores the points in the largest hand minus the
    points in their own hand.
one-alert: A warning is given when a player has one card.
one-round: Only play one round.
reverse=: The rank, typically A, that reverses the order of play.
skip=: The rank, typically Q, that skips the next player.
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
        # Avoid forced draw.
        elif prompt.endswith('(return to draw)? '):
            card = random.choice(self.rank_matches)
            self.game.human.tell('{} played the {}.'.format(self.name, card.rank + card.suit))
            return str(card)
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
        self.suit_matches = [card for card in self.hand.cards if card.suit == self.suit 
            and card.rank != self.game.change_rank]
        self.rank_matches = [card for card in self.hand.cards if card.rank == self.discard.rank 
            and card.rank != self.game.change_rank]
        self.eights = [card for card in self.hand.cards if card.rank == self.game.change_rank]
        # Check for change card matching
        if self.game.change_match and self.discard.rank != self.game.change_rank:
            self.eights = [card for card in self.eights if card.suit == self.suit]
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

        !! account for change-set. Hell account for all options.

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        self.get_status()
        # Playing a card.
        if prompt == 'What is your play? ':
            # Check for suit having been switched.
            suit_switch = self.plays[0].suit != self.suit
            suit_switch = suit_switch or self.game.change_rank in [card.rank for card in self.plays]
            # Get playable cards.
            if self.game.change_match and self.discard.rank != self.game.change_rank:
                valid_ranks = (self.discard.rank,)
            else:
                valid_ranks = (self.discard.rank, self.game.change_rank)
            maybes = [c for c in self.hand.cards if c.suit == self.suit or c.rank in valid_ranks]
            maybes = {card: 0 for card in maybes}
            # Calculate the value of each card (cards left in that suit + 2 if switching after another switch)
            final_card = None
            best_count = -5
            for card in maybes:
                if card.rank == self.game.change_rank:
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
        # Avoid forced draw.
        elif prompt.endswith('(return to draw)? '):
            card = random.choice(self.rank_matches)
            self.game.human.tell('{} played the {}.'.format(self.name, card.rank + card.suit))
            return str(card)
        # Raise an error if you weren't programmed to handle the question.
        else:
            raise ValueError('Invalid prompt to C8SmartBot: {!r}'.format(prompt))


class CrazyEights(game.Game):
    """
    A game of Crazy Eights. (game.Game)

    Attributes:
    change_match: A flag for the change card having to match suit or rank. (bool)
    change_set: A flag for the change chard only changing to it's own suit. (bool)
    deck: The deck of cards used in the game. (cards.Deck)
    draw_one: A flag for only having to draw one card when unable to play. (bool)
    draw_rank: The rank that forces a player to draw. (str)
    forced_draw: A flag for the next player being forced to draw cards. (bool)
    goal: The number of points needed to win the game. (int)
    hands: The player's hands. (dict of str: cards.Hand)
    history: The cards played so far. (list of cards.Card)
    multi-score: A flag for almost everyone scoring each round. (bool)
    num_players: The number of players requested. (int)
    num_smart: The number of smart bots requested. (int)
    one_alert: A flag for alerts when a player has one card. (bool)
    pass_count: How many players have passed in a row. (bool)
    reverse_rank: The rank that reverses the order of play. (str)
    skip_rank: The rank that skips the next player. (str)
    suit: The suit called with the last eight. (str)

    Methods:
    ask_options: Get game options from the user. (None)
    deal: Deal the cards to the players. (None)
    draw: Draw a card. (bool)
    force_draw: Draw extra cards due to special rank of previous play. (bool)
    parse_options: Parse the options passed from the interface. (None)
    pass_turn: Pass the turn. (bool)
    score: Score the round's winner. (None)
    validate_card: Validate a card to play. (bool)

    Overridden Methods:
    game_over
    handle_options
    player_turn
    set_up
    """

    aka = ['Rockaway', 'Swedish Rummy']
    categories = ['Card Games', 'Shedding Games']
    credits = CREDITS
    name = 'Crazy Eights'
    num_options = 14
    rules = RULES

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
        self.forced_draw = 0
        # Set the discard pile.
        if keep_one:
            self.deck.discards = [keeper]
            self.deck.cards.remove(keeper)
        else:
            self.deck.discard(self.deck.deal(), up = True)
            self.history.append(self.deck.discards[-1])
            self.human.tell('\nThe starting card is the {}.'.format(self.deck.discards[-1]))
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
            return not self.draw_one

    def force_draw(self, player):
        """
        Draw extra cards due to special rank of previous play. (bool)

        Parameters:
        player: The player to draw a card for. (player.Player)
        """
        # Check the hand for playable cards.
        hand = self.hands[player.name]
        playable = [card for card in hand.cards if card.rank == self.draw_rank]
        # Check for chance to play.
        if not playable:
            player.tell('You must draw {} cards.'.format(self.forced_draw))
            if not self.deck.cards:
                player.tell('There are no cards to draw so you must pass.')
                return self.pass_turn(player)
        if playable:
            player.tell('You must play a {} or draw {} cards.'.format(self.draw_rank, self.forced_draw))
            query = 'Which {} would you like to play (return to draw)? '.format(self.draw_rank)
            while True:
                play = player.ask(query)
                if not play or play.lower() in ('d', 'draw'):
                    break
                elif play in hand.cards:
                    self.play_card(player, play)
                    return False
                else:
                    message = 'That is not a valid play. Please draw or play a {}.'
                    player.tell(message.format(self.draw_rank))
        # Draw the cards.
        if self.deck.cards:
            for card in range(self.forced_draw):
                hand.draw()
                self.forced_draw = 0
                self.human.tell('{} drew a card.'.format(player.name))
                if not self.deck.cards:
                    self.human.tell('The deck is empty.')
                    if self.empty_deck == 'score':
                        self.score()
                    if self.empty_deck != 'pass':
                        self.deal(self.empty_deck == 'reshuffle')
                    if self.empty_deck != 'reshuffle':
                        return False
        # Sort the human's cards.
        if player.name == self.human.name:
            hand.cards.sort()
            hand.cards.sort(key = lambda card: card.suit)
        return False

    def game_over(self):
        """Check for the game being over. (bool)"""
        # Win if someone scored enough points.
        if max(self.scores.values()) >= self.goal:
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
        super(CrazyEights, self).handle_options()
        # Set up the players.
        self.players = [self.human]
        taken_names = [self.human.name]
        if not self.num_easy + self.num_medium:
            self.num_medium = 10 # !! switch this to num_hard when a hard bot is available.
        for bot in range(self.num_easy):
            self.players.append(C8Bot(taken_names))
            taken_names.append(self.players[-1].name)
        for bot in range(self.num_medium):
            self.players.append(C8SmartBot(taken_names))
            taken_names.append(self.players[-1].name)
        # Set the winning score.
        if not self.goal:
            self.goal = 50 * len(self.players)

    def set_options(self):
        """Define the options for the game. (None)"""
        self.option_set.add_option('one-alert', 
            question = 'Should there be an alert when a player has only one card left? bool')
        self.option_set.add_option('empty-deck', [], options.lower, default = 'score',
            valid = ('pass', 'reshuffle', 'score'),
            question = 'What should be done when the deck is empty (return for score)? ',
            error_text = 'Valid responses are pass, reshuffle, or score.')
        self.option_set.add_option('change-match',
            question = 'Should the suit change card have to match the last card played? bool')
        self.option_set.add_option('change-set',
            question = 'Should the suit change card just change to its own suit? bool')
        self.option_set.add_option('one-round', target = 'goal', value = 1, default = 0,
            question = 'Should the game end after one round? bool')
        self.option_set.add_option('multi-score',
            question = 'Should everyone but the player with the highest hand score each time? bool')
        self.option_set.add_option('draw-one',
            question = 'Should you only have to draw one card if you cannot play a card? ')
        self.option_set.add_option('easy', [], int, 2, valid = range(10), target = 'num_easy',
            question = 'How many easy bots should there be (return for 2)? ')
        self.option_set.add_option('medium', [], int, 2, valid = range(10), target = 'num_medium',
            question = 'How many medium bots should there be (return for 2)? ')
        rank_error = 'The valid card ranks are {}.'.format(', '.join(cards.Card.ranks))
        self.option_set.add_option('change', [], options.upper, '8', valid = cards.Card.ranks,
            question = 'What rank should change the suit? ', error_text = rank_error, 
            target = 'change_rank')
        self.option_set.add_option('draw', [], options.upper, '', valid = cards.Card.ranks,
            question = 'What rank should force the next player to draw? ', error_text = rank_error,
            target = 'draw_rank')
        self.option_set.add_option('reverse', [], options.upper, '', valid = cards.Card.ranks,
            question = 'What rank should reverse the order of play? ', error_text = rank_error,
            target = 'reverse_rank')
        self.option_set.add_option('skip', [], options.upper, '', valid = cards.Card.ranks,
            question = 'What rank should skip the next player? ', error_text = rank_error,
            target = 'skip_rank')

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
        player: The player whose turn it is. (Player)
        card_text: The card to play. (str)
        """
        # Play the card.
        hand = self.hands[player.name]
        hand.discard(card_text)
        # Update the tracking variables.
        self.history.append(self.deck.discards[-1])
        self.pass_count = 0
        # Handle crazy eights.
        if self.change_rank in card_text.upper() and not self.change_set:
            while True:
                suit = player.ask('What suit do you choose? ').upper()
                if suit and suit[0] in 'CDHS':
                    self.suit = suit[0]
                    break
                player.tell('Please enter a valid suit (C, D, H, or S).')
        else:
            self.suit = ''
        # Handle forced draws.
        if self.draw_rank and self.draw_rank in card_text.upper():
            self.forced_draw += cards.Card.ranks.index(card_text[0].upper())
        # Check for reversing the order of play.
        if card_text[0].upper() == self.reverse_rank:
            self.players.reverse()
            self.player_index = self.players.index(player)
        # Check for skipping players.
        if card_text[0].upper() == self.skip_rank:
            self.player_index = (self.player_index + 1) % len(self.players)
        # Check for playing their last card.
        if not hand.cards:
            self.human.tell('{} played their last card.'.format(player.name))
            self.score()
            self.deal()
            self.forced_draw = 0
        # Check for one card warning.
        elif self.one_alert and len(hand.cards) == 1:
            self.human.tell('{} has one card left.'.format(player.name))

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
        if self.deck.discards[-1].rank == self.change_rank and self.suit:
            player.tell('The suit to you is {}.'.format(self.suit))
        player.tell('Your hand is {}.'.format(hand))
        # Check for forced draw.
        if self.forced_draw:
            return self.force_draw(player)
        # Get and process the move.
        move = player.ask('What is your play? ')
        # Draw cards.
        if move.lower() in ('d', 'draw'):
            return self.draw(player)
        # Pass
        elif move.lower() in ('p', 'pass'):
            return self.pass_turn(player)
        # Play cards.
        elif move in hand.cards:
            return self.validate_card(player, move)
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
                if card.rank == self.change_rank:
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
        if self.multi_score:
            self.human.tell()
            # Get the max score.
            max_score = max(round_scores.values())
            for name, score in round_scores.items():
                indy_score = max_score - score
                self.scores[name] += indy_score
                self.human.tell('{} scores {} points.'.format(name, indy_score))
            self.human.tell()
        else:
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
        self.forced_draw = 0
        # Deal the hands.
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        self.deal()
        # Randomize the players.
        random.shuffle(self.players)

    def validate_card(self, player, card_text):
        """
        Validate a card to play. (bool)

        Parameters:
        player: The player playing the card. (Player)
        card_text: The card the player entered. (str)
        """
        # Get the relevant cards.
        hand = self.hands[player.name]
        discard = self.deck.discards[-1]
        # Check for valid play.
        if self.change_match:
            valid_ranks = (discard.rank,)
        else:
            valid_ranks = (discard.rank, self.change_rank)
        if self.suit:
            valid_suit = self.suit
        else:
            valid_suit = discard.suit
        if card_text[0].upper() in valid_ranks or card_text[1].upper() in valid_suit:
            self.play_card(player, card_text)
        # Warn for invalid plays.
        else:
            player.tell('That is not a valid play.')
            return True
        return False

if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    crazy_eights = CrazyEights(player.Player(name), 'change-match')
    crazy_eights.play()