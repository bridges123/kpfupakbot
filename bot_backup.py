import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
import datetime
import sqlite3 as sql
from parse import get_info, get_all_info, find_guy
import keyboard
import config


storage = MemoryStorage()
bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=storage)


con = sql.connect('base.db')
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS base (
            tgid INTEGER,
            snils STRING,
            status INTEGER,
            inter INTEGER,
            lastcheck INTEGER,
            lang INTEGER
            )""")
con.commit()
# 1-ru 2-en


class States(StatesGroup):
    reg = State()
    change_snils = State()
    sub_menu = State()
    change_interval = State()

# personality = ("Меню", "Menu")[lang==1]
# print("Кошка ", personality)
# # Вывод: Кошка добрая
def check_snils(answer):
    slices = answer.split('-')
    if len(slices) == 1:
        if 5 <= len(answer) <= 7:
            return True
        else:
            return False
    elif len(slices) == 4:
        if len(slices[0]) == 3 and len(slices[1]) == 3 and len(slices[2]) == 3 and len(slices[3]) == 2:
            for s in slices[0]:
                if not('0' <= s <= '9'):
                    return False
            for s in slices[1]:
                if not('0' <= s <= '9'):
                    return False
            for s in slices[2]:
                if not('0' <= s <= '9'):
                    return False
            for s in slices[3]:
                if not('0' <= s <= '9'):
                    return False
            return True
        else:
            return False


def get_snils(tgid):
    cur.execute("SELECT snils FROM base WHERE tgid == ?", (tgid,))
    snils = cur.fetchone()
    if snils is not None:
        return snils[0]
    else:
        return False


def get_status(tgid):
    cur.execute(f"SELECT status FROM base WHERE tgid == ?", (tgid,))
    status = cur.fetchone()
    if status is not None:
        return status[0]
    else:
        return False


def get_interval(tgid):
    cur.execute(f"SELECT inter FROM base WHERE tgid == ?", (tgid,))
    interval = cur.fetchone()
    if interval is not None:
        return interval[0]
    else:
        return False


def change_status(tgid, new_stat):
    try:
        cur.execute(f"UPDATE base SET status = ? WHERE tgid == ?", (new_stat, tgid))
        con.commit()
        return True
    except Exception as ex:
        print(ex + '  ' + str(tgid))
        return False


def get_speces()


def edit_snils(tgid, snils):
    try:
        cur.execute(f"UPDATE base SET snils = ? WHERE tgid == ?", (snils, tgid))
        con.commit()
    except Exception as ex:
        print(ex + '  ' + str(tgid))
        return False


def edit_lang(tgid, lang):
    cur.execute(f"UPDATE base SET lang = ? WHERE tgid == ?", (lang, tgid))
    con.commit()


def get_lang(tgid):
    cur.execute(f"SELECT lang FROM base WHERE tgid == ?", (tgid,))
    lang = cur.fetchone()
    return lang


def update_time(tgid):
    try:
        cur.execute(f"UPDATE base SET lastcheck = ? WHERE tgid == ?", (int(datetime.datetime.now().timestamp()), tgid))
        con.commit()
        return True
    except Exception as ex:
        print(ex + '  ' + str(tgid))
        return False


def add_into_base(tgid, snils, lang):
    try:
        cur.execute(f"INSERT INTO base VALUES (?, ?, ?, ?, ?, ?)", (tgid, snils, 0, 60, 0, lang))
        con.commit()
    except Exception as ex:
        print(ex + '  ' + str(tgid))
        return False


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    if get_snils(message.from_user.id):
        await bot.send_message(message.from_user.id, config.privetstvie, reply_markup=keyboard.keyboard_main)
    else:
        await bot.send_message(message.from_user.id, config.registration,
                               reply_markup=types.ReplyKeyboardRemove(),
                               parse_mode=types.ParseMode.HTML)
        await States.reg.set()


@dp.message_handler(state=States.change_snils)
async def change_sns(message: types.Message, state: FSMContext):
    answer = message.text
    lang = get_lang(message.from_user.id)
    if lang is not None:
        if message.text in ('Меню', 'Menu'):
            await bot.send_message(message.from_user.id, f"{('Меню', 'Menu')[lang==1]}", reply_markup=keyboard.keyboard_main)
            await state.finish()
        elif check_snils(answer):
            edit_snils(message.from_user.id, answer)
            await bot.send_message(message.from_user.id,
                                   f"{('Вы успешно сменили СНИЛС', 'You have successfully changed SNILS')[lang==1]}",
                                   reply_markup=keyboard.keyboard_main)
            await state.finish()
        else:
            await bot.send_message(message.from_user.id,
                                   f"{('Проверьте правильность введённых данных и попробуйте еще раз:', 'You have successfully changed SNILS')[lang==1]}")
    else:
        await bot.send_message(message.from_user.id, f"{('Ошибка языка, обратитесь в поддержку.', 'You have successfully changed SNILS')[lang==1]}",
                               reply_markup=keyboard.keyboard_main)


@dp.message_handler(state=States.reg)
async def reg(message: types.Message, state: FSMContext):
    answer = message.text
    if check_snils(answer):
        if add_into_base(message.from_user.id, answer):
            await bot.send_message(message.from_user.id,
                                   'Поздравляем с успешной регистрацией. '
                                   'Теперь вы можете отслеживать свою позицию в рейтинге!',
                                   reply_markup=keyboard.keyboard_main)
        else:
            await bot.send_message(message.from_user.id, 'Ошибка, обратитесь в поддержку')
        await state.finish()
    else:
        await bot.send_message(message.from_user.id,
                               'Проверьте правильность введённых данных и попробуйте еще раз:')


@dp.message_handler(state=States.change_interval)
async def interval(message: types.Message, state: FSMContext):
    if message.text == 'Меню':
        await bot.send_message(message.from_user.id, 'Меню:', reply_markup=keyboard.keyboard_main)
        await state.finish()
    else:
        answer = message.text
        try:
            answer = int(answer)
        except:
            await bot.send_message(message.from_user.id, 'Введите корректный интервал.')
        if 5 <= answer <= 720:
            answer = answer * 60
            if edit_interval(message.from_user.id, answer):
                mod = get_status(message.from_user.id)
                await bot.send_message(message.from_user.id, 'Интервал успешно изменён.',
                                       reply_markup=keyboard.keyboard_subs(mod))
                await States.sub_menu.set()
            else:
                await bot.send_message(message.from_user.id, 'Ошибка, обратитесь в поддержку.',
                                       reply_markup=keyboard.keyboard_main)
        else:
            await bot.send_message(message.from_user.id, 'Введите интервал от 5 до 720 минут:')


@dp.message_handler(state=States.sub_menu)
async def submenu(message: types.Message, state: FSMContext):
    if message.text == 'Меню':
        await bot.send_message(message.from_user.id, 'Меню:', reply_markup=keyboard.keyboard_main)
        await state.finish()
    elif message.text == 'Подключить':
        if change_status(message.from_user.id, 1):
            modd = get_status(message.from_user.id)
            await bot.send_message(message.from_user.id, 'Вы успешно подписались на уведомления.',
                                   reply_markup=keyboard.keyboard_subs(modd))
            if not update_time(message.from_user.id):
                await bot.send_message(message.from_user.id, 'Ошибка с подпиской, обратитесь в поддержку.',
                                       keyboard.keyboard_main)
        else:
            await bot.send_message(message.from_user.id, 'Ошибка, обратитесь в поддержку.', keyboard.keyboard_main)
        await state.finish()
    elif message.text == 'Отключить':
        if change_status(message.from_user.id, 0):
            modd = get_status(message.from_user.id)
            await bot.send_message(message.from_user.id, 'Вы успешно отключили уведомления.',
                                   reply_markup=keyboard.keyboard_subs(modd))
            await state.finish()
    elif message.text == 'Сменить интервал':
        await bot.send_message('Введите новый интервал в минутах (от 5 до 720):', reply_markup=keyboard.keyboard_menu)
        await States.change_interval.set()


@dp.message_handler(content_types=['text'], state='*')
async def text(message: types.Message, state: FSMContext):
    if message.text == '/reboot' and message.from_user.id == config.dev_id:
        get_all_info()
    if message.text in ['Меню', 'Мой рейтинг', 'Личный кабинет', 'Подписка', 'Помощь', 'Сменить СНИЛС', 'Управление подпиской']:
        snils = get_snils(message.from_user.id)
        if snils:
            if message.text == 'Меню':
                await bot.send_message(message.from_user.id, 'Меню:', reply_markup=keyboard.keyboard_main)
                await state.finish()
            elif message.text == 'Мой рейтинг':
                await bot.send_message(message.from_user.id,
                                       '<b>Ожидайте, проводится поиск ваших заявок...</b>',
                                       parse_mode=types.ParseMode.HTML,
                                       reply_markup=types.ReplyKeyboardRemove())
                result = find_guy(str(snils))
                await bot.delete_message(message.from_user.id, message.message_id + 1)
                if len(result) == 0:
                    await bot.send_message(message.from_user.id,
                                           'Пожалуйста, проверьте в Личном Кабинете Бота, '
                                           'правильно ли вы ввели <b>СНИЛС</b> или <b>id поступающего</b>.',
                                           reply_markup=keyboard.keyboard_main,
                                           parse_mode=types.ParseMode.HTML)
                else:
                    ans = "<b>Ваши заявки:</b>\n\n"
                    with open('stolbs.json', 'r') as f:
                        stolbs = json.load(f)
                        for var in result:
                            for vz in stolbs['vuzes']:
                                if vz[0] == var['stolbs'][0]:
                                    vuz = vz[1]
                            for ins in stolbs['institutes']:
                                if ins[0] == var['stolbs'][1]:
                                    inst = ins[1]
                            for sp in stolbs['specialities']:
                                if sp[0] == var['stolbs'][2]:
                                    spec = sp[1]
                            for tp in stolbs['typeofstudies']:
                                if tp[0] == var['stolbs'][3]:
                                    tip = tp[1]
                            for cat in stolbs['categories']:
                                if cat[0] == var['stolbs'][4]:
                                    category = cat[1]
                            pos = var['info'][0]
                            plan = var['other'][0]
                            kolvo = var['other'][1]
                            ans += f'ВУЗ: <b>{vuz}</b>\n' \
                                   f'Институт: <b>{inst}</b>\n' \
                                   f'Направление: <b>{spec}</b>\n' \
                                   f'Тип обучения: <b>{tip}</b> <b>{category}</b>\n' \
                                   f'Позиция в рейтинге: <b>{pos}/{kolvo}</b>\n' \
                                   f'План приёма: <b>{plan}</b>\n\n'
                    await bot.send_message(message.from_user.id,
                                           ans,
                                           reply_markup=keyboard.keyboard_main,
                                           parse_mode=types.ParseMode.HTML)
            elif message.text == 'Личный кабинет':
                status = get_status(message.from_user.id)
                if status is not None:
                    if status == 1:
                        interval = get_interval(message.from_user.id)
                        await bot.send_message(message.from_user.id,
                                               f'Ваш СНИЛС/id: <b>{snils}</b>\n'
                                               f'Статус подписки: <b>Активен</b>\n'
                                               f'Интервал уведомлений: {interval}',
                                               reply_markup=keyboard.keyboard_lk,
                                               parse_mode=types.ParseMode.HTML)
                    elif status == 0:
                        await bot.send_message(message.from_user.id,
                                               f'Ваш СНИЛС/id: <b>{snils}</b>\n'
                                               f'Статус подписки: <b>Неактивен</b>',
                                               reply_markup=keyboard.keyboard_lk,
                                               parse_mode=types.ParseMode.HTML)
                else:
                    await bot.send_message(message.from_user.id, 'Ошибка. Попробуйте обратиться в поддержку.')
            elif message.text == 'Сменить СНИЛС':
                await bot.send_message(message.from_user.id,
                                       'Ввведите новый СНИЛС/id:',
                                       reply_markup=keyboard.keyboard_menu)
                await States.change_snils.set()
            elif message.text == 'Управление подпиской':
                mod = get_status(message.from_user.id)
                if mod is not None:
                    await bot.send_message(message.from_user.id,
                                           'Здесь вы можете включить подписку на уведомления '
                                           'об изменении вашей позиции в рейтинге.',
                                           reply_markup=keyboard.keyboard_subs(mod))
                    await States.sub_menu.set()
                else:
                    await bot.send_message(message.from_user.id,
                                           'Ошибка, обратитесь в поддержку.',
                                           reply_markup=keyboard.keyboard_main)
            elif message.text == 'Мои направления':
                speces = get_speces(message.from_user.id)
                await bot.send_message(message.from_user.id,
                                       f'Ваши направления:\n\n{speces}',
                                       reply_markup=keyboard.keyboard_spec)
        else:
            await bot.send_message(message.from_user.id,
                                   'Ошибка, возможно вы не зарегистрировались. Для регистрации нажмите /start')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
