
from kivy.uix.gridlayout import GridLayout

class PlayerInfo(GridLayout):
    def __init__(self, **kwargs):
        super(PlayerInfo, self).__init__(**kwargs)
        self.text_value = "Hello"