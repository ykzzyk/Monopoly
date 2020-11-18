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
import os

from pprint import pprint
import pdb

# Local Imports

from General.general_classes import DynamicImage
from General.general_classes import PlayerIcon
from General import constants as C
import popup_classes as pc
from board_squares import *

board_square_table = {
    'Property': PropertySquare,
    'Railroad': RailroadSquare,
    'Utilities': UtilitySquare,
    'Chance': ChanceSquare,
    'Chest': ChestSquare,
    'Tax': TaxSquare,
    'Corner': CornerSquare
}


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

    def move_direct(self, final_square, start_animation=True):

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
        if start_animation:
            move_animation.start(self)

        # Update the ratio_pos of the object
        self.ratio_pos = new_pos

        # Bind the move animation to the self.player_land_place since it needs to be executed on its completion
        move_animation.bind(on_complete=lambda _, __: self.root.player_land_place(final_square=final_square))

        return move_animation

    def calculate_net_worth(self):

        net_worth = self.money

        for square_property in self.property_own:

            # Accounting for property value
            if not square_property.mortgage:
                net_worth += square_property.mortgage_value

            # Accounting for house/hotel values
            if isinstance(square_property, PropertySquare):
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

            # Finding the type of the square
            for square_type in C.BOARD_SQUARE_TYPE.keys():
                if square_name in C.BOARD_SQUARE_TYPE[square_type]:
                    this_square_type = square_type
                    break

            # Select the right type of square given the type
            BoardSquare = board_square_table[this_square_type]

            # Create the square
            self.squares[square_name] = BoardSquare(square_name, self)

        # Keeping track of the current player
        self.current_player_turn = 0

        # Next player turn tracker
        self.next_player_turn = False

        # Container for the player widget objects
        self.players = []

        # Creating a card info pop instance for later re-usable use
        self.cardInfo = pc.CardInfoPop(root=self)

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

            if isinstance(square, OwnableSquare):
                square.mortgage = False
                square.owner = None
                square.update_player_icon()

                if isinstance(square, PropertySquare):
                    square.number_of_houses = 0
                    square.full_set = False
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
        #self.buy_property(self.players[1], self.squares['Br1'])
        #self.buy_property(self.players[2], self.squares['Util1'])

        self.players[0].money = 1
        self.players[1].money = 1
        #self.players[2].money = 3
        # '''

        # Adding the player to the players info box
        Clock.schedule_once(self.parent.parent.update_players_to_frame)

    # Player Turn
    def player_start_turn(self, *args, rolls=None):

        # Check for any players that are indebted, if so, kick them OUT!
        for player in self.players:
            if player.money < 0:
                self.remove_player(player)

        # Update to next player if doubles is not true
        if self.next_player_turn:
            self.players[self.current_player_turn].doubles_counter = 0
            self.current_player_turn = (self.current_player_turn + 1) % len(self.players)

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
                self.jail_decision = pc.CardSelectPop(root=self,
                                                      current_player=self.players[self.current_player_turn],
                                                      square_property=None,
                                                      button_left='USE JAIL FREE CARD',
                                                      button_right='ROLL AGAIN')
            else:
                self.jail_decision = pc.CardSelectPop(root=self,
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
        step_1 = 5
        step_2 = 2
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

    def player_land_place(self, final_square):

        # Unbinding the stop_animation function
        self.unbind(size=self.stop_animation)

        # Rebinding the roll dice button
        self.ids.player_turn_button.bind(on_release=self.player_start_turn)

        # Process the action of the square that the player landed on
        payment = final_square.land_action(self.players[self.current_player_turn])

        # Process payment
        self.process_payment(final_square, payment)

        # Update the next turn text
        self.ids.message_player_turn.text = f"[b][color=#800000]Next is {self.players[self.current_player_turn].name}![/color][/b]"

    def process_payment(self, final_square, payment):

        # If the player can afford the rent
        if self.players[self.current_player_turn].money >= payment:
            # Pay rent
            self.players[self.current_player_turn].money -= payment

            if isinstance(final_square, OwnableSquare) and payment > 0:
                final_square.owner.money += payment
                log_text = f"{self.players[self.current_player_turn].name.upper()} paid ${payment} to {final_square.owner.name.upper()}"
                self.parent.parent.add_history_log_entry(log_text)
            elif payment > 0:
                log_text = f"{self.players[self.current_player_turn].name.upper()} paid ${payment} to the BANK"
                self.parent.parent.add_history_log_entry(log_text)

        elif self.players[self.current_player_turn].calculate_net_worth() >= payment:

            # Create popup infornming that if the next player's turn starts and
            # they still have a negative balance that they will be kick out of the game

            # Deduct their money
            self.players[self.current_player_turn].money -= payment

            if isinstance(final_square, OwnableSquare) and payment > 0:
                final_square.owner.money += payment
                log_text = f"{self.players[self.current_player_turn].name.upper()} paid ${payment} to {final_square.owner.name.upper()}"
                self.parent.parent.add_history_log_entry(log_text)
            elif payment > 0:
                log_text = f"{self.players[self.current_player_turn].name.upper()} paid ${payment} to the BANK"
                self.parent.parent.add_history_log_entry(log_text)

            if isinstance(final_square, OwnableSquare):
                self.warn_player(self.players[self.current_player_turn])
            else:
                Clock.schedule_once(functools.partial(self.warn_player, self.players[self.current_player_turn]), 3)

        else:  # They lost the game

            # Remove the player that lost
            if isinstance(final_square, OwnableSquare):
                self.remove_player(self.players[self.current_player_turn], pay_player=final_square.owner)
            else:
                Clock.schedule_once(functools.partial(self.remove_player, self.players[self.current_player_turn], None), 3)

        # Update the player's info in the right side panel
        self.parent.parent.update_players_to_frame()

    # Player movement
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
            log_text = f'{self.players[self.current_player_turn].name.upper()} passed GO and collected $200.'
            self.parent.parent.add_history_log_entry(log_text)

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
        move_animation.bind(on_complete=lambda _, __: self.player_land_place(final_square=final_square))

        # Bind the animation to the size of the window
        # print(f'Binding the stop_animation function for player: {self.players[self.current_player_turn].name}')
        self.stop_animation_flag = False
        self.bind(size=self.stop_animation)

    # Handling player decisions
    def roll_out_jail(self):

        self.next_player_turn = False

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
        self.next_player_turn = False

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
        if isinstance(square_property, PropertySquare):
            square_property.fullset_update()

        # Update the player's info in the right side panel
        self.parent.parent.update_players_to_frame()

        # Log purchase
        self.parent.parent.add_history_log_entry(
            f"{player.name.upper()} acquires {square_property.full_name} for {cost}")

    def auction_property(self, square_property):

        self.auction_pop = pc.PlayerAuctionPop(
            root=self,
            current_property=square_property
        )

        self.auction_pop.open()

    def trade(self):
        self.tradeInfo = pc.TradePop(root=self)
        self.tradeInfo.open()

    def mortgage_property(self):

        # Create mortgage popup
        self.mortgageInfo = pc.MortgagePop(root=self)
        self.mortgageInfo.open()

    def mortgage_to_buy_property(self, player, square_property):

        # Create mortgage popup
        binding_func = functools.partial(self.check_if_mortgaged_enough, player, square_property)
        self.mortgageInfo = pc.MortgagePop(root=self, dismiss_binding_fn=binding_func)
        self.mortgageInfo.open()

    def check_if_mortgaged_enough(self, player, square_property):

        print(f"check_if_mortgaged_enough function: {player} - {square_property}")

        # If they have enough money, they should buy it the property
        if player.money >= square_property.cost_value:
            self.buy_property(player, square_property)
        else:  # else auction immediately!
            self.auction_pop = pc.PlayerAuctionPop(root=self, current_property=square_property)
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
        self.buyHouseInfo = pc.BuyHousesPop(root=self)
        self.buyHouseInfo.open()

    def remove_player(self, bankrupt_player, pay_player=None, *args):

        print(bankrupt_player)

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

            wingame = pc.WinnerPop(winner=self.players[0])
            wingame.open()

        # Create popup to inform of player's bankrupcy
        else:

            lostgame = pc.LoserPop(root=self, bankrupt_player=bankrupt_player, pay_player=pay_player)
            lostgame.open()

        # Delete the player
        del bankrupt_player

    def warn_player(self, indebted_player, *args):

        warning_pop = pc.WarningPop(root=self, indebted_player=indebted_player)
        warning_pop.open()