"""
hangman_game.py

A game of hangman.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
BODY_PARTS: The symbols for the parts of the hanging body, in order. (str)
CREDITS: The credits for Hangman. (str)
DIAGRAM: The format method ready diagram of the hanging body. (str)
NUMBERS: Digits for the guess. (str)
RULES: The rules to Hangman. (str)

Classes:
Hangman: A game of Hangman. (game.Game)
"""


import collections
import os
import random
import re

from .. import game
from .. import utility


BODY_PARTS = 'O|/\\/\\'

CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

DIAGRAM = """
 +---+
 |   |
 {0}   |
{2}{1}{3}  |
{4} {5}  |
     |
+----+
"""

NUMBERS = '1234567890' * 3

RULES = """
Hangman is a word guessing game. Each player takes a turn thinking of a secret
word that the other player must guess letter by letter. To start with, you only
know how many letters are in the word. For each correct guess, you learn how
many times the letter is in the word, and where exactly in the word it is. For
each incorrect letter guessed, another body part is added to the hanging man:
head, torso, arm, arm, leg, leg. If all six body part are added, you fail. If
one player can guess their word with fewer errors than the other, they win the
game. Otherwise, the game is a draw.

COMMANDS:
frequency (freq): Get a frequency list of letters in dictionary words.
guess: Guess the whole word. An incorrect word earns a body part.

OPTIONS:
difficulty= (d=): The difficulty of the game, from 1 to 10 (default = 5).
status (s): See the status of the computer's thinking.
"""


class Hangman(game.Game):
    """
    A game of Hangman. (game.Game)

    Attributes:
    difficulty: A level of difficulty. (int)
    foul: A flag for suspected cheating. (bool)
    frequency: The frequency order of letters in the words. (str)
    guess: The current guess, with blanks. (str)
    guessed_letters: The letters guessed so far. (str)
    incorrect: The number of incorrect guesses so far. (int)
    my_score: The computer's score/the number of incorrect human guesses. (int)
    phase: Is the player answering guesses or guessing? (str)
    possibles: Words that match information given by the human. (list of str)
    rank_dict: The frequency rank for letters in the dictionary words. (dict)
    scored_words: The words for each difficulty level. (dict of int: list)
    status: A flag for showing the computer's thinking. (bool)
    vowels: The frequency order of vowels in the words. (str)
    word: The word the player is trying to guess. (str)
    word_length: The length of the word being guessed. (int)
    words: The known words. (list of str)

    Methods:
    do_frequency: Show the frequency list. (bool)
    do_guess: Guess what the word is. (bool)
    get_word: Get a word for the human to guess. (None)
    player_answer: Handle the player answering if letters are correct. (bool)
    player_guess: Handle the player guessing if letters are correct. (bool)
    score_word: Estimate the difficulty of a word. (int)

    Overridden Methods:
    __str__
    game_over
    player_action
    set_options
    set_up
    """

    aka = ['Hang']
    aliases = {'freq': 'frequency'}
    categories = ['Other Games']
    credits = CREDITS
    name = 'Hangman'
    num_options = 2
    rules = RULES

    def __str__(self):
        """Generate a human readable text representation. (str)"""
        # Generate the hanging man diagram.
        body_parts = BODY_PARTS[:self.incorrect] + ' ' * (6 - self.incorrect)
        text = DIAGRAM.format(*tuple(body_parts))
        # Add the word so far.
        if self.guess:
            text += '\n{}\n'.format(self.guess)
            text += '{}\n'.format(NUMBERS[:self.word_length])
        # Add the guessed letters.
        if self.guessed_letters:
            text += '\nGuessed: {}\n'.format(self.guessed_letters)
        return text

    def do_frequency(self, argument):
        """
        Show the frequency list. (freq)

        This is the order of the letter by their frequency in all of the words in the
        full word list.
        """
        self.human.tell('\n{}\n'.format(self.frequency))
        return True

    def do_gipf(self, arguments):
        """
        Craps gives you a random letter.
        """
        game, losses = self.gipf_check(arguments, ('craps',))
        go = True
        # A win at Craps gives you a random letter.
        if game == 'craps':
            if not losses:
                un_guessed = [letter for letter in set(self.word) if letter not in self.guessed_letters]
                bonus = random.choice(un_guessed)
                self.human.tell('\nYour bonus letter is {!r}.'.format(bonus))
                for letter_index, letter in enumerate(self.word):
                    if letter == bonus:
                        self.guess = self.guess[:letter_index] + letter + self.guess[letter_index + 1:]
        # Respond to any other games.
        else:
            self.human.tell('Tamsk.')

    def do_guess(self, argument):
        """
        Guess what the word is.

        An incorrect guess gets you another body part.
        """
        if self.word == argument.lower():
            # Record a correct guess.
            self.guess = self.word
            self.human.tell('You guessed wisely!')
        else:
            # Give a body part for an incorrect guess.
            self.incorrect += 1
            self.human.tell('You guessed poorly.')

    def game_over(self):
        """Check for end of game. (bool)"""
        # Check for end state.
        if self.incorrect == 6 or '_' not in self.guess:
            # If the computer is done, set things up for the human.
            if self.phase == 'answer':
                self.my_score = self.incorrect
                self.phase = 'guess'
                self.guessed_letters = ''
                self.incorrect = 0
                self.word_length = 0
            # If the human is done, figure out who did best.
            else:
                # Tell the human the word if they failed.
                if self.incorrect == 6:
                    self.human.tell('The word was {!r}.\n'.format(self.word))
                # Display the scores.
                self.scores[self.human.name] = self.incorrect
                self.human.tell('\nYou had {} errors, I had {}.'.format(self.incorrect, self.my_score))
                # Calculate the winner.
                if self.incorrect < self.my_score:
                    # Account for the human using unknown words.
                    if self.foul:
                        self.human.tell("It's a draw because you cheated.")
                        self.win_loss_draw[1] = 1
                    else:
                        self.human.tell('You win!')
                        self.win_loss_draw[0] = 1
                elif self.incorrect > self.my_score:
                    self.human.tell('You lose.')
                    self.win_loss_draw[1] = 1
                else:
                    self.human.tell("Alright, let's call it a draw.")
                    self.win_loss_draw[2] = 1
                return True
        return False

    def get_word(self):
        """Get a word for the human to guess. (None)"""
        # Get the human's word.
        if '_' in self.guess:
            word = self.human.ask('What was the word? ').lower()
        else:
            word = self.guess
        if word not in self.words:
            self.human.tell('I cry foul. That word is not in my dictionary.')
        # Find a word of similar difficulty.
        level = self.score_word(word) - 10 + self.difficulty
        while level not in self.scored_words:
            level += 1
        self.word = random.choice(self.scored_words[level])
        # Set the word-dependent tracking variables.
        self.word_length = len(self.word)
        self.guess = '_' * self.word_length

    def player_action(self, player):
        """
        Handle player actions. (bool)

        Parameters:
        player: The player whose turn it is. (player.Player)
        """
        if self.phase == 'answer':
            # Start computer guessing.
            if not self.word:
                query = '\nThink of a word for me to guess. How many letters are in it? '
                word_length = player.ask_int(query, low = 1)
                if isinstance(word_length, int):
                    self.word_length = word_length
                    self.guess = '_' * self.word_length
                    self.word = '???'
                    self.possibles = [word for word in self.words if len(word) == self.word_length]
                else:
                    return self.handle_cmd(word_length)
            # Handle computer guessing.
            self.human.tell(self)
            return self.player_answer()
        else:
            # Start human guessing.
            if not self.word_length:
                self.get_word()
            # Handle human guessing.
            self.human.tell(self)
            return self.player_guess()

    def player_answer(self):
        """Handle the player answering if letters are correct. (bool)"""
        # Update the human on the computer's status.
        if self.status:
            count = len(self.possibles)
            if count:
                self.human.tell('I have narrowed it down to {} words.'.format(count))
            else:
                self.human.tell('I think you are cheating.')
        if len(self.possibles) == 1:
            # Guess the only possible word.
            correct = self.human.ask('Is the word {!r}? '.format(self.possibles[0])).lower()
            if correct in utility.YES:
                self.guess = self.possibles[0]
            else:
                self.incorrect += 1
                self.possibles = []
            return False
        elif self.possibles:
            # Get the frequency of unknown letters in possible words.
            sub_freq = collections.Counter()
            valid = []
            for char_index, char in enumerate(self.guess):
                if char == '_':
                    sub_freq += collections.Counter(word[char_index] for word in self.possibles)
                    valid.append(char_index + 1)
            # Guess the most freuent unknown letter in the possible words.
            guess = sub_freq.most_common(1)[0][0]
        else:
            # If the word isn't in the dictionary, guess by overall frequency.
            self.foul = True
            for guess in self.frequency:
                if guess not in self.guessed_letters:
                    break
            valid = [index + 1 for index, letter in enumerate(self.guess) if letter == '_']
        query = '\nI guess {0!r}. Please enter the indexes where {0!r} occurs in the word: '.format(guess)
        matches = self.human.ask_int_list(query, valid = valid, cmd = False, valid_lens = range(10))
        self.guessed_letters += guess
        # Readjust possibles based on the results of the guess.
        if not matches:
            self.incorrect += 1
            self.possibles = [word for word in self.possibles if guess not in word]
        else:
            # Create a regular expression to match new possibles.
            for match in matches:
                match = int(match) - 1
                self.guess = self.guess[:match] + guess + self.guess[match + 1:]
            not_letter = '[^{}]'.format(guess)
            reg_text = self.guess.replace('_', not_letter)
            regex = re.compile(reg_text)
            # Update possibles using the regular expression.
            self.possibles = [word for word in self.possibles if regex.match(word)]

    def player_guess(self):
        """Handle the player guessing if letters are correct. (bool)"""
        # Get the player's guess.
        guess = self.human.ask('What letter do you guess? ')
        # Handle non-guesses.
        if len(guess) != 1 or guess.lower() not in 'abcdefghijklmnopqrstuvwxyz':
            return self.handle_cmd(guess)
        # Check for repeated guesses.
        if guess in self.guessed_letters:
            self.human.tell('You already guessed {!r}, try again.'.format(guess))
            return True
        # Handle the guessed letter.
        self.guessed_letters += guess
        if guess in self.word:
            for letter_index, letter in enumerate(self.word):
                if letter == guess:
                    self.guess = self.guess[:letter_index] + letter + self.guess[letter_index + 1:]
        else:
            self.incorrect += 1

    def score_word(self, word):
        """
        Estimate the difficulty of a word. (int)

        Parameters:
        word: The word to get a difficulty score for. (str)
        """
        letters = len(word)
        worst = min(self.rank_dict[letter] for letter in word.lower())
        return worst - letters

    def set_options(self):
        """Set the available game options. (None)"""
        self.option_set.add_option('status', ['s'],
            question = "Would you like updates on the computer's thinking? bool")
        self.option_set.add_option('difficulty', ['diff', 'd'], int, valid = range(1, 11), default = 5,
            question = "What difficulty level from 1 to 10 would you like to play at (return for 5)? ")

    def set_up(self):
        """Set up the game. (None)"""
        # Load the words.
        if not hasattr(self, 'words'):
            self.human.tell('Loading words...')
            letter_count = collections.Counter()
            self.words = []
            with open(os.path.join(utility.LOC, self.interface.word_list)) as word_file:
                for word in word_file:
                    self.words.append(word.strip())
                    letter_count += collections.Counter(word.strip().lower())
            # Get the frequencies.
            self.frequency = ''.join([letter for letter, count in letter_count.most_common()])
            self.vowels = ''.join([letter for letter in self.frequency if letter in 'aeiou']) + 'y'
            # Score the words.
            self.rank_dict = {letter: letter_rank + 1 for letter_rank, letter in enumerate(self.frequency)}
            self.scored_words = collections.defaultdict(list)
            for word in self.words:
                self.scored_words[self.score_word(word)].append(word)
        # Set up the game variables.
        self.phase = 'answer'
        self.word = ''
        self.guess = ''
        self.guessed_letters = ''
        self.incorrect = 0
        self.word_length = 0
        self.foul = False
