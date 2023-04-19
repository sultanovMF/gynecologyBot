# import telebot
# from telebot import types
# from telebot.handler_backends import State, StatesGroup
# from telebot.storage import StateMemoryStorage
#
# from main import UserStates
#
#
# def start(bot, message):
#     bot.send_message(message.chat.id, text='Вторая шкала')
#     bot.set_state(message.from_user.id, UserStates.body_mass_index, message.chat.id)


import telebot
from telebot import types
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

# from main import UserStates


def start(bot, message):
    print("Hello")
    # bot.send_message(message.chat.id, text='Первая шкала')
    # bot.set_state(message.from_user.id, UserStates.body_mass_index, message.chat.id)
