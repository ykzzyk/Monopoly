from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

import Util.HomeScreen


class HomeScreen(GridLayout):

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

        self.rows = 7
        self.add_widget(Label(text='Monopoly', font_size=50, height=400))
        self.spacing = [0, 100]
        self.padding = [1000, 0, 1000, 50]

        self.button_play_locally = Button(text='Play Locally', font_size=30)
        self.add_widget(self.button_play_locally)
        self.button_play_lan = Button(text='Play LAN', font_size=30)
        self.add_widget(self.button_play_lan)
        self.button_play_online = Button(text='Play Online', font_size=30)
        self.add_widget(self.button_play_online)
        self.button_options = Button(text='Options', font_size=30)
        self.add_widget(self.button_options)
        self.button_help = Button(text='Help & About', font_size=30)
        self.add_widget(self.button_help)
