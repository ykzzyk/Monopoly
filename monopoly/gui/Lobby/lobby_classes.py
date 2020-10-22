from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout


class Lobby(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    #def update(self):
    #    print(self.ids.items())


class LobbyGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


