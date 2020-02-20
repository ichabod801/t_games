"""
cards.py

Cards and decks of cards for tgames.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
ONE_SUIT: A feature set with only one suit (spades). (FeatureSet)
STANDARD_RANKS: The standard Western card ranks. (FeatureSet)
STANDARD_SUITS: The standard Western card suits. (FeatureSet)
STANDARD_WRAP_RANKS: The standard card ranks with wrapping. (FeatureSet)
TWO_SUITS: A feature set with only two suits (spades and hearts). (FeatureSet)

Classes:
CRand: Implementation of C's rand function. (object)
FeatureSet: A set of valid values for a feature (rank/suit) of a Card. (object)
Card: A standard playing card, with a suit and a rank. (object)
Pile: A sequence of cards. (MutableSequence)
Deck: A standard deck of cards. (object)
Hand: A hand of cards held by a player. (object)
TrackingCard: A card that tracks it's location. (Card)
TrackOneSuit: A tracking card with only one suit. (TrackingCard)
TrackTwoSuit: A tracking card with only two suits. (TrackingCard)
TrackingDeck: A deck that keeps track of the location of its cards. (Deck)
MultiTrackingDeck: A deck that keeps track of multiple duplicate cards. (Deck)

Functions:
by_rank: A key function for sorting Cards by rank. (int)
by_rank_suit: A key function for sorting Cards by rank then suit. (tuple)
by_suit: A key function for sorting Cards by suit. (int)
by_suit_rank: A key function for sorting Cards by suit then rank. (tuple)
by_value: A key function for sorting Cards by value. (int)
parse_text: Parse text looking for a card. (Card or list of Card)
"""


from __future__ import print_function

import collections
try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence
import random
import re

from . import utility


class CRand(object):
    """
    Implementation of C's rand function. (object)

    Attributes:
    state: The current state of the PRNG. (int)

    Overridden Methods:
    __init__
    __call__
    __repr__
    """

    def __init__(self, seed = None):
        """
        Set up the pseudo-random number generator. (None)

        Parameters:
        seed: The initial state of the PRNG. (int)
        """
        # Use a random seed if none is given.
        if seed is None:
            seed = random.randint(0, 32767)
        self.state = seed

    def __call__(self):
        """Get the next number from the PRNG. (int)"""
        self.state = (214013 * self.state + 2531011) % (2 ** 31)
        return self.state // (2 ** 16)

    def __repr__(self):
        """Computer readable text representation. (str)"""
        return 'CRand({})'.format(self.state)


class FeatureSet(object):
    """
    A set of valid values for a feature (rank/suit) of a Card. (object)

    Attributes:
    an_chars: The characters for ranks using 'an' instead of 'a'. (str)
    chars: The characters for the feature values. (str)
    colors: The colors associated with the feature values. (dict of str: str)
    names: The names of the feature values. (dict of str: str)
    skip: The number of values to skip when iterating. (int)
    values: Numeric values associated with feature values. (dict of str: int)
    wrap: A flag for ranks being wrappable. (bool)

    Methods:
    above: Check that this card is n ranks above another card. (bool)
    below: Check that this card is n ranks below another card. (bool)
    copy: Make an independent copy of the FeatureSet. (FeatureSet)
    index: Give the feature index of a character. (int)
    items: Iterate over all the items in the feature set. (iterator)
    next: Get the character after a given one. (str)
    previous: Get the character before a given one. (str)

    Overwritten Methods:
    __init__
    __contains__
    __iter__
    __len__
    __repr__
    """

    def __init__(self, chars, names, values = None, colors = None, skip = 0, wrap = False, an_chars = ''):
        """
        Set up the feature set. (None)

        Parameters:
        chars: The characters for the feature values. (str)
        names: The names of the feature values. (list of str)
        values: Numeric values associated with feature values. (list of int)
        colors: The colors associated with the feature values. (str)
        skip: The number of values to skip when iterating. (int)
        wrap: A flag for ranks being wrappable. (bool)
        an_chars: The characters for ranks using 'an' instead of 'a'. (str)
        """
        # Set default values.
        if values is None:
            values = [1] * len(chars)
        if colors is None:
            colors = 'X' * len(chars)
        # Check length of secondary attributes.
        if len(names) != len(chars):
            raise ValueError('Names and characters of feature sets must have the same length.')
        if len(values) != len(chars):
            raise ValueError('Values and characters of feature sets must have the same length.')
        if len(colors) != len(chars):
            raise ValueError('Colors and characters of feature sets must have the same length.')
        # Set the attributes.
        self.chars = chars
        self.names = dict(zip(chars, names))
        self.values = dict(zip(chars, values))
        self.colors = dict(zip(chars, colors))
        self.skip = skip
        self.wrap = wrap
        self.an_chars = an_chars

    def __contains__(self, char):
        """
        Check for a valid rank. (bool)

        Parameters:
        char: The rank character to check validity of. (str)
        """
        return char in self.names

    def __iter__(self):
        """Iterate over the characters. (iterator)"""
        return iter(self.chars[self.skip:])

    def __len__(self):
        """The number of possible feature values. (int)"""
        return len(self.chars) - self.skip

    def __repr__(self):
        """Debugging text representation. (str)"""
        return '<FeatureSet {!r}>'.format(self.chars)

    def above(self, char, other_char, n = 1):
        """
        Check that this card is n ranks above another card. (bool)

        Parameters:
        char: The feature character of the first card. (str)
        other_char: The feature character of the second card. (str)
        n: How far above to check for. (int)
        """
        # Do the standard caculation
        diff = self.chars.index(char) - self.chars.index(other_char)
        # Account for wraping.
        if self.wrap and diff < 0:
            diff += len(self) - self.skip + 1
        return diff == n

    def below(self, char, other_char, n = 1):
        """
        Check that this card is n ranks below another card. (bool)

        Parameters:
        char: The feature character of the first card. (str)
        other_char: The feature character of the second card. (str)
        n: How far below to check for. (int)
        """
        # Do the standard caculation
        diff = self.chars.index(other_char) - self.chars.index(char)
        # Account for wraping.
        if self.wrap and diff < 0:
            diff += len(self) - self.skip + 1
        return diff == n

    def copy(self):
        """Make an independent copy of the FeatureSet. (FeatureSet)"""
        names = [self.names[char] for char in self.chars]
        values = [self.values[char] for char in self.chars]
        colors = [self.colors[char] for char in self.chars]
        return FeatureSet(self.chars, names, values, colors, self.skip, self.wrap, self.an_chars)

    def index(self, char):
        """
        Give the feature index of a character. (int)

        Parameters:
        char: The character to get an index for. (str)
        """
        return self.chars.index(char)

    def items(self):
        """
        Iterate over all the items in the feature set. (iterator)

        Each interation is a tuple of (index, character, name, value)
        """
        def iter_items():
            for index, char in enumerate(self.chars):
                if index < self.skip:
                    continue
                yield (index, char, self.names[char], self.values[char], self.colors[char])
        return iter_items()

    def next(self, char):
        """
        Get the character after a given one. (str)

        Parameters:
        char: The starting character. (str)
        """
        new_num = (self.chars.index(char) + 1) % len(self.chars)
        if new_num < self.skip:
            if self.wrap:
                new_num = self.skip
            else:
                raise IndexError('There is no higher character than {!r}.'.format(char))
        return self.chars[new_num]

    def previous(self, char):
        """
        Get the character before a given character. (str)

        Parameters:
        char: The starting character. (str)
        """
        new_num = self.chars.index(char) - 1
        if new_num < self.skip:
            if self.wrap:
                new_num = len(self.chars) - 1
            else:
                raise IndexError('There is no lower character than {!r}.'.format(char))
        return self.chars[new_num]


ONE_SUIT = FeatureSet('S', ['Spades'], colors = 'B')

STANDARD_RANKS = FeatureSet('XA23456789TJQK',
    ['Joker', 'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack',
        'Queen', 'King'],
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10],
    skip = 1, an_chars = 'A8')

STANDARD_SUITS = FeatureSet('CDHS', ['Clubs', 'Diamonds', 'Hearts', 'Spades'], colors = 'BRRB')

STANDARD_WRAP_RANKS = FeatureSet('XA23456789TJQK',
    ['Joker', 'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack',
        'Queen', 'King'],
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10],
    skip = 1, wrap = True, an_chars = 'A8')

TWO_SUITS = FeatureSet('HS', ['Hearts', 'Spades'], colors = 'RB')


class Card(object):
    """
    A standared playing card, with a suit and a rank. (object)

    The color, rank, and suit attributes are length 1.

    Attributes:
    a_text: The text for the card with an 'a' or 'an'. (str)
    color: The color of the card. ('R' or 'B')
    down_text: The text to display when the card is face down. (str)
    format_types: Extra types used for the format method. (dict of str: str)
    name: The full name of the card. (str)
    rank: The rank of the card. (str)
    rank_num: The index of the rank of the card. (int)
    rank_set: The ranks set the card is part of. (FeatureSet)
    suit: The suit of the card. (str)
    suit_num: The index of the suit of the card. (int)
    suit_set: The suit set the card is part of. (FeatureSet)
    up: A flag for the card being face up. (str)
    up_text: The text to display when the card is face up. (str)
    value: The score provided by the card. (int)

    Methods:
    above: Check that this card is n ranks above another card. (bool)
    below: Check that this card is n ranks below another card. (bool)
    next: Get the next card in rank order. (Card)
    previous: Get the previous card in rank order. (Card)

    Overridden Methods:
    __init__
    __add__
    __eq__
    __format__
    __hash__
    __lt__
    __radd__
    __repr__
    __rsub__
    __str__
    __sub__
    """

    def __init__(self, rank, suit, down_text = '??', rank_set = STANDARD_RANKS, suit_set = STANDARD_SUITS):
        """
        Set up the card. (None)

        Parameters:
        rank: The rank of the card. (str)
        suit: The suit of the card. (str)
        down_text: How the card looks when face down. (str)
        ace_high: Treat the ace as higher than a king. (bool)
        rank_set: The ranks set the card is part of. (FeatureSet)
        suit_set: The suit set the card is part of. (FeatureSet)
        """
        # Set the specified paramters.
        self.rank = rank[0]
        self.suit = suit[0]
        self.rank_set = rank_set
        self.suit_set = suit_set
        # Calculate the numeric values of the card.
        self.rank_num = self.rank_set.index(self.rank)
        self.suit_num = self.suit_set.index(self.suit)
        self.value = self.rank_set.values[self.rank] * self.suit_set.values[self.suit]
        self.color = self.suit_set.colors[self.suit]
        # Calcuate the text attributes of the card.
        self.name = '{} of {}'.format(self.rank_set.names[self.rank], self.suit_set.names[self.suit])
        self.up_text = self.rank + self.suit
        self.down_text = down_text
        if self.rank in self.rank_set.an_chars:
            a_text = 'an {}'.format(self.name.lower())
        else:
            a_text = 'a {}'.format(self.name.lower())
        self.format_types = {'a': a_text, 'd': self.down_text, 'n': self.name, 'u': self.up_text}
        # Default face down.
        self.up = False

    def __add__(self, other):
        """
        Add the card as an integer. (int)

        Parameters:
        other: The integer to add to. (int)
        """
        return self.value + other

    def __eq__(self, other):
        """
        Equality comparison, by rank and suit. (bool)

        Note that str(card) == card to match user input.

        Parameters:
        other: The card to compare to.
        """
        # Compare cards by rank and suit.
        if isinstance(other, Card):
            return (self.rank, self.suit) == (other.rank, other.suit)
        # Compare strings by str.
        elif isinstance(other, str):
            return self.up_text == other.upper()
        # The rest is not implementd.
        else:
            return NotImplemented

    def __hash__(self):
        """The hash is the card text. (hash)"""
        return hash(self.up_text)

    def __format__(self, format_spec):
        """
        Return a formatted text version of the card. (str)

        The additional recognized format types are:
            a: The full name with an indefinite article.
            d: The face down two-letter abbreviation.
            n: The full name.
            u: The face up two-letter abbreviation.

        Parameters:
        format_spec: The format specification. (str)
        """
        # Use and remove format type if given.
        if format_spec and format_spec[-1] in self.format_types:
            target = self.format_types[format_spec[-1]]
            format_spec = format_spec[:-1]
        else:
            target = str(self)
        # Return the text based on type with the rest of the format spec applied.
        format_text = '{{:{}}}'.format(format_spec)
        return format_text.format(target)

    def __lt__(self, other):
        """
        For sorting by suit then rank. (bool)

        Parameters:
        other: The integer to compare to. (int)
        """
        if isinstance(other, Card):
            return (self.suit_num, self.rank_num) < (other.suit_num, other.rank_num)
        else:
            return (self.suit_num, self.rank_num) < other

    def __radd__(self, other):
        """
        Add the card as an integer. (int)

        Parameters:
        other: The integer to add to. (int)
        """
        return self.value + other

    def __repr__(self):
        """Generate computer readable text representation. (str)"""
        return 'Card({!r}, {!r})'.format(self.rank, self.suit)

    def __rsub__(self, other):
        """
        Subtract the card as an integer. (int)

        Parameters:
        other: The integer to add to. (int)
        """
        return other - self.value

    def __str__(self):
        """Generate human readable text representation. (str)"""
        if self.up:
            return self.up_text
        else:
            return self.down_text

    def __sub__(self, other):
        """
        Subtract the card as an integer. (int)

        Parameters:
        other: The integer to add to. (int)
        """
        return self.value - other

    def above(self, other, n = 1):
        """
        Check that this card is n ranks above another card. (bool)

        Parameters:
        other: The card to compare with. (Card)
        n: How many ranks above to check for. (int)
        """
        return self.rank_set.above(self.rank, other.rank, n)

    def below(self, other, n = 1):
        """
        Check that this card is n ranks below another card. (bool)

        Parameters:
        other: The card to compare with. (Card)
        n: How many ranks below to check for. (int)
        """
        return self.rank_set.below(self.rank, other.rank, n)

    def next(self):
        """Get the next card in rank order. (Card)"""
        return Card(self.rank_set.next(self.rank), self.suit, self.down_text, self.rank_set, self.suit_set)

    def previous(self):
        """Get the previous card in rank order. (Card)"""
        return Card(self.rank_set.previous(self.rank), self.suit, self.down_text, self.rank_set,
            self.suit_set)


class Pile(MutableSequence):
    """
    A sequence of cards. (MutableSequence)

    Attributes:
    cards: The cards in the pile. (list of Card)

    Methods:
    _child: Make a Pile with the same attributes but different cards. (Pile)
    insert: Insert a card into the pile. (None)
    sort: Sort the cards in the pile. (None)

    Overridden Methods:
    __init__
    __add__
    __delitem__
    __eq__
    __getitem__
    __imul__
    __len__
    __mul__
    __repr__
    __rmul__
    __setitem__
    __str__
    """

    def __init__(self, cards = []):
        """
        Put the cards in the pile. (None)

        Parameters:
        cards: The cards to put in the pile. (list of Card)
        """
        self.cards = cards

    def __add__(self, other):
        """
        Add the pile to another sequence of cards. (Pile)

        Parameters:
        other: The object to add. (object)
        """
        if isinstance(other, Pile):
            return self._child(self.cards + other.cards)
        else:
            return self._child(self.cards + other)

    def __delitem__(self, key):
        """
        Delete a card. (None)

        Parameters:
        key: The item(s) to delete. (int or slice)
        """
        del self.cards[key]

    def __eq__(self, other):
        """
        Check equality with another object. (bool)

        Parameters:
        other: The object to check equality with. (object)
        """
        if isinstance(other, Pile):
            return self.cards == other.cards
        else:
            return self.cards == other

    def __getitem__(self, key):
        """
        Get a card or slice of cards. (Card or Pile)

        Parameters:
        key: The item(s) to delete. (int or slice)
        """
        if isinstance(key, int):
            return self.cards[key]
        else:
            return self._child(self.cards[key])

    def __imul__(self, other):
        """
        Copy the cards in the pile in place. (Pile)

        Parameters:
        other: The number of copies to make. (int)
        """
        self.cards *= other
        return self

    def __len__(self):
        """Get the number of cards in the Pile. (int)"""
        return len(self.cards)

    def __mul__(self, other):
        """
        Copy the cards in the pile. (Pile)

        Parameters:
        other: The number of copies to make. (int)
        """
        return self._child(self.cards * other)

    def __repr__(self):
        """Debugging text representation."""
        return '<{} {}>'.format(self.__class__.__name__, self)

    def __rmul__(self, other):
        """
        Copy the cards in the pile. (Pile)

        Parameters:
        other: The number of copies to make. (int)
        """
        return self._child(self.cards * other)

    def __setitem__(self, key, value):
        """
        Set a card in the deck. (None)

        Parameters:
        key: The card(s) to change. (int or slice)
        value: The cards(s) to change to. (Card or list of Cards)
        """
        self.cards[key] = value

    def __str__(self):
        """Human readable text representation. (str)"""
        return '[{}]'.format(', '.join(card.up_text for card in self.cards))

    def _child(self, cards):
        """
        Make a Pile with the same attributes but different cards. (Pile)

        Paramters:
        cards: The cards to make a pile out of. (list of Card)
        """
        return Pile(cards)

    def insert(self, index, card):
        """
        Insert a card in the pile. (None)

        Parameters:
        index: Where to put the card. (int)
        card: The card to put there. (Card)
        """
        self.cards.insert(index, card)

    def sort(self, key = None, reverse = False):
        """
        Sort the cards in the pile. (None)

        Parameters:
        key: A function to get comparison keys for the cards. (callable)
        reverse: A flag for sorting in descending order. (bool)
        """
        self.cards.sort(key = key, reverse = reverse)


class Deck(Pile):
    """
    A standard deck of cards. (Pile)

    Attributes:
    card_re: A regular expression to match a card. (SRExpression)
    discards: The cards in the discard pile. (list of card)
    jokers: The number of jokers in the deck. (int)
    rank_set: The ranks of cards in the deck. (FeatureSet)
    ranks: The rank characters for cards in the deck. (str)
    shuffle_size: The number of cards left that triggers a shuffle. (int)
    suit_set: The suits of cards in the deck. (FeatureSet)
    suits: The suits characters for cards in the deck. (str)

    Methods:
    _initial_cards: Add in the initial cards for the deck. (None)
    cut: Cut the deck. (None)
    deal: Deal a card from the deck. (Card)
    deal_n_each: Deal n cards to each player. (None or list of Card)
    discard: Discard a card to the discard pile. (None)
    force: Remove a particular card from the deck. (Card)
    parse_text: Parse text looking for a card. (Card or list of Card)
    pick: Pick a card from the deck. (Card)
    player_hands: Create a set of hands for a list of players. (dict)
    shuffle: Shuffle the discards back into the deck. (None)

    Overridden Methods:
    __init__
    _child
    """

    def __init__(self, cards = None, jokers = 0, decks = 1, shuffle_size = 0, rank_set = STANDARD_RANKS,
        suit_set = STANDARD_SUITS):
        """
        Fill the deck with a standard set of cards. (None)

        Parameters:
        cards: The initial cards in the deck. (list of Card)
        jokers: The number of jokers in the deck. (int)
        decks: The number of idential decks shuffled together. (int)
        shuffle_size: The number of cards left that triggers a shuffle. (int)
        rank_set: The rank information for cards in the deck. (FeatureSet)
        suit_set: The suit information for cards in the deck. (FeatureSet)
        """
        # Set the specified attributes.
        self.shuffle_size = shuffle_size
        self.jokers = jokers
        self.rank_set = rank_set
        self.suit_set = suit_set
        # Extract attributes from the feature sets.
        self.ranks = self.rank_set.chars
        self.suits = self.suit_set.chars
        self.card_re = re.compile('\\b[{}][{}]\\b'.format(self.ranks, self.suits), re.IGNORECASE)
        # Add the standard cards.
        if cards is None:
            self._initial_cards(decks)
        else:
            self.cards = cards
        # Start with an empty discard pile.
        self.discards = []

    def _child(self, cards):
        """
        Make a Deck with the same attributes but different cards. (Deck)

        Paramters:
        cards: The cards to make a deck out of. (list of Card)
        """
        child = Deck(cards, jokers = self.jokers, shuffle_size = self.shuffle_size,
            rank_set = self.rank_set, suit_set = self.suit_set)
        child.discards = self.discards[:]
        return child

    def _initial_cards(self, decks):
        """
        Add in the initial cards for the deck. (None)

        Parameters:
        decks: How many of each card to include. (int)
        """
        # Add the base cards.
        self.cards = []
        for deck in range(decks):
            for rank in self.rank_set:
                for suit in self.suit_set:
                    self.cards.append(Card(rank, suit, rank_set = self.rank_set, suit_set = self.suit_set))
        # Get the joker ranks and suits.
        joker_ranks = self.rank_set.chars[:self.rank_set.skip]
        if self.suit_set.skip:
            joker_suits = self.suit_set.chars
        else:
            joker_suits = self.suit_set.chars[:self.suit_set.skip]
        # Add the jokers.
        for deck in range(decks):
            for rank in joker_ranks:
                for suit_index in range(self.jokers):
                    suit = joker_suits[suit_index % len(self.suit_set)]
                    self.cards.append(Card(joker_rank, suit))

    def cut(self, card_index):
        """
        Cut the deck. (None)

        Parameters:
        card_index: A number indicating where to cut the deck. (int)
        """
        card_index %= len(self.cards)
        self.cards = self.cards[card_index:] + self.cards[:card_index]

    def deal(self, up = False):
        """
        Deal a card from the deck. (Card)

        Parameters:
        up: A flag for dealing the card face up. (bool)
        """
        # Check for early reshuffle.
        if len(self.cards) <= self.shuffle_size:
            self.shuffle()
        # Deal the card.
        card = self.cards.pop()
        card.up = up
        return card

    def deal_n_each(self, n, players = None, up = True):
        """
        Deal n cards to each player. (None or list of Card)

        A list of n cards is returned if players is None. Otherwise it is assumed that
        the game the players are part of has a hands dictionary with Players as keys
        and Hands as values.

        Paramters:
        n: How many cards to deal to each player. (int)
        players: The players to deal cards to. (list of player.Player)
        up: A flag for dealing the cards face up. (bool)
        """
        # Check the players paramter.
        if not players:
            # Deal n cards.
            return [self.deal(up = up) for card in range(n)]
        else:
            # Deal n cards to each player.
            for card in range(n):
                game = players[0].game
                for player in players:
                    game.hands[player].draw(())

    def discard(self, card, up = False):
        """
        Discard a card to the discard pile. (None)

        Parameters:
        card: The card to discard. (Card)
        up: A flag for discarding face up. (bool)
        """
        self.discards.append(card)
        card.up = up

    def force(self, card_text, up = True):
        """
        Remove a particular card from the deck. (Card)

        Parameters:
        card_text: The string version of the card. (str)
        up: Flag for dealing the card face up. (bool)
        """
        card = self.cards[self.cards.index(card_text)]
        self.cards.remove(card)
        card.up = up
        return card

    def parse_text(self, text):
        """
        Parse text looking for a card. (Card or list of Card)

        Parameters:
        text: The text to parse. (str)
        """
        return parse_text(text, self)

    def pick(self, card_index, up = True):
        """
        Pick a card from the deck. (Card)

        Parameters:
        card_index: A number to determine the card picked. (int)
        up: Flag for picking the card face up. (bool)
        """
        card = self.cards.pop(card_index % len(self.cards))
        card.up = up
        return card

    def player_hands(self, players):
        """
        Create a set of hands for a list of players. (dict of Player: Hand)

        Parameters:
        players: The players to make hands for. (list of player.Player)
        """
        return {player: Hand(deck = self) for player in players}

    def shuffle(self, number = None):
        """
        Shuffle the discards back into the deck. (None)

        Parameters:
        number: The number of the shuffle, the seed for the PRNG. (int)
        """
        # Gather the discards.
        self.cards.extend(self.discards)
        if number is None:
            # Do a standard shuffle.
            random.shuffle(self.cards)
        else:
            # Do a C-style shuffle.
            rand = CRand(number)
            self.cards.sort(key = by_rank_suit)
            while self.cards:
                swap = rand() % len(self.cards)
                self.cards[swap], self.cards[-1] = self.cards[-1], self.cards[swap]
                self.discards.append(self.cards.pop())
            self.cards = self.discards[::-1]
        self.discards = []


class Hand(Pile):
    """
    A hand of cards held by a player. (Pile)

    Attributes:
    deck: The deck the cards in the hand come from. (Deck)

    Methods:
    deal: Add a card to the hand. (None)
    discard: Discard a card back to the deck. (None)
    draw: Draw a card from the deck. (None)
    find: Get a subset of the cards in the hand. (Hand)
    parse_text: Parse text looking for a card. (Card or list of Card)
    rank_in: Check that a rank is in the hand. (bool)
    ranks: Get the ranks in the hand. (list of str)
    score: Score the hand. (int)
    shift: Pass a card to another hand. (None)
    show_player: Show the hand to the player playing it. (str)
    suit_in: Check that a suit is in the hand. (bool)
    suits: Get the suits in the hand. (list of str)

    Overridden Methods:
    __init__
    __eq__
    __lt__
    """

    def __init__(self, cards = None, deck = None):
        """
        Set up the link to the deck. (None)

        Parameters:
        cards: The initial cards in the hand. (list of Card or None)
        deck: The deck the hand is dealt from. (Deck)
        """
        self.deck = deck
        if cards is None:
            self.cards = []
        else:
            self.cards = cards

    def __eq__(self, other):
        """
        Check for equality with another hand. (bool)

        Two hands are equal if they have the same cards, regardless of order.

        Parameters:
        other: The hand to check against. (Hand)
        """
        # !! needs unit testing.
        if isinstance(other, Hand):
            return sorted(self.cards) == sorted(other.cards)
        else:
            return False

    def __lt__(self, other):
        """
        Sort Hands by score. (bool)

        Parameters:
        other: The other hand to compare with. (Hand)
        """
        if isinstance(other, Pile):
            return self.score() < other.score()
        else:
            return self.cards < other

    def __repr__(self):
        """Debugging text representation."""
        return '<{} [{}]>'.format(self.__class__.__name__, ', '.join(card.up_text for card in self.cards))

    def __str__(self):
        """Human readable text representation. (str)"""
        return '{}'.format(', '.join(str(card) for card in self.cards))

    def _child(self, cards):
        """
        Make a Hand with the same attributes but different cards. (Hand)

        Paramters:
        cards: The cards to make a hand out of. (list of Card)
        """
        return Hand(cards, self.deck)

    def deal(self, card):
        """
        Add a card to the hand. (None)

        Parameters:
        card: The card to add to the hand. (Card)
        """
        self.cards.append(card)

    def draw(self, up = True):
        """
        Draw a card from the deck. (Card)

        The return value is the card drawn.

        Parameters:
        up: A flag for dealing the card face up. (None)
        """
        self.cards.append(self.deck.deal(up = up))
        return self.cards[-1]

    def discard(self, card = None, up = True):
        """
        Discard a card back to the deck. (None)

        Parameters:
        card: The card to discard, or None to discard all cards. (Card or None)
        up: A flag for discarding the card face up. (bool)
        """
        # Discard all cards.
        if card is None:
            for card in self.cards:
                self.deck.discard(card, up)
            self.cards = []
        # Discard a specified card.
        else:
            card_index = self.cards.index(card)
            self.deck.discard(self.cards[card_index], up)
            del self.cards[card_index]

    def find(self, rank = '', suit = '', not_rank = '', not_suit = '', regex = ''):
        """
        Get a subset of the cards in the hand. (Hand)

        Parameters are processed in the following order: rank, suit, re, not_rank,
        not_suit. Without parameters it returns a shallow copy of the hand.

        Parameters:
        rank: The ranks to include in the subset. (str)
        suit: The suits to include in the subset. (str)
        not_rank: The ranks to exclude from the subset. (str)
        not_suit: The suits to exclude from the subset. (str)
        regex: A regular expression each card's up_text must match. (str)
        """
        # Start with the full hand.
        cards = self.cards[:]
        # Apply postive filters.
        if rank:
            cards = [card for card in cards if card.rank in rank]
        if suit:
            cards = [card for card in cards if card.suit in suit]
        if regex:
            regex = re.compile(regex)
            cards = [card for card in cards if regex.match(card.up_text)]
        # Apply negative filters.
        if not_rank:
            cards = [card for card in cards if card.rank not in not_rank]
        if not_suit:
            cards = [card for card in cards if card.suit not in not_suit]
        # Return the cards as a Hand.
        return self._child(cards)

    def parse_text(self, text):
        """
        Parse text looking for a card. (Card or list of Card)

        Parameters:
        text: The text to parse. (str)
        """
        return parse_text(text, self.deck)

    def rank_in(self, rank):
        """
        Check that a rank is in the hand. (bool)

        Parameters:
        rank: the rank to check for. (str)
        """
        rank = rank.upper()
        return any(card.rank == rank for card in self.cards)

    def ranks(self):
        """Get the ranks in the hand. (list of str)"""
        return [card.rank for card in self.cards]

    def score(self):
        """Score the hand. (int)"""
        # Default score is high card.
        return sum(self.cards)

    def shift(self, card, hand):
        """
        Pass a card to another hand. (None)

        Parameters:
        card: The card to pass. (str)
        hand: The hand to pass it to. (Hand)
        """
        card_index = self.cards.index(card)
        hand.append(self.cards.pop(card_index))

    def show_player(self):
        """Show the hand to the player playing it. (str)"""
        return ', '.join([card.up_text for card in self.cards])

    def suit_in(self, suit):
        """
        Check that a suit is in the hand. (bool)

        Parameters:
        suit: the suit to check for. (str)
        """
        suit = suit.upper()
        return any(card.suit == suit for card in self.cards)

    def suits(self):
        """Get the suits in the hand. (list of str)"""
        return [card.suit for card in self.cards]


class TrackingCard(Card):
    """
    A card that tracks its location. (Card)

    Attributes:
    deck: The deck the card is a part of. (Deck)
    deck_location: The location of the card in the deck. (list of Card)
    game_location: The location of the card in the game. (list of Card)
    loc_txt: The location identifier for abbreviated card text. (str)
    location_text: The location identifier for full card text. (str)
    rank_num: The numeric rank of the card. (int)

    Methods:
    discard: Discard the card. (None)

    Overridden Methods:
    __init__
    __eq__
    above
    below
    """

    def __init__(self, rank, suit, deck, rank_set = STANDARD_RANKS, suit_set = STANDARD_SUITS):
        """
        Set up the card. (None)

        Initialization converts the suit to a single uppercase character.

        Parameters:
        rank: The rank of the card. (int)
        suit: The suit of the card. (str)
        deck: The deck the card comes from. (TrackingDeck)
        rank_set: The full rank information for the deck. (FeatureSet)
        suit_set: The full suit information for the deck. (FeatureSet)
        """
        super(TrackingCard, self).__init__(rank, suit, rank_set = rank_set, suit_set = suit_set)
        self.deck = deck
        if self.deck is not None:
            self.deck_location = self.deck.cards
            self.game_location = self.deck.cards
        else:
            self.deck_location = None
            self.game_location = None
        self.loc_txt = ''
        self.location_text = ''

    def __eq__(self, other):
        """
        Check equality with another card. (bool)

        Equality between tracking cards is by identity. Otherwise it's as a standard
        Card.

        Parameters:
        other: The card to compare with. (Card or str)
        """
        if isinstance(other, TrackingCard):
            return id(self) == id(other)
        else:
            return super(TrackingCard, self).__eq__(other)

    def __format__(self, format_spec):
        """
        Return a formatted text version of the card. (str)

        The additional recognized format types are:
            d: The face down two-letter abbreviation.
            n: The full name.
            u: The face up two-letter abbreviation.

        Parameters:
        format_spec: The format specification. (str)
        """
        # Use and remove format type if given.
        format_type = format_spec[-1] if format_spec else ''
        if format_type in self.format_types:
            target = self.format_types[format_type]
            format_spec = format_spec[:-1]
        else:
            target = str(self)
        # Add the location text based on the format type.
        if format_type == 'u':
            target += self.loc_txt
        elif format_type != 'd':
            target += self.location_text
        # Return the text based on type with the rest of the format spec applied.
        format_text = '{{:{}}}'.format(format_spec)
        return format_text.format(target)

    def __repr__(self):
        """Create a debugging text representation."""
        return '<TrackingCard {}{}>'.format(self.rank, self.suit)

    def discard(self):
        """Discard the card. (None)"""
        self.deck.discard(self)


class TrackingDeck(Deck):
    """
    A deck that keeps track of the location of the cards in it. (Deck)

    Attributes:
    card_map: A map for finding cards in the deck. (dict of str: card}
    card_re: A regular expression to match a card.
    game: The game the deck is a part of. (Solitaire)
    in_play: The cards currently in play. (list of Card)
    last_order: The order of the deck at the last shuffle. (list of int)
    max_rank: The highest rank in the deck. (int)

    Methods:
    find: Find a card in the deck. (Card)
    gather: Gather cards back into the deck. (None)
    stack: Put the stack in a specified order. (None)

    Overridden Methods:
    __init__
    __repr__
    __str__
    deal
    discard
    force
    """

    def __init__(self, cards = None, game = None, jokers = 0,
        rank_set = STANDARD_RANKS, suit_set = STANDARD_SUITS):
        """
        Fill the deck with a standard set of cards. (None)

        Parameters:
        cards: The initial cards in the deck. (list of Card)
        game: The game the deck is for. (game.Game)
        jokers: The number of jokers in the deck. (int)
        decks: The number of idential decks shuffled together. (int)
        shuffle_size: The number of cards left that triggers a shuffle. (int)
        rank_set: The rank information for cards in the deck. (FeatureSet)
        suit_set: The suit information for cards in the deck. (FeatureSet)
        """
        # Set the general attributes.
        self.game = game
        super(TrackingDeck, self).__init__(cards, jokers, decks = 1, shuffle_size = 0,
            rank_set = rank_set, suit_set = suit_set)
        # Set the calcuated attribute.
        self.max_rank = self.rank_set.chars[-1]
        # Set the default attributes.
        self.in_play = []
        self.last_order = self.cards[:]

    def __repr__(self):
        """Generate a computer readable text representation. (str)"""
        # Get the class names.
        class_name = self.__class__.__name__
        return '<{} for {!r}>'.format(class_name, self.game)

    def __str__(self):
        """Generate a human readable text representation. (str)"""
        # Get the relevant counts.
        cards = len(self.cards)
        in_play = len(self.in_play)
        discards = len(self.discards)
        # Get the relevant plurals.
        card_text = utility.plural(cards, 'card')
        play_text = utility.plural(in_play, 'card')
        discard_text = utility.plural(discards, 'card')
        # Generate the text.
        text = 'Deck of cards with {} {}, plus {} {} in play and {} {} discarded'
        return text.format(cards, card_text, in_play, play_text, discards, discard_text)

    def _initial_cards(self, decks = 1):
        """
        Add in the initial cards for the deck. (None)

        Parameters:
        decks: The number of decks used. (int)
        """
        # Add the base cards.
        self.cards = []
        self.card_map = {}
        for rank in self.rank_set:
            for suit in self.suit_set:
                card = TrackingCard(rank, suit, self, self.rank_set, self.suit_set)
                self.cards.append(card)
                self.card_map[card.up_text] = card
        # Get the joker ranks and suits.
        joker_ranks = self.rank_set.chars[:self.rank_set.skip]
        if self.suit_set.skip:
            joker_suits = self.suit_set.chars
        else:
            joker_suits = self.suit_set.chars[:self.suit_set.skip]
        # Add the jokers.
        for rank in joker_ranks:
            for suit_index in range(self.jokers):
                suit = joker_suits[suit_index % len(card_class.suits)]
                joker = TrackingCard(joker_rank, suit, self, rank_set, suit_set)
                self.cards.append(joker)
                self.card_map[joker.up_text] = joker

    def deal(self, game_location, up = True, card_index = -1):
        """
        Deal a card from the deck. (Card)

        Parameters:
        game_location: The new location of card in the game. (list of Card)
        up: Flag for dealing the card face up. (bool)
        card_index: The location of the card to deal. (int)
        """
        # move the card
        card = self.cards.pop(card_index)
        self.in_play.append(card)
        game_location.append(card)
        # change the cards attributes
        card.game_location = game_location
        card.deck_location = self.in_play
        card.up = up
        # return the card
        return card

    def discard(self, card):
        """
        Discard the game from play. (None)

        Parameters:
        card: The card to discard. (Card)
        """
        # move the card in the deck
        self.in_play.remove(card)
        self.discards.append(card)
        # remove the card from the game
        card.game_location.remove(card)
        # reset the card status
        card.game_location = self.game.deck.discards
        card.deck_location = self.discards

    def find(self, card_text):
        """
        Find a card in the deck. (Card)

        Paramters:
        card_text: The string version of the card. (str)
        """
        return self.card_map[card_text.upper()]

    def force(self, card_text, game_location, up = True):
        """
        Remove a particular card from the deck. (Card)

        Parameters:
        card_text: The string version of the card. (str)
        game_location: The new location of card in the game. (list of Card)
        up: Flag for dealing the card face up. (bool)
        """
        return self.deal(game_location, up = up, card_index = self.cards.index(card_text))

    def shuffle(self, number = None):
        """
        Shuffle the discards back into the deck. (None)

        Parameters:
        number: The FreeCell-style number of the shuffle. (int)
        """
        # Shuffle the cards.
        super(TrackingDeck, self).shuffle(number = number)
        # Reset the card tracking.
        for card in self.cards:
            card.deck_location = self.cards
            card.game_location = self.cards


class MultiTrackingDeck(TrackingDeck):
    """
    A deck that keeps track of the location of multiple duplicate cards. (Deck)

    Attributes:
    decks: The number of decks shuffled together. (int)
    max_rank: The highest rank in the deck. (int)

    Methods:
    parse_location: Parse a location identifier into type and count. (str, int)

    Overridden Methods:
    __init__
    find
    """

    def __init__(self, cards = None, game = None, jokers = 0, decks = 2,
        rank_set = STANDARD_RANKS, suit_set = STANDARD_SUITS):
        """
        Fill the deck with a standard set of cards. (None)

        Parameters:
        cards: The initial cards in the deck. (list of Card)
        game: The game the deck is for. (game.Game)
        jokers: The number of jokers in the deck. (int)
        decks: The number of idential decks shuffled together. (int)
        shuffle_size: The number of cards left that triggers a shuffle. (int)
        rank_set: The rank information for cards in the deck. (FeatureSet)
        suit_set: The suit information for cards in the deck. (FeatureSet)
        """
        # Set the general attributes.
        self.game = game
        self.decks = decks
        super(TrackingDeck, self).__init__(cards, jokers, decks = self.decks, shuffle_size = 0,
            rank_set = rank_set, suit_set = suit_set)
        # Set the calcuated attribute.
        reg_text = '\\b[{}][{}](?:-[twrf]?\d*)?\\b'.format(self.rank_set.chars, self.suit_set.chars)
        self.card_re = re.compile(reg_text, re.IGNORECASE)
        self.max_rank = self.rank_set.chars[-1]
        # Set the default attributes.
        self.in_play = []
        self.last_order = self.cards[:]

    def _initial_cards(self, decks):
        """
        Add in the initial cards for the deck. (None)

        Parameters:
        decks: The number of copies of each card to make. (int)
        """
        # Add the base cards.
        self.cards = []
        self.card_map = collections.defaultdict(list)
        card_number = 0
        for deck in range(self.decks):
            for rank in self.ranks[1:]:
                for suit in self.suits:
                    card = TrackingCard(rank, suit, self, self.rank_set, self.suit_set)
                    self.cards.append(card)
                    self.card_map[card.up_text].append(card)
        # Get the joker ranks and suits.
        joker_ranks = self.rank_set.chars[:self.rank_set.skip]
        if self.suit_set.skip:
            joker_suits = self.suit_set.chars
        else:
            joker_suits = self.suit_set.chars[:self.suit_set.skip]
        # Add the jokers.
        for deck in range(self.decks):
            for rank in joker_ranks:
                for suit_index in range(self.jokers):
                    suit = joker_suits[suit_index % len(card_class.suits)]
                    joker = TrackingCard(joker_rank, suit, self, rank_set, suit_set)
                    self.cards.append(joker)
                    self.card_map[joker.up_text].append(joker)

    def find(self, card_text):
        """
        Find a card in the deck. (Card)

        Paramters:
        card_text: The string version of the card. (str)
        """
        # Check for a location specifier.
        if '-' in card_text:
            card_text, location = card_text.split('-')
        else:
            location, loc_txt, location_text = '', '', ''
        # Parse the location specifier.
        if location:
            location_type, location_count = self.parse_location(location)
        else:
            # Distinguish no location from an empty location.
            location = None
        if location:
            # Get the location from the game.
            if location_type == 'F':
                location = self.game.cells
                location_text = ' in the free cells'
            elif location_type == 'R':
                try:
                    location = self.game.reserve[location_count]
                    # Distinguish single reserve games from multi-reserve games.
                    if len(self.game.reserve) > 1:
                        text = ' in the {} reserve pile'
                        location_text = text.format(utility.number_word(location_count + 1, ordinal = True))
                    else:
                        location_text = ' in the reserve'
                except IndexError:
                    location = []
            elif location_type == 'T':
                try:
                    location = self.game.tableau[location_count]
                    text = ' in the {} tableau pile'
                    location_text = text.format(utility.number_word(location_count + 1, ordinal = True))
                except IndexError:
                    location = []
            else:
                location = self.game.waste
                location_text = ' in the waste'
            # Set the abbreviated location text.
            loc_txt = '-{}'.format(location_type)
            if location_type in 'RT':
                loc_txt = '{}{}'.format(loc_txt, location_count + 1)
        # Find the cards, filtered by any location specified.
        cards = self.card_map[card_text.upper()]
        if location is not None:
            cards = [card for card in cards if card in location]
        # Set (or unset) location text.
        for card in cards:
            card.loc_txt = loc_txt
            card.location_text = location_text
        return cards

    def parse_location(self, location_text):
        """
        Parse a location identifier into type and count. (str, int)

        Parameters:
        location_text: The location identifier. (str)
        """
        location_text = location_text.upper()
        if location_text.isdigit():
            # Number only locations default to the tableau.
            location_type = 'T'
            location_count = int(location_text) - 1
        elif location_text[-1].isdigit():
            location_type = location_text[0]
            location_count = int(location_text[1:]) - 1
        else:
            # Location count defaults to 0.
            location_type = location_text
            location_count = 0
        return location_type, location_count


def by_rank(card):
    """
    A key function for sorting Cards by rank. (int)

    Parameters:
    card: The card being sorted. (Card)
    """
    return card.rank_num

def by_rank_suit(card):
    """
    A key function for sorting Cards by rank then suit. (tuple of int)

    Parameters:
    card: The card being sorted. (Card)
    """
    return (card.rank_num, card.suit_num)

def by_suit(card):
    """
    A key function for sorting Cards by suit. (int)

    Parameters:
    card: The card being sorted. (Card)
    """
    return card.suit_num

def by_suit_rank(card):
    """
    A key function for sorting Cards by suit then rank. (tuple of int)

    Parameters:
    card: The card being sorted. (Card)
    """
    return (card.suit_num, card.rank_num)

def by_value(card):
    """
    A key function for sorting Cards by value. (int)

    Parameters:
    card: The card being sorted. (Card)
    """
    return card.value

def parse_text(text, deck = None):
    """
    Parse text looking for a card. (Card or list of Card)

    Parameters:
    text: The text to parse. (str)
    deck: A deck with rank and suit information (Deck or None)
    """
    if deck is None:
        rank_set = STANDARD_RANKS
        suit_set = STANDARD_SUITS
        re_text = '\\b[{}][{}]\\b'.format(rank_set.chars, suit_set.chars)
        card_re = re.compile(re_text, re.IGNORECASE)
    else:
        rank_set = deck.rank_set
        suit_set = deck.suit_set
        card_re = deck.card_re
    cards = []
    for match in card_re.findall(text):
        cards.append(Card(*match.upper(), rank_set = rank_set, suit_set = suit_set))
    if len(cards) == 1:
        return cards[0]
    else:
        return cards


if __name__ == '__main__':
    # Run the unit testing.
    from t_tests.cards_test import *
    unittest.main()
