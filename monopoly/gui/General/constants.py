PROPERTY_INTERVAL = 0.082
CORNER_TO_PROPERTY_INTERVAL = 0.105
CORNER_OFFSET = 0.06
BORDER_OFFSET = 0.015

BOARD_SQUARE_LOCATIONS = {

    'GO': (CORNER_OFFSET, CORNER_OFFSET),

    'Br1': (CORNER_OFFSET, CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL),
    'Chest1': (CORNER_OFFSET, CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + PROPERTY_INTERVAL),
    'Br2': (CORNER_OFFSET, CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 2 * PROPERTY_INTERVAL),
    'ITax': (CORNER_OFFSET, CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 3 * PROPERTY_INTERVAL),
    'RR1': (CORNER_OFFSET, CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 4 * PROPERTY_INTERVAL),
    'Lb1': (CORNER_OFFSET, CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 5 * PROPERTY_INTERVAL),
    'Chance1': (CORNER_OFFSET, CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 6 * PROPERTY_INTERVAL),
    'Lb2': (CORNER_OFFSET, CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 7 * PROPERTY_INTERVAL),
    'Lb3': (CORNER_OFFSET, CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 8 * PROPERTY_INTERVAL),

    'Jail': (CORNER_OFFSET, 1 - (CORNER_OFFSET + BORDER_OFFSET)),

    'Pk1': (CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL, 1 - (CORNER_OFFSET + BORDER_OFFSET)),
    'Util1': (CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + PROPERTY_INTERVAL, 1 - (CORNER_OFFSET + BORDER_OFFSET)),
    'Pk2': (CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 2 * PROPERTY_INTERVAL, 1 - (CORNER_OFFSET + BORDER_OFFSET)),
    'Pk3': (CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 3 * PROPERTY_INTERVAL, 1 - (CORNER_OFFSET + BORDER_OFFSET)),
    'RR2': (CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 4 * PROPERTY_INTERVAL, 1 - (CORNER_OFFSET + BORDER_OFFSET)),
    'Or1': (CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 5 * PROPERTY_INTERVAL, 1 - (CORNER_OFFSET + BORDER_OFFSET)),
    'Chest2': (
        CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 6 * PROPERTY_INTERVAL, 1 - (CORNER_OFFSET + BORDER_OFFSET)),
    'Or2': (CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 7 * PROPERTY_INTERVAL, 1 - (CORNER_OFFSET + BORDER_OFFSET)),
    'Or3': (CORNER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 8 * PROPERTY_INTERVAL, 1 - (CORNER_OFFSET + BORDER_OFFSET)),

    'Parking': (1 - (CORNER_OFFSET + BORDER_OFFSET), 1 - (CORNER_OFFSET + BORDER_OFFSET)),

    'Rd1': (1 - (CORNER_OFFSET + BORDER_OFFSET), 1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL)),
    'Chance2': (1 - (CORNER_OFFSET + BORDER_OFFSET),
                1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + PROPERTY_INTERVAL)),
    'Rd2': (1 - (CORNER_OFFSET + BORDER_OFFSET),
            1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 2 * PROPERTY_INTERVAL)),
    'Rd3': (1 - (CORNER_OFFSET + BORDER_OFFSET),
            1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 3 * PROPERTY_INTERVAL)),
    'RR3': (1 - (CORNER_OFFSET + BORDER_OFFSET),
            1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 4 * PROPERTY_INTERVAL)),
    'Yl1': (1 - (CORNER_OFFSET + BORDER_OFFSET),
            1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 5 * PROPERTY_INTERVAL)),
    'Yl2': (1 - (CORNER_OFFSET + BORDER_OFFSET),
            1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 6 * PROPERTY_INTERVAL)),
    'Util2': (1 - (CORNER_OFFSET + BORDER_OFFSET),
              1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 7 * PROPERTY_INTERVAL)),
    'Yl3': (1 - (CORNER_OFFSET + BORDER_OFFSET),
            1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 8 * PROPERTY_INTERVAL)),

    'GO-TO-JAIL': (1 - (CORNER_OFFSET + BORDER_OFFSET), CORNER_OFFSET),

    'Gn1': (1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL), CORNER_OFFSET),
    'Gn2': (1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + PROPERTY_INTERVAL), CORNER_OFFSET),
    'Chest3': (
        1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 2 * PROPERTY_INTERVAL), CORNER_OFFSET),
    'Gn3': (1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 3 * PROPERTY_INTERVAL), CORNER_OFFSET),
    'RR4': (1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 4 * PROPERTY_INTERVAL), CORNER_OFFSET),
    'Chance3': (
        1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 5 * PROPERTY_INTERVAL), CORNER_OFFSET),
    'Bl1': (1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 6 * PROPERTY_INTERVAL), CORNER_OFFSET),
    'LTax': (1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 7 * PROPERTY_INTERVAL), CORNER_OFFSET),
    'Bl2': (1 - (CORNER_OFFSET + BORDER_OFFSET + CORNER_TO_PROPERTY_INTERVAL + 8 * PROPERTY_INTERVAL), CORNER_OFFSET),
}

BOARD_SQUARE_ATTRIBUTES = {

    'GO': {'full_name': 'GO', 'cost_value': None, 'mortgage_value': None, 'unmortgage_value': None},

    'Br1': {'full_name': 'MEDITERRANEAN AVENUE', 'cost_value': 60, 'mortgage_value': 30, 'unmortgage_value': 33},
    'Chest1': {'full_name': 'COMMUNITY CHEST', 'cost_value': None, 'mortgage_value': None, 'unmortgage_value': None},
    'Br2': {'full_name': 'BATIC AVENUE', 'cost_value': 60, 'mortgage_value': 30, 'unmortgage_value': 33},
    'ITax': {'full_name': 'INCOME TAX', 'cost_value': 200, 'mortgage_value': None, 'unmortgage_value': None},
    'RR1': {'full_name': 'READING RAILROAD', 'cost_value': 200, 'mortgage_value': 100, 'unmortgage_value': 110},
    'Lb1': {'full_name': 'ORIENTAL AVENUE', 'cost_value': 100, 'mortgage_value': 50, 'unmortgage_value': 55},
    'Chance1': {'full_name': 'CHANCE', 'cost_value': None, 'mortgage_value': None, 'unmortgage_value': None},
    'Lb2': {'full_name': 'VERMONT AVENUE', 'cost_value': 100, 'mortgage_value': 50, 'unmortgage_value': 55},
    'Lb3': {'full_name': 'CONNECTICUT AVENUE', 'cost_value': 120, 'mortgage_value': 60, 'unmortgage_value': 66},

    'Jail': {'full_name': 'JAIL', 'cost_value': None, 'mortgage_value': None, 'unmortgage_value': None},

    'Pk1': {'full_name': 'ST. CHARLES PLACE', 'cost_value': 140, 'mortgage_value': 70, 'unmortgage_value': 77},
    'Util1': {'full_name': 'ELECTRIC COMPANY', 'cost_value': 150, 'mortgage_value': None, 'unmortgage_value': None},
    'Pk2': {'full_name': 'STATES AVENUE', 'cost_value': 140, 'mortgage_value': 70, 'unmortgage_value': 77},
    'Pk3': {'full_name': 'VIRGINIA AVENUE', 'cost_value': 160, 'mortgage_value': 80, 'unmortgage_value': 88},
    'RR2': {'full_name': 'PENNSYLVANIA RAILROAD', 'cost_value': 200, 'mortgage_value': 100, 'unmortgage_value': 110},
    'Or1': {'full_name': 'ST. JAMES PLACE', 'cost_value': 180, 'mortgage_value': 90, 'unmortgage_value': 99},
    'Chest2': {'full_name': 'COMMUNITY CHEST', 'cost_value': None, 'mortgage_value': None, 'unmortgage_value': None},
    'Or2': {'full_name': 'TENNESSEE AVENUE', 'cost_value': 180, 'mortgage_value': 90, 'unmortgage_value': 99},
    'Or3': {'full_name': 'NEW YORK AVENUE', 'cost_value': 200, 'mortgage_value': 100, 'unmortgage_value': 110},

    'Parking': {'full_name': 'FREE PARKING', 'cost_value': None, 'mortgage_value': None, 'unmortgage_value': None},

    'Rd1': {'full_name': 'KENTUCKY AVENUE', 'cost_value': 220, 'mortgage_value': 110, 'unmortgage_value': 121},
    'Chance2': {'full_name': 'CHANCE', 'cost_value': None, 'mortgage_value': None, 'unmortgage_value': None},
    'Rd2': {'full_name': 'INDIANA AVENUE', 'cost_value': 220, 'mortgage_value': 110, 'unmortgage_value': 121},
    'Rd3': {'full_name': 'ILLINOIS AVENUE', 'cost_value': 240, 'mortgage_value': 120, 'unmortgage_value': 132},
    'RR3': {'full_name': 'B. & O. RAILROAD', 'cost_value': 200, 'mortgage_value': 100, 'unmortgage_value': 110},
    'Yl1': {'full_name': 'ATLANTIC AVENUE', 'cost_value': 260, 'mortgage_value': 130, 'unmortgage_value': 143},
    'Yl2': {'full_name': 'VENTNOR AVENUE', 'cost_value': 260, 'mortgage_value': 130, 'unmortgage_value': 143},
    'Util2': {'full_name': 'WATER WORKS', 'cost_value': 150, 'mortgage_value': 75, 'unmortgage_value': 83},
    'Yl3': {'full_name': 'MARVIN GARDENS', 'cost_value': 280, 'mortgage_value': 140, 'unmortgage_value': 154},

    'GO-TO-JAIL': {'full_name': 'GO TO JAIL', 'cost_value': None, 'mortgage_value': None, 'unmortgage_value': None},

    'Gn1': {'full_name': 'PACIFIC AVENUE', 'cost_value': 300, 'mortgage_value': 150, 'unmortgage_value': 165},
    'Gn2': {'full_name': 'NORTH CAROLINA AVENUE', 'cost_value': 300, 'mortgage_value': 150, 'unmortgage_value': 165},
    'Chest3': {'full_name': 'COMMUNITY CHEST', 'cost_value': None, 'mortgage_value': None, 'unmortgage_value': None},
    'Gn3': {'full_name': 'PENNSYLVANIA AVENUE', 'cost_value': 320, 'mortgage_value': 160, 'unmortgage_value': 176},
    'RR4': {'full_name': 'SHORT LINE', 'cost_value': 200, 'mortgage_value': 100, 'unmortgage_value': 110},
    'Chance3': {'full_name': 'CHANCE', 'cost_value': None, 'mortgage_value': None, 'unmortgage_value': None},
    'Bl1': {'full_name': 'PARK PLACE', 'cost_value': 350, 'mortgage_value': 175, 'unmortgage_value': 193},
    'LTax': {'full_name': 'LUXURY TAX', 'cost_value': 100, 'mortgage_value': None, 'unmortgage_value': None},
    'Bl2': {'full_name': 'BOARDWALK', 'cost_value': 400, 'mortgage_value': 200, 'unmortgage_value': 22},
}

BOARD_SQUARE_RENT = {
    'Br1': {'rent': 2, 'rent_set': 4, 'rent_house_1': 10, 'rent_house_2': 30, 'rent_house_3': 90, 'rent_house_4': 160,
            'rent_hotel_1': 250},
    'Br2': {'rent': 4, 'rent_set': 8, 'rent_house_1': 20, 'rent_house_2': 60, 'rent_house_3': 180, 'rent_house_4': 320,
            'rent_hotel_1': 450},
    'RR': {'rent': 25, 'rent_2': 50, 'rent_3': 100, 'rent_4': 200},
    'Lb12': {'rent': 6, 'rent_set': 12, 'rent_house_1': 30, 'rent_house_2': 90, 'rent_house_3': 270,
             'rent_house_4': 400, 'rent_hotel_1': 550},
    'Lb3': {'rent': 8, 'rent_set': 16, 'rent_house_1': 40, 'rent_house_2': 100, 'rent_house_3': 300,
            'rent_house_4': 450, 'rent_hotel_1': 600},

    'Pk12': {'rent': 10, 'rent_set': 20, 'rent_house_1': 50, 'rent_house_2': 150, 'rent_house_3': 450,
             'rent_house_4': 625, 'rent_hotel_1': 750},
    'Util': {},
    'Pk3': {'rent': 12, 'rent_set': 24, 'rent_house_1': 60, 'rent_house_2': 180, 'rent_house_3': 500,
            'rent_house_4': 700, 'rent_hotel_1': 900},

    'Or12': {'rent': 14, 'rent_set': 28, 'rent_house_1': 70, 'rent_house_2': 200, 'rent_house_3': 550,
             'rent_house_4': 750, 'rent_hotel_1': 950},
    'Or3': {'rent': 16, 'rent_set': 32, 'rent_house_1': 80, 'rent_house_2': 220, 'rent_house_3': 600,
            'rent_house_4': 800, 'rent_hotel_1': 1000},

    'Rd12': {'rent': 18, 'rent_set': 36, 'rent_house_1': 90, 'rent_house_2': 250, 'rent_house_3': 700,
             'rent_house_4': 875, 'rent_hotel_1': 1050},
    'Rd3': {'rent': 20, 'rent_set': 40, 'rent_house_1': 100, 'rent_house_2': 300, 'rent_house_3': 750,
            'rent_house_4': 925, 'rent_hotel_1': 1100},

    'Yl12': {'rent': 22, 'rent_set': 44, 'rent_house_1': 110, 'rent_house_2': 330, 'rent_house_3': 800,
             'rent_house_4': 975, 'rent_hotel_1': 1150},
    'Yl3': {'rent': 24, 'rent_set': 48, 'rent_house_1': 120, 'rent_house_2': 360, 'rent_house_3': 850,
            'rent_house_4': 1025, 'rent_hotel_1': 1200},

    'Gn12': {'rent': 26, 'rent_set': 52, 'rent_house_1': 130, 'rent_house_2': 390, 'rent_house_3': 900,
             'rent_house_4': 1100, 'rent_hotel_1': 1275},
    'Gn3': {'rent': 28, 'rent_set': 56, 'rent_house_1': 150, 'rent_house_2': 450, 'rent_house_3': 1000,
            'rent_house_4': 1200, 'rent_hotel_1': 1400},

    'Bl1': {'rent': 35, 'rent_set': 70, 'rent_house_1': 175, 'rent_house_2': 500, 'rent_house_3': 1100,
            'rent_house_4': 1300, 'rent_hotel_1': 1500},
    'Bl2': {'rent': 50, 'rent_set': 100, 'rent_house_1': 200, 'rent_house_2': 600, 'rent_house_3': 1400,
            'rent_house_4': 1700, 'rent_hotel_1': 2000},

}
