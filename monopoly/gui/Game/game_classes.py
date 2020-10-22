from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout


class Game(Screen):
    pass


class GameBoard(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
