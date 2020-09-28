from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

import Util.HomeScreen


class HomeScreen(GridLayout, Screen):

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

        self.rows = 8
        self.spacing = [0, 120]
        self.padding = [1000, 100, 1000, 50]

        self.add_widget(Label(text='[b][color=#FF7F00]Monopoly[/color][/b]', font_size=300, color=[1, 1, 1, 1], markup=True))
        self.add_widget(Label(text='[b][color=#FFB533]The Computer Science Edition[/color][/b]', font_size=50, color=[1, 1, 1, 1], markup=True))

        self.button_play_locally = Button(text='[b]Play Locally[/b]', font_size=50, markup=True)
        self.add_widget(self.button_play_locally)
        self.button_play_lan = Button(text='[b]Play LAN[/b]', font_size=50, markup=True)
        self.add_widget(self.button_play_lan)
        self.button_play_online = Button(text='[b]Play Online[/b]', font_size=50, markup=True)
        self.add_widget(self.button_play_online)
        self.button_options = Button(text='[b]Options[/b]', font_size=50, markup=True)
        self.add_widget(self.button_options)
        self.button_help = Button(text='[b]Help & About[/b]', font_size=50, markup=True)
        self.add_widget(self.button_help)

