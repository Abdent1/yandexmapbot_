import fnmatch
import telebot
import json
from telebot import types
from telebot.types import ReplyKeyboardRemove
from keyboa.keyboard import Keyboa
import os


# API бота
bot = telebot.TeleBot('6307682483:AAGq4H1Mh4PQ2F64410bTnwpd5nKQXWbmHM')

# Функции необходимые для добавления точек

global point_id_user
point_id_user = 1979945707

def input_address(message):
    global point_address
    point_address = message.text
    msg = bot.send_message(message.chat.id, 'Введите ССЫЛКУ на сопровождающую фотографию:')
    bot.register_next_step_handler(msg,input_img)

def input_img(message):
    global point_img
    point_img = message.text
    msg = bot.send_message(message.chat.id, 'Введите описание точки:')
    bot.register_next_step_handler(msg,input_context)

def input_context(message):
    global point_context
    point_context = message.text
    msg = bot.send_message(message.chat.id, 'Введите долготу и широту точки через пробел:')
    bot.register_next_step_handler(msg,input_lon_lat)

def input_lon_lat(message):
    point_lon_lat = message.text
    if fnmatch.fnmatch(str(point_lon_lat), '* *'):
        point_lon = str(point_lon_lat.split()[0])
        point_lat = point_lon_lat.split()[1]
        msg = bot.send_message(message.chat.id, 'Точка успешно создана!')

        #В рамках этой же функции формируем новый Json

        new_data = {'id_user': point_id_user, 'address': point_address, 'img': point_img, 'context': point_context, 'lon': point_lon, 'lat': point_lat}
        with open('Read.json', encoding='utf8') as f:  # Открываем файл
            data = json.load(f)  # Получае все данные из файла (вообще все, да)
        data.append(new_data)  # Добавляем данные
        f.close()
        with open('Read.json', 'w', encoding='utf8') as outfile:  # Открываем файл для записи
            json.dump(data, outfile, ensure_ascii=False,
                      indent=2)  # Добавляем данные (все, что было ДО добавления данных + добавленные данные)
        outfile.close()
        default_buttons(message)
        quit(os.system("python3 main.py"))  # Закроет и заново откроет файл (не работает в цикле)



    else:
        msg = bot.send_message(message.chat.id, 'Неверный формат долготы и широты (поставьте между ними пробел, уберите лишние знаки):')
        bot.register_next_step_handler(msg, input_lon_lat)


# Вывод кнопок
def default_buttons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # вывод кнопок
    btn1 = types.KeyboardButton('Добавить точку')
    btn2 = types.KeyboardButton('Удалить точку')

    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, 'Что вы желаете сделать далее?', reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Начать")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 С помощью данного бота вы можете добавлять и убирать точки на карте.", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    adm = [908945149, 52881874]  # список из id пользователей, if Для разрешения на работу
    if message.chat.id not in adm:
        bot.send_message(message.chat.id, 'Не дозволено')
    else:

        if message.text == '👋 Начать':

            default_buttons(message)


        elif message.text == 'Добавить точку':

            msg = bot.send_message(message.chat.id, 'Введите адрес точки:', reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, input_address)

# Удаление точки
        elif message.text == 'Удалить точку':

            address_listing = []
            with open('Read.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            f.close()
            for p_id in data:
                address_one = p_id.get('address')
                address_listing.append(address_one)

            # Создаём пустой dict
            myDict = dict()
            myDict = {address_listing[i]: i for i in range(0, len(address_listing), 1)}
            myList = [{key.strip(): str(value)} for key, value in myDict.items()]
            kb_address = Keyboa(items=myList, items_in_row=3)
            bot.send_message(chat_id=message.chat.id, text='Выберите точку для удаления', reply_markup= kb_address())

            @bot.callback_query_handler(func=lambda call: True)
            def callback_inline(call):
                search_value=call.data
                msg1 = next((key for item in myList for key, value in item.items() if value == search_value), None)
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

                point_del = msg1
                with open('Read.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    minimal = 0
                    check = 0
                    for txt in data:
                        if txt['address'] == point_del:
                            data.pop(minimal)
                            check = check + 1
                        else:
                            None
                            minimal = minimal + 1
                if check == 1:
                    bot.send_message(message.chat.id, 'Точка успешно удалена!')
                else:
                    bot.send_message(message.chat.id, 'Точка с данным адресом не найдена!')
                f.close()
                with open('Read.json', 'w', encoding='utf-8') as outfile:
                    json.dump(data, outfile, ensure_ascii=False, indent=2)
                outfile.close()





bot.polling(none_stop=True, interval=0)