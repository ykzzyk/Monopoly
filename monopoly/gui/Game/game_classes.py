from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.label import Label
import random


class Game(Screen):
    pass


class GameBoard(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dice_dict = {1: '\u2680', 2: '\u2681', 3: '\u2682', 4: '\u2683', 5: '\u2684', 6: '\u2685'}
        self.dice_1 = random.choice(list(self.dice_dict.values()))
        self.dice_2 = random.choice(list(self.dice_dict.values()))
        print(self.dice_1)

    def roll_dice(self, event):



        '''
        step_1 = list(dice_dict.keys())[list(dice_dict.values()).index(dice_1)]
        step_2 = list(dice_dict.keys())[list(dice_dict.values()).index(dice_2)]

        steps = step_1 + step_2
        print(steps)

        dice = Label(text='', font_size='20', pos=(500, 1000))

        dice.text = f'{dice_1} {dice_2}'
        print(dice.text)

        if step_1 == step_2:
            print('Please roll again!')
            self.roll_dice(event)
        '''