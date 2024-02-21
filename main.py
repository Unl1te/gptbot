import datetime
import os.path
import random
from data import music_dict
import openai
import telebot
from telebot import types
import sqlite3
import glob
openai.api_key = "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"
bot = telebot.TeleBot('6181255243:AAEIQUX36n4fkJraLs1XK8bhsGeoJhaqhEI')
imagination = "Вы добрый и полезный помощник"
opts = {
    "alias": ('секретные тяги', 'Секретные тяги'),
}
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {'role': 'user', 'content': 'I am a regular user who needs an answer to a question'},
    {"role": "assistant", "content": "Greetings! What do you want to know?"},
]


def update(messages, role, content):
    messages.append({"role": role, "content": content})

    return messages
    # Дата база


def database(message):

    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    connect.commit()
    user_id = message.chat.id

    cursor.execute(f"SELECT * FROM login_id WHERE id = {user_id}")
    data = cursor.fetchone()
    # Если база пуста
    if data is None:
        user_id = message.chat.id
        cursor.execute("INSERT INTO login_id VALUES(?, ?)", (user_id, 0))

        connect.commit()
    else:
        pass


def log(message):
    print("<!------!>")
    print(datetime.datetime.now())
    print("Сообщение от {0} {1} (id = {2}) \n {3}".format(message.from_user.first_name,
                                                          message.from_user.last_name,
                                                          str(message.from_user.id), message.text))


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Картинки")
    item2 = types.KeyboardButton("Ассистент")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)


@bot.message_handler(message=['Поменять'])
def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Картинки")
    item2 = types.KeyboardButton("Ассистент")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)


@bot.message_handler(func=lambda _: True)
def handle_message(message):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    connect.commit()

    database(message)

    user_id = message.chat.id

    x = cursor.execute("SELECT chams FROM login_id WHERE id == ?", (user_id,)).fetchone()
    change_module = x[0]

    # Система смены
    if message.text == 'Поменять':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Картинки")
        item2 = types.KeyboardButton("Ассистент")
        markup.add(item1, item2)
        bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)

    # Поменять на генератор картинок
    elif message.text == "Картинки":

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        item = types.KeyboardButton('Поменять')
        markup.add(item)

        cursor.execute("UPDATE login_id SET chams = 1 WHERE id == ?;", (message.chat.id,))
        connect.commit()

        bot.send_message(chat_id=message.from_user.id, text="Уговорил = Картинки!", reply_markup=markup)

    # Поменять на чат гпт
    elif message.text == "Ассистент":

        cursor.execute("UPDATE login_id SET chams = 0 WHERE id == ?;", (message.chat.id,))
        connect.commit()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton('Поменять')
        markup.add(item)
        bot.send_message(chat_id=message.from_user.id, text="Уговорил = Ассистент", reply_markup=markup)

    # Секретное слово
    elif message.text.startswith(opts["alias"]):
        audio_file = random.choice(music_dict[1])
        bot.send_audio(message.from_user.id, audio=open(audio_file, 'rb'), title="Modern Tyaging – Cheza Cheza Tyagi")
        print(opts["alias"])

    # Генератор картинок
    elif change_module == 1:
        response = openai.Image.create(
            prompt=message.text,
            n=1,
            size="1024x1024",
        )
        log(message)
        textt = response['data'][0]['url']
        bot.send_message(chat_id=message.from_user.id, text=f'<a href ="{textt}">{message.text}</a>', parse_mode='html')
        print('Ответ от Shiza \n', str(response['data'][0]['url']))

    # Около стандартный чат гпт
    elif change_module == 0:
        update(messages, 'user', message.text)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        bot.send_message(chat_id=message.from_user.id, text=response['choices'][0]['message']['content'])
        log(message)
        print('Ответ от Shiza \n', str(response['choices'][0]['message']['content']))


bot.polling()
