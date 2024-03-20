import telebot
from telebot import types # для указание типов
import mysql.connector
from mysql.connector import Error
#####################################################################################
def create_database(connection, query): #Создание базы данных
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print('База данных успешно создана')
    except Error as e:
        print(f"Error: '{e}'")
def execute_query(connection, query): #Выполнение запросов 
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print('Запрос успешно выполнен')
    except Error as e:
        print(f"Error: '{e}'")
#####################################################################################
try: #Подключение к бд
    connection = mysql.connector.connect(
        host='localhost',
        user="root",
        passwd="123456adS",
        database="stavki_ded"
    )
    cursor = connection.cursor()
    print('Подключение к БД успешно')
except Error as e:
    print(f"Ошибка '{e}' произошла")

create_database_query = "CREATE DATABASE stavki_ded"
create_database(connection, create_database_query) #создание БД
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT,
  chat_id INT, 
  name TEXT NOT NULL,
  key_buy INT,
  admin INT,
  PRIMARY KEY (id)
) ENGINE = InnoDB
"""
execute_query(connection, create_users_table)

bot = telebot.TeleBot('6899209881:AAHiEydcBqbJK_xpgtGKeIpTBoDbXhrJMCA', parse_mode=None)
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    chat_id = message.chat.id
    print('Пользователь', chat_id, 'пытается авторизоваться. (use cmd /start)')
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
    user = cursor.fetchone()
    if not user:
        insert_query = "INSERT INTO users (chat_id, name) VALUES (%s, %s)"
        cursor.execute(insert_query, (chat_id, message.from_user.first_name))
        connection.commit()
    cursor.execute("SELECT admin FROM users WHERE chat_id = %s", (chat_id,))
    user = cursor.fetchone()
    buy_key_btn = types.KeyboardButton("🛒 Купить ключ")
    have_key_btn = types.KeyboardButton("🔑 У меня есть ключ")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)    
    markup.add(have_key_btn, buy_key_btn)
    bot.send_message(message.chat.id, text="Добро пожаловать в прогнозы от деда Ставыча\nДля получения доступа к боту вам нужно приобрести ключ\nЕсли у вас есть ключ, можете использовать кнопку меню.".format(message.from_user), reply_markup=markup)
############################################################################################################################
@bot.message_handler(commands=['settings'])
def send_settings(message):
    chat_id = message.chat.id #Проверка админ-прав
    print('Пользователь', message.chat.id, 'пытется авторизоваться в админ-панеле')
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT admin FROM users WHERE chat_id = %s", (chat_id,))
    admin_level = cursor.fetchone()
    cursor.close() #Проверка админ-прав
    if admin_level and admin_level[0] >= 1:
        print('Пользователь', message.chat.id, 'авторизовался в админ-панеле')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        free_pages_button = types.KeyboardButton('🆓 Бесплатная новость для всех пользователей')
        new_pages_button = types.KeyboardButton('📰 Новая новость для платных пользователей')
        sale_price_button = types.KeyboardButton('🛍 Добавить скидку на продукт')
        statistic_button = types.KeyboardButton('📊 Статистика бота')
        add_promo = types.KeyboardButton('®️ Добавить промокод')
        off_bot = types.KeyboardButton('❌ Оключить бота')
        markup.add(free_pages_button)
        markup.add(new_pages_button)
        markup.add(sale_price_button)
        markup.add(statistic_button, add_promo)
        markup.add(off_bot)
        bot.send_message(chat_id, "Добрый день, уважаемый администратор.\nИспользуйте кнопки для управления админ-панелью\nВсе действия логируются в файл нашему системному администратору", reply_markup=markup)

############################################################################################################################
@bot.message_handler(content_types=['text'])
def func(message):
    if(message.text == "🛒 Купить ключ"):
        buy_key_url_7 = types.KeyboardButton("Купить ключ на 7 дней")
        buy_key_url_30 = types.KeyboardButton("Купить ключ на 30 дней")
        menu_buttom = types.KeyboardButton('🟥 Вернуться в меню')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(buy_key_url_7, buy_key_url_30)
        markup.add(menu_buttom)
        bot.send_message(message.chat.id, text="На данный момент действует скидка 50% на покупку бота по прогнозам\n1000 рублей - 7 дней\n2750 - 30 дней\n".format(message.from_user), reply_markup=markup)
    elif(message.text == 'Купить ключ на 7 дней' or message.text == '/buykey7day'):
        print('Пользователь', message.chat.id, 'пытается приобрести ключ на 7 дней. (use cmd /buykey7day)')
        markup = types.InlineKeyboardMarkup()
        buy_key_url_7_day = types.InlineKeyboardButton("Онлайн оплата 7 дней", url='https://ru.freepik.com/photos/котики')
        markup.add(buy_key_url_7_day)
        bot.send_message(message.chat.id, "Для совершения оплаты перейдите по ссылке и продолжайте следовать инструкции\nОплата принимается:\nСПБ\nМИР\nVISA/MASTERCARD".format(message.from_user), reply_markup=markup)
    elif(message.text == 'Купить ключ на 30 дней' or message.text == '/buykey30day'):
        print('Пользователь', message.chat.id, 'пытается приобрести ключ на 30 дней. (use cmd /buykey30day)')
        markup = types.InlineKeyboardMarkup()
        buy_key_url_30_day = types.InlineKeyboardButton("Онлайн оплата 30 дней", url='https://ru.freepik.com/photos/котики')
        markup.add(buy_key_url_30_day)
        bot.send_message(message.chat.id, "Для совершения оплаты перейдите по ссылке и продолжайте следовать инструкции\nОплата принимается:\nСПБ\nМИР\nVISA/MASTERCARD".format(message.from_user), reply_markup=markup)
    elif(message.text == "🟥 Вернуться в меню"):
        buy_key_btn = types.KeyboardButton("🛒 Купить ключ")
        have_key_btn = types.KeyboardButton("🔑 У меня есть ключ")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)    
        markup.add(have_key_btn, buy_key_btn)
        bot.send_message(message.chat.id, text="Добро пожаловать в прогнозы от деда Ставыча\nДля получения доступа к боту вам нужно приобрести ключ\nЕсли у вас есть ключ, можете использовать кнопку меню.".format(message.from_user), reply_markup=markup)
    elif(message.text == '🔑 У меня есть ключ' or message.text == '/havekey'):
        print('Пользователь', message.chat.id, 'пытается ввести ключ (use cmd /havekey)')
        markup = types.InlineKeyboardMarkup()
        support_url = types.InlineKeyboardButton("🆘 Связаться с поддержкой", url='https://t.me/Phaelwy')
        markup.add(support_url)
        bot.send_message(message.chat.id, text="Введите ключ который вы получили в сообщении. Весь функционал бота будет активарован вам автоматически\nСпасибо за то что доверяете нам.".format(message.from_user), reply_markup=markup)
        #
        user_text = message.text
        if user_text == test_key:
            print('Yes')
        else:
            print('no')
    elif(message.text == '🆓 Бесплатная новость для всех пользователей'):
        chat_id = message.chat.id #Проверка админ-прав
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT admin FROM users WHERE chat_id = %s", (chat_id,))
        admin_level = cursor.fetchone()
        cursor.close()
        if admin_level and admin_level[0] >= 3:
            print('Okey')
###################################################

bot.infinity_polling()

