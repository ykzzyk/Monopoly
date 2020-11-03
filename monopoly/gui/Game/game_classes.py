from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle, Line
from kivy.animation import Animation

import queue
import random
import time
import functools

from pprint import pprint

# Local Imports

from General.general_classes import DynamicImage
from General import constants as C


class Game(Screen):
    pass


class Player(DynamicImage):
    rectangle = ObjectProperty(None)

    def __init__(self, **kwargs):

        # Save the board location
        self.board_location = kwargs.pop('board_location')
        self.root = kwargs['root']
        self.name = kwargs.pop('player_name')

        # Obtain the pixel value of the board location
        kwargs['ratio_pos'] = C.BOARD_LOCATIONS[self.board_location]
        kwargs['ratio_size'] = (0.05, 0.05)

        # Run parent inheritance
        super().__init__(**kwargs)
        self.doubles_counter = 0
        self.in_jail = False
        self.in_jail_counter = -1
        self.money = 1500

        self.root_size_before = self.root.size

    def move(self, new_board_location):

        # Obtain the list of the board locations
        list_board_locations = list(C.BOARD_LOCATIONS.keys())

        # Obtain the numeric location of the old board location
        start = list_board_locations.index(self.board_location)

        # Obtain the numeric location of the new board location
        end = list_board_locations.index(new_board_location)

        # Update the board location
        self.board_location = new_board_location

        # Create animation for the whole movement
        total_animations = Animation()

        if start >= end:
            end = end + len(list_board_locations)

        for i in range(start + 1, end + 1):
            # Applying modulus on i
            i = i % len(list_board_locations)

            # Obtain the intermediate board location keys
            board_location_key = list_board_locations[i]

            # Obtain the pixel location
            new_pos = C.BOARD_LOCATIONS[board_location_key]

            # Update the pos
            new_centered_pos = (
                new_pos[0] * self.root.width - self.size[0] / 4, new_pos[1] * self.root.height - self.size[1] / 4)

            # Create animation object
            move_animation = Animation(pos=new_centered_pos, duration=0.1)

            # Append animation to list
            total_animations += move_animation

        # Start the sequential animations
        total_animations.start(self)

        # Bind the animation to the size of the window
        self.stop_animation_flag = False
        self.binding_function = lambda x, y: self.stop_animation(new_pos, x, y)

        # total_animations.bind(on_complete=unbinding_function)
        self.root.bind(size=self.binding_function)

        # Update the ratio_pos of the object
        self.ratio_pos = new_pos

    def move_direct(self, destination):

        # Update the board location
        self.board_location = destination

        # Obtain the pixel location
        new_pos = C.BOARD_LOCATIONS[destination]

        # Update the pos
        new_centered_pos = (
            new_pos[0] * self.root.width - self.size[0] / 4, new_pos[1] * self.root.height - self.size[1] / 4
        )

        # Create animation object
        move_animation = Animation(pos=new_centered_pos, duration=0.3)

        # Start the sequential animations
        move_animation.start(self)

        # Update the ratio_pos of the object
        self.ratio_pos = new_pos

    def stop_animation(self, final_pos, instance, value):

        if self.stop_animation_flag is False:
            # Stop all animations occuring on the self player widget
            Animation.stop_all(self)

            # Set the final pos to the widget
            self.ratio_pos = final_pos

        # Make sure this function only passes once
        self.stop_animation_flag = True

        # Unbind this function
        self.root.unbind(size=self.binding_function)


class GameBoard(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        player1 = Player(root=self, source='assets/player_icons/duck.png', board_location='GO', player_name='Duck')
        player2 = Player(root=self, source='assets/player_icons/squirrel.png', board_location='GO',
                         player_name='Squirrel')

        self.players = [player1, player2]

        for player in self.players:
            self.add_widget(player)

        self.current_player_turn = 0

        self.cardInfo = CardInfoPop(root=self)

    def roll_dice(self, event):
        dice_dict = {1: '\u2680', 2: '\u2681', 3: '\u2682', 4: '\u2683', 5: '\u2684', 6: '\u2685'}
        dice_1 = random.choice(list(dice_dict.values()))
        dice_2 = random.choice(list(dice_dict.values()))

        self.ids.dice_1.text = f'[b][color=#000000]{dice_1}[/color][/b]'
        self.ids.dice_2.text = f'[b][color=#000000]{dice_2}[/color][/b]'

        step_1 = list(dice_dict.keys())[list(dice_dict.values()).index(dice_1)]
        step_2 = list(dice_dict.keys())[list(dice_dict.values()).index(dice_2)]

        return step_1, step_2

    def move_player(self, steps):

        # Obtain the players location and index along all the possible locations
        original_place = self.players[self.current_player_turn].board_location
        original_id = list(C.BOARD_LOCATIONS.keys()).index(original_place)

        # Calculate the final step location
        final_id = (steps + original_id) % len(list(C.BOARD_LOCATIONS.keys()))

        # Retrive the key for the location
        final_place = list(C.BOARD_LOCATIONS.keys())[final_id]

        # Move player
        self.players[self.current_player_turn].move(final_place)

    def player_turn(self, rolls=None):

        # If player in jail, perform jail behavior
        if self.players[self.current_player_turn].in_jail:

            # If the player has been in jail for three times, then kick them out
            if self.players[self.current_player_turn].in_jail_counter > 2:
                self.players[self.current_player_turn].money -= 50
                self.players[self.current_player_turn].in_jail_counter = -1

            # Else, ask them if they would like to pay to get out or try to roll doubles
            else:
                self.jail_select = JailSelectPop(root=self, current_player=self.players[self.current_player_turn].name)
                self.jail_select.open()

                return 0

        '''
        # Roll the dice and get their values
        if rolls is None:
            step_1, step_2 = self.roll_dice(None)
        else:
            step_1, step_2 = rolls
        '''
        step_1 = 2
        step_2 = 2

        next_player_turn = True

        # If doubles, update counter and make sure the player goes again
        if step_1 == step_2:
            # Updating counter
            self.players[self.current_player_turn].doubles_counter += 1

            # Set an flag for next player turn
            next_player_turn = False

        # else:
        # Next player's turn

        # Check if doubles three times, if so, move the player to jail
        if self.players[self.current_player_turn].doubles_counter == 3:

            # Reset counter
            self.players[self.current_player_turn].doubles_counter = 0

            # Move the player to Jail
            self.players[self.current_player_turn].move_direct('Jail')

            # Update jail attributes
            self.players[self.current_player_turn].in_jail = True
            self.players[self.current_player_turn].in_jail_counter = 0

            # If going to jail, the next player plays instead
            next_player_turn = True

        else:
            # Calculate the total
            steps = step_1 + step_2

            # Update the current turn text
            self.ids.message_current_player_turn.text = f"[b][color=#800000]Current player {self.players[self.current_player_turn].name}[/color][/b]"

            # If player is not in jail, let them move
            self.move_player(steps)

        # Update to next player if doubles is not true
        if next_player_turn:
            self.players[self.current_player_turn].doubles_counter = 0
            self.current_player_turn = (self.current_player_turn + 1) % len(self.players)

        # Update the next turn text
        self.ids.message_next_player_turn.text = f"[b][color=#800000]\n\nNext is {self.players[self.current_player_turn].name}![/color][/b]"

    def roll_out_jail(self):

        # Roll the dice
        # step_1, step_2 = self.roll_dice(None)
        step_1 = step_2 = 2

        # If they roll doubles, then let them out
        if step_1 == step_2:
            self.players[self.current_player_turn].doubles_counter = 0
            self.players[self.current_player_turn].in_jail = False
            self.players[self.current_player_turn].in_jail_counter = -1
            self.player_turn([step_1, step_2])

        # If they don't roll a doubles, they stay in jail and move to the next player
        else:
            self.players[self.current_player_turn].in_jail_counter += 1
            self.current_player_turn = (self.current_player_turn + 1) % len(self.players)
            self.ids.message_next_player_turn.text = f"[b][color=#800000]\n\nNext is {self.players[self.current_player_turn].name}![/color][/b]"
            return 0

    def pay_out_jail(self):

        # Change attributes to make player out of jail
        self.players[self.current_player_turn].money -= 50
        self.players[self.current_player_turn].in_jail = False
        self.players[self.current_player_turn].in_jail_counter = -1

    def cardInfoPopup(self):
        self.cardInfo.get_card(self.cardInfo.chance, 'chance')
        self.cardInfo.open()
        Clock.schedule_once(lambda dt: self.cardInfo.dismiss(), 3)


class CardInfoPop(Popup):
    def __init__(self, **kwargs):
        # Obtain root reference
        self.root = kwargs.pop('root')

        super().__init__(**kwargs)

        self.chance = queue.Queue(maxsize=0)
        self.chance.put('ADVANCE TO ST.CHARLES PLACE.\nIF YOU PASS GO, COLLECT $200.')
        self.chance.put(
            'MAKE GENERAL REPAIRS\nON ALL YOUR PROPERTY:\nFOR EACH HOUSE PAY $25.\nFOR EACH HOTEL, PAY $100.')
        self.chance.put('GO BACK THREE SPACES.')
        self.chance.put('GET OUT OF JAIL FREE.')
        self.chance.put('ADVANCE TO BOARDWALK.')
        self.chance.put('TAKE A TRIP TO READING\nRAILROAD. IF YOU PASS GO,\nCOLLECT $200.')
        self.chance.put('YOUR BULIDING LOAN MATURES.\nCOLLECT $150.')
        self.chance.put('ADVANCE TO ILLINOIS AVENUE.\nIF YOU PASS GO, COLLECT $200.')
        self.chance.put('ADVANCE TO THE NEAREST\nUTILITY.')
        self.chance.put('GO DIRECTLY TO JAIL.\nDO NOT COLLECT $200.')
        self.chance.put('SPEEDING FINE. PAY $15.')
        self.chance.put('ADVANCE TO THE NEXT\nRAILROAD.')
        self.chance.put('YOU HAVE BEEN ELECTED\nCHAIRMAN OF THE BOARD.\nPAY EACH PLAYER $50.')

        self.chest = queue.Queue(maxsize=0)
        self.chest.put('LIFE INSURANCE MATURES.\nCOLLECT $100.')
        self.chest.put('YOU INHERIT $100.')
        self.chest.put('SCHOOL FEES. PAY $50.')
        self.chest.put('GET OUT OF JAIL FREE.')
        self.chest.put('INCOME TAX REFUND.\nCOLLECT $20.')
        self.chest.put('HOLIDAY FUND MATURES.\nCOLLECT $100.')
        self.chest.put("DOCTOR'S FEES. PAY $50.")
        self.chest.put('HOSPITAL FEES. PAY $100.')
        self.chest.put('GO DIRECTLY TO JAIL.\nDO NOT COLLECT $200.')
        self.chest.put("COLLECT $25 CONSULTANCY FEE.\nIT'S YOUR BIRTHDAY.\nCOLLECT $10 FROM EACH PLAYER.")
        self.chest.put('FROM SALE OF STOCK, YOU GET $50.')
        self.chest.put('YOU HAVE WON SECOND PRIZE\nIN A BEAUTY CONTEST.\nCOLLECT $10.')
        self.chest.put('YOU ARE ASSESSED FOR STREET REPAIRS:\nPAY $40 PER HOUSE AND $115 PER HOTEL YOU OWN.')
        self.chest.put('ADVANCE TO GO. COLLECT $200.')
        self.chest.put('BANK ERROR IN YOUR FAVOR.\nCOLLECT $200.')

    def get_card(self, cards, name):
        card = cards.get()
        cards.put(card)

        # Change the card texts
        self.ids.card_info.text = f'[b][color=#000000]{card}[/color][/b]'
        # Change the display image
        self.ids.card_image.source = f"assets/background/{name}.png"

        return card


class JailSelectPop(Popup):
    def __init__(self, **kwargs):
        # Obtain root reference
        self.root = kwargs.pop('root')
        self.current_player = kwargs.pop('current_player')

        super().__init__(**kwargs)

        self.ids.current_player_name.text = f"[b][color=#000000]{self.current_player}, do you want to PAY $50 or ROLL DOUBLES to get out of jail?[/b][/color]"

    def player_decision(self, choice):

        if choice == 'roll':
            # Execute the roll_out_jail from the gameboard
            self.root.roll_out_jail()
        elif choice == 'pay':
            self.root.pay_out_jail()

        # Dismiss the popup
        self.dismiss()
