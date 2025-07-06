from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, keyboard_button, \
    KeyboardButton, KeyboardButtonPollType


location_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                        keyboard=[[KeyboardButton(text = "Share location",
                                                request_location=True)],
                                                  [KeyboardButton(text="Manual input")]
                                                  ])

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True, # inline_keyboard="select a menu item",
                                    keyboard= [ [KeyboardButton(text = 'Forecast'),
                                                    KeyboardButton(text = 'AI tips')],
                                                [KeyboardButton(text = 'Customize location'),
                                                    KeyboardButton(text = 'Customize schedule')],
                                                [KeyboardButton(text = 'Delete info')],])


#AI keyboard that appears when you try to on/off tips from AI
ai_tips_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                              keyboard=[[KeyboardButton(text = 'Get a tip')],
                                        [KeyboardButton(text = 'Automatic tips on / off')],
                                        [KeyboardButton(text = 'Back')]
                                        ])

location_keyboard_2 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                        keyboard=[[KeyboardButton(text = "Share location",request_location=True)],
                                                  [KeyboardButton(text="Manual input")],
                                                  [KeyboardButton(text = "Back")]
                                                  ])

#this keyboard is used in setting up a schedule
schedule_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                               keyboard=[[KeyboardButton(text = 'Current schedule'), KeyboardButton(text = 'Change or set schedule')],
                                         [KeyboardButton(text = 'Delete schedule')],
                                         [KeyboardButton(text = 'Back')]
                                         ])

def generate_hour_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = str(h), callback_data=f"hour_{h}") for h in range(row, row+6)]
        for row in range(0, 24, 6)
    ])
    return keyboard

def generate_minute_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(m), callback_data=f"minute_{m}") for m in range(row, row + 20, 5)]
        for row in range(0, 60, 20)
    ])
    return keyboard

def generate_location_keyboard(locations):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{loc['name']}, {loc['region']}", callback_data=f"location_{i}")]
        for i, loc in enumerate(locations)
    ])
    return keyboard