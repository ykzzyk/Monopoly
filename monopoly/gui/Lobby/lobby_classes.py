from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout


class Lobby(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class LobbyGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def print_ids(self):
        for key, val in self.ids.items():
            print("key={0}, val={1}".format(key, val))


class PlayerInfo(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
