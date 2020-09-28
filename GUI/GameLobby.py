from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

import Util.GameLobby


class GameLobby(GridLayout, Screen):
    def __init__(self, **kwargs):
        super(GameLobby, self).__init__(**kwargs)

        self.rows = 3

        self.add_widget(Label(text='[b][color=#FF7F00]Game Lobby[/color][/b]', font_size=180, color=[1, 1, 1, 1],
                              markup=True))

        # Middle Design
        self.middle = GridLayout(cols=2)

        self.middle.add_widget(
            Label(text='[b][color=#FFB533]Players[/color][/b]', font_size=50, color=[1, 1, 1, 1],
                  markup=True))

        self.middle.add_widget(
            Label(text='[b][color=#FFB533]Game Information[/color][/b]', font_size=50, color=[1, 1, 1, 1],
                  markup=True))

        self.add_widget(self.middle)

        # Buttom Design
        self.buttom = GridLayout(cols=3)

        self.buttom.padding = [200, 350, 200, 150]
        self.buttom.spacing = [100, 0]

        self.button_quit = Button(text='[b]Quit[/b]', font_size=50, markup=True)
        self.buttom.add_widget(self.button_quit)

        self.button_join_game = Button(text='[b]Join Game[/b]', font_size=50, markup=True)
        self.buttom.add_widget(self.button_join_game)

        self.button_create_game = Button(text='[b]Create Game[/b]', font_size=50, markup=True)
        self.buttom.add_widget(self.button_create_game)

        self.add_widget(self.buttom)

