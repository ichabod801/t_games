"""
gin_rummy_game.py

A game of Gin Rummy.

Constants:
CREDITS: The credits for Gin Rummy. (str)
RULES: The rules for Gin Rummy. (str)

Classes:
GinRummy: A game of Gin Rummy. (game.Game)
"""


import random

from .. import cards
from .. import game
from .. import player
from .. import utility


CREDITS = """
Game Design: Elwood T. Baker and C. Graham Baker
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
To be written.
"""


class GinRummy(game.Game):
    """
    A game of Gin Rummy. (game.Game)

    Attributes:
    end: The number of points that signals the end of a game. (int)
    wins: The number of hands each player has won. (dict of str: int)

    Class Attributes:
    card_values: The points per card by rank. (dict of str: int)

    Methods:
    deal: Deal the cards. (None)
    do_knock: Lay out your cards and attempt to win the hand. (bool)
    do_discard: Discard a card and end your turn. (bool)
    do_scores: Show the current scores. (bool)
    spread: Spread cards from a player's hand. (tuple of list of cards.Card)

    Overridden Methods:
    game_over
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['Gin', 'Knock Poker', 'Poker Gin', 'Gin Poker']
    aliases = {'g': 'group', 'k': 'knock', 'p': 'pass', 's': 'score'}
    card_values = dict(zip('A23456789TJQK', (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10)))
    categories = ['Card Games']
    credits = CREDITS
    name = 'Gin Rummy'
    num_options = 0
    rules = RULES

    def deal(self):
        """Deal the cards. (None)"""
        # Gather and shuffle all the cards.
        for hand in self.hands.values():
            hand.discard()
        self.deck.shuffle()
        # Deal 10 cards to each player.
        self.human.tell('\n{} deals.'.format(self.dealer.name))
        for card in range(10):
            for hand in self.hands.values():
                hand.draw()
        # Discard one card.
        self.deck.discard(self.deck.deal(), up = True)
        # Handle dibs on the first discard.
        # Non-dealer gets first chance at the discard.
        non_dealer = self.players[0] if self.players[1] == self.dealer else self.players[1]
        non_dealer.tell('Your hand is {}.'.format(self.hands[non_dealer.name]))
        query = 'Would you like the top card of the discard pile ({})? '.format(self.deck.discards[-1])
        take_discard = non_dealer.ask(query).lower()
        if take_discard in utility.YES:
            self.hands[non_dealer.name].deal(self.deck.discards.pop())
            self.player_index = self.players.index(self.dealer)
        else:
            # The dealer then gets a chance at the discard.
            self.dealer.tell('Your hand is {}.'.format(self.hands[self.dealer.name]))
            take_discard = self.dealer.ask(query).lower()
            if take_discard in utility.YES:
                self.hands[self.dealer.name].deal(self.deck.discards.pop())
                self.player_index = self.players.index(non_dealer)
            else:
                # If no one wants it, non-dealer starts with the top card off the deck.
                self.hands[non_dealer.name].draw()
                self.player_index = self.players.index(self.dealer)
        self.card_drawn = True

    def do_discard(self, argument):
        """
        Discard a card from your hand and end your turn. (d)
        """
        # Get the player info.
        player = self.players[self.player_index]
        hand = self.hands[player.name]
        # Validate the card.
        if argument in hand:
            # Discard valid cards.
            hand.discard(argument)
            self.deck.discards[-1].up = True
            return False
        else:
            # Give a warning if the card is not valid.
            player.error('You do not have that card to discard.')
            return True

    def do_group(self, arguments):
        """
        Groups the cards provided as arguments and places them at the beginning of
        your hand. (g)
        """
        # Get the player information
        player = self.players[self.player_index]
        hand = self.hands[player.name]
        # Validate the cards.
        card_text = arguments.split()
        try:
            cards = [hand.cards[hand.cards.index(card_name)] for card_name in card_text]
        except ValueError:
            player.error('You do not have all of those cards in your hand.')
            return True
        # Put the cards at the beginning of the hand.
        for card in cards:
            hand.cards.remove(card)
        hand.cards = cards + hand.cards
        return True

    def do_knock(self, argument):
        """
        Set out your cards in an attempt to win the hand. (k)
        """
        # !! needs a way to cancel out of it.
        attacker = self.players[self.player_index]
        defender = self.players[1 - self.player_index]
        # Get the attacker's discard
        while True:
            discard = attacker.ask('Which card would you like to discard? ')
            if discard in self.hands[attacker.name]:
                break
            attacker.tell('You do not have that card to discard.')
            attacker.tell('Your hand is {}.'.format(self.hands[attacker.name]))
        self.hands[attacker.name].discard(discard)
        # Spread the dealer's hand.
        attack_melds, attack_deadwood = self.spread(attacker)
        attack_score = sum([self.card_values[card.rank] for card in attack_deadwood])
        if attack_score > self.knock_min:
            attacker.error('You do not have a low enough score to knock.')
            return False
        elif attack_score:
            defense_melds, defense_deadwood = self.spread(defender, attack_melds)
        else:
            defender.tell('Gin! You may not lay off.')
            defense_melds, defense_deadwood = self.spread(defender)
        defense_score = sum([self.card_values[card.rank] for card in defense_deadwood])
        # Score the hands.
        score_diff = defense_score - attack_score
        if not attack_score:
            winner, score = attacker, 25 + score_diff
        elif score_diff > 0:
            winner, score = attacker, score_diff
        else:
            winner, score = defender, 25 - score_diff
        # Update the game score.
        self.human.tell('{} scored {} points.'.format(winner.name, score))
        self.scores[winner.name] += score
        self.wins[winner.name] += 1
        self.do_scores('')
        # Redeal.
        if self.scores[winner.name] < self.end:
            for hand in self.hands.values():
                hand.discard()
            self.dealer = winner
            self.deal()
        return False

    def do_scores(self, arguments):
        """
        Show the current game scores. (s)
        """
        current = self.players[self.player_index]
        current.tell('\nCurrent Scores:')
        for player in self.players:
            current.tell('{}: {}'.format(player.name, self.scores[player.name]))

    def game_over(self):
        """Check for end of game and calculate the final score. (bool)"""
        if max(self.scores.values()) >= self.end:
            self.human.tell('\nThe game is over.')
            # Give the ender the game bonus.
            ender = self.players[self.player_index]
            self.human.tell('{} scores 100 points for ending the game.')
            self.scores[ender.name] += 100
            # Check for a sweep bonus.
            opponent = self.players[1 - self.player_index]
            if not self.wins[opponent.name]:
                self.human.tell('{} doubles their score for sweeping the game.')
                self.scores[ender.name] *= 2
            # Give each payer 25 points for each win.
            for player in self.players:
                if self.wins[player.name]:
                    win_points = 25 * self.wins[player.name]
                    text = '{} gets {} extra points for winning {} hands.'
                    self.human.tell(text.format(player.name, win_points, self.wins[player.name]))
            # Determine the winner.
            if self.scores[ender] > self.scores[opponent]:
                winner = ender
                loser = opponent
            else:
                winner = opponent
                loser = ender
            # Reset the scores.
            for player in self.players:
                self.scores[player] -= self.scores[loser]
            # Announce the winner.
            self.human.tell('\n{} won the game by {} points.'.format(winner.name, self.scores[winner.name]))
            return True
        else:
            return False

    def handle_options(self):
        """Handle the option settings for this game. (None)"""
        self.players = [self.human, player.Cyborg(taken_names = [self.human.name])]

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # !! need to deal with the end of the deck.
        # Show the game status.
        player.tell('\nDiscard Pile: {}'.format(', '.join([str(card) for card in self.deck.discards])))
        player.tell('Your Hand: {}'.format(self.hands[player.name]))
        # Handle the player action.
        if self.card_drawn:
            # Get a move
            move = player.ask('What is your move? ').lower()
            go = self.handle_cmd(move)
            if not go:
                self.card_drawn = False
        else:
            # Draw a card.
            move = player.ask('Would like to draw from the discards or the top of the deck? ').lower()
            if move == 'discards' or move == self.deck.discards[-1]:
                self.hands[player.name].deal(self.deck.discards.pop())
            else:  # !! put in a don't understand. Currently 'discard' draws from top of deck.
                self.hands[player.name].draw()
            self.card_drawn = True
            go = True
        return go

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the cards.
        self.deck = cards.Deck()
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        self.dealer = random.choice(self.players)
        self.deal()
        # Adjust for the starting player (Game.play resets player_index after set_up runs)
        if self.player_index == 0:
            self.players.reverse()
        # Set up the tracking variables.
        self.wins = {player.name: 0 for player in self.players}
        self.end = 100
        self.knock_min = 10

    def spread(self, player, attack = []):
        """
        Spread cards from a player's hand. (tuple of list of cards.Card)

        Parameters:
        player: The player who is spreading cards. (player.Player)
        attack: The melds that were spread by the attacking player. (list of list)
        """
        # !! show the player their cards
        # Get the available cards.
        cards = self.hands[player.name].cards[:]
        # Show the attack, if any.
        if attack:
            player.tell('\nThe attacking melds: ')
            for meld in attack:
                player.tell(', '.join(str(card) for card in meld))
        # Get the melds and layoffs.
        scoring_sets = []
        while True:
            meld = player.ask('\nEnter a set of cards to score: ').split()
            # Check for no more scoring cards.
            if not meld:
                break
            # Validate cards
            if not all(card in cards for card in meld):
                player.error('You do not have all of those cards.')
            # Validate melds.
            if len(meld) >= 3:
                valid = self.validate_meld(meld)
            # Validate layoffs.
            else:
                for target in attack:
                    valid = self.validate_meld(target + meld)
                    if valid:
                        break
            # Handle the cards.
            if valid:
                # Shift cards out of the temporary hand.
                scoring_sets.append([])
                for card in meld:
                    # !! converting to card may cause problems laying off
                    scoring_sets[-1].append(cards.pop(cards.index(card)))
                if not cards:
                    break
            else:
                # Warn if the meld or layoff is invalid.
                if attack:
                    player.error('That is not a valid meld or layoff.')
                else:
                    player.error('That is not a valid meld.')
        # Return the melds and the deadwood.
        return scoring_sets, cards

    def validate_meld(self, meld):
        """
        Validate a meld entered by a user. (bool)

        Parameter:
        meld: The set of cards to validate. (list of str)
        """
        valid = False
        # Sort the cards.
        try:
            meld.sort(key = lambda card: self.deck.ranks.index(card[0].upper()))
        except IndexError:
            return False
        # Check for a set.
        if len(set(card[0].upper() for card in meld)) == 1:
            valid = True
        # Check for a run.
        elif len(set(card[1].upper() for card in meld)) == 1:
            if ''.join(card[0].upper() for card in meld) in self.deck.ranks:
                valid = True
        return valid