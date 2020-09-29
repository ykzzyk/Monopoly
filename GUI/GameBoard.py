from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window

import GUI.HomeScreen

import Util.GameBoard


class GameBoard(GridLayout, Screen):
    def __init__(self, **kwargs):
        super(GameBoard, self).__init__(**kwargs)

        self.app = App.get_running_app()

        self.cols = 2

        self.add_widget(Button(text='[b][color=#FF7F00]Map[/color][/b]', markup=True, size_hint_x=2, on_press=self.home_screen_page))

        self.info = GridLayout(rows=2)

        self.info.add_widget(
            Button(text='[b][color=#FFB533]Players Information[/color][/b]', font_size=50, color=[1, 1, 1, 1],
                   markup=True))

        self.info.add_widget(
            Button(text='[b][color=#FFB533]History[/color][/b]', font_size=50, color=[1, 1, 1, 1],
                   markup=True))

        self.add_widget(self.info)

    def home_screen_page(self, event):
        self.app.screen_manager.switch_to(GUI.HomeScreen.HomeScreen(name='home_screen'))
