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
from board_squares import *


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
            if isinstance(square_property, PropertySquare) and (square_property.number_of_houses != 0):
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
            if not isinstance(square_property, PropertySquare) or (square_property.full_set is False):
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
