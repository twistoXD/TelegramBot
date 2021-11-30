import sqlite3
import telebot
import config

from telebot import types
from newsapi import NewsApiClient

import hashlib

bot = telebot.TeleBot(config.TOKEN)
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

newsapi= NewsApiClient(api_key=config.API)

password=''
log=''



#база данных
def db_table_reg(message):
    cursor.execute(f"SELECT id FROM users WHERE login = '{log}'").fetchone()
    conn.commit()
    if cursor.fetchone() is None:
        id = message.chat.id
        cursor.execute(f'INSERT INTO users (id,login,password) VALUES (?,?,?)', (id,log,password))
        conn.commit()
        bot.send_message(message.chat.id, 'Вы успешно зарегистрированы'.format(message.from_user,bot.get_me()),parse_mode = "html")
    else:
        bot.send_message(message.chat.id, 'Такой логин уже существует'.format(message.from_user,bot.get_me()),parse_mode = "html")
        regg(message)



def db_table_log(message):
    cursor.execute(f"SELECT id FROM users WHERE login = '{log}'").fetchone()
    conn.commit()
    if cursor.fetchone() is None:
        cursor.execute(f"SELECT id FROM users WHERE login = '{log}' AND password='{password}'")
        conn.commit()
        if cursor.fetchone() is None:
            bot.send_message(message.chat.id, 'Неверный логин или пароль'.format(message.from_user,bot.get_me()),parse_mode = "html")
            
        else:
            bot.send_message(message.chat.id, 'Вы успешно вошли в аккаунт'.format(message.from_user,bot.get_me()),parse_mode = "html")
            id = message.chat.id
            cursor.execute(f'INSERT INTO user (id_user) VALUES ({id})')
            conn.commit()
            logUser(message)
            
    else:
        bot.send_message(message.chat.id, 'Такого пользователя не существует'.format(message.from_user,bot.get_me()),parse_mode = "html")



def logUser(message):
    cursor.execute(f"SELECT id_user FROM user WHERE id_user = '{message.chat.id}'")
    conn.commit()
    if cursor.fetchall() == []:
        return True
    else:
        return False




def login_reg(message):
    global log
    log = hashlib.md5(message.text.encode()).hexdigest()

    bot.send_message(message.chat.id, 'Введите ваш пароль:'.format(message.from_user,bot.get_me()),parse_mode = "html")
    bot.register_next_step_handler(message,password_reg)

def password_reg(message):
    global password
    password = hashlib.md5(message.text.encode()).hexdigest()
    db_table_reg(message)



def login_log(message):
    global log
    log = hashlib.md5(message.text.encode()).hexdigest()

    bot.send_message(message.chat.id, 'Введите ваш пароль:'.format(message.from_user,bot.get_me()),parse_mode = "html")
    bot.register_next_step_handler(message,password_log)

def password_log(message):
    global password
    password = hashlib.md5(message.text.encode()).hexdigest()
    db_table_log(message)










#регистрация

@bot.message_handler(commands = ['start'])  
def welcome(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/reg")
    item2 = types.KeyboardButton("/login")
    item3 = types.KeyboardButton("/news")
    markup.add(item1,item2,item3)

    bot.send_message(message.chat.id,"Приветствую, это твой новостной бот".format(message.from_user,bot.get_me()), parse_mode = "html",reply_markup = markup)


@bot.message_handler(commands = ['reg'])
def regg(message):

    bot.send_message(message.chat.id, 'Регистрация пользователя'.format(message.from_user,bot.get_me()),parse_mode = "html")
    bot.send_message(message.chat.id, 'Введите ваш логин:'.format(message.from_user,bot.get_me()),parse_mode = "html")
    bot.register_next_step_handler(message,login_reg)



@bot.message_handler(commands = ['login'])
def login(message):
    logUser(message)
    if logUser(message) == True:
        bot.send_message(message.chat.id, 'Вход в аккаунт'.format(message.from_user,bot.get_me()),parse_mode = "html")
        bot.send_message(message.chat.id, 'Введите ваш логин:'.format(message.from_user,bot.get_me()),parse_mode = "html")
        bot.register_next_step_handler(message,login_log)
    else:
        bot.send_message(message.chat.id, 'Вы уже вошли в аккаунт'.format(message.from_user,bot.get_me()),parse_mode = "html")











#новости
@bot.message_handler(commands = ['news'])
def news(message):

    if logUser(message) == False:
        keyboardNews = types.InlineKeyboardMarkup()

        health = types.InlineKeyboardButton(text = 'Медицина', callback_data = 'health')
        keyboardNews.add(health)

        science = types.InlineKeyboardButton(text = 'Наука', callback_data = 'science')
        keyboardNews.add(science)

        technology = types.InlineKeyboardButton(text = 'Технологии', callback_data = 'technology')
        keyboardNews.add(technology)

        bot.send_message(message.chat.id,"Выберите категорию новостей :".format(message.from_user,bot.get_me()),
        parse_mode = "html",reply_markup = keyboardNews)

    else:
        bot.send_message(message.chat.id,"Вы не выполнили вход в ваш аккаунт".format(message.from_user,bot.get_me()),parse_mode = "html")
 

@bot.callback_query_handler(func = lambda call: True)
def callback_news(call):
    if call.data != None:
        if call.data=="health" or call.data=="science" or call.data=="technology":
            for x in get_news(categ=call.data):  
                bot.send_message(call.message.chat.id, {x})




def get_news(categ):
       data = newsapi.get_top_headlines(category = categ, language='ru', page_size=5)
       articles = data['articles']
       news=[]
       for x,y in enumerate(articles):

              text=(f"{articles[x]['title']}\n\n{articles[x]['description']}\n\nURL: {articles[x]['url']}\n")       
              news.append(text)
              
       return news














bot.polling(non_stop=True)