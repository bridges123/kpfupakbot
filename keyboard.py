import json
import requests
from aiogram import types


keyboard_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_position = types.KeyboardButton('Мой рейтинг')
button_lk = types.KeyboardButton('Личный кабинет')
button_help = types.KeyboardButton('Помощь')
keyboard_main.add(button_position)
keyboard_main.add(button_help, button_lk)


# keyboard_main_eng = types.ReplyKeyboardMarkup(resize_keyboard=True)
# button_position_eng = types.KeyboardButton('My rating')
# button_lk_eng = types.KeyboardButton('Profile')
# button_help_eng = types.KeyboardButton('Help')
# keyboard_main_eng.add(button_position)
# keyboard_main_eng.add(button_help, button_lk)


keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_menu = types.KeyboardButton('Меню')
keyboard_menu.add(button_menu)


keyboard_lk = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_change_snils = types.KeyboardButton('Сменить СНИЛС')
button_subscribtion_manage = types.KeyboardButton('Управление подпиской')
button_change_lang = types.KeyboardButton('Сменить язык')
keyboard_lk.add(button_change_snils, button_subscribtion_manage)
keyboard_lk.add(button_change_lang, button_menu)


keyboard_spec = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_add = types.KeyboardButton('Добавить')
button_remove = types.KeyboardButton('Удалить')
keyboard_spec.add(button_add, button_remove)
keyboard_spec.add(button_menu)


def keyboard_subs(mode):
    keyboard_subscribe = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if mode == 1:
        button_sub_mode = types.KeyboardButton('Отключить')
    else:
        button_sub_mode = types.KeyboardButton('Подключить')
    button_interval = types.KeyboardButton('Сменить интервал')
    keyboard_subscribe.add(button_sub_mode, button_interval)
    keyboard_subscribe.add(button_menu)
    return keyboard_subscribe
