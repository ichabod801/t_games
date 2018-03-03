"""
cribbage_game.py

A game of Cribbage.

Constants:
Credits: The credits for Cribbage. (str)

Classes:
Cribbage: A game of Cribbage. (game.Game)
"""


import tgames.game as game
import tgames.cards as cards


CREDITS = """
Game Design: John Suckling
Game Programming: Craig "Ichabod" O'Brien
"""


class Cribbage(game.Game):
	"""
	A game of Cribbage. (game.Game)

	Attributes:
	deck: The deck of cards used in the game. (cards.Deck)
	hands: The player's hands in the game. (dict of str: cards.Hand)
	"""

	aka = ['Crib']
	categories = ['Card Game', 'Matching Game']
	credits = CREDITS
	name = 'Cribbage'

	def set_up(self):
		"""Set up the game. (None)"""
		self.deck = cards.Deck()
		self.deck.shuffle()
		self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
		self.hands['The Crib'] = cards.Hand(self.deck)