
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
import pdb

# Local Imports

from General.general_classes import DynamicImage
from General import constants as C


class Game(Screen):
    
    def update_players_to_frame(self, *args):

        #print("Game: update_players_to_frame")
        #print(self.ids.game_board.players)

        for i, player in enumerate(self.ids.game_board.players):

            player_data_obj = self.ids.info_frame.ids[f'player_{i+1}']

            # Place into the data from the player into the player_data_obj 
            player_data_obj.ids['player_text'].text = f'[b][color=#FF7F00]{player.name}\n{player.money}[/color][/b]'
            player_data_obj.ids['player_icon'].image_source = player.source
        

class Player(DynamicImage):
    rectangle = ObjectProperty(None)

    def __init__(self, **kwargs):

        # Save the board location
        self.root = kwargs['root']  # Do not pop (DynamicImage requires it)
        self.current_square = self.root.squares[kwargs.pop('starting_square')]
        self.name = kwargs.pop('player_name')

        # Obtain the pixel value of the board location
        kwargs['ratio_pos'] = self.current_square.physical_location
        kwargs['ratio_size'] = (0.05, 0.05)

        # Run parent inheritance
        self.doubles_counter = 0
        self.in_jail_counter = -1
        self.money = 1500
        self.house = 0
        self.hotel = 0
        self.jail_free_card = False
        self.property_own = []

        self.root_size_before = self.root.size

        super().__init__(**kwargs)

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

        return move_animation

    def __str__(self):
        return f"Player [Name: {self.name} - Money: {self.money} - Property Own: {self.property_own}]"

    def __repr__(self):
        return self.__str__()

class GameBoard(Widget):

    # Initialization of objects
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Constructing all the squares
        self.squares = {}
        for square_name in C.BOARD_SQUARE_LOCATIONS.keys():
            self.squares[square_name] = BoardSquare(square_name)

        # Keeping track of the current player
        self.current_player_turn = 0

        # Creating a card info pop instance for later re-usable use
        self.cardInfo = CardInfoPop(root=self)

        # Accessing ids after they are avaliable
        Clock.schedule_once(lambda _: self.ids.player_turn_button.bind(on_release=self.player_start_turn))

    def add_players(self, players_info):
        print(f'add_players fn: {players_info}')

        # Creating the player objects
        self.players = []
        for player_name, player_icon in players_info.items():
            self.players.append(Player(
                root=self, 
                source="assets/player_icons/" + player_icon + ".png", 
                starting_square='GO', 
                player_name=player_name
                )
            )

        # Randomly shuffling the list to determine who goes first
        random.shuffle(self.players)

        # Informing the lobby who goes first
        self.ids.message_player_turn.text = f"[b][color=#800000]Player {self.players[0].name} Goes first![/color][/b]"

        # Adding the player to the gameboard
        for player in self.players:
            self.add_widget(player)

        # Adding the player to the players info box
        Clock.schedule_once(self.parent.parent.update_players_to_frame)

    def place_ownership_icon(self, player, square_property):

        # If there was a previous owner icon, remove that widget
        if square_property.owner_icon != None:
            self.remove_widget(square_property.owner_icon)

        # Create a grey-version of the player's icon to visualize ownership
        square_property.owner_icon = DynamicImage(
            root=self,
            source=player.source, 
            ratio_pos=player.ratio_pos, 
            ratio_size=(player.ratio_size[0]//2, player.ratio_size[1]//2)
        )

        """
        with square_property.owner_icon.canvas:
            Rectangle(source='assets/buttons/light_grey.jpg', pos=self.pos, size=self.size)
        """
        
        # Adding the image to the game_board
        self.add_widget(square_property.owner_icon, index=-1)

    # Handling player movement
    def player_start_turn(self, *args, rolls=None):

        # Update the current turn text
        self.ids.message_player_turn.text = f"[b][color=#800000]Current player {self.players[self.current_player_turn].name}[/color][/b]"

        # If the player has been in jail for three times, then kick them out
        if self.players[self.current_player_turn].in_jail_counter > 1:
            if not self.players[self.current_player_turn].jail_free_card:
                self.players[self.current_player_turn].money -= 50
            self.players[self.current_player_turn].in_jail_counter = -1
            self.players[self.current_player_turn].jail_free_card = False

        # Else, ask them if they would like to pay to get out or try to roll doubles
        elif self.players[self.current_player_turn].in_jail_counter >= 0:
            if self.players[self.current_player_turn].jail_free_card:
                self.jail_decision = CardSelectPop(root=self,
                                                   current_player=self.players[self.current_player_turn],
                                                   square_property=None,
                                                   button_left='Use Jail Free Card',
                                                   button_right='ROLL AGAIN')
            else:
                self.jail_decision = CardSelectPop(root=self,
                                                   current_player=self.players[self.current_player_turn],
                                                   square_property=None,
                                                   button_left='PAY $50',
                                                   button_right='ROLL AGAIN')

            self.jail_decision.open()

            return 0

        '''
        # Roll the dice and get their values
        if rolls is None:
            step_1, step_2 = self.roll_dice(None)
        else:
            step_1, step_2 = rolls
        '''
        step_1 = 1
        step_2 = 0

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
            move_animation = self.players[self.current_player_turn].move_direct(self.squares['Jail'])
            move_animation.bind(on_complete=lambda _, __: self.player_end_turn(final_square=self.squares['Jail']))

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

        self.player_land_place(final_square)

        # Update to next player if doubles is not true
        if self.next_player_turn:
            self.players[self.current_player_turn].doubles_counter = 0
            self.current_player_turn = (self.current_player_turn + 1) % len(self.players)

        # Update the next turn text
        self.ids.message_player_turn.text = f"[b][color=#800000]Next is {self.players[self.current_player_turn].name}![/color][/b]"

    def player_land_place(self, final_square):

        # Processing the action depending on the square name
        # If the player lands on the 'GO-TO-JAIL' square
        if final_square.name == 'GO-TO-JAIL':
            self.players[self.current_player_turn].move_direct(self.squares['Jail'])
            self.players[self.current_player_turn].in_jail_counter = 0

        # If land on the chance:
        elif final_square.type == "Chance":
            chance_card = self.cardInfo.get_card(self.cardInfo.chance, 'chance')
            self.cardInfo.open()
            Clock.schedule_once(lambda dt: self.cardInfo.dismiss(), 3)

            if 'ST.CHARLES PLACE' in chance_card:
                if self.players[self.current_player_turn].current_square != self.squares['Chance1']:
                    self.players[self.current_player_turn].money += 200
                self.players[self.current_player_turn].move_direct(self.squares['Pk1'])
            elif 'HOUSE' in chance_card:
                self.players[self.current_player_turn].money -= 25 * self.players[self.current_player_turn].house
                self.players[self.current_player_turn].money -= 100 * self.players[self.current_player_turn].hotel
            elif 'THREE' in chance_card:
                # Final square ID
                final_id = self.players[self.current_player_turn].current_square.sequence_id - 3
                final_square = self.squares[list(self.squares.keys())[final_id]]
                self.players[self.current_player_turn].move_direct(final_square)
            elif 'JAIL FREE' in chance_card:
                self.players[self.current_player_turn].jail_free_card = True
            elif 'BOARDWALK' in chance_card:
                self.players[self.current_player_turn].move_direct(self.squares['Bl2'])
            elif 'READING' in chance_card:
                if self.players[self.current_player_turn].current_square == self.squares['Chance3']:
                    self.players[self.current_player_turn].money += 200
                self.players[self.current_player_turn].move_direct(self.squares['RR1'])
            elif 'LOAN MATURES' in chance_card:
                self.players[self.current_player_turn].money += 150
            elif 'ILLINOIS AVENUE' in chance_card:
                if self.players[self.current_player_turn].current_square == self.squares['Chance3']:
                    self.players[self.current_player_turn].money += 200
                self.players[self.current_player_turn].move_direct(self.squares['Rd3'])

            elif 'NEAREST' in chance_card:
                if self.players[self.current_player_turn].current_square == self.squares['Chance1']:
                    self.players[self.current_player_turn].move_direct(self.squares['Util1'])
                elif self.players[self.current_player_turn].current_square == self.squares['Chance2']:
                    self.players[self.current_player_turn].move_direct(self.squares['Util2'])
                elif self.players[self.current_player_turn].current_square == self.squares['Chance3']:
                    self.players[self.current_player_turn].move_direct(self.squares['Util2'])

            elif 'NEXT\nRAILROAD' in chance_card:
                if self.players[self.current_player_turn].current_square == self.squares['Chance1']:
                    self.players[self.current_player_turn].move_direct(self.squares['RR2'])
                elif self.players[self.current_player_turn].current_square == self.squares['Chance2']:
                    self.players[self.current_player_turn].move_direct(self.squares['RR3'])
                elif self.players[self.current_player_turn].current_square == self.squares['Chance3']:
                    self.players[self.current_player_turn].move_direct(self.squares['RR1'])
            elif 'TO JAIL' in chance_card:
                self.players[self.current_player_turn].move_direct(self.squares['Jail'])
                self.players[self.current_player_turn].in_jail_counter = 0
            elif 'SPEEDING FINE' in chance_card:
                self.players[self.current_player_turn].money -= 15
            elif 'PAY EACH PLAYER' in chance_card:
                for player in self.players:
                    if player != self.players[self.current_player_turn]:
                        player.money += 50
                        self.players[self.current_player_turn].money -= 50

        # If land on chest
        elif final_square.type == "Chest":
            chest_card = self.cardInfo.get_card(self.cardInfo.chest, 'chest')
            self.cardInfo.open()
            Clock.schedule_once(lambda dt: self.cardInfo.dismiss(), 3)

            if ('MATURES' in chest_card) or ('YOU INHERIT $100' in chest_card):
                self.players[self.current_player_turn].money += 100
            elif ("DOCTOR'S FEES" in chest_card) or ('SCHOOL FEES' in chest_card):
                self.players[self.current_player_turn].money -= 50
            elif 'JAIL FREE' in chest_card:
                self.players[self.current_player_turn].jail_free_card = True
            elif 'INCOME TAX REFUND' in chest_card:
                self.players[self.current_player_turn].money += 20
            elif 'HOSPITAL FEES' in chest_card:
                self.players[self.current_player_turn].money -= 100
            elif 'TO JAIL' in chest_card:
                self.players[self.current_player_turn].move_direct(self.squares['Jail'])
                self.players[self.current_player_turn].in_jail_counter = 0
            elif 'BIRTHDAY' in chest_card:
                self.players[self.current_player_turn].money += 25
                for player in self.players:
                    if player != self.players[self.current_player_turn]:
                        player.money -= 10
                        self.players[self.current_player_turn].money += 10
            elif 'FROM SALE OF STOCK' in chest_card:
                self.players[self.current_player_turn].money += 50
            elif 'WON SECOND PRIZE' in chest_card:
                self.players[self.current_player_turn].money += 10
            elif 'STREET REPAIRS' in chest_card:
                self.players[self.current_player_turn].money -= 40 * self.players[self.current_player_turn].house
                self.players[self.current_player_turn].money -= 115 * self.players[self.current_player_turn].hotel
            elif 'TO GO' in chest_card:
                self.players[self.current_player_turn].move_direct(self.squares['GO'])
                self.players[self.current_player_turn].money += 200
            elif 'BANK ERROR' in chest_card:
                self.players[self.current_player_turn].money += 200

        # If land on tax penalty squares
        elif final_square.type == "Tax":
            
            if final_square.name == 'ITax':
                self.players[self.current_player_turn].money -= 200

            elif final_square.name == 'LTax':
                self.players[self.current_player_turn].money -= 100

        # If land on property
        elif final_square.type == "Property" or final_square.type == "Railroad" or final_square.type == 'Utilities': # Also handle railroads
            
            # if the property is not owned
            if (final_square.owner is None):
                
                # Determine if the player has enough money to buy the property
                if self.players[self.current_player_turn].money >= final_square.cost_value:
                    # Buy or Auction
                    self.buy_or_auction = CardSelectPop(root=self,
                                                        current_player=self.players[self.current_player_turn],
                                                        square_property=final_square,
                                                        button_left='BUY',
                                                        button_right='AUCTION')
                else:
                    self.buy_or_auction = CardSelectPop(root=self,
                                                        current_player=self.players[self.current_player_turn],
                                                        square_property=final_square,
                                                        button_left='MORTGAGE',
                                                        button_right='AUCTION')
                self.buy_or_auction.open()

            # else the property is owned
            else:

                # If the property is owned by someone else
                if (final_square.owner != self.players[self.current_player_turn]):
                    
                    if final_square.type == 'Property' or final_square.type == 'Railroad':
                        
                        # If the player can afford the rent
                        if self.players[self.current_player_turn].money >= final_square.rent:
                            self.players[self.current_player_turn].money -= final_square.rent
                            final_square.owner.money += final_square.rent
                        
                        # else
                        else:
                            self.mortgage_or_sell = CardSelectPop(root=self,
                                                            current_player=self.players[self.current_player_turn],
                                                            square_property=final_square,
                                                            button_left='MORTGAGE',
                                                            button_right='SELL')
                    
                    elif final_square.type == 'Utilities':
                        pass
                    
        # Update the player's info in the right side panel
        self.parent.parent.update_players_to_frame()

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

        # Determine if the player passes go
        final_id = steps + start_id

        # if passed GO
        if final_id >= len(list(self.squares.keys())):
            self.players[self.current_player_turn].money += 200

        # Calculate the final step location
        final_id = (final_id) % len(list(self.squares.keys()))

        # Retrive the key for the location
        final_square_name = list(self.squares.keys())[final_id]
        final_square = self.squares[final_square_name]

        # Move player
        move_animation = self.players[self.current_player_turn].move(final_square)

        # Perform bindings
        # Unbind the roll dice button to prevent glitching
        self.ids.player_turn_button.unbind(on_release=self.player_start_turn)

        # Bind the completion of the animation to rebinding the roll_dice function
        move_animation.bind(on_complete=lambda _, __: self.player_end_turn(final_square=final_square))

        # Bind the animation to the size of the window
        # print(f'Binding the stop_animation function for player: {self.players[self.current_player_turn].name}')
        self.stop_animation_flag = False
        self.bind(size=self.stop_animation)

    # Handling player decisions
    def roll_out_jail(self):

        # Roll the dice
        # step_1, step_2 = self.roll_dice(None)
        step_1 = 3
        step_2 = 2

        # If they roll doubles, then let them out
        if step_1 == step_2:
            self.players[self.current_player_turn].doubles_counter = 0
            self.players[self.current_player_turn].in_jail_counter = -1
            self.player_start_turn([step_1, step_2])

        # If they don't roll a doubles, they stay in jail and move to the next player
        else:
            self.players[self.current_player_turn].in_jail_counter += 1
            self.current_player_turn = (self.current_player_turn + 1) % len(self.players)
            self.ids.message_player_turn.text = f"[b][color=#800000]\n\nNext is {self.players[self.current_player_turn].name}![/color][/b]"
            return 0

    def pay_out_jail(self):

        # Change attributes to make player out of jail
        if not self.players[self.current_player_turn].jail_free_card:
            self.players[self.current_player_turn].money -= 50
        self.players[self.current_player_turn].in_jail_counter = -1
        self.players[self.current_player_turn].jail_free_card = False

    def buy_property(self, player, square_property):
        
        # Deduce the player's money according to the properties value
        player.money -= square_property.cost_value

        # Modify the attribute owned in square_property to the player
        square_property.owner = player

        # Place the ownership icon
        self.place_ownership_icon(player, square_property)

        # Store the property into the player.property_own
        player.property_own.append(square_property)

        # Update the player's info in the right side panel
        self.parent.parent.update_players_to_frame()

    def auction_property(self):
        pass

    def mortgage_property(self):
        pass

    def sell_belongings(self):
        pass

    # Handling animations
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

        self.chance.put('SPEEDING FINE. PAY $15.')
        self.chance.put('YOUR BULIDING LOAN MATURES.\nCOLLECT $150.')
        self.chance.put('TAKE A TRIP TO READING\nRAILROAD. IF YOU PASS GO,\nCOLLECT $200.')
        self.chance.put('ADVANCE TO ILLINOIS AVENUE.\nIF YOU PASS GO, COLLECT $200.')
        self.chance.put('GET OUT OF JAIL FREE.')
        self.chance.put('YOU HAVE BEEN ELECTED\nCHAIRMAN OF THE BOARD.\nPAY EACH PLAYER $50.')
        self.chance.put('ADVANCE TO THE NEAREST\nUTILITY.')
        self.chance.put('ADVANCE TO THE NEXT\nRAILROAD.')
        self.chance.put('GO DIRECTLY TO JAIL.\nDO NOT COLLECT $200.')
        self.chance.put('GO BACK THREE SPACES.')
        self.chance.put('ADVANCE TO ST.CHARLES PLACE.\nIF YOU PASS GO, COLLECT $200.')
        self.chance.put(
            'MAKE GENERAL REPAIRS\nON ALL YOUR PROPERTY:\nFOR EACH HOUSE PAY $25.\nFOR EACH HOTEL, PAY $100.')
        self.chance.put('ADVANCE TO BOARDWALK.')

        self.chest = queue.Queue(maxsize=0)
        self.chest.put('INCOME TAX REFUND.\nCOLLECT $20.')
        self.chest.put('HOLIDAY FUND MATURES.\nCOLLECT $100.')
        self.chest.put("DOCTOR'S FEES. PAY $50.")
        self.chest.put('HOSPITAL FEES. PAY $100.')
        self.chest.put('GO DIRECTLY TO JAIL.\nDO NOT COLLECT $200.')
        self.chest.put("COLLECT $25 CONSULTANCY FEE.\nIT'S YOUR BIRTHDAY.\nCOLLECT $10 FROM EACH PLAYER.")
        self.chest.put('FROM SALE OF STOCK, YOU GET $50.')
        self.chest.put('YOU HAVE WON SECOND PRIZE\nIN A BEAUTY CONTEST.\nCOLLECT $10.')
        self.chest.put('YOU ARE ASSESSED FOR STREET REPAIRS:\nPAY $40 PER HOUSE AND \n$115 PER HOTEL YOU OWN.')
        self.chest.put('ADVANCE TO GO. COLLECT $200.')
        self.chest.put('BANK ERROR IN YOUR FAVOR.\nCOLLECT $200.')
        self.chest.put('LIFE INSURANCE MATURES.\nCOLLECT $100.')
        self.chest.put('YOU INHERIT $100.')
        self.chest.put('SCHOOL FEES. PAY $50.')
        self.chest.put('GET OUT OF JAIL FREE.')

    def get_card(self, cards, name):
        card = cards.get()
        cards.put(card)

        # Change the card texts
        self.ids.card_info.text = f'[b][color=#000000]{card}[/color][/b]'
        # Change the display image
        self.ids.card_image.source = f"assets/background/{name}.png"

        return card


class CardSelectPop(Popup):

    def __init__(self, **kwargs):
        # Obtain root reference
        self.root = kwargs.pop('root')
        self.current_player = kwargs.pop('current_player')
        self.square_property = kwargs.pop('square_property')
        self.button_right = kwargs.pop('button_right')
        self.button_left = kwargs.pop('button_left')

        super().__init__(**kwargs)
        
        if self.square_property is not None:
            self.ids.label_1.text = f"[b][color=#000000]For {self.square_property.full_name}, do {self.current_player.name} want to PAY ${self.square_property.cost_value} or AUCTION?[/b][/color]"
        else:
            self.ids.label_1.text = f"[b][color=#000000]Do {self.current_player.name} want to PAY $50 or ROLL DOUBLES to get out of jail?[/b][/color]"
        
        self.ids.button_left.text = f'[b][color=#ffffff]{self.button_left}[/b][/color]'
        self.ids.button_right.text = f'[b][color=#ffffff]{self.button_right}[/b][/color]'

    def player_decision(self, choice):

        # Execute the roll_out_jail from the gameboard
        if choice == 'ROLL AGAIN':
            self.root.roll_out_jail()

        # Execute the pay_out_jail from the gameboard
        elif choice == 'PAY $50':
            self.root.pay_out_jail()

        # Execute the buy_property from the gameboard
        elif choice == 'BUY':
            self.root.buy_property(self.current_player, self.square_property)

        # Execute the mortgage_property from the gameboard
        elif choice == 'MORTGATE':
            self.root.mortgage_property()

        # Execute the auction_property from the gameboard
        elif choice == 'AUCTION':
            self.root.auction_property()

        elif choice == "SELL":
            self.root.sell_belongings()

        # Dismiss the popup
        self.dismiss()


class PlayerData(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BoardSquare:

    def __init__(self, square_name):

        # Storing the name of the square
        self.name = square_name

        # Determing if the cart is chest or community
        if "Chance" in self.name:
            self.type = "Chance"
        elif "Chest" in self.name:
            self.type = "Chest"
        elif "RR" in self.name:
            self.type = "Railroad"
        elif "Util" in self.name:
            self.type = "Utilities"
        elif "Tax" in self.name:
            self.type = "Tax"
        elif self.name == "GO" or self.name == "Jail" or self.name == "GO-TO-JAIL" or self.name == "Parking":
            self.type = "Corner"
        else:
            self.type = "Property"
        

        # Obtain the square's pixel_ratio location
        self.physical_location = C.BOARD_SQUARE_LOCATIONS[square_name]

        # Obtain the chronological number of the property
        self.sequence_id = list(C.BOARD_SQUARE_LOCATIONS.keys()).index(square_name)

        # Obtain the square's property cost (if applicable)
        self.cost_value = C.BOARD_SQUARE_ATTRIBUTES[square_name]['cost_value']
        self.full_name = C.BOARD_SQUARE_ATTRIBUTES[square_name]['full_name']
        self.mortgage_value = C.BOARD_SQUARE_ATTRIBUTES[square_name]['mortgage_value']
        self.unmortgage_value = C.BOARD_SQUARE_ATTRIBUTES[square_name]['unmortgage_value']
        
        # For color set properties
        if square_name in C.BOARD_SQUARE_RENT.keys():
            self.rents = C.BOARD_SQUARE_RENT[square_name]
            self.rent = self.rents['rent']

        # Pre-set values of properties
        self.owner = None
        self.owner_icon = None
        self.number_of_houses = 0
        self.has_hotel = False
        self.mortgage = False

    def __str__(self):
        return f"BoardSquare [Name: {self.name} - Cost Value: {self.cost_value} - Owner: {self.owner}]"

    def __repr__(self):
        return f"BoardSquare [Name: {self.name} - Cost Value: {self.cost_value}]"
