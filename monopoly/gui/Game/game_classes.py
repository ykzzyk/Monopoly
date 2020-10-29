from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle, Line
import queue
import random


class Game(Screen):
    pass


class GameMap(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        # self.rectangle = Rectangle(pos=(500, 500), size=(self.width, self.width), source='assets/duck.png')
        # self.canvas.add(self.rectangle)


class Player(Label):
    rectangle = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # self.rectangle = Rectangle(pos=self.pos, size=(self.width, self.width), source='assets/duck.png')
        # self.canvas.add(self.rectangle)

    def move(self, pos):
        self.pos = pos
        self.rectangle.pos = self.pos


class GameBoard(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cardInfo = CardInfoPop()
        game_map = GameMap()
        self.add_widget(game_map)

        self.player1 = Player()
        self.add_widget(self.player1)

        print(self.width)

        # self.circle1 = Line(circle=(self.width * 1.2, self.width * 1.2, self.width // 4), close=True, width=2)
        # self.canvas.add(self.circle1)
        #
        # self.circle2 = Line(circle=(self.width * 3.1, self.width * 1.2, self.width // 4), close=True, width=2)
        # self.canvas.add(self.circle2)
        #
        # self.circle3 = Line(circle=(self.width * 4.6, self.width * 1.2, self.width // 4), close=True, width=2)
        # self.canvas.add(self.circle3)
        #
        # self.circle4 = Line(circle=(self.width * 6.05, self.width * 1.2, self.width // 4), close=True, width=2)
        # self.canvas.add(self.circle4)
        #
        # self.circle5 = Line(circle=(self.width * 7.5, self.width * 1.2, self.width // 4), close=True, width=2)
        # self.canvas.add(self.circle5)
        #
        # self.circle6 = Line(circle=(self.width * 9, self.width * 1.2, self.width // 4), close=True, width=2)
        # self.canvas.add(self.circle6)
        #
        # self.circle7 = Line(circle=(self.width * 10.5, self.width * 1.2, self.width // 4), close=True, width=2)
        # self.canvas.add(self.circle7)
        #
        # self.circle8 = Line(circle=(self.width * 11.95, self.width * 1.2, self.width // 4), close=True, width=2)
        # self.canvas.add(self.circle8)
        #
        # self.circle9 = Line(circle=(self.width * 13.45, self.width * 1.2, self.width // 4), close=True, width=2)
        # self.canvas.add(self.circle9)
        #
        # self.circle10 = Line(circle=(self.width * 14.95, self.width * 1.2, self.width // 4), close=True, width=2)
        # self.canvas.add(self.circle10)
        #
        # self.circle11 = Line(circle=(self.width * 16.85, self.width * 1.2, self.width // 4), close=True, width=2)
        # self.canvas.add(self.circle11)

        # self.player1.move([100, 200])

    def roll_dice(self, event):
        dice_dict = {1: '\u2680', 2: '\u2681', 3: '\u2682', 4: '\u2683', 5: '\u2684', 6: '\u2685'}
        dice_1 = random.choice(list(dice_dict.values()))
        dice_2 = random.choice(list(dice_dict.values()))

        self.ids.dice_1.text = f'[b][color=#000000]{dice_1}[/color][/b]'
        self.ids.dice_2.text = f'[b][color=#000000]{dice_2}[/color][/b]'

        step_1 = list(dice_dict.keys())[list(dice_dict.values()).index(dice_1)]
        step_2 = list(dice_dict.keys())[list(dice_dict.values()).index(dice_2)]

        steps = step_1 + step_2
        print(steps)

        self.player1.move([self.player1.pos[0] + 50, 0])

        """
        if step_1 == step_2:
            print('Please roll again!')
            self.roll_dice(event)
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
