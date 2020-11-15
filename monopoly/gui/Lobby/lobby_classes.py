from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.properties import DictProperty
from kivy.clock import Clock

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

        self.players = {}
        self.game_mode = 'LOCAL'
        self.taken_options = []

    def request_new_player_info(self):

        # Determine if there is still room for a new player
        if len(list(self.players.keys())) >= 8:
            return 

        # create popup
        add_player_popup = AddPlayerPopup(root=self)
        
        # Open the popup
        add_player_popup.open()

    def add_player(self, player_name, player_icon):

        # Finding the corresponding player_entry
        player_entry = self.parent.parent.ids['lobby_inter_grid'].ids['player_box'].ids[f'player{len(list(self.players.keys()))+1}']

        # Then change the player_info text to whatever you would like
        player_entry.ids['player_text'].text = f'[b][color=#FF0000]{player_name}\n{self.game_mode}[/color][/b]'
        
        # Adding the player icon to the player info
        player_entry.ids['player_icon'].image_source = "assets/player_icons/" + player_icon + ".png"

        # Remove the selected player icon to prevent people using the same icon
        self.taken_options.append(player_icon)

        # Saving the information of the players into the lobby_options
        self.players[player_name] = player_icon

        # Make the start_game_button enabled if the number of players >= 2
        if len(self.players) >= 2:
            self.ids.start_game_button.disabled = False
        else:
            self.ids.start_game_button.disabled = True

class AddPlayerPopup(Popup):

    def __init__(self, **kwargs):

        # Get the LobbyOption reference
        self.root = kwargs.pop('root')

        # Keep a variable to ensure that no spamming affects the addition of players
        self.used = False

        # Get list of all possible player icons
        self.options = DictProperty({})

        new_options = {}

        # Adding all player icons to the self.options dictionary
        for player_icon_fp in pathlib.Path('assets/player_icons').iterdir():
            
            # Getting the display name of the player icon
            player_icon_name = player_icon_fp.stem

            # Check if the player icon has been already taken
            if player_icon_name in self.root.taken_options:
                continue

            # Populating the new_options dictionary
            new_options[player_icon_name] = str(player_icon_fp)

        # Make the first avaliable image show
        first_icon = list(new_options.keys())[0]
        Clock.schedule_once(lambda _: self.change_default_values(default_icon_name=first_icon),0)

        # Overwriting the self.options with new_options
        self.options = new_options

        # Apply the inheritance
        super().__init__(**kwargs)

    def change_default_values(self, default_icon_name):

        # Making the default icon the first available icon
        self.ids.selected_player_icon.text = default_icon_name

        # Make the default player name text increase everytime 
        self.ids.player_id.text = f'player{len(list(self.root.players.keys()))+1}'
    
    def accept_player_info(self):

        # If accepting player info, the popup window has been used
        if self.used is False:

            # Make sure that single use
            self.used = True

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



