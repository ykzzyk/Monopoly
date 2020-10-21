from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

import Util.HomeScreen
import GUI.GameLobby
import GUI.Feedback


class HomeScreen(GridLayout, Screen):

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

        self.app = App.get_running_app()

        self.rows = 8
        self.spacing = [0, self.app.width / 24]
        self.padding = [self.app.width / 2.88, self.app.width / 28.8, self.app.width / 2.88, self.app.width / 57.6]

        self.add_widget(
            Label(text='[b][color=#FF7F00]Monopoly[/color][/b]', font_size=self.app.width / 9.6, color=[1, 1, 1, 1],
                  markup=True))
        self.add_widget(
            Label(text='[b][color=#FFB533]The Computer Science Edition[/color][/b]', font_size=self.app.width / 57.6,
                  color=[1, 1, 1, 1],
                  markup=True))

        self.button_play_locally = Button(text='[b]Play Locally[/b]',
                                          font_size=self.app.width / 57.6,
                                          markup=True,
                                          on_release=self.game_lobby_page)
        self.add_widget(self.button_play_locally)
        self.button_play_lan = Button(text='[b]Play LAN[/b]', font_size=self.app.width / 57.6, markup=True,
                                      on_release=self.game_lobby_page)
        self.add_widget(self.button_play_lan)
        self.button_play_online = Button(text='[b]Play Online[/b]', font_size=self.app.width / 57.6, markup=True,
                                         on_release=self.game_lobby_page)
        self.add_widget(self.button_play_online)

        self.button_help = Button(text='[b]Help & Feedback[/b]', font_size=self.app.width / 57.6, markup=True,
                                  on_release=self.feedback_page)
        self.add_widget(self.button_help)

        self.button_exit = Button(text='[b]Exit[/b]', font_size=self.app.width / 57.6, markup=True,
                                  on_release=App.get_running_app().stop)
        self.add_widget(self.button_exit)

    def game_lobby_page(self, event):
        self.app.screen_manager.switch_to(GUI.GameLobby.GameLobby(name='game_lobby'))

    def feedback_page(self, event):
        self.app.screen_manager.switch_to(GUI.Feedback.Feedback(name='feedback'))
