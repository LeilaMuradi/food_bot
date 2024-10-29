import telebot
from telebot import types
import json

TOKEN = '7688187740:AAFKAO8TWJVpF_rr678izTriiXW0BQzauPI'

bot = telebot.TeleBot(TOKEN)

ITEMS_PER_PEGA = 4


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 'Привет! Бот для заказа еды готов!', reply_markup=button_menu())


user_info = {}


def button_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton("Меню🍜")
    btn2 = types.KeyboardButton("Корзина🧺")
    btn3 = types.KeyboardButton("Заказать✅")
    markup.add(btn1, btn2, btn3)

    return markup


@bot.message_handler(commands=['add_info'])
def add_info(message):
    chat_id = message.chat.id
    user_info[chat_id] = {}
    msg = bot.send_message(chat_id, "Введите ваше имя:")
    bot.register_next_step_handler(msg, process_name_step)


# Обработка имени
def process_name_step(message):
    chat_id = message.chat.id
    user_info[chat_id]['name'] = message.text
    msg = bot.send_message(chat_id, "Введите ваш номер телефона:")
    bot.register_next_step_handler(msg, process_phone_step)


# Обработка номера телефона
def process_phone_step(message):
    chat_id = message.chat.id
    user_info[chat_id]['phone'] = message.text
    bot.send_message(chat_id,
                     f"Ваше имя: {user_info[chat_id]['name']}\nВаш номер телефона: {user_info[chat_id]['phone']}")
    add_clients(user_info[chat_id]['name'], user_info[chat_id]['phone'])


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == "Меню🍜":
        bot.send_message(message.chat.id, 'Вы выбрали Меню🍜', reply_markup=generate_markup())
    elif message.text == "Корзина🧺":
        items_in_cart = get_cart(message.chat.id)

        markup = types.InlineKeyboardMarkup()
        for item in items_in_cart:
            minus_button = types.InlineKeyboardButton("-", callback_data=f"minus_{item}")
            name_button = types.InlineKeyboardButton(f"{item[0]} x{item[1]}", callback_data=f"name_{item}")
            plus_button = types.InlineKeyboardButton("+", callback_data=f"plus_{item}")
            # Добавляем кнопки в строку markup
            markup.add(minus_button, name_button, plus_button)

        bot.send_message(message.chat.id, "Корзина:", reply_markup=markup)
    elif message.text == "Заказать✅":
        items = get_cart(message.chat.id)
        message_text = "Ваша корзина:\n"
        for item in items:
            message_text += "✨ " +  str(item[0]) + " x" + str(item[1]) + "\n"

        bot.send_message(message.chat.id, message_text)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn2 = types.KeyboardButton("Отмена❌")
        btn3 = types.KeyboardButton("Потвердить✅")
        markup.add(btn2, btn3)

        bot.send_message(message.chat.id, "Подтвердите правильность заказа.", reply_markup=markup)
    if message.text == "Отмена❌":
            bot.send_message(message.chat.id, 'Заказ не принят в работу. Вы можете изменить заказ.', reply_markup=button_menu())
    elif message.text == "Потвердить✅":
        bot.send_message(message.chat.id, "Введите адрес текстом или геометкой Telegram.")
        bot.register_next_step_handler_by_chat_id(message.chat.id, callback=create_order)

def create_order(message):
    if message.content_type == 'text':
        address = message.text
    elif message.content_type == 'location':
        address = f'{message.location.latitude}, {message.location.longitude}'
    else:
        bot.send_message(message.chat.id, "Ошибка распознавания адреса")
        return

    cost = calculate_cart_total(message.chat.id)

    bot.send_message(message.chat.id, f"Вы выбрали адрес: {address}")
    bot.send_message(message.chat.id, f"Стоимость заказа: {cost}")
    bot.send_message(message.chat.id, "Доступна только оплата наличными курьеру")
    bot.send_message(message.chat.id, "Заказ принят в работу🚀", reply_markup=button_menu())


def calculate_cart_total(client_id):
    total_price = 0

    with open("menu.json", 'r', encoding="utf-8") as file:
        data = json.load(file)

    clients = data.get("clients", [])
    for client in clients:
        if client.get("id") == str(client_id):
            cart = client.get("cart", [])
            for cart_item in cart:
                item_name = cart_item[0]

                for menu_item in menu_items:
                    if menu_item["name"] == item_name:
                        item_price = int(menu_item["price"].split()[0])  # Преобразуем цену в число, убрав "руб."
                        item_quantity = cart_item[1]
                        total_price += item_price * item_quantity

    return total_price



def add_clients(name, phone):
    try:
        with open('menu.json', 'r', encoding='utf-8') as file:
            food = json.load(file)
    except FileNotFoundError:
        food = {"clients": []}

    food["clients"].append({
        "name": name,
        "phone": phone
    })

    with open('menu.json', 'w', encoding='utf-8') as file:
        json.dump(food, file, ensure_ascii=False)


menu_items = [
    {"name": "Грибной суп", "price": "450 руб.", "photo": "mushroom_soup.png"},
    {"name": "Салат Цезарь", "price": "550 руб.", "photo": "caesar.png"},
    {"name": "Утка с апельсинами", "price": "700 руб.", "photo": "duck_orange.png"},
    {"name": "Бефстроганов", "price": "650 руб.", "photo": "stroganoff.png"},
    {"name": "Ризотто", "price": "500 руб.", "photo": "risotto.png"},
    {"name": "Тирамису", "price": "400 руб.", "photo": "tiramisu.png"},
    {"name": "Блины", "price": "300 руб.", "photo": "pancakes.png"},
    {"name": "Паста Карбонара", "price": "550 руб.", "photo": "carbonara.png"},
    {"name": "Гаспачо", "price": "350 руб.", "photo": "gazpacho.png"},
    {"name": "Фалафель", "price": "400 руб.", "photo": "falafel.png"}]


def generate_markup(page=0):
    markup = types.InlineKeyboardMarkup()
    start_index = page * ITEMS_PER_PEGA
    end_index = start_index + ITEMS_PER_PEGA

    for items in menu_items[start_index: end_index]:
        button = types.InlineKeyboardButton(f"{items["name"]} , {items["price"]}",
                                            callback_data=f'item_{menu_items.index(items)}')
        markup.add(button)

    if page > 0:
        markup.add(types.InlineKeyboardButton(text='<<', callback_data=f'page_{page - 1}'))

    if end_index < len(menu_items):
        markup.add(types.InlineKeyboardButton(text='>>', callback_data=f'page_{page + 1}'))

    return markup


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(call.id)
    if call.data.startswith('page_'):
        _, page = call.data.split('_')
        markup = generate_markup(int(page))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите элемент:", reply_markup=markup)
    elif call.data.startswith('item_'):
        _, item_index = call.data.split('_')
        add_to_cart(call.message.chat.id, menu_items[int(item_index)])
        bot.send_message(call.message.chat.id, f'{menu_items[int(item_index)]["name"]} добавлено в заказ')


def add_to_cart(client_id, item):
    with open("menu.json", 'r', encoding="utf-8") as file:
        data = json.load(file)

    clients = data.get("clients", [])
    for client in clients:
        if client.get("id") == str(client_id):
            for cart_item in client["id"]:
                if cart_item[0] == item:
                    cart_item[1] += 1
            else:
                client["cart"].append([item, 1])

    with open("menu.json", 'w', encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def delete_to_cart(client_id, item):
    with open("menu.json", 'r', encoding="utf-8") as file:
        data = json.load(file)

    clients = data.get("clients", [])
    for client in clients:
        if str(client.get("id")) == str(client_id):
            for cart_item in client["id"]:
                if cart_item[0] == item:
                    cart_item[1] -= 1
                    if cart_item[1] == 0:
                        del cart_item[1]
            else:
                client["cart"].pop([item, 1])

    with open("menu.json", 'w', encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)



def get_cart(client_id):
    with open("menu.json", 'r', encoding="utf-8") as file:
        data = json.load(file)

    clients = data.get("clients", [])
    for client in clients:
        if client.get("id") == str(client_id):
            return client.get("cart", [])

    return None  # Возвращаем None, если клиент с указанным ID не найден


bot.polling()
