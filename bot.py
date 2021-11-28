import json
import numpy as np
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
    return status[0]


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
    return True


def get_lang(tgid):
    cur.execute(f"SELECT lang FROM base WHERE tgid == ?", (tgid,))
    lang = cur.fetchone()
    return lang[0]


def edit_interval(tgid, interv):
    try:
        cur.execute(f"UPDATE base SET inter = ? WHERE tgid == ?", (interv, tgid))
        con.commit()
        return True
    except Exception as ex:
        print(str(ex) + '  ' + str(tgid))
        return False


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
        return True
    except Exception as ex:
        print(str(ex) + '  ' + str(tgid))
        return False


def get_all_subs():
    cur.execute(f"SELECT * FROM base WHERE status == ?", (1,))
    fetch = cur.fetchall()
    gayes = []
    if fetch is not None:
        for s in fetch:
            gayes.append(s)
        return gayes
    else:
        return False


async def podpiska():
    subs = get_all_subs()
    if subs:
        for sub in subs:
            if (int(datetime.datetime.now().timestamp()) - sub[4]) > sub[3]:
                res = find_guy(str(sub[1]))
                if len(res) == 0:
                    await bot.send_message(sub[0],
                                           f"{('Пожалуйста, проверьте в Личном Кабинете Бота, ', '<b> Wait, we are looking for your applications ... </b>')[sub[5] == 1]}"
                                           f"{('правильно ли вы ввели <b>СНИЛС</b> или <b>id поступающего</b>.', '<b> Wait, we are looking for your applications ... </b>')[sub[5] == 1]}",
                                           reply_markup=keyboard.keyboard_main,
                                           parse_mode=types.ParseMode.HTML)
                    change_status(sub[0])
                else:
                    ans = ('<b>Ваши заявки:</b>\n\n', '<b> Your applications: </b>\n\n')[sub[5] == 1]
                    with open('stolbs.json', 'r') as f:
                        stolbs = json.load(f)
                        for var in res:
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
                            with open('info.json', 'r') as fi:
                                all_info = json.load(fi)
                                gays = all_info[var['stolbs'][0]][var['stolbs'][1]][var['stolbs'][2]] \
                                    [var['stolbs'][3]][var['stolbs'][4]]
                                ind = gays[0].index('Сумма конкурсных баллов')
                                guys_list = []
                                for gay in gays:
                                    if gay[1] != sub[1]:
                                        try:
                                            guys_list.append(int(gay[8]))
                                        except:
                                            pass
                                    else:
                                        break
                            med = np.median(guys_list)
                            try:
                                med = int(med)
                            except:
                                pass
                            if sub[5] == 0:
                                ans += f'ВУЗ: <b>{vuz}</b>\n' \
                                       f'Институт: <b>{inst}</b>\n' \
                                       f'Направление: <b>{spec}</b>\n' \
                                       f'Тип обучения: <b>{tip}</b> <b>{category}</b>\n' \
                                       f'Позиция в рейтинге: <b>{pos}/{kolvo}</b>\n' \
                                       f'План приёма: <b>{plan}</b>\n' \
                                       f'Медина баллов: <b>{med}</b>\n\n'
                            else:
                                ans += f'HEI: <b>{vuz}</b>\n' \
                                       f'Istitute: <b>{inst}</b>\n' \
                                       f'Direction: <b>{spec}</b>\n' \
                                       f'Type of training: <b>{tip}</b> <b>{category}</b>\n' \
                                       f'Ranking position: <b>{pos}/{kolvo}</b>\n' \
                                       f'Admission plan: <b>{plan}</b>\n' \
                                       f'Medina points: <b>{med}</b>\n\n'
                    await bot.send_message(sub[0],
                                           ans,
                                           reply_markup=keyboard.keyboard_main,
                                           parse_mode=types.ParseMode.HTML)
    await asyncio.sleep(60)


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
                                   f"{('Проверьте правильность введённых данных и попробуйте еще раз:', 'Check the correctness of the entered data and try again:')[lang==1]}")
    else:
        await bot.send_message(message.from_user.id, f"{('Ошибка языка, обратитесь в поддержку.', 'Language error, contact support.')[lang==1]}",
                               reply_markup=keyboard.keyboard_main)


@dp.message_handler(state=States.reg)
async def reg(message: types.Message, state: FSMContext):
    answer = message.text
    if check_snils(answer):
        if add_into_base(message.from_user.id, answer, 0):
            await bot.send_message(message.from_user.id,
                                   f"{('Поздравляем с успешной регистрацией.', 'Congratulations on your successful registration.')[0]}"
                                   f"{('Теперь вы можете отслеживать свою позицию в рейтинге!', 'Now you can track your ranking position!')[0]}",
                                   reply_markup=keyboard.keyboard_main)
            await state.finish()
        else:
            await bot.send_message(message.from_user.id, f"{('Ошибка, обратитесь в поддержку.', 'Error, contact support.')[0]}")
    else:
        await bot.send_message(message.from_user.id,
                               f"{('Проверьте правильность введённых данных и попробуйте еще раз:', 'Check the correctness of the entered data and try again:')[0]}")


@dp.message_handler(state=States.change_interval)
async def interval(message: types.Message, state: FSMContext):
    answer = message.text
    lang = get_lang(message.from_user.id)
    if lang is not None:
        if message.text in ('Меню', 'Menu'):
            await bot.send_message(message.from_user.id, f"{('Меню', 'Menu')[lang==1]}", reply_markup=keyboard.keyboard_main)
            await state.finish()
        else:
            answer = message.text
            try:
                answer = int(answer)
            except:
                await bot.send_message(message.from_user.id, f"{('Введите корректный интервал.', 'Please enter the correct spacing.')[lang == 1]}")
            if 5 <= answer <= 720:
                answer = answer * 60
                if edit_interval(message.from_user.id, answer):
                    mod = get_status(message.from_user.id)
                    await bot.send_message(message.from_user.id, f"{('Интервал успешно изменён.', 'You have successfully changed spacing')[lang==1]}",
                                           reply_markup=keyboard.keyboard_subs(mod))
                    await States.sub_menu.set()
                else:
                    await bot.send_message(message.from_user.id, f"{('Ошибка, обратитесь в поддержку.', 'Error, contact support.')[lang==1]}",
                                           reply_markup=keyboard.keyboard_main)
            else:
                await bot.send_message(message.from_user.id, f"{('Введите интервал от 5 до 720 минут:', 'Enter an interval from 5 to 720 minutes:')[lang==1]}")
    else:
        await bot.send_message(message.from_user.id,
                               f"{('Проверьте правильность введённых данных и попробуйте еще раз:', 'Check the correctness of the entered data and try again:')[lang==1]}")


@dp.message_handler(state=States.sub_menu)
async def submenu(message: types.Message, state: FSMContext):
    answer = message.text
    lang = get_lang(message.from_user.id)
    if lang is not None:
        if message.text in ('Меню', 'Menu'):
            await bot.send_message(message.from_user.id, f"{('Меню', 'Menu')[lang==1]}", reply_markup=keyboard.keyboard_main)
            await state.finish()
        elif message.text == f"{('Подключить', 'Connect')[lang==1]}":
            if change_status(message.from_user.id, 1):
                modd = get_status(message.from_user.id)
                await bot.send_message(message.from_user.id, f"{('Вы успешно подписались на уведомления.', 'You have successfully subscribed')[lang==1]}",
                                       reply_markup=keyboard.keyboard_subs(modd))
                if not update_time(message.from_user.id):
                    await bot.send_message(message.from_user.id, f"{('Ошибка с подпиской, обратитесь в поддержку.', 'Error with subscribtion, contact support.')[lang==1]}",
                                           keyboard.keyboard_main)
                    await state.finish()
            else:
                await bot.send_message(message.from_user.id, f"{('Ошибка, обратитесь в поддержку.', 'Error, contact support.')[lang==1]}", keyboard.keyboard_main)
                await state.finish()
        elif message.text == 'Отключить':
            if change_status(message.from_user.id, 0):
                modd = get_status(message.from_user.id)
                await bot.send_message(message.from_user.id, 'Вы успешно отключили уведомления.',
                                       reply_markup=keyboard.keyboard_subs(modd))
            else:
                await bot.send_message(message.from_user.id, 'Ошибка, обратитесь в поддержку.', keyboard.keyboard_main)
                await state.finish()
        elif message.text == 'Сменить интервал':
            await bot.send_message(message.from_user.id, 'Введите новый интервал в минутах (от 5 до 720):',
                                   reply_markup=keyboard.keyboard_menu)
            await States.change_interval.set()
    else:
        await bot.send_message(message.from_user.id,
                               f"{('Проверьте правильность введённых данных и попробуйте еще раз:', 'Check the correctness of the entered data and try again:')[lang==1]}")


@dp.message_handler(content_types=['text'], state='*')
async def text(message: types.Message, state: FSMContext):
    if message.text == '/reboot' and message.from_user.id == config.dev_id:
        get_all_info()
    lang = get_lang(message.from_user.id)
    if lang is not None:
        if message.text in ['Меню', 'Мой рейтинг', 'Личный кабинет', 'Подписка', 'Помощь', 'Сменить СНИЛС', 'Сменить язык', 'Управление подпиской', 'Мои направления', 'Menu', 'My rating', 'My account', 'Subscription', 'Help', 'Change SNILS', 'Subscription management', 'My directions']:
            snils = get_snils(message.from_user.id)
            if snils:
                if message.text in ('Меню', 'Menu'):
                    await bot.send_message(message.from_user.id, f"{('Меню', 'Menu')[lang==1]}", reply_markup=keyboard.keyboard_main)
                    await state.finish()
                elif message.text in ('Мой рейтинг', 'My rating'):
                    await bot.send_message(message.from_user.id,
                                           f"{('<b>Ожидайте, проводится поиск ваших заявок...</b>', '<b> Wait, we are looking for your applications ... </b>')[lang==1]}",
                                           parse_mode=types.ParseMode.HTML,
                                           reply_markup=types.ReplyKeyboardRemove())
                    result = find_guy(str(snils))
                    await bot.delete_message(message.from_user.id, message.message_id + 1)
                    lang = get_lang(message.from_user.id)
                    if len(result) == 0:
                        await bot.send_message(message.from_user.id,
                                               f"{('Пожалуйста, проверьте в Личном Кабинете Бота, ', '<b> Wait, we are looking for your applications ... </b>')[lang==1]}"
                                               f"{('правильно ли вы ввели <b>СНИЛС</b> или <b>id поступающего</b>.', '<b> Wait, we are looking for your applications ... </b>')[lang==1]}",
                                               reply_markup=keyboard.keyboard_main,
                                               parse_mode=types.ParseMode.HTML)
                    else:
                        ans = ('<b>Ваши заявки:</b>\n\n', '<b> Your applications: </b>\n\n')[lang==1]
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
                                with open('info.json', 'r') as fi:
                                    all_info = json.load(fi)
                                    gays = all_info[var['stolbs'][0]][var['stolbs'][1]][var['stolbs'][2]] \
                                    [var['stolbs'][3]][var['stolbs'][4]]
                                    ind = gays[0].index('Сумма конкурсных баллов')
                                    guys_list = []
                                    for gay in gays:
                                        if gay[1] != snils:
                                            try:
                                                guys_list.append(int(gay[8]))
                                            except:
                                                pass
                                        else:
                                            break
                                mediana = np.median(guys_list)
                                try:
                                    mediana = int(mediana)
                                except:
                                    pass
                                if lang == 0:
                                    ans += f'ВУЗ: <b>{vuz}</b>\n' \
                                           f'Институт: <b>{inst}</b>\n' \
                                           f'Направление: <b>{spec}</b>\n' \
                                           f'Тип обучения: <b>{tip}</b> <b>{category}</b>\n' \
                                           f'Позиция в рейтинге: <b>{pos}/{kolvo}</b>\n' \
                                           f'План приёма: <b>{plan}</b>\n' \
                                           f'Медина баллов: <b>{mediana}</b>\n\n'
                                else:
                                    ans += f'HEI: <b>{vuz}</b>\n' \
                                           f'Istitute: <b>{inst}</b>\n' \
                                           f'Direction: <b>{spec}</b>\n' \
                                           f'Type of training: <b>{tip}</b> <b>{category}</b>\n' \
                                           f'Ranking position: <b>{pos}/{kolvo}</b>\n' \
                                           f'Admission plan: <b>{plan}</b>\n' \
                                           f'Medina points: <b>{mediana}</b>\n\n'
                        await bot.send_message(message.from_user.id,
                                               ans,
                                               reply_markup=keyboard.keyboard_main,
                                               parse_mode=types.ParseMode.HTML)
                elif message.text in ('Личный кабинет', 'My account'):
                    lang = get_lang(message.from_user.id)
                    status = get_status(message.from_user.id)
                    if status is not None:
                        if status == 1:
                            interval = get_interval(message.from_user.id)
                            if interval is not None:
                                if lang == 0:
                                    await bot.send_message(message.from_user.id,
                                                           f'Ваш СНИЛС/id: <b>{snils}</b>\n'
                                                           f'Статус подписки: <b>Активен</b>\n'
                                                           f'Интервал уведомлений: {interval//60}',
                                                           reply_markup=keyboard.keyboard_lk,
                                                           parse_mode=types.ParseMode.HTML)
                                else:
                                    await bot.send_message(message.from_user.id,
                                                           f'Your SNILS/id: <b>{snils}</b>\n'
                                                           f'Subscription status: <b>Active</b>\n'
                                                           f'Notification interval: {interval//60}',
                                                           reply_markup=keyboard.keyboard_lk,
                                                           parse_mode=types.ParseMode.HTML)
                            else:
                                await bot.send_message(message.from_user.id, 'Ошибка интервала, обратитесь в поддержку',
                                                       reply_markup=keyboard.keyboard_main)
                        elif status == 0:
                            interval = get_interval(message.from_user.id)
                            if interval is not None:
                                if lang == 0:
                                    await bot.send_message(message.from_user.id,
                                                           f'Ваш СНИЛС/id: <b>{snils}</b>\n'
                                                           f'Статус подписки: <b>Неактивен</b>',
                                                           reply_markup=keyboard.keyboard_lk,
                                                           parse_mode=types.ParseMode.HTML)
                                else:
                                    await bot.send_message(message.from_user.id,
                                                           f'Your SNILS/id: <b>{snils}</b>\n'
                                                           f'Subscription status: <b>Inactive</b>',
                                                           reply_markup=keyboard.keyboard_lk,
                                                           parse_mode=types.ParseMode.HTML)
                            else:
                                await bot.send_message(message.from_user.id, 'Ошибка интервала, обратитесь в поддержку',
                                                       reply_markup=keyboard.keyboard_main)
                    else:
                        await bot.send_message(message.from_user.id, f"{('Ошибка, обратитесь в поддержку.', 'Error, contact support.')[lang==1]}")
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
                elif message.text == 'Сменить язык':
                    lng = get_lang(message.from_user.id)
                    print(lng)
                    if lng == 0:
                        if edit_lang(message.from_user.id, 1):
                            await bot.send_message(message.from_user.id, 'Language was changed successfully',
                                                   reply_markup=keyboard.keyboard_lk)
                        else:
                            await bot.send_message(message.from_user.id, 'Ошибка смены языка, обратитесь в поддержку',
                                                   reply_markup=keyboard.keyboard_lk)
                    else:
                        if edit_lang(message.from_user.id, 0):
                            await bot.send_message(message.from_user.id, 'Язык успешно изменён.',
                                                   reply_markup=keyboard.keyboard_lk)
                        else:
                            await bot.send_message(message.from_user.id, 'Language changing was failed.',
                                                   reply_markup=keyboard.keyboard_lk)
            else:
                await bot.send_message(message.from_user.id,
                                       f"{('Ошибка, возможно вы не зарегистрировались. Для регистрации нажмите /start', 'Error, you may not have registered. To register, press / start')[lang==1]}")
    else:
        await bot.send_message(message.from_user.id,
                               f"{('Проверьте правильность введённых данных и попробуйте еще раз:', 'Check the correctness of the entered data and try again:')[lang==1]}")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(podpiska())
    executor.start_polling(dp, skip_updates=True)
