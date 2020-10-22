from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

"""
Lobby (lobby)
    LobbyGrid (lobby_grid)
        Label (lobby_title)
        LobbyInterGrid (lobby_inter_grid)
            PlayerBox (player_box)
                PlayerEntry (player1)
                    PlayerInfo (player_info)
                        Label (player_text)
                        PlayerIcon (player_icon)
                    Button (ready_button)
            GameInfoBox (game_info_box)
                Label (game_info_title)
                Label (game_info)
                Label (log_info)
        LobbyOptions(lobby_options)
            Button (quit_button)
            Button (add_player_button)
            Button (start_game_button)
"""

class Lobby(Screen):
    pass

class LobbyGrid(GridLayout):
    pass

class LobbyOptions(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num_of_players = 0

    def add_player(self):

        # Selecting the player ID
        player_id = f'player{self.num_of_players+1}'

        # Find the next avaliable PlayerEntry
        player_entry = self.parent.ids.lobby_inter_grid.ids.player_box.ids[player_id]

        # create popup
        add_player_popup = AddPlayerPopup()
        add_player_popup.open()

        # Then change the player_info text to whatever you would like
        player_entry.ids.player_info.ids.player_text.text = '[b][color=#FF7F00]Test Player\nTest IP Address[/color][/b]'
        self.num_of_players += 1

class AddPlayerPopup(Popup):
    pass

class PlayerBox(BoxLayout):
    pass

class PlayerEntry(GridLayout):
    pass

class PlayerInfo(GridLayout):
    pass

class GameInfoBox(BoxLayout):
    pass



