import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import requests

# Здесь нужно вставить ваш токен, полученный у @BotFather
TOKEN = "6351726688:AAGTox1QbMDrR-DUDwwyiiA7hn_2iQzwJqc"

# ID чата вашей группы, в которую будут отправляться отзывы
GROUP_CHAT_ID = "-1001569304334"

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user = message.from_user.first_name
    bot.send_message(message.chat.id,
                     f"Привет, {user}! Добро пожаловать в наш ресторан. "
                     "Вы можете оставить свой отзыв, нажав на кнопку 'Оставить отзыв' или воспользоваться другими функциями.",
                     reply_markup=get_main_menu_keyboard())


# Функция для создания основного меню
def get_main_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Оставить отзыв')
    keyboard.row('Меню', 'Сайт')
    keyboard.row('Контакты')
    return keyboard

# Обработчик кнопки "Меню"
@bot.message_handler(func=lambda message: message.text == "Меню")
def handle_menu(message):
    menu_url = "https://primerest.uz/menu.pdf"
    try:
        # Загружаем PDF файл по URL
        response = requests.get(menu_url)
        if response.status_code == 200:
            with open('menu.pdf', 'wb') as file:
                file.write(response.content)
            with open('menu.pdf', 'rb') as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.send_message(message.chat.id, "Не удалось загрузить меню.")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при загрузке меню.")


# Обработчик кнопки "Сайт"
@bot.message_handler(func=lambda message: message.text == "Сайт")
def handle_website(message):
    website_url = "https://www.primerest.uz"
    bot.send_message(message.chat.id, f"Посетите наш сайт: {website_url}")


# Обработчик кнопки "Контакты"
@bot.message_handler(func=lambda message: message.text == "Контакты")
def handle_contacts(message):
    restaurant_name = "Prime Restaurant"
    restaurant_address = "Улица Тараккиёт / 2й проезд"
    restaurant_phone = "+998 99 188 15 15"
    restaurant_instagram = "https://www.instagram.com/prime_rest/"
    bot.send_message(message.chat.id, f"Название ресторана: {restaurant_name}\n"
                                      f"Адрес: {restaurant_address}\n"
                                      f"Телефон: {restaurant_phone}\n"
                                      f"Инстаграм: {restaurant_instagram}")

# Обработчик кнопки "Оставить отзыв"
@bot.message_handler(func=lambda message: message.text == "Оставить отзыв")
def handle_leave_review(message):
    bot.send_message(message.chat.id, "Пожалуйста, напишите свой отзыв о нашем ресторане.")
    bot.register_next_step_handler(message, handle_review_text)


# Обработчик текстового сообщения с отзывом
def handle_review_text(message):
    review_text = message.text
    user = message.from_user.first_name
    bot.send_message(message.chat.id,
                     f"Спасибо за ваш отзыв, {user}! Теперь выберите, хотите ли вы поделиться номером для обратной связи "
                     "или остаться анонимным.",
                     reply_markup=get_contact_choice_keyboard())
    bot.register_next_step_handler(message, handle_contact_choice, review_text)


# Функция для создания клавиатуры выбора контакта
def get_contact_choice_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row(KeyboardButton('Поделиться номером', request_contact=True))
    keyboard.row('Остаться анонимным')
    return keyboard


# Обработчик выбора пользователя по поводу контакта
def handle_contact_choice(message, review_text):
    user = message.from_user.first_name

    if message.contact:
        contact_info = message.contact
        bot.send_message(message.chat.id, f"Спасибо, {user}, что поделились контактом! "
                                          f"Теперь нажмите кнопку 'Отправить', чтобы отправить отзыв.",
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).row('Отправить'))
    else:
        contact_info = None
        bot.send_message(message.chat.id, f"Спасибо, {user}, что остались анонимным! "
                                          f"Теперь нажмите кнопку 'Отправить', чтобы отправить анонимный отзыв.",
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).row('Отправить'))

    bot.register_next_step_handler(message, handle_send_review, review_text, contact_info)



# Обработчик отправки отзыва в группу
def handle_send_review(message, review_text, contact_info):
    user = message.from_user.first_name
    contact_info_str = "анонимный отзыв" if not contact_info else f"Контакт: {contact_info.first_name} " \
                                                                 f"{contact_info.last_name} - {contact_info.phone_number}"

    bot.send_message(GROUP_CHAT_ID,
                     f"Отзыв от {user}:\n\n{review_text}\n\n{contact_info_str}")
    bot.send_message(message.chat.id, f"Спасибо, {user}, ваш отзыв отправлен в группу! Мы очень рады, "
                                      f"что вы посетили наш ресторан.",
                     reply_markup=get_main_menu_keyboard())


# Обработчик команды /cancel
@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    user = message.from_user.first_name
    bot.send_message(message.chat.id, f"{user}, вы отменили оставление отзыва. "
                                      "Вы можете всегда вернуться и оставить отзыв позже.",
                     reply_markup=get_main_menu_keyboard())


if __name__ == "__main__":
    bot.polling(none_stop=True)
