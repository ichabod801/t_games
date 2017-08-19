"""
cards.py

Cards and decks of cards for tgames.

Classes:
Card: A standard playing card, with a suit and a rank. (object)
Deck: A standard deck of cards. (object)
"""

class Card(object):
    """
    A standared playing card, with a suit and a rank. (object)

    The rank and suit attributes are length 1.

    Class Attributes:
    suits: The suit characters. (str)
    suit_names: The names of the suits. (list of str)
    ranks: The rank characters. (str)
    rank_names: The names of the ranks. (list of str)

    Attributes:
    name: The full name of the card. (str)
    rank: The rank of the card. (str)
    suit: The suit of the card. (str)
    up: A flag for the card being face up. (str)

    Overridden Methods:
    __init__
    __repr__
    __str__
    """

    suits = 'CDHS'
    suit_names = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
    ranks = 'XA23456789TJQK'
    rank_names = ['Joker', 'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']
    rank_names += ['Jack', 'Queen', 'King']

    def __init__(self, rank, suit):
        """
        Set up the card. (None)

        Parameters:
        rank: The rank of the card. (str)
        suit: The suit of the card. (str)
        """
        # Specified paramters.
        self.rank = rank[0]
        self.suit = suit[0]
        # Calculate the name.
        rank_name = self.rank_names[self.ranks.index(self.rank)]
        suit_name = self.suit_names[self.suits.index(self.suit)]
        self.name = '{} of {}'.format(rank_name, suit_name)
        # Default face down.
        self.up = False

    def __repr__(self):
        """Debugging text representation. (str)"""
        return 'Card({}, {})'.format(self.rank, self.suit)

    def __str__(self):
        """Human readable text representation. (str)"""
        if self.up:
            text = self.rank + self.suit
        else:
            text = '%%'

class Deck(object):
    """
    A standard deck of cards. (object)

    Attributes:
    cards: The cards in the deck. (list of card)
    discards: The cards in the discard pile. (list of card)

    Methods:
    deal: Deal a card from the deck. (Card)
    discard: Discard a card to the discard pile. (None)
    shuffle: Shuffle the discards back into the deck. (None)
    """

    def __init__(self, jokers = 0):
        """
        Fill the deck with a standard set of cards. (None)

        Parameters:
        jokers: The number of jokers in the deck.
        """
        # Add the standard cards.
        self.cards = []
        for rank in Card.ranks:
            for suit in Card.suit:
                self.cards.append(Card(rank, suit))
        # Add any requested jokers.
        for suit_index in range(jokers):
            self.cards.append(Card('X', Card.suits[suit_index % len(Card.suits)]))
        # Start with an empty discard pile.
        self.discards = []

    def deal(self, up = False):
        """
        Deal a card from the deck. (Card)

        Parameters:
        up: A flag for dealing the card face up. (bool)
        """
        card = self.cards.pop()
        card.up = up
        return card

    def discard(self, card):
        """
        Discard a card to the discard pile. (None)

        Parameters:
        card: The card to discard. (Card)
        """
        self.discards.append(card)
        card.up = False

    def shuffle(self):
        """Shuffle the discards back into the deck. (None)"""
        self.cards.extend(self.discards)
        random.shuffle(self.cards)
        self.discards = []
