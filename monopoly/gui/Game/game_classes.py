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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history_log = []

    def update_players_to_frame(self, *args):

        for i in range(8):

            # Select the player if applicable
            if i < len(self.ids.game_board.players):
                player = self.ids.game_board.players[i]
            else:
                player = None

            # Select the correct player data object
            player_data_obj = self.ids.info_frame.ids[f'player_{i + 1}']

            if player:
                # Calculate Net worth
                player_net_worth = player.calculate_net_worth()

                # Calculating the spacing
                spacing = " " * (10 - len(str(player.money)))

                # Place into the data from the player into the player_data_obj
                player_data_obj.ids['player_text'].text = \
                    f'[b][color=#FF0000]{player.name}\nMoney: {int(player.money)}{spacing}Net Worth: {int(player_net_worth)}[/color][/b]'
                player_data_obj.ids['player_icon'].image_source = player.source
            else:
                player_data_obj.ids['player_text'].text = ""
                player_data_obj.ids['player_icon'].image_source = ""

    def add_history_log_entry(self, entry):

        # Append the entry to the back-end history
        self.history_log.append(entry)

        # Remove if the entry is full
        if len(self.history_log) > 100:
            self.history_log.pop(0)

        # Construct log text to be place in the history log
        log_text = "[b][color=#FF0000]" + "\n".join(self.history_log) + "[/color][/b]"

        # Update the history log text
        self.ids.history_log.text = log_text


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

        # Extend turn
        self.root.extend_turn = True

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

        # Bind the move animation to the self.player_end_turn since it needs to be executed on its completion
        move_animation.bind(on_complete=lambda _, __: self.root.player_end_turn(final_square=final_square))

    def calculate_net_worth(self):

        net_worth = self.money

        for square_property in self.property_own:

            # print(square_property)

            # Accounting for property value
            if not square_property.mortgage:
                net_worth += square_property.mortgage_value

            # Accounting for house/hotel values
            if square_property.type == 'Property':
                worth_of_house = square_property.buy_house_cost / 2
                net_worth += worth_of_house * square_property.number_of_houses

        return net_worth

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

        # Container for the player widget objects
        self.players = []

        # Keeping track of indebted players
        self.debt_players = []

        # Creating a card info pop instance for later re-usable use
        self.cardInfo = CardInfoPop(root=self)

        # Accessing ids after they are avaliable
        Clock.schedule_once(lambda _: self.ids.player_turn_button.bind(on_release=self.player_start_turn))

    def init(self):

        # Log game start!
        self.parent.parent.add_history_log_entry("Game started!")

        # Remove any players
        if self.players:
            for player in self.players:
                self.remove_widget(player)
                del player

            self.players = []

        # Clear out the properties
        for square in self.squares.values():
            square.mortgage = False
            square.owner = None
            square.number_of_houses = 0
            square.full_set = False

            if square.type == 'Property' or square.type == 'Railroad' or square.type == 'Utilities':
                square.update_player_icon()
                if square.type == 'Property':
                    square.update_house_markers()

    def add_players(self, players_info):

        # Creating the player objects
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

        # ''' ! Testing
        #self.buy_property(self.players[0], self.squares['Br2'])
        #self.buy_property(self.players[0], self.squares['Br1'])


        # self.buy_property(self.players[1], self.squares['Util1'])

        #self.players[0].money = 1000
        #self.players[1].money = 1000
        # self.players[2].money = 300
        # '''

        # Adding the player to the players info box
        Clock.schedule_once(self.parent.parent.update_players_to_frame)

    # Handling player movement
    def player_start_turn(self, *args, rolls=None):

        # Check for any players that are indebted, if so, kick them OUT!
        if self.debt_players:
            for player in self.debt_players:
                self.debt_players.remove(player)
                if player.money < 0:
                    self.remove_player(player)

        # Update the current turn text
        self.ids.message_player_turn.text = f"[b][color=#800000]Current player {self.players[self.current_player_turn].name}[/color][/b]"

        # If the player has been in jail for three times, then kick them out
        if self.players[self.current_player_turn].in_jail_counter > 1:

            log_text = f"{self.players[self.current_player_turn]} has been in JAIL too long. Gets out and pay $50."
            self.parent.parent.add_history_log_entry(log_text)

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
                                                   button_left='USE JAIL FREE CARD',
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
        # '''

        # """
        step_1 = 6
        step_2 = 1
        # """

        self.next_player_turn = True

        # If doubles, update counter and make sure the player goes again
        if step_1 == step_2:
            # Log double event
            self.parent.parent.add_history_log_entry(
                f"{self.players[self.current_player_turn].name.upper()} rolled a double. Go again.")

            # Updating counter
            self.players[self.current_player_turn].doubles_counter += 1

            # Set an flag for next player turn
            self.next_player_turn = False

        # Check if doubles three times, if so, move the player to jail
        if self.players[self.current_player_turn].doubles_counter == 3:

            # Log double event
            self.parent.parent.add_history_log_entry(
                f"{self.players[self.current_player_turn].name.upper()} rolled three doubles in a row. Go to JAIL.")

            # Reset counter
            self.players[self.current_player_turn].doubles_counter = 0

            # Move the player to Jail
            self.players[self.current_player_turn].move_direct(self.squares['Jail'])

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
        if self.next_player_turn and (self.extend_turn is False):
            self.players[self.current_player_turn].doubles_counter = 0
            self.current_player_turn = (self.current_player_turn + 1) % len(self.players)

        # Update the next turn text
        self.ids.message_player_turn.text = f"[b][color=#800000]Next is {self.players[self.current_player_turn].name}![/color][/b]"

    def player_land_place(self, final_square):

        # Extend turn
        self.extend_turn = False

        # Default value of payment is 0
        payment = 0

        # Processing the action depending on the square name
        # If the player lands on the 'GO-TO-JAIL' square
        if final_square.name == 'GO-TO-JAIL':
            self.players[self.current_player_turn].move_direct(self.squares['Jail'])
            self.players[self.current_player_turn].in_jail_counter = 0

        # If land on the chance:
        elif final_square.type == "Chance":  # TODO: Implement charging rent if moved to a property that is owned
            chance_card = self.cardInfo.get_card(self.cardInfo.chance, 'chance')
            self.cardInfo.open()
            Clock.schedule_once(lambda dt: self.cardInfo.dismiss(), 3)

            if 'ST.CHARLES PLACE' in chance_card:
                if self.players[self.current_player_turn].current_square != self.squares['Chance1']:
                    payment = -200
                self.players[self.current_player_turn].move_direct(self.squares['Pk1'])

            elif 'HOUSE' in chance_card:  # TODO: Implement this feature
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
                    payment = -200
                self.players[self.current_player_turn].move_direct(self.squares['RR1'])

            elif 'LOAN MATURES' in chance_card:
                payment = -150

            elif 'ILLINOIS AVENUE' in chance_card:
                if self.players[self.current_player_turn].current_square == self.squares['Chance3']:
                    payment = -200
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
                payment = 15
            elif 'PAY EACH PLAYER' in chance_card:  # TODO: Implement this one
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
                payment = -100

            elif ("DOCTOR'S FEES" in chest_card) or ('SCHOOL FEES' in chest_card):
                payment = 50

            elif 'JAIL FREE' in chest_card:
                self.players[self.current_player_turn].jail_free_card = True

            elif 'INCOME TAX REFUND' in chest_card:
                payment = -20

            elif 'HOSPITAL FEES' in chest_card:
                payment = 100

            elif 'TO JAIL' in chest_card:
                self.players[self.current_player_turn].move_direct(self.squares['Jail'])
                self.players[self.current_player_turn].in_jail_counter = 0

            elif 'BIRTHDAY' in chest_card:  # TODO: Implement this!
                self.players[self.current_player_turn].money += 25
                for player in self.players:
                    if player != self.players[self.current_player_turn]:
                        player.money -= 10
                        self.players[self.current_player_turn].money += 10

            elif 'FROM SALE OF STOCK' in chest_card:
                payment = 50

            elif 'WON SECOND PRIZE' in chest_card:
                payment = -10

            elif 'STREET REPAIRS' in chest_card:  # TODO: Implement this feature
                self.players[self.current_player_turn].money -= 40 * self.players[self.current_player_turn].house
                self.players[self.current_player_turn].money -= 115 * self.players[self.current_player_turn].hotel

            elif 'TO GO' in chest_card:
                self.players[self.current_player_turn].move_direct(self.squares['GO'])
                payment = -200

            elif 'BANK ERROR' in chest_card:
                payment = -200

        # If land on tax penalty squares
        elif final_square.type == "Tax":

            if final_square.name == 'ITax':
                payment = 200

            elif final_square.name == 'LTax':
                payment = 100

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
                elif self.players[self.current_player_turn].calculate_net_worth() >= final_square.cost_value:
                    self.buy_or_auction = CardSelectPop(root=self,
                                                        current_player=self.players[self.current_player_turn],
                                                        square_property=final_square,
                                                        button_left='MORTGAGE',
                                                        button_right='AUCTION')
                else:
                    self.buy_or_auction = PlayerAuctionPop(root=self, current_property=final_square)

                self.buy_or_auction.open()

            # else the property is owned
            else:

                # If the property is owned by someone else and it is not mortgage, PAY RENT!
                if final_square.owner != self.players[self.current_player_turn] and final_square.mortgage is False:
                    # Calculate the rent due for the final_square
                    payment = final_square.calculate_rent()

        self.process_payment(final_square, payment)

    def process_payment(self, final_square, payment):

        # If the player can afford the rent
        if self.players[self.current_player_turn].money >= payment:
            # Pay rent
            self.players[self.current_player_turn].money -= payment

            if final_square.owner and payment > 0:
                final_square.owner.money += payment
                log_text = f"{self.players[self.current_player_turn].name.upper()} paid ${payment} to {final_square.owner.name.upper()}"
                self.parent.parent.add_history_log_entry(log_text)
            elif payment > 0:
                log_text = f"{self.players[self.current_player_turn].name.upper()} paid ${payment} to the BANK"
                self.parent.parent.add_history_log_entry(log_text)

        elif self.players[self.current_player_turn].calculate_net_worth() >= payment:

            # Create popup infornming that if the next player's turn starts and
            # they still have a negative balance that they will be kick out of the game
            warning_pop = WarningPop(root=self, indebted_player=self.players[self.current_player_turn])
            warning_pop.open()

            # Deduct their money
            self.players[self.current_player_turn].money -= payment

            if final_square.owner and payment > 0:
                final_square.owner.money += payment
                log_text = f"{self.players[self.current_player_turn].name.upper()} paid ${payment} to {final_square.owner.name.upper()}"
                self.parent.parent.add_history_log_entry(log_text)
            elif payment > 0:
                log_text = f"{self.players[self.current_player_turn].name.upper()} paid ${payment} to the BANK"
                self.parent.parent.add_history_log_entry(log_text)

            # Place player in the debted players list
            self.debt_players.append(self.players[self.current_player_turn])

        else:  # They lost the game

            # Remove the player that lost
            if final_square.owner:
                self.remove_player(self.players[self.current_player_turn], pay_player=final_square.owner)
            else:
                self.remove_player(self.players[self.current_player_turn])

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

        # Log movement
        self.parent.parent.add_history_log_entry(
            f"{self.players[self.current_player_turn].name.upper()} rolls a total of {steps} and lands on {final_square.full_name}")

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
        step_1, step_2 = self.roll_dice(None)
        # step_1 = 2
        # step_2 = 2

        # If they roll doubles, then let them out
        if step_1 == step_2:

            log_text = f"{self.players[self.current_player_turn].name.upper()} rolls doubles and leaves JAIL without paying the fee"
            self.parent.parent.add_history_log_entry(log_text)

            self.players[self.current_player_turn].doubles_counter = 0
            self.players[self.current_player_turn].in_jail_counter = -1
            self.player_start_turn([step_1, step_2])

        # If they don't roll a doubles, they stay in jail and move to the next player
        else:

            log_text = f"{self.players[self.current_player_turn].name.upper()} did not roll doubles. Stays in JAIL"
            self.parent.parent.add_history_log_entry(log_text)

            self.players[self.current_player_turn].in_jail_counter += 1
            self.current_player_turn = (self.current_player_turn + 1) % len(self.players)
            self.ids.message_player_turn.text = f"[b][color=#800000]\n\nNext is {self.players[self.current_player_turn].name}![/color][/b]"
            return 0

    def pay_out_jail(self):

        # Change attributes to make player out of jail
        if self.players[self.current_player_turn].jail_free_card:
            log_text = f"{self.players[self.current_player_turn].name.upper()} used GET-OUT-OF-JAIL card"
        else:
            self.players[self.current_player_turn].money -= 50
            log_text = f"{self.players[self.current_player_turn].name.upper()} paid $50 to get-out of JAIL"

        self.players[self.current_player_turn].in_jail_counter = -1
        self.players[self.current_player_turn].jail_free_card = False

        self.parent.parent.add_history_log_entry(log_text)

    def buy_property(self, player, square_property, cost=None):

        # Deduce the player's money according to the properties value
        if cost or (cost == 0):
            player.money -= cost
        else:
            player.money -= square_property.cost_value
            cost = square_property.cost_value

        # Modify the attribute owned in square_property to the player
        square_property.owner = player

        # Place the ownership icon
        square_property.update_player_icon()

        # Store the property into the player.property_own
        player.property_own.append(square_property)

        # Update the fullset attribute if the set is completed in this buy action
        square_property.fullset_update()

        # Update the player's info in the right side panel
        self.parent.parent.update_players_to_frame()

        # Log purchase
        self.parent.parent.add_history_log_entry(
            f"{player.name.upper()} acquires {square_property.full_name} for {cost}")

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

        # Create mortgage popup
        self.mortgageInfo = MortgagePop(root=self)
        self.mortgageInfo.open()

    def mortgage_to_buy_property(self, player, square_property):

        # Create mortgage popup
        binding_func = functools.partial(self.check_if_mortgaged_enough, player, square_property)
        self.mortgageInfo = MortgagePop(root=self, dismiss_binding_fn=binding_func)
        self.mortgageInfo.open()

    def check_if_mortgaged_enough(self, player, square_property):

        print(f"check_if_mortgaged_enough function: {player} - {square_property}")

        # If they have enough money, they should buy it the property
        if player.money >= square_property.cost_value:
            self.buy_property(player, square_property)
        else: # else auction immediately!
            self.auction_pop = PlayerAuctionPop(root=self, current_property=square_property)
            self.auction_pop.open()

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

    def remove_player(self, bankrupt_player, pay_player=None):

        # Give all the properties to the pay player if applicable
        if pay_player:
            for square_property in bankrupt_player.property_own:
                self.buy_property(pay_player, square_property, cost=0)
                square_property.update_player_icon()
        else:  # Give the properties back to the bank
            for square_property in bankrupt_player.property_own:
                square_property.owner = None
                square_property.mortgage = False
                square_property.update_player_icon()

        # Account for the deletion of the player
        if self.players.index(bankrupt_player) <= self.current_player_turn:
            self.current_player_turn -= 1

        # Remove bankrupt player from the list
        self.remove_widget(bankrupt_player)
        self.players.remove(bankrupt_player)

        # Check if only one player left
        if len(self.players) == 1:

            wingame = WinnerPop(winner=self.players[0])
            wingame.open()

        # Create popup to inform of player's bankrupcy
        else:

            lostgame = LoserPop(root=self, bankrupt_player=bankrupt_player, pay_player=pay_player)
            lostgame.open()

        # Delete the player
        del bankrupt_player


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
        self.mortgage = False
        self.full_set = False

    def __str__(self):
        return f"BoardSquare [Name: {self.name} - Cost Value: {self.cost_value} - Owner: {self.owner}]"

    def __repr__(self):
        return f"BoardSquare [Name: {self.name} - Cost Value: {self.cost_value}]"

    def update_player_icon(self):

        # If the square property has an owner, place the ownership icon
        if self.owner:

            # If there was a previous owner icon, remove that widget
            if self.owner_icon is not None:
                self.root.remove_widget(self.owner_icon)

            if self.mortgage:
                color = (0.1, 0.1, 0.1, 1)
            else:
                color = (1, 1, 1, 1)

            # Create a grey-version of the player's icon to visualize ownership
            self.owner_icon = DynamicImage(
                root=self.root,
                source=self.owner.source,
                ratio_pos=self.owner_icon_placement,
                ratio_size=(self.owner.ratio_size[0] / 2, self.owner.ratio_size[1] / 2),
                color=color
            )

            # Adding the image to the game_board
            self.root.add_widget(self.owner_icon, index=-1)

        else:  # remove the ownership icon

            self.root.remove_widget(self.owner_icon)
            self.owner_icon = None

    def calculate_rent(self):

        if self.type == 'Property':

            if self.full_set:
                if self.number_of_houses == 5:
                    return self.rents['rent_hotel_1']
                elif self.number_of_houses == 0:
                    return self.rents['rent_set']
                else:
                    return self.rents[f'rent_house_{self.number_of_houses}']
            else:
                return self.rents['rent']

        elif self.type == 'Railroad':

            # Count how many railroads they have
            rr_counter = 0
            for square_property in self.owner.property_own:
                if square_property.type == 'Railroad':
                    rr_counter += 1

            return self.rents[f'rent_{rr_counter}']

        else:  # Utilities
            step_1, step_2 = self.root.roll_dice(None)
            total_steps = step_1 + step_2

            # Count how many utilities they have
            util_counter = 0
            for square_property in self.owner.property_own:
                if square_property.type == 'Utilities':
                    util_counter += 1

            # If the player own the full property of the Utilities
            if util_counter == len(C.BOARD_SQUARE_FULLSETS['Utilities']):
                rent = 10 * total_steps

            else:
                # If the player only own one of the full property of the Utilities
                rent = 4 * total_steps

            log_text = f"{self.players[self.current_player_turn].name.upper()} rolls a total of {total_steps}, pays {rent} to {self.owner.name.upper()}"
            self.parent.parent.add_history_log_entry(log_text)

            return rent

    def fullset_update(self):

        # Check for full set condition
        current_set = self.property_set
        set_counter = 0
        for square_property in self.owner.property_own:

            if current_set == square_property.property_set:
                set_counter += 1

        # Check if set is full for the player
        full_set = (set_counter == len(C.BOARD_SQUARE_FULLSETS[current_set]))

        # Obtain the set's properties and modify their full_set attribute
        for square_property in self.owner.property_own:

            if square_property.property_set == current_set:
                square_property.full_set = full_set

    def update_house_markers(self):

        color_values = []
        r = [1, 0, 0, 1]
        g = [0, 1, 0, 1]
        n = [0, 0, 0, 0]

        # Select the correct color sequence given the number of houses
        if self.number_of_houses < 5:
            for i in range(4):  # 0, 1, 2, 3
                if i < self.number_of_houses:
                    color_values.append(g)
                else:
                    color_values.append(n)
        else:
            color_values = [r, n, n, n]

        # Change the color attribute of the houses
        for house, color in zip(self.houses, color_values):
            house.color = color


class CardInfoPop(Popup):
    def __init__(self, **kwargs):
        # Obtain root reference
        self.root = kwargs.pop('root')

        super().__init__(**kwargs)

        self.chance = queue.Queue(maxsize=0)

        self.chance.put('ADVANCE TO ILLINOIS AVENUE.\nIF YOU PASS GO, COLLECT $200.')
        self.chance.put('GO DIRECTLY TO JAIL.\nDO NOT COLLECT $200.')
        self.chance.put('SPEEDING FINE. PAY $15.')
        self.chance.put('YOUR BUILDING LOAN MATURES.\nCOLLECT $150.')
        self.chance.put('TAKE A TRIP TO READING\nRAILROAD. IF YOU PASS GO,\nCOLLECT $200.')
        self.chance.put('GET OUT OF JAIL FREE.')
        self.chance.put('YOU HAVE BEEN ELECTED\nCHAIRMAN OF THE BOARD.\nPAY EACH PLAYER $50.')
        self.chance.put('ADVANCE TO THE NEAREST\nUTILITY.')
        self.chance.put('ADVANCE TO THE NEXT\nRAILROAD.')
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
        elif choice == 'PAY $50' or choice == 'USE JAIL FREE CARD':
            self.root.pay_out_jail()

        # Execute the buy_property from the gameboard
        elif choice == 'BUY':
            self.root.buy_property(self.current_player, self.square_property)

        # Execute the mortgage_property from the gameboard
        elif choice == 'MORTGAGE':
            self.root.mortgage_to_buy_property(self.current_player, self.square_property)

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
            self.skipped_bids = 1

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

        if self.skipped_bids > len(self.players_info) - 1:

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

        # Log the auction and its winner, for what price as well
        log_text = f"{self.bid_winner.player.name.upper()} wins the auction for {self.current_property.full_name} by paying {self.highest_bid}"
        self.root.parent.parent.add_history_log_entry(log_text)

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

        if (self.left_player is not None) and (self.right_player is not None):
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

            # Add right's ownership
            self.root.buy_property(self.right_player, traded_square_property, cost=0)

        # Right player gets the left properties
        for traded_square_property in self.right_square_properties:
            # Remove right's ownership
            self.right_player.property_own.remove(traded_square_property)

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

        # Trade event log
        left_property = ",".join([sq.full_name for sq in self.left_square_properties])
        right_property = ",".join([sq.full_name for sq in self.right_square_properties])

        left_property = left_property if left_property else "no property"
        right_property = right_property if right_property else "no property"

        log_text = f"{self.left_player.name.upper()} traded {left_property} and ${left_slider_value} for {self.right_player.name.upper()}'s {right_property} and ${right_slider_value}"
        self.root.parent.parent.add_history_log_entry(log_text)

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

        if 'dismiss_binding_fn' in kwargs.keys():
            self.dismiss_binding_fn = kwargs.pop('dismiss_binding_fn')
        else:
            self.dismiss_binding_fn = None

        super().__init__(**kwargs)

        self.selected_square_properties = []
        self.ids.accept_btn.disabled = True

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

        if selected_player is not None:
            self.ids.accept_btn.disabled = False

    def update_property_container(self, selected_player):

        # Clean property container
        self.ids.property_container.clear_widgets()

        # Fill the property container given the properties of the
        # selected player
        for square_property in selected_player.property_own:

            # If the property has houses, then it cannot be mortgaged
            if square_property.number_of_houses != 0:
                continue

            # Determine color of property
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

        # if self.total_money != self.player.money:
        #     self.ids.select_name_btn.disabled = True
        # else:
        #     self.ids.select_name_btn.disabled = False
        if self.mortgage_unmortgage_money:
            self.ids.select_name_btn.disabled = True
        else:
            self.ids.select_name_btn.disabled = False

    def accept(self):

        # The properties that were selected must be mortgage/unmortgage
        for square_property in self.selected_square_properties:
            # Update the mortgage boolean
            square_property.mortgage = not square_property.mortgage

            # Call the gameboard to make the properties look mortgage or unmortgage
            square_property.update_player_icon()

        # Modify the player's money given the mortgage_unmortgage money
        self.player.money = self.total_money

        # Inform root to update property ownership and update player's money
        self.root.parent.parent.update_players_to_frame()

        # Log mortgage event
        mortgaged_property = ",".join(
            [square_property.full_name for square_property in self.selected_square_properties if
             square_property.mortgage is True])
        unmortgaged_property = ",".join(
            [square_property.full_name for square_property in self.selected_square_properties if
             square_property.mortgage is False])
        mortgaged_property = mortgaged_property if mortgaged_property else "no property"
        unmortgaged_property = unmortgaged_property if unmortgaged_property else "no property"

        log_text = f"{self.player.name.upper()} mortgaged {mortgaged_property} and unmortgage {unmortgaged_property}"
        self.root.parent.parent.add_history_log_entry(log_text)

        # Dismiss the popup
        self.dismiss()

    def dismiss(self):

        if self.dismiss_binding_fn:
            self.dismiss_binding_fn()

        super().dismiss()


class BuyHousesPop(Popup):

    def __init__(self, **kwargs):
        # Obtain root reference
        self.root = kwargs.pop('root')
        self.btns = {}
        self.entries = {}
        self.total_money = 0

        super().__init__(**kwargs)

        self.selected_square_properties = []
        self.ids.accept_btn.disabled = True

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

        if selected_player is not None:
            self.ids.accept_btn.disabled = False

    def update_property_container(self, selected_player):

        # Clean property container
        self.ids.property_container.clear_widgets()

        # Fill the property container given the properties of the
        # selected player
        for square_property in selected_player.property_own:

            # If the property is not part of a full set, then ignore it
            if square_property.full_set is False or square_property.type != 'Property':
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

                # No matter what, if you have a mortgage property, you cannot buy/sell houses
                if entry.square_property.mortgage:
                    entry.ids.buy_houses.disabled = True
                    entry.ids.sell_houses.disabled = True

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
                # Change the attributes of the property to the new number of houses
                entry.square_property.number_of_houses = entry.total_houses

                # Update the visibility of the house markers depending on the number
                # of houses.
                entry.square_property.update_house_markers()

        # Modify the player's money given the mortgage_unmortgage money
        self.player.money = self.total_money

        # Inform root to update property ownership and update player's money
        self.root.parent.parent.update_players_to_frame()

        # Log buy/sell houses
        bought_text = []
        sold_text = []
        for set_name in self.entries.keys():
            for entry in self.entries[set_name]:

                house_diff = entry.total_houses - entry.initial_houses
                if entry.total_houses != 5 and entry.initial_houses != 5:
                    if house_diff > 0:
                        bought_text.append(f"{house_diff} house(s) for {entry.square_property.full_name}")
                    elif house_diff < 0:
                        sold_text.append(f'{-house_diff} house(s) for {entry.square_property.full_name}')
                elif entry.total_houses == 5 and entry.initial_houses != 5:
                    bought_text.append(f"an hotel for {entry.square_property.full_name}")
                elif entry.initial_houses == 5 and entry.total_houses != 5:
                    sold_text.append(f"an hotel for {entry.square_property.full_name}")

        bought_text = ",".join(bought_text) if bought_text else "no houses/hotel"
        sold_text = ",".join(sold_text) if sold_text else "no houses/hotel"

        log_text = f"{self.player.name.upper()} bought {bought_text} and sold {sold_text}"
        self.root.parent.parent.add_history_log_entry(log_text)

        # Dismiss the popup
        self.dismiss()


class BuyHousesEntry(GridLayout):
    square_property = ObjectProperty()
    initial_houses = NumericProperty()
    total_houses = NumericProperty()


class LoserPop(Popup):
    def __init__(self, **kwargs):

        self.root = kwargs.pop('root')
        self.bankrupt_player = kwargs.pop('bankrupt_player')
        self.pay_player = kwargs.pop('pay_player')

        super().__init__(**kwargs)

        self.ids.loser_icon.source = self.bankrupt_player.source

        if self.pay_player:
            self.ids.loser_info.text = f'[b][color=#000000]SORRY, {self.bankrupt_player.name.upper()} LOST THE GAME!\n' \
                                       f'ALL YOUR BELONGS WILL BE GIVEN TO {self.pay_player.name.upper()}.[/b][/color]'
            log_text = f"{self.bankrupt_player.name.upper()} is bankrupt. All belongings are given to the {self.pay_player.name.upper()}"
        else:
            self.ids.loser_info.text = f'[b][color=#000000]SORRY, {self.bankrupt_player.name.upper()} LOST THE GAME!\n' \
                                       f'ALL YOUR BELONGS WILL BE GIVEN\nTO THE BANK.[/b][/color]'
            log_text = f"{self.bankrupt_player.name.upper()} is bankrupt. All belongings are given to the BANK"

        self.root.parent.parent.add_history_log_entry(log_text)


class WarningPop(Popup):
    def __init__(self, **kwargs):
        self.root = kwargs.pop('root')
        self.indebted_player = kwargs.pop('indebted_player')

        super().__init__(**kwargs)

        self.ids.indebted_player_icon.source = self.indebted_player.source
        self.ids.indebted_player_info.text = f'[b][color=#000000]{self.indebted_player.name.upper()} YOU NEED TO PAY THE DEBT\nOR WILL BE BANKRUPTED.[/b][/color]'

        log_text = f"{self.indebted_player.name.upper()} should pay off their debt. If not, they LOSE!"
        self.root.parent.parent.add_history_log_entry(log_text)


class WinnerPop(Popup):
    def __init__(self, **kwargs):
        self.winner = kwargs.pop('winner')

        super().__init__(**kwargs)

        # Place the player's icon image source in to the winner's icon source
        self.ids.winner_icon.source = self.winner.source
        self.ids.winner_info.text = f'[b][color=#000000]{self.winner.name.upper()} YOU WIN!\nCONGRATS![/b][/color]'
