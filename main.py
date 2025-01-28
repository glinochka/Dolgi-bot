import telebot

from telebot import types

from db import *

from decouple import config

from random import shuffle

import os

token = config('token', default='(')

bot = telebot.TeleBot(token)

s_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton('/new_dolg')
btn2 = types.KeyboardButton('/pay_dolg')
s_markup.add(btn1, btn2)


def count_dolg():

    table = count()
    table.sort()
    title = table[0][0]
    s = f'Сумма долгов.\n{title}:\n'
    for i in table:
        if title != i[0]:
            title = i[0]
            s += f'{title}:\n'
        s += f'\t{i[1]}у - {i[2]} руб.\n'
    return s



@bot.message_handler(commands=['registr'])
def name_reg(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('/exit')
    markup.add(btn1)
    bot.send_message(message.chat.id, "Введите имя:", reply_markup=markup)
    bot.register_next_step_handler(message, pass_reg)


def pass_reg(message):
    if message.text == '/exit':
        bot.send_message(message.chat.id, 'ой', reply_markup=s_markup)
        return
    user_login = message.text
    bot.set_state(message.from_user.id, user_login)

    if user_login in users():
        bot.send_message(message.chat.id,
                         "Такой пользователь уже существует\nвведите любой текст для повторной попытки")
        bot.register_next_step_handler(message, name_reg)
    else:
        bot.send_message(message.chat.id, 'Введите пароль:')
        bot.register_next_step_handler(message, reg_to_db)


def reg_to_db(message):

    if message.text == '/exit':
        bot.send_message(message.chat.id, 'ой', reply_markup=s_markup)
        return
    user_login = bot.get_state(message.from_user.id)
    user_to_db(user_login, hash_password(message.text), message.chat.id)
    bot.delete_message(message.chat.id, message.id)

    bot.send_message(message.chat.id, f'Вы успешно зарегистрированы!',
                     reply_markup=s_markup)



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "зарегистрируйтесь (/registr).",
                     reply_markup=s_markup)





@bot.message_handler(commands=['new_dolg'])
def new_dolg(message):
    keyboard = types.InlineKeyboardMarkup()
    for i in users():
        if i != user(message.chat.id):
            keyboard.add(types.InlineKeyboardButton(text=i, callback_data=i))

    bot.send_message(message.from_user.id, "должник:",reply_markup=keyboard)

@bot.message_handler(commands=['pay_dolg'])
def pay_dolg(message):
    keyboard = types.InlineKeyboardMarkup()

    for i in dolgi(user(message.chat.id)):
        keyboard.add(types.InlineKeyboardButton(text=f'{i[1]}у - {i[2]} руб.', callback_data=i[0]))

    bot.send_message(message.from_user.id, "какой долг погасили?",reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data:
        if call.data in users():
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(call.message.chat.id, f"{call.data} должен...", reply_markup=s_markup)

            bot.set_state(call.message.chat.id, f'{call.message.chat.id} {call.data}')
            bot.register_next_step_handler(call.message, submit)

        elif all(map(str.isdigit, call.data)):
            d = dolg(int(call.data))
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(call.message.chat.id, f"{d[1]}у был отправлен запрос", reply_markup=s_markup)

            yes = types.InlineKeyboardButton(text='да', callback_data='yes '+call.data)
            no = types.InlineKeyboardButton(text='нет', callback_data='no '+call.data)
            key_submit = types.InlineKeyboardMarkup()
            key_submit.add(yes, no)

            bot.send_message(chat(d[1]), f"{d[0]} вернул {d[2]} руб. ?",
                             reply_markup=key_submit)

        elif call.data.split()[0] in 'yesno':
            bot.delete_message(call.message.chat.id, call.message.id)
            d = dolg(int(call.data.split()[1]))
            if call.data.split()[0] == 'yes':
                minus_dolg(int(call.data.split()[1]))
                bot.send_message(chat(d[0]),
                                 f"{user(call.message.chat.id)} подтвердил погашение долга в {d[2]} руб.", )
                bot.send_message(chat(d[0]), count_dolg(), )
                bot.send_message(chat(d[1]), count_dolg(), )
            else:
                bot.send_message(chat(d[0]),
                                 f"{user(call.message.chat.id)} не подтвердил погашение долга в {d[2]} руб.", )


        else:

            if call.data.split()[0] != 'нет':
                bot.delete_message(call.message.chat.id, call.message.id)

                dolg_to_db(user(call.message.chat.id),call.data.split()[1],int(call.data.split()[0]))

                bot.send_message(call.message.chat.id,  count_dolg(), )

                bot.send_message(chat(call.data.split()[1]), f"{user(call.message.chat.id)} подтвердил свой долг в {call.data.split()[0]} руб.",)
                bot.send_message(chat(call.data.split()[1]), count_dolg(), )
            else:
                bot.delete_message(call.message.chat.id, call.message.id)
                bot.send_message(chat(call.data.split()[1]), f"{user(call.message.chat.id)} не подтвердил свой долг в {call.data.split()[2]} руб.", )



def submit(message):

    cr_dol = bot.get_state(message.chat.id).split()
    yes = types.InlineKeyboardButton(text='да', callback_data = f'{message.text} {user(cr_dol[0])}')
    no = types.InlineKeyboardButton(text='нет', callback_data = f'нет {user(cr_dol[0])} {message.text}')
    key_submit = types.InlineKeyboardMarkup()
    key_submit.add(yes,no)
    bot.send_message(chat(cr_dol[1]), f"вы должны {user(cr_dol[0])}у {message.text} руб.", reply_markup=key_submit)

    bot.send_message(message.chat.id, f"{cr_dol[1]}у был отправлен запрос", reply_markup=s_markup)

bot.infinity_polling()