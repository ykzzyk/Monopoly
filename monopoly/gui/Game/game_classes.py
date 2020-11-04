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
        self.root = kwargs['root'] # Do not pop (DynamicImage requires it)
        self.current_square = self.root.squares[kwargs.pop('starting_square')]
        self.name = kwargs.pop('player_name')

        # Obtain the pixel value of the board location
        kwargs['ratio_pos'] = self.current_square.physical_location
        kwargs['ratio_size'] = (0.05, 0.05)

        # Run parent inheritance
        super().__init__(**kwargs)
        self.doubles_counter = 0
        self.in_jail_counter = -1
        self.money = 1500

        self.root_size_before = self.root.size

    def move(self, final_square):

        # Obtain the numeric location of the old board location
        start = self.current_square.sequence_id

        # Obtain the numeric location of the new board location
        end = final_square.sequence_id

        # Update the board location
        self.current_square = final_square

        # Create animation for the whole movement
        total_animations = Animation()

        if start >= end:
            end = end + len(self.root.squares)

        for i in range(start + 1, end + 1):
            # Applying modulus on i
            i = i % len(self.root.squares)

            # Obtain the intermediate board location name
            square_name = list(self.root.squares.keys())[i]

            # Obtain the pixel location
            new_pos = self.root.squares[square_name].physical_location

            # Update the pos
            new_centered_pos = (
                new_pos[0] * self.root.width - self.size[0] / 4, new_pos[1] * self.root.height - self.size[1] / 4)

            # Create animation object
            move_animation = Animation(pos=new_centered_pos, duration=0.1)

            # Append animation to list
            total_animations += move_animation

        # Start the sequential animations
        total_animations.start(self)

        # Update the ratio_pos of the object
        self.ratio_pos = new_pos

        return total_animations

    def move_direct(self, final_square):

        # Update the board location
        self.current_square = final_square

        # Obtain the pixel location
        new_pos = final_square.physical_location

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


class GameBoard(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Constructing all the squares
        self.squares = {}
        for square_name in C.BOARD_SQUARE_LOCATIONS.keys():            
            self.squares[square_name] = BoardSquare(square_name)

        # Constructing the players
        player1 = Player(root=self, source='assets/player_icons/duck.png', starting_square='GO', player_name='Duck')
        player2 = Player(root=self, source='assets/player_icons/squirrel.png', starting_square='GO',
                         player_name='Squirrel')

        self.players = [player1, player2]

        for player in self.players:
            self.add_widget(player)

        # Keeping track of the current player
        self.current_player_turn = 0

        # Creating a card info pop instance for later re-usable use
        self.cardInfo = CardInfoPop(root=self)

        # Accessing ids after they are avaliable
        Clock.schedule_once(lambda _: self.ids.player_turn_button.bind(on_release=self.player_start_turn))

    def player_start_turn(self, *args, rolls=None):

        # Update the current turn text
        self.ids.message_player_turn.text = f"[b][color=#800000]Current player {self.players[self.current_player_turn].name}[/color][/b]"

        # If the player has been in jail for three times, then kick them out
        if self.players[self.current_player_turn].in_jail_counter > 1:
            self.players[self.current_player_turn].money -= 50
            self.players[self.current_player_turn].in_jail_counter = -1

        # Else, ask them if they would like to pay to get out or try to roll doubles
        elif self.players[self.current_player_turn].in_jail_counter >= 0:
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
        step_1 = 3
        step_2 = 4

        self.next_player_turn = True

        # If doubles, update counter and make sure the player goes again
        if step_1 == step_2:
            # Updating counter
            self.players[self.current_player_turn].doubles_counter += 1

            # Set an flag for next player turn
            self.next_player_turn = False

        # Check if doubles three times, if so, move the player to jail
        if self.players[self.current_player_turn].doubles_counter == 3:

            # Reset counter
            self.players[self.current_player_turn].doubles_counter = 0

            # Move the player to Jail
            self.players[self.current_player_turn].move_direct('Jail')

            # Update jail attributes
            self.players[self.current_player_turn].in_jail_counter = 0

            # If going to jail, the next player plays instead
            self.next_player_turn = True

        else:
            # Calculate the total
            steps = step_1 + step_2

            # If player is not in jail, let them move
            self.move_player(steps)

    def player_end_turn(self, final_square):

        # Unbinding the stop_animation function
        self.unbind(size=self.stop_animation)

        # Rebinding the roll dice button
        self.ids.player_turn_button.bind(on_release=self.player_start_turn)

        # Processing the action depending on the square name
        # If land on the chance:
        if final_square.is_chance:
            self.cardInfoPopup('chance')

        elif final_square.is_chest:
            self.cardInfoPopup('chest')

        # Update to next player if doubles is not true
        if self.next_player_turn:
            self.players[self.current_player_turn].doubles_counter = 0
            self.current_player_turn = (self.current_player_turn + 1) % len(self.players)

        # Update the next turn text
        self.ids.message_player_turn.text = f"[b][color=#800000]Next is {self.players[self.current_player_turn].name}![/color][/b]"
    
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
        start_id = self.players[self.current_player_turn].current_square.sequence_id

        # Calculate the final step location
        final_id = (steps + start_id) % len(list(self.squares.keys()))

        # Retrive the key for the location
        final_square_name = list(self.squares.keys())[final_id]
        final_square = self.squares[final_square_name]

        # Move player
        move_animation = self.players[self.current_player_turn].move(final_square)

        # Perform bindings
        # Unbind the roll dice button to prevent glitching
        self.ids.player_turn_button.unbind(on_release=self.player_start_turn)

        # Bind the completion of the animation to rebinding the roll_dice function
        move_animation.bind(on_complete=lambda _,__: self.player_end_turn(final_square=final_square))

        # Bind the animation to the size of the window
        #print(f'Binding the stop_animation function for player: {self.players[self.current_player_turn].name}')
        self.stop_animation_flag = False
        self.bind(size=self.stop_animation)

    def roll_out_jail(self):

        # Roll the dice
        # step_1, step_2 = self.roll_dice(None)
        step_1 = 1
        step_2 = 3

        # If they roll doubles, then let them out
        if step_1 == step_2:
            self.players[self.current_player_turn].doubles_counter = 0
            self.players[self.current_player_turn].in_jail_counter = -1
            self.player_start_turn([step_1, step_2])

        # If they don't roll a doubles, they stay in jail and move to the next player
        else:
            self.players[self.current_player_turn].in_jail_counter += 1
            self.current_player_turn = (self.current_player_turn + 1) % len(self.players)
            self.ids.message_next_player_turn.text = f"[b][color=#800000]\n\nNext is {self.players[self.current_player_turn].name}![/color][/b]"
            return 0

    def pay_out_jail(self):

        # Change attributes to make player out of jail
        self.players[self.current_player_turn].money -= 50
        self.players[self.current_player_turn].in_jail_counter = -1

    def cardInfoPopup(self, card_type):
        self.cardInfo.get_card(self.cardInfo.chance, card_type)
        self.cardInfo.open()
        Clock.schedule_once(lambda dt: self.cardInfo.dismiss(), 3)

    def stop_animation(self, *args):

        if self.stop_animation_flag is False:
            # Stop all animations occuring on the currently moving player widget
            Animation.stop_all(self.players[self.current_player_turn])

        # Make sure this function only passes once
        self.stop_animation_flag = True

        # Unbind this function
        self.unbind(size=self.stop_animation)


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


class BoardSquare:

    def __init__(self, square_name):

        # Storing the name of the square
        self.name = square_name

        # Determing if the cart is chest or community
        if "Chance" in self.name:
            self.is_chance = True
        else:
            self.is_chance = False

        if "Chest" in self.name:
            self.is_chest = True
        else:
            self.is_chest = False

        # Obtain the square's pixel_ratio location
        self.physical_location = C.BOARD_SQUARE_LOCATIONS[square_name]

        # Obtain the chronological number of the property
        self.sequence_id = list(C.BOARD_SQUARE_LOCATIONS.keys()).index(square_name)

        # Obtain the square's property cost (if applicable)
        self.cost_value = C.BOARD_SQUARE_COST[square_name]

        # Pre-set values of properties
        self.owner = None
        self.number_of_houses = 0
        self.has_hotel = False
        self.mortgage = False