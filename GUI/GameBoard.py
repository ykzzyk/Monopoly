from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window

import Util.GameBoard


class GameBoard(GridLayout, Screen):
    def __init__(self, **kwargs):
        super(GameBoard, self).__init__(**kwargs)

        self.cols = 2

        # self.add_widget(Button(text='[b][color=#FF7F00]Map[/color][/b]', font_size=180, color=[1, 1, 1, 1],
        #                        markup=True, width=Window.height))

        self.add_widget(Button(text='[b][color=#FF7F00]Map[/color][/b]', markup=True))#, width=self.width))

        self.info = GridLayout(rows=2)

        self.info.add_widget(
            Button(text='[b][color=#FFB533]Players Information[/color][/b]', font_size=50, color=[1, 1, 1, 1],
                   markup=True))

        self.info.add_widget(
            Button(text='[b][color=#FFB533]History[/color][/b]', font_size=50, color=[1, 1, 1, 1],
                   markup=True))

        self.add_widget(self.info)
