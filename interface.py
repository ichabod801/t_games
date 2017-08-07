"""
interface.py
"""

import os
from string import ascii_uppercase

import game
import player

class Interface(object):

    def __init__(self, human):
        self.human = human
        self.load_games()

    def load_games(self):
        # import game files
        for dir_path, dir_name, file_names in os.walk('.'):
            for file_name in file_names:
                if file_name.endswith('_game.py'):
                    __import__(file_name[:-3])
        # categorize game classes
        self.categories = {'sub-categories': {}, 'games': []}
        self.games = {}
        search = [game.Game]
        while search:
            game_class = search.pop()
            # Store game by name
            self.games[game_class.name.lower()] = game_class
            for alias in game_class.aka:
                self.games[alias] = game_class
            # Store game by category
            category = self.categories
            for game_category in game_class.categories:
                if game_category not in category:
                    category['sub-categories'][game_category] = {'sub-categories': {}, 'games': []}
                category = category['sub-categories'][game_category]
            category['games'].append(game_class)
            search.extend(game_class.__subclasses__())

    def menu(self):
        category = self.categories
        previous = []
        while True:
            choices = self.show_menu(category)
            selection = self.human.ask('What is your selection? ')
            if selection.upper() in choices:
                choice = choices[selection.upper()]
                if choice[:-9] in category['sub-categories']:
                    previous.append(category)
                    category = category['sub-categories'][choice[:-9]]
                elif choice == 'Previous Menu':
                    category = previous.pop()
                elif choice == 'Quit':
                    break
                else:
                    self.play_game([game for game in category['games'] if game.name == choice][0])
            elif selection.lower().startswith('play'):
                game_name = selection[4:].strip()
                if game_name in self.games:
                    self.play_game(self.games[game_name])
                    print()
                else:
                    print("I don't know how to play that game.")
            else:
                self.human.tell('That is not a valid selection.')

    def play_game(self, game_class):
        game = game_class(self.human, '')
        while True:
            results = game.play()
            if self.human.ask('Would you like to play again? ').lower() not in ('yes', 'y', '1'):
                break

    def show_menu(self, category):
        categories = sorted([sub_category + ' Category' for sub_category in category['sub-categories']])
        games = sorted([game.name for game in category['games']])
        selections = categories + games
        if category != self.categories:
            selections.append('Previous Menu')
        selections.append('Quit')
        choices = [(excel_column(n + 1), selection) for n, selection in enumerate(selections)]
        for choice, selection in choices:
            print('{}: {}'.format(choice, selection))
        print()
        return dict(choices)

def excel_column(n):
    column = ''
    characters = [''] + list(ascii_uppercase)
    while n:
        column = ascii_uppercase[(n % 26) - 1] + column
        n //= 27
    return column

if __name__ == '__main__':
    interface = Interface(player.Player('Ichabod'))
    interface.menu()


