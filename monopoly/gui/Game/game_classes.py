
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

from pprint import pprint

# Local Imports

from General.general_classes import DynamicImage
from General import constants as C


class Game(Screen):
    pass


class Player(DynamicImage):
    rectangle = ObjectProperty(None)

    def __init__(self,**kwargs):

        # Save the board location
        self.board_location = kwargs.pop('board_location')
        self.root = kwargs['root']

        # Obtain the pixel value of the board location
        kwargs['ratio_pos'] = C.BOARD_LOCATIONS[self.board_location]
        kwargs['ratio_size'] = (0.05, 0.05)
        
        # Run parent inheritance
        super().__init__(**kwargs)

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

        if start > end:
            end = end + len(list_board_locations)

        for i in range(start+1, end+1):

            # Applying modulus on i
            i = i % len(list_board_locations)

            # Obtain the intermediate board location keys
            board_location_key = list_board_locations[i]
        
            # Obtain the pixel location
            new_pos = C.BOARD_LOCATIONS[board_location_key]

            # Update the pos
            new_centered_pos = (new_pos[0]*self.root.width-self.size[0]/4, new_pos[1]*self.root.height-self.size[1]/4)

            # Create animation object
            move_animation = Animation(pos=new_centered_pos, duration=0.3)

            # Append animation to list
            total_animations += move_animation

        # Start the sequential animations
        total_animations.start(self)

        # Update the ratio_pos of the object
        self.ratio_pos = new_pos

class GameBoard(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.created_player = False
        self.cardInfo = CardInfoPop()

    def roll_dice(self, event):
        dice_dict = {1: '\u2680', 2: '\u2681', 3: '\u2682', 4: '\u2683', 5: '\u2684', 6: '\u2685'}
        dice_1 = random.choice(list(dice_dict.values()))
        dice_2 = random.choice(list(dice_dict.values()))

        self.ids.dice_1.text = f'[b][color=#000000]{dice_1}[/color][/b]'
        self.ids.dice_2.text = f'[b][color=#000000]{dice_2}[/color][/b]'

        step_1 = list(dice_dict.keys())[list(dice_dict.values()).index(dice_1)]
        step_2 = list(dice_dict.keys())[list(dice_dict.values()).index(dice_2)]
        steps = step_1 + step_2

        # Create player
        if self.created_player is False:
            self.player1 = Player(root = self, source='assets/duck.png', board_location='GO')
            self.add_widget(self.player1)
            self.created_player = True
            return 0

        # Obtain the players location and index along all the possible locations
        original_place = self.player1.board_location
        original_id = list(C.BOARD_LOCATIONS.keys()).index(original_place)
        
        # Calculate the final step location
        final_id = (steps + original_id) % len(list(C.BOARD_LOCATIONS.keys()))
        
        # Retrive the key for the location
        final_place = list(C.BOARD_LOCATIONS.keys())[final_id]
        
        # Move the player
        self.player1.move(final_place)

        """
        self.test_images = []
        i = 0

        for line_name in C.BOARD_LOCATIONS.keys():

            for square_name, square_ratio_pos in C.BOARD_LOCATIONS[line_name].items():

                print(f'{square_name}: {square_ratio_pos}')

                self.test_images.append(DynamicImage(
                    source='assets/squirrel.png',
                    ratio_size=(0.05, 0.05),
                    ratio_pos=square_ratio_pos,
                    root=self
                ))

                self.add_widget(self.test_images[i])
                i += 1

        """

    def cardInfoPopup(self):
        self.cardInfo.get_card(self.cardInfo.chance, 'chance')
        self.cardInfo.open()
        Clock.schedule_once(lambda dt: self.cardInfo.dismiss(), 3)


class CardInfoPop(Popup):
    def __init__(self, **kwargs):
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
        self.ids.card_image.source = f"assets/{name}.png"

        return card
