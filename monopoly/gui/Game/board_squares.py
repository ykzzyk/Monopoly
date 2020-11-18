import abc

from kivy.clock import Clock

from General.general_classes import DynamicImage
from General.general_classes import PlayerIcon
from General import constants as C
import popup_classes as pc


class AbstractBoardSquare(abc.ABC):

    def __init__(self, square_name, root):
        # Store the board widget
        self.root = root

        # Storing the name of the square
        self.name = square_name

        # Obtain the square's pixel_ratio location
        self.physical_location = C.BOARD_SQUARE_LOCATIONS[square_name]

        # Obtain the chronological number of the property
        self.sequence_id = list(C.BOARD_SQUARE_LOCATIONS.keys()).index(square_name)

        # Obtain the square's property cost (if applicable)
        self.full_name = C.BOARD_SQUARE_ATTRIBUTES[square_name]['full_name']

    def __str__(self):
        return f"BoardSquare [Name: {self.name}]"

    def __repr__(self):
        return f"BoardSquare [Name: {self.name}]"

    @abc.abstractmethod
    def land_action(self):
        pass


class OwnableSquare(AbstractBoardSquare):

    def __init__(self, square_name, root):
        super().__init__(square_name, root)

        # Pre-set values of properties
        self.owner = None
        self.owner_icon = None
        self.mortgage = False

        self.cost_value = C.BOARD_SQUARE_ATTRIBUTES[square_name]['cost_value']
        self.mortgage_value = C.BOARD_SQUARE_ATTRIBUTES[square_name]['mortgage_value']
        self.unmortgage_value = C.BOARD_SQUARE_ATTRIBUTES[square_name]['unmortgage_value']

        # Determine the set for the property
        for property_set in C.BOARD_SQUARE_FULLSETS.keys():
            if square_name in C.BOARD_SQUARE_FULLSETS[property_set]:
                self.property_set = property_set

        # For only properties and railroads
        if not isinstance(self, UtilitySquare):
            if square_name in C.BOARD_SQUARE_RENT.keys():
                self.rents = C.BOARD_SQUARE_RENT[square_name]

        # Calculating the player ownership icon placement
        add = lambda x, y: x + y
        subtract = lambda x, y: x - y

        def offset(data, axis, fn, value=C.PLAYER_ICON_OFFSET):
            if axis == 'x':
                return (fn(data[0], value), data[1])
            return (data[0], fn(data[1], value))

        # For determine the overall section (line{1,2,3,4} or corner) of the property
        self.section = None
        for section in C.BOARD_LINES.keys():
            if square_name in C.BOARD_LINES[section]:
                self.section = section

        if self.section == 'Line1':
            if isinstance(self, RailroadSquare) or isinstance(self, UtilitySquare):
                self.owner_icon_placement = offset(self.physical_location, 'x', add, value=C.RR_PLAYER_ICON_OFFSET)
            else:  # Property Square
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
            if isinstance(self, RailroadSquare) or isinstance(self, UtilitySquare):
                self.owner_icon_placement = offset(self.physical_location, 'y', subtract, value=C.RR_PLAYER_ICON_OFFSET)
            else:  # PropertySquare
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
            if isinstance(self, RailroadSquare) or isinstance(self, UtilitySquare):
                self.owner_icon_placement = offset(self.physical_location, 'x', subtract, value=C.RR_PLAYER_ICON_OFFSET)
            else:  # PropertySquare
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
            if isinstance(self, RailroadSquare) or isinstance(self, UtilitySquare):
                self.owner_icon_placement = offset(self.physical_location, 'y', add, value=C.RR_PLAYER_ICON_OFFSET)
            else:  # PropertySquare
                self.owner_icon_placement = offset(self.physical_location, 'y', subtract)
                self.set_line = offset(self.physical_location, 'y', add, value=C.SET_LINE_OFFSET)
                self.house_locations = [
                    offset(self.set_line, 'x', add, value=1.15 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'x', add, value=0.5 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'x', subtract, value=0.175 * C.HOUSE_OFFSET),
                    offset(self.set_line, 'x', subtract, value=0.85 * C.HOUSE_OFFSET)
                ]
                self.buy_house_cost = 200

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

    def land_action(self, player):

        payment = 0

        # if the property is not owned
        if self.owner is None:

            # Determine if the player has enough money to buy the property
            if player.money >= self.cost_value:
                # Buy or Auction
                self.root.buy_or_auction = pc.CardSelectPop(root=self.root,
                                                            current_player=player,
                                                            square_property=self,
                                                            button_left='BUY',
                                                            button_right='AUCTION')
            elif player.calculate_net_worth() >= self.cost_value:
                self.root.buy_or_auction = pc.CardSelectPop(root=self.root,
                                                            current_player=player,
                                                            square_property=self,
                                                            button_left='MORTGAGE',
                                                            button_right='AUCTION')
            else:
                self.root.buy_or_auction = pc.PlayerAuctionPop(root=self.root, current_property=self)

            self.root.buy_or_auction.open()

        # else the property is owned
        else:

            # If the property is owned by someone else and it is not mortgage, PAY RENT!
            if self.owner != player and self.mortgage is False:
                # Calculate the rent due for the self
                payment = self.calculate_rent()

        return payment

    def __str__(self):
        return f"BoardSquare [Name: {self.name} - Cost Value: {self.cost_value} - Owner: {self.owner}]"

    def __repr__(self):
        return f"BoardSquare [Name: {self.name} - Cost Value: {self.cost_value}]"


class PropertySquare(OwnableSquare):

    def __init__(self, square_name, root):
        super().__init__(square_name, root)

        self.number_of_houses = 0  # 5 = 1 hotel
        self.full_set = False

        # Draw the houses
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

    def calculate_rent(self):
        if self.full_set:
            if self.number_of_houses == 5:
                return self.rents['rent_hotel_1']
            elif self.number_of_houses == 0:
                return self.rents['rent_set']
            else:
                return self.rents[f'rent_house_{self.number_of_houses}']
        else:
            return self.rents['rent']

    def fullset_update(self):

        # Check for full set condition
        set_counter = 0
        for square_property in self.owner.property_own:
            if isinstance(square_property, PropertySquare):
                if self.property_set == square_property.property_set:
                    set_counter += 1

        # Check if set is full for the player
        full_set = (set_counter == len(C.BOARD_SQUARE_FULLSETS[self.property_set]))

        # Obtain the set's properties and modify their full_set attribute
        for square_property in self.owner.property_own:
            if isinstance(square_property, PropertySquare):
                if square_property.property_set == self.property_set:
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


class RailroadSquare(OwnableSquare):

    def calculate_rent(self):
        # Count how many railroads they have
        rr_counter = 0
        for square_property in self.owner.property_own:
            if isinstance(square_property, RailroadSquare):
                rr_counter += 1

        return self.rents[f'rent_{rr_counter}']


class UtilitySquare(OwnableSquare):

    def calculate_rent(self):
        step_1, step_2 = self.root.roll_dice(None)
        total_steps = step_1 + step_2

        # Count how many utilities they have
        util_counter = 0
        for square_property in self.owner.property_own:
            if isinstance(square_property, UtilitySquare):
                util_counter += 1

        # If the player own the full property of the Utilities
        if util_counter == len(C.BOARD_SQUARE_FULLSETS['Utilities']):
            rent = 10 * total_steps

        else:
            # If the player only own one of the full property of the Utilities
            rent = 4 * total_steps

        log_text = f"{self.root.players[self.root.current_player_turn].name.upper()} rolls a total of {total_steps}, pays {rent} to {self.owner.name.upper()}"
        self.root.parent.parent.add_history_log_entry(log_text)

        return rent


class ChanceSquare(AbstractBoardSquare):

    def land_action(self, player):

        chance_card = self.root.cardInfo.get_card(self.root.cardInfo.chance, 'chance')
        self.root.cardInfo.open()

        Clock.schedule_once(lambda dt: self.root.cardInfo.dismiss(), 3)

        payment = 0
        move_animation = False

        if 'ST.CHARLES PLACE' in chance_card:
            if player.current_square != self.root.squares['Chance1']:
                payment = -200
            move_animation = player.move_direct(self.root.squares['Pk1'], start_animation=False)

        elif 'HOUSE' in chance_card:  # TODO: Implement this feature
            player.money -= 25 * player.house
            player.money -= 100 * player.hotel
        elif 'THREE' in chance_card:
            # Final square ID
            final_id = player.current_square.sequence_id - 3
            final_square = self.root.squares[list(self.root.squares.keys())[final_id]]
            move_animation = player.move_direct(final_square, start_animation=False)

        elif 'JAIL FREE' in chance_card:
            player.jail_free_card = True

        elif 'BOARDWALK' in chance_card:
            move_animation = player.move_direct(self.root.squares['Bl2'], start_animation=False)

        elif 'READING' in chance_card:
            if player.current_square == self.root.squares['Chance3']:
                payment = -200
            move_animation = player.move_direct(self.root.squares['RR1'], start_animation=False)

        elif 'LOAN MATURES' in chance_card:
            payment = -150

        elif 'ILLINOIS AVENUE' in chance_card:
            if player.current_square == self.root.squares['Chance3']:
                payment = -200
            move_animation = player.move_direct(self.root.squares['Rd3'], start_animation=False)

        elif 'NEAREST' in chance_card:
            if player.current_square == self.root.squares['Chance1']:
                move_animation = player.move_direct(self.root.squares['Util1'], start_animation=False)
            elif player.current_square == self.root.squares['Chance2']:
                move_animation = player.move_direct(self.root.squares['Util2'], start_animation=False)
            elif player.current_square == self.root.squares['Chance3']:
                move_animation = player.move_direct(self.root.squares['Util2'], start_animation=False)

        elif 'NEXT\nRAILROAD' in chance_card:
            if player.current_square == self.root.squares['Chance1']:
                move_animation = player.move_direct(self.root.squares['RR2'], start_animation=False)
            elif player.current_square == self.root.squares['Chance2']:
                move_animation = player.move_direct(self.root.squares['RR3'], start_animation=False)
            elif player.current_square == self.root.squares['Chance3']:
                move_animation = player.move_direct(self.root.squares['RR1'], start_animation=False)

        elif 'TO JAIL' in chance_card:
            move_animation = player.move_direct(self.root.squares['Jail'], start_animation=False)
            player.in_jail_counter = 0

        elif 'SPEEDING FINE' in chance_card:
            payment = 15

        elif 'PAY EACH PLAYER' in chance_card:  # TODO: Implement this one
            for other_player in self.root.players:
                if other_player != player:
                    other_player.money += 50
                    player.money -= 50

        # Save the animation to the card info to start the animation once the cardInfo is dismissed
        self.root.cardInfo.add_animation(move_animation, player)

        return payment

    def dismiss(self):

        super().dismiss()


class ChestSquare(AbstractBoardSquare):

    def land_action(self, player):

        chest_card = self.root.cardInfo.get_card(self.root.cardInfo.chest, 'chest')
        self.root.cardInfo.open()
        Clock.schedule_once(lambda dt: self.root.cardInfo.dismiss(), 3)

        payment = 0
        move_animation = False

        if ('MATURES' in chest_card) or ('YOU INHERIT $100' in chest_card):
            payment = -100

        elif ("DOCTOR'S FEES" in chest_card) or ('SCHOOL FEES' in chest_card):
            payment = 50

        elif 'JAIL FREE' in chest_card:
            player.jail_free_card = True

        elif 'INCOME TAX REFUND' in chest_card:
            payment = -20

        elif 'HOSPITAL FEES' in chest_card:
            payment = 100

        elif 'TO JAIL' in chest_card:
            move_animation = player.move_direct(self.root.squares['Jail'], start_animation=False)
            player.in_jail_counter = 0

        elif 'BIRTHDAY' in chest_card:  # TODO: Implement this!
            player.money += 25
            for other_player in self.root.players:
                if other_player != player:
                    other_player.money -= 10
                    player.money += 10

        elif 'FROM SALE OF STOCK' in chest_card:
            payment = 50

        elif 'WON SECOND PRIZE' in chest_card:
            payment = -10

        elif 'STREET REPAIRS' in chest_card:  # TODO: Implement this feature
            player.money -= 40 * player.house
            player.money -= 115 * player.hotel

        elif 'TO GO' in chest_card:
            move_animation = player.move_direct(self.root.squares['GO'], start_animation=False)
            payment = -200

        elif 'BANK ERROR' in chest_card:
            payment = -200

        # Save the animation to the card info to start the animation once the cardInfo is dismissed
        self.root.cardInfo.add_animation(move_animation, player)

        return payment


class CornerSquare(AbstractBoardSquare):

    def land_action(self, player):
        if self.name == 'GO-TO-JAIL':
            player.move_direct(self.root.squares['Jail'])
            player.in_jail_counter = 0

        return 0


class TaxSquare(AbstractBoardSquare):
    def land_action(self, player):
        if self.name == 'ITax':
            payment = 200

        elif self.name == 'LTax':
            payment = 100

        return payment
