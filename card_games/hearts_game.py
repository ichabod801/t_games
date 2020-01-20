"""
hearts_game.py

A game of Hearts.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
ACE_HIGH_RANKS: The ranks for when aces are high in Hearts. (cards.FeatureSet)
CREDITS: The credits for Hearts. (str)
FACE_RANKS: The ranks for 'face' scoring in Hearts. (cards.FeatureSet)
HEART_SUITS: The suits (and suit values) for Hearts. (cards.FeatureSet)
OPTIONS: The options for Hearts. (str)
PIP_RANKS: The ranks for 'pip' scoring in Hearts. (cards.FeatureSet)
RANK_RANKS: The ranks for 'rank' scoring in Hearts. (cards.FeatureSet)
RULES: The rules to Hearts. (str)

Classes:
HeartBot: A simple bot for Hearts. (player.Bot)
SmeartBot: A bot for Hearts that understands shooting the Moon. (HeartBot)
Hearts: A game of Hearts. (game.Game)
"""


import collections
import itertools
import random
import re

from .. import cards
from .. import game
from .. import player
from .. import utility


ACE_HIGH_RANKS = cards.FeatureSet('X23456789TJQKA',
    ['Joker', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack',
        'Queen', 'King', 'Ace'],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    skip = 1, an_chars = 'A8')

CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

FACE_RANKS = cards.FeatureSet('X23456789TJQKA',
    ['Joker', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack',
        'Queen', 'King', 'Ace'],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 4, 5],
    skip = 1, an_chars = 'A8')

HEARTS_SUITS = cards.FeatureSet('CDHS', ['Clubs', 'Diamonds', 'Hearts', 'Spades'], [0, 0, 1, 0],
    colors = 'RRBB')

OPTIONS = """
all-break (ab): Hearts may not lead a trick before a penalty card has been
    played.
bonus= (b=): The card (usually the JD) that removes up to 10 points from your
    score. The points are removed from the current hand score, and cannot
    make your hand score negative.
break-hearts (bh): Hearts may not lead a trick before a heart has been played.
easy= (ez=): The number of easy bots to play against.
end= (e=): The points one players needs to stop the game, defaults to 100.
extras= (x=): How do deal with extra cards where there are not four players.
    Valid settings are:
    ditch (d): Ditch low cards from Clubs and Diamonds to even out hands.
    first (f): The extra cards form a kitty that goes to the winner of the
        first trick.
    heart (h): The extra cards form a kitty that goes to the winner of the
        first heart.
    jokers (j): Jokers are added to the deck to even out the hands.
gonzo: Equivalent to 'bonus = jd break-hearts heart-score = face low-club
    no-tricks = 5 pass-dir = rot-left'. b=jd bh hs=f lc nt=5 pd=@
heart-score= (hs=): How hearts are scored. Valid setting are:
    face (f): Hearts score 1, face cards score more: J = 2, Q = 3, K = 4, A =5.
    one (o): Hearts score one point each.
    pips (p): Hearts score the number of pips on them, face cards and the ace
        score 10 points.
    rank (r): Hearts score their rank in points, with J = 11, Q = 12, K = 13,
        and A = 14.
jokers-follow (jf): Jokers may not lead tricks.
joker-points (jp): Jokers score one point each.
lady-score= (lp=): The points scored for the QS. Defaults to 13, sometimes it
    is 0 or 25.
low-club (lc): The player with the lowest club in the deck (typically 2C) must
    start the first trick of each hand.
keep-spades: Players may not pass the Queen, King, or Ace of Spades.
medium= (md=): The number of medium hard bots to play against.
moon= (m=): How shooting the Moon is scored. Valid settings are:
    old (o): Every player that didn't shoot gains 26 points.
    new (n): The shooting player loses 26 points.
    auto (a): 'Old' unless that would end the game, in which case 'new'.
no-tricks= (nt=): The number of points taken off if a player wins no tricks.
num-pass= (np=): The number of cards passed.
pass-dir= (pd=): The direction in which cards are passed. Valid settings are:
    central (c): Everyone passes to the center. The cards are reshuffled and
        dealt back to the players.
    dealer (d): Dealer's choice.
    left (l): Pass to the left.
    left-right (lr): Alternate passing to the left and right.
    lran: Cards are passed left, then right, then across, then there is a round
        without passing. Rinse and repeat.
    not (n): Cards are not passed at all.
    right (r): Pass to the right (the default).
    right-left (rl): Alternate passing to the right and left.
    rot-left (@): Each round pass to the left of the player you passed to last
        round. Start to the left, and when passing to yourself just don't pass.
    scatter (s): Each player passes one other card to each other player.
"""

PIP_RANKS = cards.FeatureSet('X23456789TJQKA',
    ['Joker', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack',
        'Queen', 'King', 'Ace'],
    [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 10],
    skip = 1, an_chars = 'A8')

RANK_RANKS = cards.FeatureSet('X23456789TJQKA',
    ['Joker', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack',
        'Queen', 'King', 'Ace'],
    [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    skip = 1, an_chars = 'A8')

RULES = """
In the standard four player game, 13 cards are dealt to each player. Each
player chooses three cards to pass to their right, and recieves three cards
from their left.

The player to the left of the dealer starts by playing a card. Each player in
turn must play a card, matching the suit of the first card if they can. Whoever
plays the highest card in the suit of the first card (the suit led) wins the
trick and all of the cards.

When all the cards are played the round is scored. Each heart won in a trick
scores one point, and the Queen of Spades scores 13 points. Note that points
are bad: you want to have a low score. Cards that give points are called
penalty cards. If one player manages to get all of the penalty cards, they
shoot the Moon. Instead of getting 26 points, they get no points and every
other player gets 26 points.

After scoring the round, the deal shifts to the left, and a new hand is dealt.
The game ends when anyone's score goes over 100 points. Whoever has the least
points at that time wins the game.

You can use the scores command to see the current game score for each player,
and you can use the taken command to see the cards you have taken so far in
the current deal.
"""


class HeartBot(player.Bot):
    """
    A simple bot for Hearts. (player.Bot)

    Attribute:
    hand: The player's cards in the game. (cards.Hand)

    Methods:
    follow: Play a card to an existing trick. (cards.Card)
    lead: Play a card to start a new trick. (cards.Card)
    pass_cards: Determine which cards to pass. (list of cards.Card)
    pass_count: Determine how many cards to pass with dealer's choice. (int)
    pass_direction: Determine which direction to pass w/ dealer's choice. (str)
    play: Play a card to start or add to a trick. (card.Card)

    Overridden Methods:
    ask
    ask_int
    set_up
    tell
    """

    def ask(self, prompt):
        """
        Get a response from the bot. (str)

        Parameters:
        prompt: The question to ask the bot. (str)
        """
        # Handle passing.
        if 'want to pass' in prompt:
            return ' '.join(str(card) for card in self.pass_cards())
        # Handle dealer's choice of pass direction.
        elif prompt.startswith('What direction'):
            return self.pass_direction()
        # Handle everything else.
        else:
            return super(HeartBot, self).ask(prompt)

    def ask_card(self, prompt, valid = [], default = None, cmd = True):
        """
        Get a card from the player. (cards.Card)

        Parameters:
        prompt: The question asking for the card. (str)
        valid: The valid values for the card. (container of int)
        default: The default choice. (cards.Card or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        # Handle passing cards.
        if prompt.startswith('What is'):
            return self.play()
        # Handle everything else.
        else:
            return super(HeartBot, self).ask(prompt)

    def ask_int(self, prompt, low = None, high = None, valid = [], default = None, cmd = True):
        """
        Get an integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (int or None)
        high: The highest acceptable value for the integer. (int or None)
        valid: The valid values for the integer. (container of int)
        default: The default choice. (int or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        if prompt.startswith('How many cards'):
            self.hand = self.game.hands[self]  # This may be asked during game setup, before bot setup.
            return self.pass_count(low, high)
        else:
            return super(HeartBot, self).ask(prompt)

    def follow(self):
        """Play a card to an existing trick. (str)"""
        # Get the cards matching the suit led.
        trick_starter = self.game.trick[0]
        trick_cards = self.game.trick.find(suit = trick_starter.suit)
        trick_max = sorted(trick_cards, key = cards.by_rank)[-1]
        point_cards = [card for card in self.game.trick if card.value > 0]
        if self.game.joker_points:
            point_cards.extend(self.game.trick.find(rank = 'X'))
        last_player = len(self.game.trick) + 1 == len(self.game.players)
        playable = self.hand.find(suit = trick_starter.suit)
        if playable:
            # Get the playable cards that lose.
            playable.sort(key = cards.by_rank)
            losers = [card for card in playable if card.rank_num < trick_max.rank_num]
            # Play the highest possible loser, or the lowest possible card in hopes of losing.
            if self.game.random_move:
                card = random.choice(playable)
            elif losers and 'QS' in losers:
                card = 'QS'
            elif losers and last_player and not point_cards:
                card = playable[-1]
                if card == 'QS' and len(playable) > 1:
                    card = playable[-2]
            elif losers:
                card = losers[-1]
            elif last_player:
                card = playable[-1]
                if card == 'QS' and len(playable) > 1:
                    card = playable[-2]
            elif playable[0] == 'QS' and len(playable) > 1:
                card = playable[1]
            else:
                card = playable[0]
        else:
            # Check for random play.
            if self.game.random_move:
                card = random.choice(self.hand.cards)
            # Get rid of the queen if you can.
            elif 'QS' in self.hand:
                card = 'QS'
            # Otherwise get rid of hearts if you can.
            else:
                hearts = [card for card in self.hand if card.suit == 'H']
                hearts.sort(key = cards.by_rank)
                if hearts:
                    card = hearts[-1]
                else:
                    # If you have no penalty cards, get rid of the highest card you can.
                    card = sorted(self.hand, key = cards.by_rank)[-1]
        return card

    def lead(self):
        """Play a card to start a trick. (cards.Card)"""
        # Open with the lowest card you have in the hopes of losing.
        self.hand.sort(key = cards.by_rank)
        play_index = 0
        card = self.hand[play_index]
        # Don't lead with jokers if it's banned.
        while self.game.jokers_follow and card.rank == 'X':
            play_index += 1
            card = self.hand[play_index]
        # Don't lead with hearts if they're not broken.
        while not self.game.hearts_broken and card.suit == 'H':
            play_index += 1
            card = self.hand[play_index]
        # Avoid leading the QS.
        if card == 'QS' and play_index < len(self.hand) - 1:
            card = self.hand[play_index + 1]
        return card

    def pass_cards(self):
        """Determine which cards to pass. (list of card.Card)"""
        # Get rid of high spades.
        if self.game.keep_spades:
            to_pass = []
        else:
            to_pass = self.hand.find(regex = '[QKA]S')
        # Get rid of high hearts
        hearts = self.hand.find(suit = 'H')
        hearts.sort(key = cards.by_rank, reverse = True)
        to_pass.extend(hearts)
        # If that's not enough, get rid of other high cards.
        if len(to_pass) < self.game.num_pass:
            other = [card for card in self.hand if card not in to_pass]
            if self.game.keep_spades:
                other = [card for card in other if card not in ('QS', 'KS', 'AS')]
            other.sort(key = cards.by_rank, reverse = True)
            to_pass.extend(other)
        return to_pass[:self.game.num_pass]

    def pass_count(self, low, high):
        """
        Determine how many cards to pass with dealer's choice. (int)

        Parameters:
        low: The lowest acceptable value for the integer. (int or None)
        high: The highest acceptable value for the integer. (int or None)
        """
        # Pass just enough to get rid of the nasty cards.
        high_hearts = len([card for card in self.hand if card.suit == 'H' and card.rank_num > 10])
        high_spades = len([card for card in self.hand if card.suit == 'S' and card.rank_num > 11])
        return max(low, min(high, high_hearts + high_spades))

    def pass_direction(self):
        """Determine which direction to pass cards with dealer's choice. (str)"""
        # Who cares, pass randomly.
        return random.choice(('left', 'right', 'across'))

    def play(self):
        """Play a card to start or add to a trick. (card.Card)"""
        # Handle continuing a trick.
        if self.game.trick:
            return self.follow()
        else:
            return self.lead()

    def set_up(self):
        """Set up the bot. (None)"""
        # Create a shortcut to your hand for easier programming.
        self.hand = self.game.hands[self]

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        # Mute.
        pass


class SmeartBot(HeartBot):
    """
    A bot for Hearts that understands shooting the Moon. (HeartBot)

    Attributes:
    got_points: Which players have score points this deal. (dict of str: int)
    shooter: The name of the player trying to shoot the moon. (str)
    strategy: The strategy the bot is usingto make moves. (str)
    tricks: The number of tricks played this deal. (int)

    Class Attributes:
    danger_cards: Cards that signal trying to shoot the moon. (list of str)

    Methods:
    defend: Make a move to stop a player from shooting the moon. (cards.Card)
    set_tracking: Set up the tracking variables for a new deal. (None)
    shoot: Make a move trying to shoot the moon. (cards.Card)
    strategy_check: See if the bot's strategy needs revision. (None)

    Overridden Methods:
    pass_cards
    play
    set_up
    """

    danger_cards = ('QH', 'KH', 'AH', 'QS', 'KS', 'AS')

    def defend(self):
        """Make a move to stop a player from shooting the moon. (cards.Card)"""
        standard = super(SmeartBot, self).play()
        if isinstance(standard, str):
            standard = cards.Card(*standard)
            standard.up = True
        base_check = standard.suit == 'H' or standard in self.danger_cards
        if base_check or (self.game.joker_points and standard.rank == 'X'):
            suit_cards = self.game.trick.find(suit = self.game.trick[0].suit)
            suit_cards.sort(key = cards.by_rank)
            if not suit_cards:
                return standard
            best_card = suit_cards[-1]
            best_index = self.game.trick.index(best_card)
            best_player = self.game.players[self.game.player_index - len(self.game.trick) + best_index]
            self.hand.sort(key = cards.by_rank)
            if best_player.name == self.shooter:
                playable = self.hand.find(suit = self.game.trick[0].suit)
                if playable:
                    winners = [card for card in playable if card.rank_num > best_card.rank_num]
                    if winners:
                        return winners[0]
                    elif playable[0].suit == 'X':
                        return playable[1]
                    else:
                        return playable[0]
                else:
                    non_points = [card for card in self.hand if card.value == 0]
                    if self.game.joker_points:
                        non_points = [card for card in non_points if card.rank != 'X']
                    if non_points:
                        return non_points[0]
                    else:
                        return self.hand.cards[0]
            else:
                return standard
        else:
            return standard

    def pass_cards(self):
        """
        Determine which cards to pass. (list of card.Card)

        Based on strategy tips from viphearts.com.
        """
        self.set_tracking()
        by_suit = collections.Counter(card.suit for card in self.hand)
        if len(set(['QS', 'KS', 'AS', 'KH', 'AH']).intersection(self.hand)) >= 4:
            if ('QH' in self.hand and by_suit['H'] > 4) or by_suit['H'] > 5:
                self.strategy = 'shoot'
                to_pass = self.hand[:]
                to_pass.sort(key = lambda card: card.rank_num + 2 * (card.suit in ('HS')))
        if self.strategy == 'standard':
            to_pass = []
            # Don't pass spades unless you have high ones and few spades.
            high_spades = set(['QS', 'KS', 'AS']).intersection(self.hand)
            low_spades = [card for card in self.hand if card.suit == 'S' and card.rank_num < 12]
            if high_spades and len(low_spades) < 3:
                to_pass.extend(high_spades)
            # Don't pass the ace of hearts, but pass other high hearts if you have few low hearts.
            high_hearts = set(['JH', 'QH', 'KH']).intersection(self.hand)
            low_hearts = set(char + 'H' for char in '234567').intersection(self.hand)
            if high_hearts and len(low_hearts) < 3:
                to_pass.extend(high_hearts)
            # Pass the low club if it's the starter card.
            if self.game.low_club and self.game.low_club in self.hand:
                to_pass.append(self.game.low_club)
            # Always pass QS to your right.
            if self.game.this_pass == 'right' and 'QS' in self.hand and 'QS' not in to_pass:
                to_pass.append('QS')
            # Watch out for the keep-spades option.
            if self.game.keep_spades:
                to_pass = [card for card in to_pass if card not in ('QS', 'KS', 'AS')]
            # Never pass QS to you left.
            if self.game.this_pass == 'left' and 'QS' in to_pass and len(to_pass) > self.game.num_pass:
                to_pass.remove('QS')
            # Never pass safe suit aces.
            if 'AC' in to_pass and len(to_pass) > self.game.num_pass:
                to_pass.remove('AC')
            if 'AD' in to_pass and len(to_pass) > self.game.num_pass:
                to_pass.remove('AD')
            # Fill out the cards to pass.
            if len(to_pass) < self.game.num_pass:
                if by_suit['C'] < by_suit['D'] and not self.game.low_club:
                    suits = 'CD'
                else:
                    suits = 'DC'
                to_pass.extend(card for card in self.hand if card.suit == suits[0] and card not in to_pass)
                to_pass.extend(card for card in self.hand if card.suit == suits[1] and card not in to_pass)
                if len(to_pass) < self.game.num_pass:
                    to_pass.extend(card for card in self.hand if card.suit == 'S' and card not in to_pass)
                    if self.game.keep_spades:
                        to_pass = [card for card in to_pass if card not in ('QS', 'KS', 'AS')]
                    if len(to_pass) < self.game.num_pass:
                        to_pass.extend(card for card in self.hand if card.suit == 'H')
            # Remove duplicates while maintaining order.
            new_pass = []
            for card in to_pass:
                if card not in new_pass:
                    new_pass.append(card)
            to_pass = new_pass
            # Check for valid pass.
            if len(to_pass) < self.game.num_pass:
                raise player.BotError('Invalid pass ({}) with hand = {}.'.format(to_pass, self.hand))
        return to_pass[:self.game.num_pass]

    def play(self):
        """Play a card to a trick. (cards.Card)"""
        self.strategy_check()
        if self.strategy == 'standard' or self.game.random_move:
            return super(SmeartBot, self).play()
        elif self.strategy == 'shoot':
            return self.shoot()
        else:
            return self.defend()

    def set_tracking(self):
        """Set up the tracking variables for a new deal. (None)"""
        self.strategy = 'standard'
        self.got_points = {player.name: False for player in self.game.players}
        self.tricks = 0
        self.shooter = ''

    def set_up(self):
        """Get the bot ready to play. (None)"""
        super(SmeartBot, self).set_up()
        self.set_tracking()

    def shoot(self):
        """Make a move trying to shoot the moon. (cards.Card)"""
        self.hand.cards.sort(key = cards.by_rank)
        if self.game.trick:
            # Try to win the trick.
            matching = [card for card in self.hand if card.suit == self.game.trick[0].suit]
            if matching:
                return matching[-1]
            else:
                # If you can't win the trick, lose without giving points while maintaining high cards.
                not_hearts = [card for card in self.hand if card.suit != 'H']
                if not_hearts:
                    return not_hearts[0]
                else:
                    # If you must play a heart, switch back to a standard strategy.
                    self.strategy = 'standard'
                    return self.hand.cards[-1]
        else:
            # Lead to win the trick.
            return self.hand.cards[-1]

    def strategy_check(self):
        """See if the bot's strategy needs revision. (None)"""
        # Update the tracking variables.
        self.tricks += 1
        if self.game.last_trick:
            # Get the points from the last trick.
            last_penalties = [card for card in self.game.last_trick if card.suit == 'H']
            if self.game.joker_points:
                last_penalties.extend([card for card in self.game.last_trick if card.rank == 'X'])
            # Update who has scored points.
            if last_penalties or 'QS' in self.game.last_trick:
                self.got_points[self.game.last_winner.name] = True
        # Look for signs of someone trying to shoot (leading a high card early).
        if self.strategy == 'standard':
            if self.game.trick and self.game.trick[0] in self.danger_cards and self.tricks < 5:
                self.strategy = 'defend'
                self.shooter = self.game.players[self.game.player_index - len(self.game.trick)].name
        # Go back to avoidance if more than one person has points.
        if self.strategy in ('defend', 'shoot'):
            if sum(self.got_points.values()) > 1:
                self.strategy = 'standard'


class Hearts(game.Game):
    """
    A game of Hearts. (game.Game)

    Attributes:
    all_break: A flag for any penalty card breaking hearts. (bool)
    bonus: The card that removes 10 points from a player's score. (cards.Card)
    break_hearts: A flag for hearts needing to be played before leading. (bool)
    breakers: The cards that can break hearts. (set of cards.Card)
    dealer: The next player to deal cards. (player.Player)
    deck: The deck of cards used in the game. (cards.Deck)
    easy: The number of easy bots in the game. (int)
    end: How many points end the game. (int)
    extras: How to handle extra cards in the deck. (str)
    hands: The players' hands of cards. (dict of str: cards.Hand)
    heart_score: How the hearts should be scored. (str)
    heart_points: The points scored by each rank of hearts. (dict of str: int)
    hearts_broken: A flag that hearts can lead. (bool)
    jokers_follow: A flag for jokers being unable to lead tricks. (bool)
    joker_points: A flag for jokers being worth a point. (bool)
    keep_spades: A flag preventing the passing of high spades. (bool)
    kitty: How extra cards are handled during the deal. (str)
    lady_points: How many points the QS scores. (int)
    last_trick: The last trick won by a player. (cards.Hand)
    low_club: The club that must lead each round. (cards.Card or False)
    max_score: The maximum possible score for a hand. (int)
    medium: The number of medium hard bots in the game. (int)
    moon: How shooting the moon is scored. (str)
    no_tricks: How many points you get for not winning any tricks. (int)
    not_warning: A flag for warning that there is no passing this trick. (bool)
    num_pass: The number of cards each player passes. (int)
    pass_dir: The direction(s) that cards are passed. (generator)
    pass_to: Who is passing to who. (dict of str: str)
    passes: The cards passed by each player. (dict of str: cards.Hand)
    phase: Whether the players are passing cards or playing tricks. (str)
    random_move: A flag for the rest of the trick being played randomly. (bool)
    taken: The cards from the tricks each player has taken. (dict)
    this_pass: How cards are passed this hand. (str)
    trick: The cards in the current trick. (cards.Hand)
    tricks: The number of trick played so far. (int)
    this_pass: Then direction to pass cards for this hand. (str)

    Class Attributes:
    card_re: A regular expression detecting cards. (re.SRE_Pattern)
    pass_aliases: Aliases of pass-dir option settings. (dict of str: str)
    pass_dirs: The directions to pass for pass-dire settings. (dict)

    Methods:
    deal: Deal the cards to the players. (None)
    dealers_choice: Generator for dealer's choice of passing. (generator)
    do_pass: Pass one or more cards to another player. (bool)
    do_play: Play a card, to either start or contribute to a trick. (bool)
    do_scores: Show the current scores in the game. (s)
    do_taken: View the cards you have taken so far this deal. (t)
    handle_opt_player: Handle the player option settings for this game. (None)
    handle_opt_deal: Handle the deal option settings for this game. (None)
    handle_opt_pass: Handle the passing option settings for this game. (None)
    handle_opt_play: Handle the play option settings for this game. (None)
    handle_opt_player: Handle the player option settings for this game. (None)
    handle_opt_score: Handle the scoring option settings for this game. (None)
    pass_cards: Handle the actual passing of the cards between players. (None)
    score_players: Score each player's hand. (dict, str)
    score_round: Score one deck's worth of tricks. (None)
    set_dealer: Determine the first dealer for the game. (None)
    set_pass: Set up the passing of cards for this hand. (None)
    trick_winner: Determine who won the trick. (None)

    Overridden Methods:
    game_over
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['Black Lady', 'Black Maria', 'Black Widow', '<3']
    aliases = {'p': 'play'}
    card_re = re.compile(r'\s*[x123456789tjqka][cdhs]\s*', re.IGNORECASE)
    categories = ['Card Games']
    credits = CREDITS
    name = 'Hearts'
    num_options = 16
    options = OPTIONS
    pass_aliases = {'l': 'left', 'r': 'right', 'rl': 'right-left', 'lr': 'left-right', '@': 'rot-left',
        'c': 'central', 'd': 'dealer', 'n': 'not', 's': 'scatter'}
    pass_dirs = {'left': ('left',), 'right': ('right',), 'left-right': ('left', 'right'),
        'right-left': ('right', 'left'), 'rot-left': (), 'central': ('center',), 'dealer': (),
        'not': ('not',), 'lran': ('left', 'right', 'across', 'not'), 'scatter': ('scatter',)}
    rules = RULES

    def deal(self):
        """Deal the cards to the players. (None)"""
        # Deal the cards out equally, leaving any extras aside.
        self.deck.shuffle()
        player_index = (self.players.index(self.dealer) + 1) % len(self.players)
        for player in itertools.cycle(self.players[player_index:] + self.players[:player_index]):
            self.hands[player].draw()
            if player == self.dealer and len(self.deck) < len(self.players):
                break
        for hand in self.hands.values():
            hand.sort()
        self.human.tell('{} deals.'.format(self.dealer))
        # Eldest hand starts, and is the next dealer.
        self.dealer = self.players[player_index]
        self.hearts_broken = not (self.break_hearts or self.all_break)

    def dealers_choice(self):
        """Generator for dealer's choice of passing. (generator)"""
        # Set the valid choices.
        valid_dirs = ('left', 'right', 'not', 'center', 'scatter', 'across')
        if len(self.players) not in (4, 6):
            valid_dirs = valid[:-1]
        valid_text = 'Please choose {}.'.format(utility.oxford(valid_dirs, 'or'))
        # Generate the direction and the pass count.
        while True:
            # Get the dealer for this deal (self.dealer is dealer for next deal at this point)
            dealer = self.players[self.players.index(self.dealer) - 1]
            dealer.tell('\nYour hand is: {}.'.format(self.hands[dealer]))
            # Get a valid direction.
            while True:
                pass_dir = dealer.ask('What direction shoud cards be passed? ')
                pass_dir = self.pass_aliases.get(pass_dir, pass_dir)
                if pass_dir in valid_dirs:
                    break
                dealer.error('{!r} is not a valid choice.'.format(pass_dir))
                dealer.error(valid_text)
            # Get or calculate the pass count.
            if pass_dir == 'scatter':
                self.num_pass = len(self.players) - 1
            elif pass_dir == 'not':
                self.num_pass = 0
            else:
                self.num_pass = dealer.ask_int('How many cards should be passed? ', low = 1, high = 4)
            # Yield the direction.
            yield pass_dir

    def do_gipf(self, arguments):
        """
        Calvin Cards randomized the rest of the plays this round.
        """
        # Run the edge, if possible.
        game, losses = self.gipf_check(arguments, ('calvin cards',))
        # Winning Calvin Cards randomizes moves for the rest of the trick.
        if game == 'calvin cards':
            if not losses:
                self.random_move = True
        # Otherwise I'm confused.
        else:
            self.human.tell('Bless your heart.')
        return True

    def do_pass(self, arguments):
        """
        Pass one or more cards to another player.
        """
        # Get the player and their hand.
        player = self.current_player
        hand = self.hands[player]
        #print('{} passes {} from {}.'.format(player, arguments, hand))
        # Get the actual card objects.
        cards = [card.strip().upper() for card in self.card_re.findall(arguments)]
        # Make sure all of the cards are in their hand and legal.
        error = False
        for card in cards:
            if card not in hand:
                player.error('You do not have the {}.'.format(card))
                error = True
            elif self.keep_spades and card in ('QS', 'KS', 'AS'):
                player.error('You may not pass the {}.'.format(card))
                error = True
        if error:
            return True
        else:
            # Shift the cards to their passing stack.
            for card in cards:
                hand.shift(card, self.passes[player])

    def do_play(self, arguments):
        """
        Play a card, to either start or contribute to a trick.  (p)
        """
        # Get the player and their hand.
        player = self.current_player
        hand = self.hands[player]
        #print(player.name, hand)
        # Check for a valid card.
        if isinstance(arguments, cards.Card):
            to_play = arguments
        elif self.card_re.match(arguments):
            to_play = self.deck.parse_text(arguments)
        else:
            player.error('{!r} is not a card in the deck.'.format(arguments))
            return True
        print(to_play, repr(to_play), to_play.rank_num, to_play.suit_num)
        # Check for valid timing.
        if self.phase != 'trick':
            player.error('This is not the right time to play cards.')
            return True
        # Check for possession of the card.
        elif to_play not in hand:
            player.error('You do not have the {:u} to play.'.format(to_play))
            return True
        if self.trick:
            # Check that the card follows suit, or that the player is void in that suit.
            trick_suit = self.trick[0].suit
            if to_play.suit != trick_suit and hand.suit_in(trick_suit):
                player.error('You must play a card of the suit led.')
                return True
            hand.shift(to_play, self.trick)
            if player != self.human:
                self.human.tell('{} played the {}.'.format(player, to_play))
        else:
            # Get the player's playable cards.
            playable = hand.cards[:]
            if self.jokers_follow:
                playable = [card for card in playable if card.rank != 'X']
            if not self.hearts_broken:
                playable = [card for card in playable if card.suit != 'H']
            # Validate the card they are leading with.
            if to_play.rank == 'X' and self.jokers_follow and playable:
                player.error('You cannot lead with a joker.')
                return True
            if to_play.suit == 'H' and not self.hearts_broken and playable:
                player.error('You cannot lead with a heart until they are broken.')
                return True
            hand.shift(to_play, self.trick)
            if player != self.human:
                self.human.tell('{} lead with the {}.'.format(player, to_play))

    def do_scores(self, arguments):
        """
        Show the current scores in the game. (s)
        """
        current = self.current_player
        current.tell()
        for player in self.players:
            current.tell('{}: {}'.format(player, self.scores[player.name]))
        current.tell('\nThe game ends when a player reaches {} points.\n'.format(self.end))
        return True

    def do_taken(self, arguments):
        """
        View the cards you have taken so far this deal. (t)
        """
        player = self.current_player
        taken = self.taken[player]
        if taken:
            cards = taken[:]
            cards.sort()
            player.tell('\nSo far this deal you have taken: {}.\n'.format(cards))
        else:
            player.tell('\nYou have not taken any cards yet this deal.\n')
        return True

    def game_over(self):
        """Determine if the game is over. (bool)"""
        # Check for someone breaking the "winning" score.
        if max(self.scores.values()) >= self.end:
            # Get the scores of interest.
            human_score = self.scores[self.human]
            winning_score = min(self.scores.values())
            # Calculate the humans win/loss/draw.
            for name, score in self.scores.items():
                if score > human_score:
                    self.win_loss_draw[0] += 1
                elif score < human_score:
                    self.win_loss_draw[1] += 1
                elif name != human_score:
                    self.win_loss_draw[2] += 1
                # Tell the human who won.
                if score == winning_score:
                    self.human.tell('{} wins with {} points.'.format(name, score))
            # Set the number turns to the number of tricks.
            self.turns = self.tricks
            return True
        else:
            return False

    def handle_opt_deal(self):
        """Handle the deal option settings for this game. (None)"""
        self.kitty = ''
        if self.extras[0] == 'd':
            ditch_stack = ['3D', '3C', '2D', '2C']
            while len(self.deck) % len(self.players):
                self.deck.force(ditch_stack.pop())
        elif self.extras[0] == 'f':
            self.kitty = 'first'
        elif self.extras[0] == 'h':
            self.kitty = 'heart'
        elif self.extras[0] == 'j':
            suits = itertools.cycle('CD')
            while len(self.deck) % len(self.players):
                self.deck.append(cards.Card('X', next(suits)))

    def handle_opt_pass(self):
        """Handle the passing option settings for this game. (None)"""
        if not self.num_pass:
            self.num_pass = 3 if len(self.players) < 5 else 2
        self.pass_dir = self.pass_aliases.get(self.pass_dir, self.pass_dir)
        self.not_warning = (self.pass_dir != 'not')
        if self.pass_dir == 'scatter':
            self.num_pass = len(self.players) - 1
        if self.pass_dir == 'rot-left':
            dirs = ['left-{}'.format(player_index) for player_index in range(1, len(self.players) + 1)]
            self.pass_dir = itertools.cycle(tuple(['left'] + dirs[1:-1] + ['not']))
        elif self.pass_dir == 'dealer':
            self.pass_dir = self.dealers_choice()
        else:
            self.pass_dir = itertools.cycle(self.pass_dirs[self.pass_dir])

    def handle_opt_play(self):
        """Handle the play option settings for this game. (None)"""
        if self.low_club:
            clubs = [card for card in self.deck if card.suit == 'C']
            clubs.sort(key = cards.by_rank, reverse = True)
            self.low_club = clubs.pop()
            while self.jokers_follow and self.low_club.rank == 'X':
                self.low_club = clubs.pop()

    def handle_opt_player(self):
        """Handle the player option settings for this game. (None)"""
        self.players = [self.human]
        if self.easy + self.medium > 5:
            self.option_set.errors.append('There can be at most five bots in the game.')
        for bot in range(self.easy):
            self.players.append(HeartBot(taken_names = [player.name for player in self.players]))
        for bot in range(self.medium):
            self.players.append(SmeartBot(taken_names = [player.name for player in self.players]))

    def handle_opt_score(self):
        """Handle the scoring option settings for this game. (None)"""
        rank_set = ACE_HIGH_RANKS
        if self.heart_score[0] == 'f':
            rank_set = FACE_RANKS
        elif self.heart_score[0] == 'p':
            rank_set = PIP_RANKS
        elif self.heart_score[0] == 'r':
            rank_set = RANK_RANKS
        self.deck = cards.Deck(rank_set = rank_set, suit_set = HEARTS_SUITS)
        lady_index = self.deck.index('QS')
        self.deck[lady_index].value = self.lady_points
        if self.bonus:
            bonus_index = self.deck.index(self.bonus)
            self.deck[bonus_index].value = -10
        self.max_score = sum(rank_set.values.values()) + self.lady_points
        self.breakers = set([card for card in self.deck if card.suit == 'H'])
        if self.all_break:
            self.breakers.add('QS')
        if self.joker_points:
            jokers = [card for card in self.deck if card.rank == 'X']
            self.max_score += len(jokers)
            if self.all_break:
                self.breakers.update(jokers)
        if self.bonus:
            self.bonus = cards.Card(*self.bonus)
            self.max_score -= 10

    def handle_options(self):
        """Handle the option settings for this game. (None)"""
        super(Hearts, self).handle_options()
        self.handle_opt_player()
        self.handle_opt_score()
        self.handle_opt_deal()
        self.handle_opt_pass()
        self.handle_opt_play()

    def pass_cards(self):
        """Handle the actual passing of the cards between players. (None)"""
        # Handle passing to the center.
        if self.this_pass == 'center':
            center = []
            for player in self.players:
                center.extend(self.passes[player])
                self.passes[player].cards = []
            random.shuffle(center)
            for player in itertools.cycle(self.players):
                self.hands[player].append(center.pop())
                if not center:
                    break
        # Handle scatter passing.
        elif self.this_pass == 'scatter':
            for pass_from in self.players:
                for pass_to in self.players:
                    if pass_from != pass_to:
                        self.hands[pass_to].append(self.passes[pass_from].pop(0))
        # Handle passing from player to player.
        else:
            for pass_from in self.players:
                pass_to = self.pass_to[pass_from]
                #print('passing from {} to {}'.format(pass_from, pass_to))
                self.hands[pass_to].extend(self.passes[pass_from])
                self.passes[pass_from].cards = []
        human_got = self.hands[self.human][-self.num_pass:]
        pass_text = utility.oxford(human_got, word_format = 'the {}')
        self.human.tell('You were passed {}.'.format(pass_text))
        # Sort the hands.
        for hand in self.hands.values():
            hand.cards.sort()

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Handle passing.
        if self.phase == 'pass':
            # Get the cards to pass.
            player.tell('\nYour hand is: {}.'.format(self.hands[player]))
            if self.this_pass == 'scatter':
                pass_text = utility.oxford([other.name for other in self.players if other != player])
            else:
                pass_text = self.pass_to[player]
            query = '\nWhich {} do you want to pass to {}? '
            move = player.ask(query.format(utility.number_plural(self.num_pass, 'card'), pass_text))
            # If the correct number of cards are found, pass them.
            if len(self.card_re.findall(move)) == self.num_pass:
                go = self.do_pass(move)
                # If everyone has set up a passing stack, actually pass the cards.
                if all(self.passes.values()):
                    self.pass_cards()
                    self.phase = 'trick'
                    # Set the first player.
                    if self.low_club:
                        for player in self.players:
                            if self.low_club in self.hands[player]:
                                self.next_player = player
                                break
                    else:
                        # Note that self.dealer refers to the next dealer, to the left of the current one.
                        self.next_player = self.dealer
                return go
            else:
                # If incorrect number of cards, try to run a command.
                return self.handle_cmd(move)
        # Handle playing tricks
        elif self.phase == 'trick':
            # Display the game status.
            if self.trick:
                player.tell('The trick to you is: {}.'.format(self.trick))
            else:
                self.human.tell('')  # Make sure tricks are blocked out in the ouput.
                player.tell('You lead the trick.')
            player.tell('Your hand is: {}.'.format(self.hands[player]))
            if self.low_club and self.low_club in self.hands[player]:
                if player == self.human:
                    self.human.tell('You must play the {}.'.format(self.low_club))
                move = self.low_club
            else:
                move = player.ask_card('What is your play? ')
            if isinstance(move, cards.Card):
                # Handle card text as plays.
                go = self.do_play(move)
                # Check for the trick being finished.
                if len(self.trick) == len(self.players):
                    self.tricks += 1
                    self.trick_winner()
                return go
            else:
                # Handle other text as commands.
                return self.handle_cmd(move)

    def score_players(self):
        """
        Score each player's hand. (dict, str)

        The return value is a dictionary of the raw points scored, and the name of the
        shooter, if any.
        """
        round_points = {}
        shooter = ''
        for player in self.players:
            # Count the scoring cards.
            hearts, heart_points, lady, jokers = 0, 0, 0, 0
            bonus = self.bonus if self.bonus in self.taken[player] else None
            points = self.taken[player].score()
            hearts = len([card for card in self.taken[player] if card.suit == 'H'])
            lady = 'QS' in self.taken[player]
            jokers = len([card for card in self.taken[player] if card.rank == 'X'])
            # Calculate and store the unadjusted points.
            if self.joker_points:
                points += jokers
            points = max(0, points)
            round_points[player] = points
            # Display the card counts and points.
            score_text = '{} had {} {}'.format(player.name, hearts, utility.plural(hearts, 'heart'))
            score_bits = ['{} {}'.format(hearts, utility.plural(hearts, 'heart'))]
            if lady:
                score_bits.append('the Queen of Spades')
            if self.joker_points and jokers:
                score_bits.append('{} {}'.format(jokers, utility.plural(jokers, 'joker')))
            if bonus:
                score_bits.append('the {:n}'.format(bonus))
            point_text = '{} {}'.format(points, utility.plural(points, 'point'))
            base_text = '{} had {}, for {} this round.'
            score_text = base_text.format(player, utility.oxford(score_bits), point_text)
            self.human.tell(score_text)
            # Inform and record any sucessful shooter.
            if points == self.max_score or (bonus or points == self.max_score - 10):
                self.human.tell('{} shot the moon!'.format(player))
                shooter = player.name
            # Check for taking no tricks.
            if not self.taken[player] and self.no_tricks:
                text = '{} gets {} points taken off for winning no tricks.'
                self.human.tell(text.format(player, self.no_tricks))
                round_points[player] = -self.no_tricks
        return round_points, shooter

    def score_round(self):
        """Score one deck's worth of tricks. (None)"""
        self.human.tell('')
        # Calculate the points this round for each player.
        round_points, shooter = self.score_players()
        # Adjust the round points if anyone shot the moon.
        if shooter:
            moon_value = self.max_score + 10 * bool(self.bonus)
            auto_old = self.moon[0] == 'a' and max(self.scores.values()) + moon_value < self.end
            if self.moon[0] == 'o' or auto_old:
                for player in round_points:
                    if player == shooter:
                        round_points[player] = 0
                    else:
                        round_points[player] += moon_value
            else:
                round_points[shooter] = -moon_value
        # Adjust and display the overall points.
        self.human.tell('\nOverall Scores:')
        for player in self.players:
            self.scores[player] = max(self.scores[player] + round_points[player], 0)
            self.human.tell('{}: {}'.format(player, self.scores[player]))

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
                    if max_rank == 14:
                        # Correct rank index for aces.
                        max_rank = 1
                    max_name = self.deck.rank_set.names[self.deck.rank_set.chars[max_rank]].lower()
                    s = 'es' if max_name == 'six' else 's'
                    self.human.tell("\nThere was a tie of {}{}.".format(max_name, s))
                    max_rank = -1
                    players = max_players
                    max_players = []
                    player_index = 0

    def set_options(self):
        """Set the possible options for the game. (None)"""
        # Get a card verifier.
        def is_card(text):
            return len(text) == 2 and text[0] in cards.Card.ranks and text[1] in cards.Card.suits
        # Set the bot options.
        self.option_set.add_option('easy', ['ez'], int, 1, valid = range(5),
            question = 'How many easy bots do you want to play against (return for 1)? ')
        self.option_set.add_option('medium', ['md'], int, 2, valid = range(5),
            question = 'How many medium bots do you want to play against (return for 2)? ')
        # Set the deal/card options.
        self.option_set.add_option('extras', ['x'], default = 'ditch',
            valid = ('d', 'ditch', 'f', 'first', 'h', 'heart', 'j', 'joker'),
            question = 'How should extra cards be handled (return or ditch them)? ',
            error_text = 'Please choose ditch, first, heart, or joker.')
        self.option_set.add_option('jokers-follow', ['jf'],
            question = 'Should jokers not be allowed to lead? bool')
        self.option_set.add_option('joker-points', ['jp'],
            question = 'Should jokers score one point each? bool')
        # Set the pass options.
        self.option_set.add_option('keep-spades', ['ks'],
            question = 'Should passing QS, KS, and AS be banned? bool')
        self.option_set.add_option('num-pass', ['np'], int, 0, valid = range(5),
            question = 'How many cards should be passed (return for 3, 2 with 5+ players)? ')
        self.option_set.add_option('pass-dir', ['pd'], default = 'right',
            valid = ('r', 'right', 'l', 'left', 'rl', 'right-left', 'lr', 'left-right', 'lran', 'rot-left',
            '@', 'central', 'c', 'dealer', 'd', 'not', 'n', 'scatter', 's'),
            question = 'In what direction should cards be passed (return for right)? ')
        # Set the play options.
        self.option_set.add_option('all-break', ['ab'],
            question = 'Should hearts not be able to lead until a penalty card is played? bool')
        self.option_set.add_option('break-hearts', ['bh'],
            question = 'Should hearts not be able to lead until a heart is played otherwise? bool')
        self.option_set.add_option('bonus', ['b'], str.upper, '', check = is_card,
            question = 'What card should remove up to 10 points from your score (return for none)? ')
        self.option_set.add_option('low-club', ['lc'],
            question = 'Should the lowest club lead the first trick of each deal? bool')  # !! interaction with kitty
        # Set the score options.
        self.option_set.add_option('heart-score', ['hs'], str.lower, 'one',
            valid = ('o', 'one', 'p', 'pips', 'r', 'rank', 'f', 'face'),
            question = 'How should hearts be scored (one, face, pip or rank, return for one)? ')
        self.option_set.add_option('lady-score', ['ls'], int, 13, valid = range(0, 50),
            target = 'lady_points',
            question = 'How much should the Queen of Spades score (return for 13)? ')
        self.option_set.add_option('moon', ['m'], str.lower, 'old',
            valid = ('a', 'auto', 'n', 'new', 'o', 'old'),
            question = 'How should shooting the Moon be scored (new, auto, or return for old)? ')
        self.option_set.add_option('no-tricks', ['nt'], int, 0, valid = range(0, 25),
            question = 'How many points should be taken off if a player wins no tricks? ')
        self.option_set.add_option('end', ['e'], int, 100, valid = range(50, 1000),
            question = 'How many points for one player should end the game (return for 100)? ')
        # Set the option groups.
        gonzo = 'bonus = jd break-hearts heart-score = face low-club no-tricks = 5 pass-dir = rot-left'
        self.option_set.add_group('gonzo', ['gz'], gonzo)

    def set_pass(self):
        """Set up the passing of cards for this hand. (None)"""
        # Set the game tracking to passing.
        self.phase = 'pass'
        self.this_pass = next(self.pass_dir)
        # Check for not passing.
        if self.this_pass == 'not':
            if self.not_warning:
                self.human.tell('\nThere is no passing this round.')
            self.phase = 'trick'
            return None
        # Translate the pass direction into passees.
        if self.this_pass == 'left':
            pass_to = self.players[1:] + self.players[:1]
        elif self.this_pass == 'right':
            pass_to = self.players[-1:] + self.players[:-1]
        elif self.this_pass == 'across':
            offset = len(self.players) // 2
            pass_to = self.players[offset:] + self.players[:offset]
        elif self.this_pass.startswith('left-'):
            offset = int(self.this_pass.split('-')[1])
            pass_to = self.players[offset:] + self.players[:offset]
        # Set up the passing dictionary.
        if self.this_pass == 'center':
            self.pass_to = {pass_from: 'the center' for pass_from in self.players}
        elif self.this_pass == 'scatter':
            self.pass_to = {pass_from: self.this_pass for pass_from in self.players}
        else:
            self.pass_to = {passer: passee.name for passer, passee in zip(self.players, pass_to)}

    def set_up(self):
        """Set up the game. (None)"""
        # Set up hands, including pseudo-hands for holding various sets of cards.
        self.hands = {player: cards.Hand(deck = self.deck) for player in self.players}
        self.passes = {player: cards.Hand(deck = self.deck) for player in self.players}
        self.taken = {player: cards.Hand(deck = self.deck) for player in self.players}
        self.trick = cards.Hand(deck = self.deck)
        self.last_trick = cards.Hand(deck = self.deck)
        random.shuffle(self.players)
        # Handle the initial deal
        self.set_dealer()
        self.deal()
        # Set up the tracking variables.
        self.set_pass()
        self.tricks = 0
        self.random_move = False

    def trick_winner(self):
        """Determine who won the trick. (None)"""
        # Find the winning card.
        trick_suit = self.trick[0].suit
        suit_cards = [card for card in self.trick if card.suit == trick_suit]
        winning_card = sorted(suit_cards)[-1]
        card_index = self.trick.cards.index(winning_card)
        # Find the winning player.
        winner_index = (self.player_index + 1 + card_index) % len(self.players)
        winner = self.players[winner_index]
        # Handle the win.
        self.human.tell('\n{} won the trick with the {}.'.format(winner, winning_card))
        self.taken[winner].extend(self.trick.cards)
        # Handle any kitty.
        if self.deck:
            kitty_win = self.kitty == 'first'
            kitty_win = kitty_win or 'heart' and [card for card in self.trick if card.suit == 'H']
            if kitty_win:
                self.taken[winner].cards.extend(self.deck)
                text = 'You won {} from the kitty.'
                winner.tell(text.format(utility.oxford(self.deck, word_format = 'the {:u}')))
                if winner != self.human:
                    self.human.tell('{} won the kitty.'.format(winner))
                self.deck.cards = []
        # Check for breaking hearts.
        if not self.hearts_broken and self.breakers.intersection(self.trick):
            self.hearts_broken = True
        # Clear the trick.
        self.last_trick = self.trick
        self.last_winner = winner
        self.trick = cards.Hand(deck = self.deck)
        self.random_move = False
        # Check for the end of the round.
        if not self.hands[self.human]:
            self.score_round()
            for taken in self.taken.values():
                taken.discard()
            if max(self.scores.values()) < self.end:
                self.deal()
                self.set_pass()
        else:
            self.player_index = winner_index - 1
