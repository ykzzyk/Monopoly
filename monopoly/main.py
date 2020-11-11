import os
import sys
import pathlib

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.graphics import *
from kivy.properties import NumericProperty
import webbrowser

import pdb

# Imports tools
import tools

# Importing all GUI
import gui

# TODO:
"""
    - Auction Bidding
    - Trade
    - Buy Houses and Hotels
    - Rent Update
    - Sell Houses and Hotels
    - Mortgage/Unmortgage properties
    - Player Bankrupt/Win Condition
"""

cwd = pathlib.Path(os.path.abspath(__file__)).parent
gui_widgets = cwd / 'gui'

tools.fh.import_dir(gui_widgets)


class Start(Screen):
    pass


class Feedback(Screen):
    def send_email(self, event):
        webbrowser.open("mailto:yzhang5@mail.stmarytx.edu", new=1)
        print('open email successfully!')


class Home(Screen):
    pass


class WindowManager(ScreenManager):

    def __init__(self, **kwargs):

        # Adding the no transition argument
        kwargs['transition'] = NoTransition()

        super().__init__(**kwargs)

    def start_game(self):

        # Start the game only if 2 or more players have been added
        if len(list(self.ids['lobby'].ids['lobby_options'].players.keys())) > 1:

            # Change to the next screen
            self.current = 'game'

            # Pass the players from the lobby to the game
            self.ids['game'].ids["game_board"].add_players(self.ids['lobby'].ids['lobby_options'].players)

        else:

            # Notify that players have not been added
            pass


class MonopolyApp(App):

    def build(self):
        Window.fullscreen = 0
        Window.clearcolor = (1, 1, 1, 1)
        self.title = 'Monopoly'

        return kv


if __name__ == "__main__":
    # Loading the primary application .kv file
    kv = Builder.load_file("kivy.kv")
    MonopolyApp().run()
