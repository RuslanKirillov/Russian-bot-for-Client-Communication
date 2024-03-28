import telebot
from telebot import types # для указание типов
import mysql.connector
from mysql.connector import Error
import os
import logging
from datetime import datetime
from setting_bot import api_TOKEN1
#####################################################################################
import requests
from requests.exceptions import ReadTimeout

try:
    response = requests.get('https://api.telegram.org/', timeout=60)
    # Обработка успешного ответа
except ReadTimeout:
    # Код для обработки таймаута
    print("Запрос превысил время ожидания. Проблемы с TelegramAPI сервером")
####################################################################################
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
def check_admin_rights(chat_id, connection):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT admin FROM users WHERE chat_id = %s", (chat_id,))
        admin_level = cursor.fetchone()
        cursor.close()
        # Возвращает True, если уровень админа 3 и выше, иначе False
        return admin_level and admin_level[0] >= 3
    except Exception as e:
        print(f"An error occurred: {e}")
        return False  # В случае возникновения исключения возвращает False
def check_admin_system(chat_id, connection):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT admin FROM users WHERE chat_id = %s", (chat_id,))
        admin_level = cursor.fetchone()
        cursor.close()
        # Возвращает True, если уровень админа 6 и выше, иначе False
        return admin_level and admin_level[0] >= 6
    except Exception as e:
        print(f"An error occurred: {e}")
        return False  # В случае возникновения исключения возвращает False
def after_text_2(message):
    msg = message.text
    with open('msg_file.txt', 'w') as inf:
        inf.write(msg)
    logging.info(f'{message.from_user.first_name} [ID:{message.chat.id}] изменил текст в TePost Editor:\n{msg}')
    print(f'{message.from_user.first_name} [ID:{message.chat.id}] изменил текст в TePost Editor:\n{msg}')
    msg = None
    bot.send_message(message.chat.id, text='Текст успешно сохранён, используйте для настройки кнопки управления TePost Editor')
def find_user_in_db(connection, user_name):
    """Ищет информацию о пользователе в базе данных"""
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE name = %s"
    cursor.execute(query, (user_name,))
    records = cursor.fetchall()
    cursor.close()
    return records
def process_user_search(message):
    if connection is not None:
        user_name = message.text
        user_info = find_user_in_db(connection, user_name)
        if user_info:
            logging.info(f'{message.from_user.first_name} [ID:{message.chat.id}] узнал информацию о пользователе: {user_name}, выведенная информация: {user_info}')
            print(f'{message.from_user.first_name} [ID:{message.chat.id}] узнал информацию о пользователе: {user_name}, выведенная информация: {user_info}')
            info_to_send = f"Информация о пользователе {user_name}: \nID:{user_info}"
            bot.send_message(message.chat.id, info_to_send)
        else:
            bot.send_message(message.chat.id, 'Пользователь не найден.')
    else:
        bot.send_message(message.chat.id, 'Не удалось подключиться к базе данных.')

##################################SETTINGS##################################################
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
infolog_log = f"infolog_{current_time}.log"
menu_buttom = types.KeyboardButton('🟥 Вернуться в меню')
logging.basicConfig(level=logging.INFO, filename=infolog_log,filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
#logging.debug("A DEBUG Message")
#logging.info("An INFO")
#logging.warning("A WARNING")
#logging.error("An ERROR")
#ogging.critical("A message of CRITICAL severity")
#####################################################################################
try: #Подключение к бд
    connection = mysql.connector.connect(
        host='localhost',
        user="root",
        passwd="123456adS",
        database="stavki_ded"
    )
    cursor = connection.cursor()
    logging.info('Подключение к DataBase успешно')
    print('Подключение к DataBase успешно')
except Error as e:
    logging.info(f"Ошибка '{e}' произошла")
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

bot = telebot.TeleBot(api_TOKEN1, parse_mode=None)
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    chat_id = message.chat.id
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
    user = cursor.fetchone()
    if not user:
        insert_query = "INSERT INTO users (chat_id, name) VALUES (%s, %s)"
        cursor.execute(insert_query, (chat_id, message.from_user.first_name))
        connection.commit()
    cursor.execute("SELECT admin FROM users WHERE chat_id = %s", (chat_id,))
    user = cursor.fetchone()
    logging.info(f'{message.from_user.first_name} [ID:{message.chat.id}] авторизовался в боте')
    print(f'{message.from_user.first_name} [ID:{message.chat.id}] авторизовался в боте')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    send_helpbtm = types.KeyboardButton("🆘 Связь с администрацией бота")
    marafon_btml = types.KeyboardButton('💰 Марафон от 1000 до 5000')
    donate_btm = types.KeyboardButton('💸 Помочь проекту')
    info_btml = types.KeyboardButton("👨‍🦳 О боте")
    markup.add(send_helpbtm)
    markup.add(marafon_btml)
    markup.add(donate_btm)
    markup.add(info_btml)
    if check_admin_rights(message.chat.id, connection):
        admin_panelbtm = types.KeyboardButton("🛠 Админ-панель")
        markup.add(admin_panelbtm)
    bot.send_message(message.chat.id, text='''🤖🏆 Добро пожаловать в мир азарта и неожиданных выигрышей вместе с вашим надёжным виртуальным помощником! ⚽️🏀🎾

🚀 Наш бот предоставляет изысканные спортивные прогнозы, чтобы вы могли сорвать крупный куш! Наши аналитики — настоящие эксперты в индустрии ставок, и они всегда готовы поделиться своими знаниями, чтобы помочь вам выиграть. 🏅💰

💌 Бот будет присылать вам самые желанные ставки с высокими коэффициентами прямо в ваш чат. И самое заманчивое — сейчас он абсолютно бесплатен для всех жителей СНГ! 🌍🤑

🔍 У вас возникли вопросы? Нажмите на кнопки ниже, чтобы получить всю необходимую информацию, и наши операторы с радостью на них ответят. 👇

✨ Готовы поразиться новым возможностям в ставках? Если ваш ответ "да", то обязательно включите уведомления от бота! Коэффициенты меняются мгновенно, и каждая секунда может решать исход игры!🔔📈

Пусть удача всегда будет на вашей стороне! 🍀'''.format(message.from_user), reply_markup=markup)
############################################################################################################################
@bot.message_handler(content_types=['text'])
def func(message):
    if(message.text == "🆘 Связь с администрацией бота"):
        markup = types.InlineKeyboardMarkup()
        id_send_help_btml = types.InlineKeyboardButton('Обратиться в поддержку', url='https://t.me/noUser125')
        markup.add(id_send_help_btml)
        bot.send_message(message.chat.id, text= '''Добро пожаловать в нашу службу поддержки, уважаемый пользователь! Вы находитесь в разделе общения с администрацией.

Здесь вы можете обратиться к нам с любыми вопросами или проблемами. Пожалуйста, описывайте ваш запрос подробно для быстрого и точного ответа. 

Для начала взаимодействия, просто кликните на кнопку ниже. Мы ждём вашего сообщения!'''.format(message.from_user), reply_markup=markup)
    elif(message.text == '🛠 Админ-панель' or message.text =='/settings'):
        if check_admin_rights(message.chat.id, connection):
            logging.info(f'{message.from_user.first_name} [ID:{message.chat.id}] авторизовался в админ-панеле.')
            print(f'{message.from_user.first_name} [ID:{message.chat.id}] авторизовался в админ-панеле.')
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            free_pages_button = types.KeyboardButton('📝 Открыть TePost Editor')
            sale_price_button = types.KeyboardButton('🛍 Добавить скидку на продукт')
            statistic_button = types.KeyboardButton('📊 Статистика бота')
            add_promo = types.KeyboardButton('®️ Добавить промокод')
            set_user = types.KeyboardButton('👨‍💻 Настройка пользователей')
            off_bot = types.KeyboardButton('❌ Оключить бота')
            markup.add(free_pages_button)
            markup.add(sale_price_button)
            markup.add(statistic_button, add_promo)
            markup.add(set_user)
            markup.add(off_bot)
            bot.send_message(message.chat.id, text = "Добро пожаловать, уважаемый администратор.\nИспользуйте кнопки для управления админ-панелью\nВсе действия логируются в файл нашему системному администратору".format(message.from_user), reply_markup=markup)
    elif(message.text == '💰 Марафон от 1000 до 5000'):
        bot.send_message(message.chat.id, text = 'Пока марафон не был объявлен. Следите за новостями')
    elif(message.text == '💸 Помочь проекту'):
        markup = types.InlineKeyboardMarkup()
        donate_btm = types.InlineKeyboardButton('Задонатить проекту', url = 'https://t.me/noUser125')
        markup.add(donate_btm)
        bot.send_message(message.chat.id, text = '''
Поддержите наш бот: ваша помощь - наша поддержка 🤝💡
Захотели отблагодарить нас за выигрыш? Отличная идея! Ваша поддержка помогает нам оплачивать труд команды и содержание оборудования. 🛠️💻
Чтобы сделать взнос, воспользуйтесь ссылкой ниже. Мы предлагаем различные способы оплаты для удобства. Пока что проект живет на ваши донаты, и каждый вклад ценен для нас! 🙏💖'''.format(message.from_user), reply_markup=markup)
    elif(message.text == '👨‍🦳 О боте'):
        bot.send_message(message.chat.id, text = '''
Этот бот - результат слияния передовых технологий и глубоких знаний команды экспертов в области спорта. 🤖🏅

Если вы обладаете профессиональным опытом в спортивных прогнозах и заинтересованы в сотрудничестве с нами, мы будем рады получить от вас сообщение. 🤝📧

Наша небольшая, но преданная команда из двух человек всегда стремится предоставлять нашим пользователям только выгодные предложения. 💼💡

У нас грандиозные планы, и вы можете стать частью этого увлекательного путешествия. Не удаляйте бота - следите за нашими обновлениями и используйте наши прогнозы для достижения успеха. 🚀🎯

Связаться с отделом развития можно по электронной почте: kirilooth@yandex.ru 📥''' )
    elif(message.text == '👨‍💻 Настройка пользователей' or message.text == '👨‍💻 Назад в UserEditor'):
        if check_admin_rights(message.chat.id, connection):
            logging.info(f'{message.from_user.first_name} [ID:{message.chat.id}] попытался зайти в права пользователей. (Неудачно)')
            bot.send_message(message.chat.id, text='Уважаемый администратор, вам запрещенно изменять права для пользователей. Для получения этой функции обратитесь к системному администратору.')
        if check_admin_system(message.chat.id, connection):
            logging.info(f'{message.from_user.first_name} [ID:{message.chat.id}] зашел в права пользователей. (Удачно)')
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            check_btm = types.InlineKeyboardButton('🔍 Информация о пользователе')
            setadm_btm = types.InlineKeyboardButton('📝 Изменить права для пользователя')
            ban_btm = types.InlineKeyboardButton('⛔️ Заблокировать пользователя')
            markup.add(check_btm)
            markup.add(setadm_btm)
            markup.add(ban_btm)
            markup.add(menu_buttom)
            bot.send_message(message.chat.id, text='''Используйте кнопки управления в меню\nВсе действия логгируются системному администратору'''.format(message.from_user), reply_markup=markup)
    elif(message.text == "🟥 Вернуться в меню"):
 #edit edit edit
        if check_admin_rights(message.chat.id, connection):
            admin_panelbtm = types.KeyboardButton("🛠 Админ-панель")
            markup.add(admin_panelbtm)
        bot.send_message(message.chat.id, text="Добро пожаловать в прогнозы от деда Ставыча\nДля получения доступа к боту вам нужно приобрести ключ\nЕсли у вас есть ключ, можете использовать кнопку меню.".format(message.from_user), reply_markup=markup)
    elif(message.text == '📝 Открыть TePost Editor' or message.text == '🟥 Вернуться в TePost Editor'):
        if check_admin_rights(message.chat.id, connection):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True) 
            edit_textbtm = types.InlineKeyboardButton('💬 Изменить текст')
            edit_imgbtm = types.InlineKeyboardButton('📷 Изменить изображение')
            promo_postbtm = types.InlineKeyboardButton('🪧 Предосмотр поста')
            send_postbtm = types.InlineKeyboardButton('📩 Отправить пост')
            markup.add(edit_textbtm, edit_imgbtm)
            markup.add(promo_postbtm)
            markup.add(send_postbtm)
            markup.add(menu_buttom)
            logging.info(f'{message.from_user.first_name} [ID:{message.chat.id}] открыл TePost Editor')
            print(f'{message.from_user.first_name} [ID:{message.chat.id}] открыл TePost Editor')
            bot.send_message(message.chat.id, text = 'Используйте кнопки для редактирования поста\nTePost Editor - специальная разработка для данного бота\nВсе действия логгируются системному администратору'.format(message.from_user), reply_markup=markup)
    elif(message.text == '💬 Изменить текст'):
        if check_admin_rights(message.chat.id, connection):
            msg = bot.send_message(message.chat.id, text='Введите текст который вы хотите опубликовать в посте\nВ посте запрещено:\n- Использовать мат, ругательство\n- Оскороблять кого-либо, выражать ненависть\nПосле того как вы отправите текст используйте кнопки TePost Editor')
            bot.register_next_step_handler(msg, after_text_2)
    elif(message.text == '🔍 Информация о пользователе'):
        if check_admin_system(message.chat.id, connection):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back_user_btm = types.InlineKeyboardButton('👨‍💻 Назад в UserEditor')
            markup.add(back_user_btm)
            markup.add(menu_buttom)
            msg = bot.send_message(message.chat.id, 'Введите имя пользователя:')
            bot.register_next_step_handler(msg, process_user_search)
    elif(message.text == '📷 Изменить изображение'):
        if check_admin_rights(message.chat.id, connection):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            addimg_btm = types.InlineKeyboardButton('📸 Добавить/изменить изображение')
            delimg_btm = types.InlineKeyboardButton('❌ Удалить изображение')
            back_tepost_btm = types.InlineKeyboardButton('🟥 Вернуться в TePost Editor')
            markup.add(addimg_btm, delimg_btm)
            markup.add(back_tepost_btm)
            bot.send_message(message.chat.id, text ='Используйте кнопки для управления'.format(message.from_user), reply_markup=markup)
    elif(message.text == '📸 Добавить/изменить изображение'):
        if check_admin_rights(message.chat.id, connection):
            bot.reply_to(message, "Пожалуйста, отправьте изображение.\n")
                        # Переводим пользователя в режим "ожидает отправки изображения"
                        # Здесь должна быть ваша логика изменения состояния пользователя
            @bot.message_handler(content_types=['photo'])
            def handle_photos(message):
                if check_admin_rights(message.chat.id, connection):  # Проверяем права пользователя
                    file_id = message.photo[-1].file_id  # Получаем ID фото с наивысшим качеством
                    file_info = bot.get_file(file_id)  # Получаем объект файла
                    downloaded_file = bot.download_file(file_info.file_path)  # Скачиваем файл
                    with open('img_msg.jpg', 'wb') as new_file:  # Открываем файл для записи в бинарном режиме
                        new_file.write(downloaded_file)  # Записываем скаченный файл                   
                    bot.reply_to(message, "Ваше изображение сохранено.")
                    logging.info(f'{message.from_user.first_name} [ID:{message.chat.id}] изменил фотографию для поста.')
                    print(f'{message.from_user.first_name} [ID:{message.chat.id}] изменил фотографию для поста.')
    elif(message.text == '❌ Удалить изображение'):
        if check_admin_rights(message.chat.id, connection):
            if os.path.isfile("img_msg.jpg"):
                os.remove("img_msg.jpg")
                bot.reply_to(message, 'Изображение успешно удаленно.')
                logging.info(f' {message.from_user.first_name} [ID:{message.chat.id}] удалил фотографию в TePost Editor.')
                print(f'{message.from_user.first_name} [ID:{message.chat.id}] удалил фотографию в TePost Editor.')
            else:
                bot.reply_to(message, 'Изображение не найденно. Вернитесь в TePost Editor')
                print(f'{message.from_user.first_name} [ID:{message.chat.id}] попытался удалить фотографию в TePost Editor. (Фото уже удаленно)')
    elif(message.text == '🪧 Предосмотр поста'):
        if check_admin_rights(message.chat.id, connection):
            print_msg = ''
            with open('msg_file.txt', 'r') as inf:
                print_msg = inf.read()
            try:
                with open('img_msg.jpg', 'rb') as imginf:
                    print_img = imginf.read()  # Считываем содержимое изображения
                bot.send_message(message.chat.id, text='Вот пример как будет выглядеть пост:')
                bot.send_photo(message.chat.id, photo=print_img, caption=print_msg)
            except:
                bot.send_message(message.chat.id, text='Вот пример как будет выглядеть пост:')
                bot.send_message(message.chat.id, text = print_msg)
                logging.info(f' {message.from_user.first_name} [ID:{message.chat.id}] открыл предпросмотр нового поста.')
                print(f'{message.from_user.first_name} [ID:{message.chat.id}] открыл предпросмотр нового поста.')
    elif(message.text == '📩 Отправить пост'):
        if check_admin_rights(message.chat.id, connection):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            sendfree_btm = types.InlineKeyboardButton('🆓 Отправить пост всем')
            sendsupport_btm = types.InlineKeyboardButton('💰 Отправить платный пост')
            back_tepost_btm = types.InlineKeyboardButton('🟥 Вернуться в TePost Editor')
            markup.add(sendfree_btm, sendsupport_btm)
            markup.add(back_tepost_btm)
            bot.send_message(message.chat.id, text='Перед отправкой воспользуйтесь предосмотром поста\nИспользуйте кнопки для отправки\nПост всем - отправить пост всем кто запустил бота\nПост платный - только оплаченные пользователи'.format(message.from_user), reply_markup=markup)
    elif(message.text == '🆓 Отправить пост всем'):
        if check_admin_rights(message.chat.id, connection):
            cursor = connection.cursor()
            query = "SELECT chat_id FROM users"
            cursor.execute(query)
            user_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()

            yes_msg = 0
            no_msg = 0
            print_msg = ''

            with open('msg_file.txt', 'r') as inf:
                print_msg = inf.read()

            # Переменная для содержимого фото. Если фото нет, переменная останется None.
            print_img = None
            try:
                with open('img_msg.jpg', 'rb') as imginf:
                    print_img = imginf.read()
            except Exception as e:
                # Если фото не смогло быть загружено, печатаем ошибку и продолжаем.
                print(f"Не удалось загрузить файл изображения: {e}")

            # Перебираем всех пользователей и отправляем им сообщение или фото.
            for user_id in user_ids:
                try:
                    # Пытаемся отправить фото если оно доступно.
                    if print_img:
                        bot.send_photo(user_id, photo=print_img, caption=print_msg)
                    else:
                        # Если фото нет, отправляем только текстовое сообщение.
                        bot.send_message(user_id, text=print_msg)
                    yes_msg += 1  # Успех, сообщение отправлено.
                except Exception as e:
                    # Если возникла ошибка при отправке, печатаем её и инкрементируем счётчик ошибок.
                    print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                    no_msg += 1

            # В конце отправляем статистику об отправке сообщений.
            bot.send_message(message.chat.id, text=f'Ваш пост был отправлен пользователям бота.\nСтатистика сообщений:\n{yes_msg} - ✔️ Удачно\n{no_msg} - ✖️ Неудачно')
            logging.info(f'{message.from_user.first_name} [ID:{message.chat.id}] отправил пост всем пользователям. {yes_msg} - Успешно, {no_msg} - Неуспешно.')
            print(f'{message.from_user.first_name} [ID:{message.chat.id}] отправил пост всем пользователям. {yes_msg} - Успешно, {no_msg} - Неуспешно.')
    elif(message.text == '❌ Оключить бота'):
        if check_admin_system(message.chat.id, connection):
            bot.send_message(message.chat.id, text='use cmd:/bot_off_21')
        else:
            bot.send_message(message.chat.id, text='Отключать бота имеет право только системный администратор\nОбратитесь к администратору в Telegram')
    elif(message.text == '/bot_off_21'):
        if check_admin_system(message.chat.id, connection):
            bot.send_message(message.chat.id, text='Отключение бота')
            print(f'{message.from_user.first_name}[ID:{message.chat.id}] отключил бота')
            bot.stop_polling()

###################################################

bot.infinity_polling()

