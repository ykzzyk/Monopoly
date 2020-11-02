from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.properties import DictProperty

import pathlib

import pdb

"""
Lobby (lobby)
    GridLayout (lobby_grid)
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

class LobbyOptions(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num_of_players = 0
        self.game_mode = 'LOCAL'

    def request_new_player_info(self):

        # create popup
        add_player_popup = AddPlayerPopup(root=self)
        add_player_popup.open()

    def add_player(self, player_name, player_icon):

        # Finding the corresponding player_entry
        player_entry = self.ids[f'player{self.num_of_players+1}']

        # Then change the player_info text to whatever you would like
        player_entry.ids['player_text'].text = f'[b][color=#FF7F00]{player_name}\n{self.game_mode}[/color][/b]'
        
        # Adding the player icon to the player info
        player_entry.ids['player_icon']

        # Update the number of players
        self.num_of_players += 1

class AddPlayerPopup(Popup):

    def __init__(self, **kwargs):

        # Get the LobbyOption reference
        self.root = kwargs.pop('root')

        # Get list of all possible player icons
        self.options = DictProperty({})

        new_options = {}

        # Adding all player icons to the self.options dictionary
        for player_icon_fp in pathlib.Path('assets/player_icons').iterdir():
            
            # Getting the display name of the player icon
            player_icon_name = player_icon_fp.stem

            # Populating the new_options dictionary
            new_options[player_icon_name] = str(player_icon_fp)

        # Overwriting the self.options with new_options
        self.options = new_options

        # Apply the inheritance
        super().__init__(**kwargs)
    
    def accept_player_info(self):

        # Obtain the entered information
        input_player_name = self.ids['player_id'].text
        input_player_icon = self.ids['selected_player_icon'].text

        # Pass the information to the root 
        self.root.add_player(input_player_name, input_player_icon)

        # Close the pop-up once acceptance is completed
        self.dismiss()

class PlayerBox(BoxLayout):
    pass

class PlayerEntry(GridLayout):
    pass

class GameInfoBox(BoxLayout):
    pass



