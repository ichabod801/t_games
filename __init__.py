"""
__init__.py

Package initializer for tgames.

todo:
write more real games (trac ticket #69)
    board/chase: fox and geese, tafl
    board/displace: mancala, checkers, chess (wrapper for Sunfish), [battleships]
    board/race: backgammon, snakes and ladders
    board/space: connect four, halma
    card/solitaire: port my solitaire suite
    card/trick: hearts, spades
    card/matching: cribbage, snip snap snorem
    card/shedding: crazy eights, spit
    card/rummy: rummy, tonk
    card/accumulating: war, slapjack
    card/other: ace-jack, peace and love
    dice/jeopardy: [pig], zip
    dice/category: yacht, poker dice
    dice/liar: dudo, liar's dice
    dice/other: solidice, mate
    gambling/dice: craps, mexico
    gambling/cards: black jack, baccarat
    gambling/other: roulette, slot machines
    other/adventure: [hunt the wumpus], adventure
    other/simulation: hamurabi, my space traders (with bot traders), global thermonuclear war
    other/word: hangman, ghost (small word list?)
    other/other: RPS(LS), number guessing game 
clean up
    documentation
    output (one blank line)

Functions:
play: Play some text games. (None)
"""

from __future__ import print_function

import tgames.dice as dice
import tgames.game as game
import tgames.interface as interface
import tgames.player as player

def play():
    """Play some text games. (None)"""
    human = player.Human()
    menu = interface.Interface(human)
    menu.menu()

if __name__ == '__main__':
    play()