from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout


class Lobby(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class LobbyGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title_text = '[b][color=#FF7F00]Hello[/color][/b]'


class PlayerInfo(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
