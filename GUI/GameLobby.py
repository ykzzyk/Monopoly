from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

import GUI.HomeScreen
import GUI.GameBoard

import Util.GameLobby


class GameLobby(GridLayout, Screen):
    def __init__(self, **kwargs):
        super(GameLobby, self).__init__(**kwargs)

        self.app = App.get_running_app()

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

        self.button_quit = Button(text='[b]Quit[/b]', font_size=50, markup=True, on_press=self.home_screen_page)
        self.buttom.add_widget(self.button_quit)

        self.button_join_game = Button(text='[b]Join Game[/b]', font_size=50, markup=True, on_press=self.game_board_page)
        self.buttom.add_widget(self.button_join_game)

        self.button_create_game = Button(text='[b]Create Game[/b]', font_size=50, markup=True, on_press=self.game_board_page)
        self.buttom.add_widget(self.button_create_game)

        self.add_widget(self.buttom)

    def home_screen_page(self, event):
        self.app.screen_manager.switch_to(GUI.HomeScreen.HomeScreen(name='home_screen'))

    def game_board_page(self, event):
        self.app.screen_manager.switch_to(GUI.GameBoard.GameBoard(name='game_board'))