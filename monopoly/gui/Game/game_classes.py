from kivy.uix.screenmanager import Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty
from kivy.graphics import Rectangle, Line, Color
from kivy.animation import Animation

import queue
import random
import time
import functools

from pprint import pprint
import pdb

# Local Imports

from General.general_classes import DynamicImage
from General.general_classes import PlayerIcon
from General import constants as C


class Game(Screen):

    def update_players_to_frame(self, *args):
        # print("Game: update_players_to_frame")
        # print(self.ids.game_board.players)

        for i, player in enumerate(self.ids.game_board.players):
            player_data_obj = self.ids.info_frame.ids[f'player_{i + 1}']

            # Place into the data from the player into the player_data_obj 
            player_data_obj.ids[
                'player_text'].text = f'[b][color=#FF7F00]{player.name}\n{int(player.money)}[/color][/b]'
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
            self.squares[square_name] = BoardSquare(square_name, self)

        # Keeping track of the current player
        self.current_player_turn = 0

        # Creating a card info pop instance for later re-usable use
        self.cardInfo = CardInfoPop(root=self)

        # Accessing ids after they are avaliable
        Clock.schedule_once(lambda _: self.ids.player_turn_button.bind(on_release=self.player_start_turn))

    def add_players(self, players_info):

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

        # ! Testing
        self.buy_property(self.players[0], self.squares['Br1'])
        self.buy_property(self.players[0], self.squares['Br2'])

        # Adding the player to the players info box
        Clock.schedule_once(self.parent.parent.update_players_to_frame)

    def place_ownership_icon(self, player, square_property):

        # If there was a previous owner icon, remove that widget
        if square_property.owner_icon is not None:
            self.remove_widget(square_property.owner_icon)

        if square_property.mortgage:
            color = (0.1, 0.1, 0.1, 1)
        else:
            color = (1, 1, 1, 1)

        # Create a grey-version of the player's icon to visualize ownership
        square_property.owner_icon = DynamicImage(
            root=self,
            source=player.source,
            ratio_pos=square_property.owner_icon_placement,
            ratio_size=(player.ratio_size[0] / 2, player.ratio_size[1] / 2),
            color=color
        )

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
        #'''

        # """
        step_1 = 2
        step_2 = 1
        # """

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
        elif final_square.type == "Property" or final_square.type == "Railroad" or final_square.type == 'Utilities':  # Also handle railroads

            # if the property is not owned
            if final_square.owner is None:

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

                # If the property is owned by someone else and it is not mortgage, PAY RENT!
                if final_square.owner != self.players[self.current_player_turn] and final_square.mortgage is False:

                    if final_square.type == 'Property' or final_square.type == 'Railroad':

                        # If the player can afford the rent
                        if self.players[self.current_player_turn].money >= final_square.rent:
                            # Pay rent
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
        final_id = final_id % len(list(self.squares.keys()))

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

    def buy_property(self, player, square_property, cost=None):

        # Deduce the player's money according to the properties value
        if cost or (cost == 0):
            player.money -= cost
        else:
            player.money -= square_property.cost_value

        # Modify the attribute owned in square_property to the player
        square_property.owner = player

        # Place the ownership icon
        self.place_ownership_icon(player, square_property)

        # Store the property into the player.property_own
        player.property_own.append(square_property)

        # Check for full set condition
        current_set = square_property.property_set
        set_counter = 0
        for square_property in player.property_own:

            if current_set == square_property.property_set:
                set_counter += 1

        # Check if set is full for the player
        if set_counter == len(C.BOARD_SQUARE_FULLSETS[current_set]):

            # Obtain the set's properties and modify their full_set attribute
            for square_property in player.property_own:

                if square_property.property_set == current_set:
                    square_property.full_set = True
                    square_property.rent = square_property.rents['rent_set']

        # Update the player's info in the right side panel
        self.parent.parent.update_players_to_frame()

    def auction_property(self, square_property):
        self.auction_pop = PlayerAuctionPop(
            root=self,
            current_property=square_property
        )

        self.auction_pop.open()

    def trade(self):
        self.tradeInfo = TradePop(root=self)
        self.tradeInfo.open()

    def mortgage_property(self):
        self.mortgageInfo = MortgagePop(root=self)
        self.mortgageInfo.open()

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

    def buy_houses(self):
        self.buyHouseInfo = BuyHousesPop(root=self)
        self.buyHouseInfo.open()


class BoardSquare:

    def __init__(self, square_name, root):

        # Store the board widget
        self.root = root

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

        # For determine the overall section (line{1,2,3,4} or corner) of the property
        self.section = None
        for section in C.BOARD_LINES.keys():
            if square_name in C.BOARD_LINES[section]:
                self.section = section

        # Determine the set for the property
        if self.type == 'Property' or self.type == 'Railroad' or self.type == 'Utilities':
            for property_set in C.BOARD_SQUARE_FULLSETS.keys():
                if square_name in C.BOARD_SQUARE_FULLSETS[property_set]:
                    self.property_set = property_set

        # Calculating the player ownership icon placement
        add = lambda x, y: x + y
        subtract = lambda x, y: x - y

        def offset(data, axis, fn, value=C.PLAYER_ICON_OFFSET):
            if axis == 'x':
                return (fn(data[0], value), data[1])
            return (data[0], fn(data[1], value))

        if self.section == 'Line1':
            if self.type == 'Railroad':
                self.owner_icon_placement = offset(self.physical_location, 'x', add, value=C.RR_PLAYER_ICON_OFFSET)
            else:
                self.owner_icon_placement = offset(self.physical_location, 'x', subtract)
                self.set_line = offset(self.physical_location, 'x', add, value=C.SET_LINE_OFFSET)
                self.house_locations = [
                    offset(self.set_line, 'y', add, value=1.15 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'y', add, value=0.5 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'y', subtract, value=0.175 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'y', subtract, value=0.85 * C.HOUSE_OFFSET)
                ]
                self.buy_house_cost = 50

        elif self.section == 'Line2':
            if self.type == 'Railroad':
                self.owner_icon_placement = offset(self.physical_location, 'y', subtract, value=C.RR_PLAYER_ICON_OFFSET)
            else:
                self.owner_icon_placement = offset(self.physical_location, 'y', add)
                self.set_line = offset(self.physical_location, 'y', subtract,
                                       value=C.SET_LINE_OFFSET - 0.65 * C.BORDER_OFFSET)
                self.house_locations = [
                    offset(self.set_line, 'x', add, value=1.15 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'x', add, value=0.5 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'x', subtract, value=0.175 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'x', subtract, value=0.85 * C.HOUSE_OFFSET)
                ]
                self.buy_house_cost = 100

        elif self.section == 'Line3':
            if self.type == 'Railroad':
                self.owner_icon_placement = offset(self.physical_location, 'x', subtract, value=C.RR_PLAYER_ICON_OFFSET)
            else:
                self.owner_icon_placement = offset(self.physical_location, 'x', add)
                self.set_line = offset(self.physical_location, 'x', subtract,
                                       value=C.SET_LINE_OFFSET - 0.65 * C.BORDER_OFFSET)
                self.house_locations = [
                    offset(self.set_line, 'y', add, value=1.15 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'y', add, value=0.5 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'y', subtract, value=0.175 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'y', subtract, value=0.85 * C.HOUSE_OFFSET)
                ]
                self.buy_house_cost = 150

        elif self.section == 'Line4':
            if self.type == 'Railroad':
                self.owner_icon_placement = offset(self.physical_location, 'y', add, value=C.RR_PLAYER_ICON_OFFSET)
            else:
                self.owner_icon_placement = offset(self.physical_location, 'y', subtract)
                self.set_line = offset(self.physical_location, 'y', add, value=C.SET_LINE_OFFSET)
                self.house_locations = [
                    offset(self.set_line, 'x', add, value=1.15 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'x', add, value=0.5 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'x', subtract, value=0.175 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'x', subtract, value=0.85 * C.HOUSE_OFFSET)
                ]
                self.buy_house_cost = 200

        # For color set properties
        if square_name in C.BOARD_SQUARE_RENT.keys():
            self.rents = C.BOARD_SQUARE_RENT[square_name]
            self.rent = self.rents['rent']

        # Draw the houses
        if self.type == 'Property':
            self.houses = []

            for house_location in self.house_locations:
                # Create a rectangle
                house = DynamicImage(
                    root=self.root,
                    source='assets/background/house_square.png',
                    color=[0, 1, 0, 0],
                    ratio_pos=house_location,
                    ratio_size=(0.01, 0.01),
                    keep_ratio=False
                )

                # Store them in the property square
                self.houses.append(house)

                # Add the image to the board
                self.root.add_widget(house, index=-1)

        # Pre-set values of properties
        self.owner = None
        self.owner_icon = None
        self.number_of_houses = 0  # 5 = 1 hotel
        self.has_hotel = False
        self.mortgage = False
        self.full_set = False

    def __str__(self):
        return f"BoardSquare [Name: {self.name} - Cost Value: {self.cost_value} - Owner: {self.owner}]"

    def __repr__(self):
        return f"BoardSquare [Name: {self.name} - Cost Value: {self.cost_value}]"


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
            self.root.auction_property(self.square_property)

        elif choice == "SELL":
            self.root.sell_belongings()

        # Dismiss the popup
        self.dismiss()


class PlayerData(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PlayerAuctionPop(Popup):

    def __init__(self, **kwargs):
        # Obtain root reference
        self.root = kwargs.pop('root')
        self.current_property = kwargs.pop('current_property')

        super().__init__(**kwargs)

        self.ids.current_square.text = f'[b][color=#ff0000]{self.current_property.full_name}[/b][/color]'
        self.highest_bid = 10

        # Create timer
        self.timer_value = 10
        self.timer = Clock.schedule_interval(self.update_timer_value, 1)

        # Remove the left-side button and place the players icons and money
        Clock.schedule_once(self.set_player_icons, 0)

    def set_player_icons(self, *args):

        # Remove the unwanted label
        self.ids.player_container.remove_widget(self.ids.player_1)

        # Create all the players, in the right order
        self.players_info = []
        for counter, i in enumerate(
                range(self.root.current_player_turn, self.root.current_player_turn + len(self.root.players))):
            # Apply modolus
            i = i % len(self.root.players)

            # Indexing the player
            player = self.root.players[i]

            # Create player info
            player_info = AuctionPlayerInfo(player=player)

            # Setting the data
            player_info.image_source = player.source
            player_info.money = player.money
            player_info.money_text = f"[b][color=#000000]${player_info.money}[/b][/color]"

            # Add the player info to the front-end
            self.ids.player_container.add_widget(player_info, index=counter)

            # Store into list
            self.players_info.append(player_info)

        # Reverse python list of players info to make the first added also the first in the
        # list
        self.players_info.reverse()

        # Make the first player to auction to be colored red
        self.current_bidder = -1
        self.skipped_bids = 0
        # self.set_color(self.players_info[self.current_bidder], color='red')
        self.bid_winner = None  # self.players_info[self.current_bidder]
        self.next_player()

    def update_timer_value(self, *args):

        # Updating the text value
        self.ids.timer.text = f"[b][color=#000000]{self.timer_value}[b][color=#000000]"

        # Skip to the next player
        if self.timer_value == 0:
            # Account for skipped bid counter
            self.skipped_bids += 1

            # Set current bidder to black, since they skipped
            self.set_color(self.players_info[self.current_bidder], color='black')

            # Select next player
            self.next_player()

        # Reducing the timer value
        self.timer_value -= 1

    def add_bid(self, bid):

        # Player decide to skip the bid
        if bid == 0:

            # Account for skipped bid counter
            self.skipped_bids += 1

            # Set current bidder to black, since they skipped
            self.set_color(self.players_info[self.current_bidder], color='black')

            # If the first person skips, then make them the initial winner
            if self.bid_winner is None:
                self.bid_winner = self.players_info[self.current_bidder]
                self.set_color(self.players_info[self.current_bidder], color='blue')

        # Current bidder increased the bid
        else:

            # Reset skipped_bids counter
            self.skipped_bids = 0

            # Make the previous winner from blue to black
            if self.bid_winner is not None:
                self.set_color(self.bid_winner, color='black')

            # Set the winner
            self.bid_winner = self.players_info[self.current_bidder]

            # The current bidder is now the winner
            self.set_color(self.bid_winner, color='blue')

            # Update the bid value and its corresponding text
            self.highest_bid += bid
            self.ids.highest_bid.text = f"[b][color=#000000]HIGHEST BID: {self.highest_bid}[/color][/b]"

        self.next_player()

    def next_player(self):

        if self.skipped_bids > len(self.players_info) - 2:

            # If the first person skips, then make them the initial winner
            if self.bid_winner is None:
                self.bid_winner = self.players_info[0]
                self.set_color(self.players_info[0], color='blue')

            # Determine the player_winner (player class) given the bid_winner (player_info)
            self.root.buy_property(self.bid_winner.player, self.current_property, cost=self.highest_bid)
            self.dismiss()
            return

        # Reset timer for the next player
        self.timer_value = 10

        # Update the current bidder
        self.current_bidder = (self.current_bidder + 1) % len(self.players_info)

        # Current bidder needs to be colored red
        self.set_color(self.players_info[self.current_bidder], color='red')

        # Disable the buttons if the player does not have required money
        if self.players_info[self.current_bidder].player.money - self.highest_bid < 100:
            self.ids.bid_100.disabled = True
        else:
            self.ids.bid_100.disabled = False

        if self.players_info[self.current_bidder].player.money - self.highest_bid < 50:
            self.ids.bid_50.disabled = True
        else:
            self.ids.bid_50.disabled = False

        if self.players_info[self.current_bidder].player.money - self.highest_bid < 20:
            self.ids.bid_20.disabled = True
        else:
            self.ids.bid_20.disabled = False

        if self.players_info[self.current_bidder].player.money - self.highest_bid < 10:
            self.ids.bid_10.disabled = True
        else:
            self.ids.bid_10.disabled = False

        # Check if the now current bidder has enough money to pay the bid,
        # if not, skip them automatically
        if self.players_info[self.current_bidder].player.money <= self.highest_bid:
            # Account for skipped bid counter
            self.skipped_bids += 1

            # Set current bidder to black, since they skipped
            self.set_color(self.players_info[self.current_bidder], color='black')

            # Move the next player
            self.next_player()

    def set_color(self, players_info, color='black'):

        if color == 'red':
            players_info.player_icon_border_color = [1, 0, 0]
            players_info.money_text = f"[b][color=#ff0000]${players_info.money}[/b][/color]"
        elif color == 'blue':
            players_info.player_icon_border_color = [0, 0, 1]
            players_info.money_text = f"[b][color=#0000ff]${players_info.money}[/b][/color]"
        else:  # Black
            players_info.player_icon_border_color = [0, 0, 0]
            players_info.money_text = f"[b][color=#000000]${players_info.money}[/b][/color]"

    def dismiss(self):

        # Stop the clock event
        self.timer.cancel()

        # Then officially dismiss
        super().dismiss()


class AuctionPlayerInfo(BoxLayout):

    def __init__(self, **kwargs):
        self.player = kwargs.pop('player')
        super().__init__(**kwargs)

    money = NumericProperty(0)
    money_text = StringProperty("0")
    image_source = StringProperty("None")
    widget_color = ListProperty([1, 1, 1, 0])  # rgba
    player_icon_border_color = ListProperty([0, 0, 0])  # rgb


class TradePop(Popup):

    def __init__(self, **kwargs):
        # Obtain root reference
        self.root = kwargs.pop('root')

        super().__init__(**kwargs)

        # Btns list of players
        self.left_btns = {}
        self.right_btns = {}

        # Selected players
        self.left_player = None
        self.right_player = None

        # Properties selected containers
        self.left_square_properties = []
        self.right_square_properties = []

        # Disable the accept button
        self.ids.accept_btn.disabled = True

        Clock.schedule_once(self.create_dropdown, 0)

    def create_dropdown(self, *args):

        self.dropdown_list_left = DropDown()
        self.dropdown_list_right = DropDown()

        for player in self.root.players:
            player_name = player.name.upper()
            # button for dropdown list 1
            btn_left = Button(
                text=f'[b][color=#ffffff]{player_name}[/b][/color]', size_hint_y=None,
                height=self.width // 25,
                markup=True
            )

            # button for dropdown list 2
            btn_right = Button(
                text=f'[b][color=#ffffff]{player_name}[/b][/color]', size_hint_y=None,
                height=self.width // 25,
                markup=True
            )

            # Storing the btn references into a list
            self.left_btns[player_name] = btn_left
            self.right_btns[player_name] = btn_right

            # Create the binding function
            btn_left.bind(on_release=lambda btn_left: self.dropdown_list_left.select(btn_left.text))
            btn_right.bind(on_release=lambda btn_right: self.dropdown_list_right.select(btn_right.text))

            # Add the widget to the dropdown window
            self.dropdown_list_left.add_widget(btn_left)
            self.dropdown_list_right.add_widget(btn_right)

        # Bind the select name btns to opening the dropdown window
        self.ids.select_name_btn_left.bind(on_release=self.dropdown_list_left.open)
        self.ids.select_name_btn_right.bind(on_release=self.dropdown_list_right.open)

        # Binding the select name btns to also update their text values
        self.dropdown_list_left.bind(
            on_select=functools.partial(self.select_player, self.ids.select_name_btn_left, 'left')
        )
        self.dropdown_list_right.bind(
            on_select=functools.partial(self.select_player, self.ids.select_name_btn_right, 'right')
        )

    def select_player(self, btn, side, instance, button_text):

        # Obtain the true value in the text
        previous_player_name = btn.text.split(']')[2].split('[')[0]
        player_name = button_text.split(']')[2].split('[')[0]

        # If the selection change from not the default value
        if previous_player_name != 'SELECT PLAYER NAME':
            self.dropdown_list_right.add_widget(self.right_btns[previous_player_name])
            self.dropdown_list_left.add_widget(self.left_btns[previous_player_name])

        # Removing the corresponding button from
        # right dropdown window
        self.dropdown_list_left.remove_widget(self.left_btns[player_name])
        self.dropdown_list_right.remove_widget(self.right_btns[player_name])

        # Update text to given x
        btn.text = button_text

        # Find the matching player given the player_name
        selected_player = None
        for player in self.root.players:
            if player.name.upper() == player_name:
                selected_player = player
                break

        # Store the selected player
        if side == 'left':
            self.left_player = selected_player
            self.ids.left_slider.max = self.left_player.money
        elif side == 'right':
            self.right_player = selected_player
            self.ids.right_slider.max = self.right_player.money

        # Update the property container with the selected player
        self.update_property_container(selected_player, side)

        if (self.left_player is None) or (self.right_player is None):
            self.ids.accept_btn.disabled = True
        else:
            self.ids.accept_btn.disabled = False

    def update_property_container(self, selected_player, side):

        # Clean property container
        if side == 'left':
            self.ids.left_property_container.clear_widgets()
        elif side == 'right':
            self.ids.right_property_container.clear_widgets()

        # Fill the property container given the properties of the
        # selected player
        for square_property in selected_player.property_own:

            # Create button for property
            property_btn = PropertyButton(
                text=f'[b][color=#000000]{square_property.full_name}[/b][/color]',
                markup=True,
                background_normal="",
                square_property=square_property
            )

            # Bind the property button to function
            property_btn.bind(on_release=functools.partial(self.property_button_press, side))

            # Add button to the property container
            if side == 'left':
                self.ids.left_property_container.add_widget(property_btn)
            elif side == 'right':
                self.ids.right_property_container.add_widget(property_btn)

    def property_button_press(self, side, btn_instance):

        square_property_container = self.left_square_properties if side == 'left' else self.right_square_properties

        # If the property is already selected, deselect it by:
        if btn_instance.square_property in square_property_container:

            # Remove from the list
            square_property_container.remove(btn_instance.square_property)

            # Change the color of the button back to white
            btn_instance.background_normal = ""

        else:

            # Append to the list
            square_property_container.append(btn_instance.square_property)

            # Change the color of the button to be highlighted
            btn_instance.background_normal = "assets/buttons/red.png"

    def accept(self):
        # Exchange properties
        # Left player gets the right properties
        for traded_square_property in self.left_square_properties:
            # Remove left's ownership
            self.left_player.property_own.remove(traded_square_property)

            # Check for set completion is removed
            current_set = traded_square_property.property_set
            for square_property in self.left_player.property_own:

                if square_property.property_set == current_set:
                    square_property.full_set = False
                    square_property.rent = square_property.rents['rent']

            # Add right's ownership
            self.root.buy_property(self.right_player, traded_square_property, cost=0)

        # Right player gets the left properties
        for traded_square_property in self.right_square_properties:
            # Remove right's ownership
            self.right_player.property_own.remove(traded_square_property)

            # Check for set completion is removed
            current_set = traded_square_property.property_set
            for square_property in self.right_player.property_own:

                if square_property.property_set == current_set:
                    square_property.full_set = False
                    square_property.rent = square_property.rents['rent']

            # Add left's ownership
            self.root.buy_property(self.left_player, traded_square_property, cost=0)

        # Exchange money
        left_slider_value = int(self.ids.left_slider.value)
        right_slider_value = int(self.ids.right_slider.value)

        self.left_player.money -= left_slider_value
        self.right_player.money += left_slider_value

        self.left_player.money += right_slider_value
        self.right_player.money -= right_slider_value

        # Inform root to update property ownership and update player's money
        self.root.parent.parent.update_players_to_frame()

        # Dismiss the popup
        self.dismiss()


class PropertyButton(Button):
    square_property = ObjectProperty()

    pass


class MortgagePop(Popup):

    def __init__(self, **kwargs):
        # Obtain root reference
        self.root = kwargs.pop('root')
        self.btns = {}
        self.mortgage_unmortgage_money = 0
        self.total_money = 0

        super().__init__(**kwargs)

        self.selected_square_properties = []

        Clock.schedule_once(self.create_dropdown, 0)

    def create_dropdown(self, *args):

        self.dropdown_list = DropDown()

        for player in self.root.players:
            player_name = player.name.upper()
            # button for dropdown list 1
            btn = Button(
                text=f'[b][color=#ffffff]{player_name}[/b][/color]', size_hint_y=None,
                height=self.width // 25,
                markup=True
            )

            # Storing the btn references into a list
            self.btns[player_name] = btn

            # Create the binding function
            btn.bind(on_release=lambda btn: self.dropdown_list.select(btn.text))

            # Add the widget to the dropdown window
            self.dropdown_list.add_widget(btn)

        # Bind the select name btns to opening the dropdown window
        self.ids.select_name_btn.bind(on_release=self.dropdown_list.open)

        # Binding the select name btns to also update their text values
        self.dropdown_list.bind(
            on_select=functools.partial(self.select_player, self.ids.select_name_btn)
        )

    def select_player(self, btn, instance, button_text):

        # Obtain the true value in the text
        previous_player_name = btn.text.split(']')[2].split('[')[0]
        player_name = button_text.split(']')[2].split('[')[0]

        # If the selection change from not the default value
        if previous_player_name != 'SELECT PLAYER NAME':
            self.dropdown_list.add_widget(self.btns[previous_player_name])

        # Removing the corresponding button from
        # right dropdown window
        self.dropdown_list.remove_widget(self.btns[player_name])

        # Update text to given x
        btn.text = button_text

        # Find the matching player given the player_name
        selected_player = None
        for player in self.root.players:
            if player.name.upper() == player_name:
                selected_player = player
                break

        # Storing the selected player
        self.player = selected_player

        # Update the player_current_money label
        self.ids.player_current_money.text = f"[b][color=#000000]Player Current Money: ${self.player.money}[/b][/color]"

        # Update the property container with the selected player
        self.update_property_container(selected_player)

    def update_property_container(self, selected_player):

        # Clean property container
        self.ids.property_container.clear_widgets()

        # Fill the property container given the properties of the
        # selected player
        for square_property in selected_player.property_own:
            property_color = "assets/buttons/red.png" if square_property.mortgage is False else "assets/buttons/light_grey.jpg"

            # Create button for property
            property_btn = PropertyButton(
                text=f'[b][color=#000000]{square_property.full_name}[/b][/color]',
                markup=True,
                background_normal=property_color,
                square_property=square_property
            )

            # Bind the property button to function
            property_btn.bind(on_release=functools.partial(self.property_button_press))

            # Add button to the property container
            self.ids.property_container.add_widget(property_btn)

    def property_button_press(self, btn_instance):

        # If the property is already selected, deselect it by:
        if btn_instance.square_property in self.selected_square_properties:

            # Remove from the list
            self.selected_square_properties.remove(btn_instance.square_property)

            # Change the color of the button back to white
            if btn_instance.square_property.mortgage is True:
                btn_instance.background_normal = "assets/buttons/light_grey.jpg"
                self.mortgage_unmortgage_money += btn_instance.square_property.unmortgage_value
            else:
                btn_instance.background_normal = "assets/buttons/red.png"
                self.mortgage_unmortgage_money -= btn_instance.square_property.mortgage_value

        else:

            # Append to the list
            self.selected_square_properties.append(btn_instance.square_property)

            # Change the color of the button to be highlighted
            if btn_instance.square_property.mortgage is True:
                btn_instance.background_normal = "assets/buttons/red.png"
                self.mortgage_unmortgage_money -= btn_instance.square_property.unmortgage_value
            else:
                btn_instance.background_normal = "assets/buttons/light_grey.jpg"
                self.mortgage_unmortgage_money += btn_instance.square_property.mortgage_value

        # Update the property_money
        if self.mortgage_unmortgage_money < 0:
            self.ids.mortgage_unmortgage_money.text = f"[b][color=#000000]Property Money: -${abs(self.mortgage_unmortgage_money)}[/b][/color]"
        else:
            self.ids.mortgage_unmortgage_money.text = f"[b][color=#000000]Property Money: ${abs(self.mortgage_unmortgage_money)}[/b][/color]"

        # Update the total_money
        self.total_money = self.player.money + self.mortgage_unmortgage_money
        self.ids.total_money.text = f"[b][color=#000000]Total Money: ${self.total_money}[/b][/color]"

        if self.total_money != self.player.money:
            self.ids.select_name_btn.disabled = True
        else:
            self.ids.select_name_btn.disabled = False

    def accept(self):

        # The properties that were selected must be mortgage/unmortgage
        for square_property in self.selected_square_properties:
            # Update the mortgage boolean
            square_property.mortgage = not square_property.mortgage

            # Call the gameboard to make the properties look mortgage or unmortgage
            self.root.place_ownership_icon(self.player, square_property)

        # Modify the player's money given the mortgage_unmortgage money
        self.player.money = self.total_money

        # Inform root to update property ownership and update player's money
        self.root.parent.parent.update_players_to_frame()

        # Dismiss the popup
        self.dismiss()


class BuyHousesPop(Popup):

    def __init__(self, **kwargs):
        # Obtain root reference
        self.root = kwargs.pop('root')
        self.btns = {}
        self.entries = {}
        self.total_money = 0

        super().__init__(**kwargs)

        self.selected_square_properties = []

        Clock.schedule_once(self.create_dropdown, 0)

    def create_dropdown(self, *args):

        self.dropdown_list = DropDown()

        for player in self.root.players:
            player_name = player.name.upper()
            # button for dropdown list 1
            btn = Button(
                text=f'[b][color=#ffffff]{player_name}[/b][/color]', size_hint_y=None,
                height=self.width // 25,
                markup=True
            )

            # Storing the btn references into a list
            self.btns[player_name] = btn

            # Create the binding function
            btn.bind(on_release=lambda btn: self.dropdown_list.select(btn.text))

            # Add the widget to the dropdown window
            self.dropdown_list.add_widget(btn)

        # Bind the select name btns to opening the dropdown window
        self.ids.select_name_btn.bind(on_release=self.dropdown_list.open)

        # Binding the select name btns to also update their text values
        self.dropdown_list.bind(
            on_select=functools.partial(self.select_player, self.ids.select_name_btn)
        )

    def select_player(self, btn, instance, button_text):

        # Obtain the true value in the text
        previous_player_name = btn.text.split(']')[2].split('[')[0]
        player_name = button_text.split(']')[2].split('[')[0]

        # If the selection change from not the default value
        if previous_player_name != 'SELECT PLAYER NAME':
            self.dropdown_list.add_widget(self.btns[previous_player_name])

        # Removing the corresponding button from
        # right dropdown window
        self.dropdown_list.remove_widget(self.btns[player_name])

        # Update text to given x
        btn.text = button_text

        # Find the matching player given the player_name
        selected_player = None
        for player in self.root.players:
            if player.name.upper() == player_name:
                selected_player = player
                break

        # Storing the selected player
        self.player = selected_player

        # Update the player_current_money label
        self.ids.player_current_money.text = f"[b][color=#000000]Player Current Money: ${self.player.money}[/b][/color]"

        # Update the property container with the selected player
        self.update_property_container(selected_player)

    def update_property_container(self, selected_player):

        # Clean property container
        self.ids.property_container.clear_widgets()

        # Fill the property container given the properties of the
        # selected player
        for square_property in selected_player.property_own:

            # If the property is not part of a full set, then ignore it
            if square_property.full_set is False:
                continue

            # Create button for property
            entry = BuyHousesEntry(
                square_property=square_property,
                initial_houses=square_property.number_of_houses,
                total_houses=square_property.number_of_houses
            )

            # Add it to the entries of the popup
            if entry.square_property.property_set not in self.entries.keys():
                self.entries[entry.square_property.property_set] = [entry]
            else:
                self.entries[entry.square_property.property_set].append(entry)

            # Place property name
            entry.ids.property_name.text = f'[b][color=#000000]{entry.square_property.full_name}[/b][/color]'

            # Updateing the entry's text
            self.update_house_numbers(entry)

            # Update the button status
            self.update_button_status()

            # Bind the property button to function
            # entry.bind(on_release=functools.partial(self.property_button_press))
            entry.ids.buy_houses.bind(on_release=functools.partial(self.buy_houses, entry))
            entry.ids.sell_houses.bind(on_release=functools.partial(self.sell_houses, entry))

            # Add button to the property container
            self.ids.property_container.add_widget(entry)

        # Update the money values
        self.update_money_values()

    def update_button_status(self):

        for set_name in self.entries.keys():

            # Checking all the other entries within the same set
            number_of_total_houses = list(map(lambda x: x.total_houses, self.entries[set_name]))

            # Determine the min and max
            min_val, max_val = min(number_of_total_houses), max(number_of_total_houses)

            for entry in self.entries[set_name]:

                # Determine if the entry's specific buttons are enabled or disabled
                if min_val == max_val:
                    if min_val == 0:
                        entry.ids.buy_houses.disabled = False
                        entry.ids.sell_houses.disabled = True
                    elif max_val == 5:
                        entry.ids.buy_houses.disabled = True
                        entry.ids.sell_houses.disabled = False
                    else:
                        entry.ids.buy_houses.disabled = False
                        entry.ids.sell_houses.disabled = False

                elif entry.total_houses == min_val:
                    entry.ids.buy_houses.disabled = False
                    entry.ids.sell_houses.disabled = True
                elif entry.total_houses == max_val:
                    entry.ids.sell_houses.disabled = False
                    entry.ids.buy_houses.disabled = True

    def update_money_values(self):

        self.total_money = 0

        for set_name in self.entries.keys():

            # Determine the cost of the house for the set
            cost_of_house = self.entries[set_name][0].square_property.buy_house_cost

            # Determine the houses bought and the houses sold
            houses_bought = 0
            houses_sold = 0

            for entry in self.entries[set_name]:
                houses_diff = entry.total_houses - entry.initial_houses

                if houses_diff > 0:
                    houses_bought += houses_diff
                else:
                    houses_sold -= houses_diff

            # Calculate the total cost
            self.total_money += int(houses_sold * (cost_of_house / 2))
            self.total_money -= int(houses_bought * cost_of_house)

        # Update the buy_sell money and the player's total money
        if self.total_money >= 0:
            self.ids.buy_sell_money.text = f"[b][color=#000000]Property Money: ${self.total_money}[/b][/color]"
        else:
            self.ids.buy_sell_money.text = f"[b][color=#000000]Property Money: -${abs(self.total_money)}[/b][/color]"

        # Update the total money of the player after the transaciton
        self.total_money += self.player.money
        self.ids.total_money.text = f"[b][color=#000000]Total Money: ${self.total_money}[/b][/color]"

        # Disable buttons if the player does not have enough money to pay for the houses/hotel
        self.cannot_pay()

    def update_house_numbers(self, entry):

        # Updateing the entry's text
        if entry.total_houses == 5:
            entry.ids.houses_numbers.text = "[b][color=#000000]1[/b][/color]"
            entry.ids.house.color = [1, 0, 0, 1]
        else:
            entry.ids.houses_numbers.text = f"[b][color=#000000]{entry.total_houses}[/b][/color]"
            entry.ids.house.color = [0, 1, 0, 1]

    def cannot_pay(self):

        # Disable buttons based on not enough money
        for set_name in self.entries.keys():

            # Determine the cost of the house for the set
            cost_of_house = self.entries[set_name][0].square_property.buy_house_cost

            # If they don't have enough money to buy houses in this set
            if cost_of_house > self.total_money:
                for entry in self.entries[set_name]:
                    entry.ids.buy_houses.disabled = True

    def buy_houses(self, entry, btn_instance):

        # Increase the entry's total houses
        entry.total_houses += 1

        # Updateing the entry's text
        self.update_house_numbers(entry)

        # Place the houses/hotel number
        self.update_button_status()

        # Update money values
        self.update_money_values()

        if self.total_money != self.player.money:
            self.ids.select_name_btn.disabled = True
        else:
            self.ids.select_name_btn.disabled = False

    def sell_houses(self, entry, btn_instance):

        # Increase the entry's total houses
        entry.total_houses -= 1

        # Updateing the entry's text
        self.update_house_numbers(entry)

        # Update total houses number displayed
        self.update_button_status()

        # Update money values
        self.update_money_values()

        if self.total_money != self.player.money:
            self.ids.select_name_btn.disabled = True
        else:
            self.ids.select_name_btn.disabled = False

    def accept(self):

        # Update the houses visible after buying/selling houses/hotel
        for set_name in self.entries.keys():
            for entry in self.entries[set_name]:

                color_values = []
                r = [1, 0, 0, 1]
                g = [0, 1, 0, 1]
                n = [0, 0, 0, 0]

                # Select the correct color sequence given the number of houses
                if entry.total_houses < 5:
                    for i in range(4):  # 0, 1, 2, 3
                        if i < entry.total_houses:
                            color_values.append(g)
                        else:
                            color_values.append(n)
                else:
                    color_values = [r, n, n, n]

                # Change the color attribute of the houses
                for house, color in zip(entry.square_property.houses, color_values):
                    house.color = color

                # Change the attributes of the property to the new number of houses
                entry.square_property.number_of_houses = entry.total_houses

                # Update the rent of the square_property given the number of houses
                if entry.square_property.number_of_houses == 5:
                    entry.square_property.rent = entry.square_property.rents['rent_hotel_1']
                elif entry.square_property.number_of_houses == 0:
                    entry.square_property.rent = entry.square_property.rents['rent_set']
                else:
                    entry.square_property.rent = entry.square_property.rents[
                        f'rent_house_{entry.square_property.number_of_houses}']

        # Modify the player's money given the mortgage_unmortgage money
        self.player.money = self.total_money

        # Inform root to update property ownership and update player's money
        self.root.parent.parent.update_players_to_frame()

        # Dismiss the popup
        self.dismiss()


class BuyHousesEntry(GridLayout):
    square_property = ObjectProperty()
    initial_houses = NumericProperty()
    total_houses = NumericProperty()
