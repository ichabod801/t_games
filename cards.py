"""
cards.py

Cards and decks of cards for tgames.

Classes:
Card: A standard playing card, with a suit and a rank. (object)
Deck: A standard deck of cards. (object)
"""

class Card(object):

    suits = 'CDHS'
    suit_names = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
    ranks = 'XA23456789TJQK'
    rank_names = ['Joker', 'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']
    rank_names += ['Jack', 'Queen', 'King']

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        rank_name = self.rank_names[self.ranks.index(self.rank)]
        suit_name = self.suit_names[self.suits.index(self.suit)]
        self.name = '{} of {}'.format(rank_name, suit_name)
        self.up = False

    def __repr__(self):
        return 'Card({}, {})'.format(self.rank, self.suit)

    def __str__(self):
        if self.up:
            text = self.rank + self.suit
        else:
            text = '%%'

class Deck(object):

    def __init__(self):
        self.cards = []
        for rank in Card.ranks:
            for suit in Card.suit:
                self.cards.append(Card(rank, suit))
        self.discards = []

    def deal(self, up = False):
        card = self.cards.pop()
        card.up = up
        return card

    def discard(self, card):
        self.discards.append(card)
        card.up = False

    def shuffle(self):
        self.cards.extend(self.discards)
        random.shuffle(self.cards)
        self.discards = []
