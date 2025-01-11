import telebot # импортируем основную библиотеку
from telebot import types
import asyncio

from sekret.key import TOKEN # импортируем токен
from animals_and_their_characteristics import animals # импортируем данные (я бы назвал дерево), о животных
from questions import questions # импортируем вопросы
from photo_generation import get_animal_name
from telegram_bot.check import check_emil
from smtp import send_mail

bot = telebot.TeleBot(TOKEN)

# для id сообщение, дабы потом его удалить
last_message_id = None

# словарь где id пользователя будет указывать на словарь с current_question - счётчик вопросов, answers - список ответов
user_states = {}

# словарь начальных команд(планирую засунуть в файл с вопросоми или с животными), для клавы
commands = {
    "start": "Начать диолог",
    "help": "Помощь"
}


# Добавим состояние для ввода email и сообщения
def reset_user_state(chat_id):
    user_states[chat_id] = {
        "current_question": 0,
        "answers": [],
        "step": None,  # Текущее состояние: None, "email", "text"
        "eml": None,
        "text": None
    }



@bot.message_handler(commands=["start", "help"])
def initial_message(message):
    """Первые сообщение информирующие о запуске бота."""
    reset_user_state(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for cmd in commands:
        button = types.KeyboardButton(f'/{cmd}')
        markup.add(button)
    bot.send_message(
        message.chat.id,
        "Добро пожаловать на викторину «Какое у вас тотемное животное?»",
        reply_markup=markup
    )
    bot.send_message(
        message.chat.id,
        "Нажмите /values, чтобы начать викторину."
    )



@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    """Обработка нажатия кнопки."""
    chat_id = call.message.chat.id
    if call.data == "EMAIL":
        # Сбросить состояние для поддержки
        user_states[chat_id]["step"] = "email"
        bot.send_message(chat_id, "Пожалуйста, введите свою почту:")



@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get("step") == "email")
def get_email(message):
    """Получение email пользователя."""
    chat_id = message.chat.id
    email = message.text
    if check_emil(email):  # Проверка e-mail
        user_states[chat_id]["eml"] = email
        user_states[chat_id]["step"] = "text"
        bot.send_message(chat_id, "Теперь введите сообщение для поддержки:")
    else:
        bot.send_message(chat_id, "Неверный формат e-mail. Попробуйте снова.")



@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get("step") == "text")
def get_text(message):
    """Получение текста для поддержки."""
    chat_id = message.chat.id
    text = message.text
    email = user_states[chat_id].get("eml")
    user_states[chat_id]["text"] = text
    user_states[chat_id]["step"] = None  # Сброс состояния после завершения

    # Отправка сообщения через SMTP
    try:
        print(f"Отправка сообщения: {text} на адрес: {email}")
        asyncio.run(send_mail(msg=text, to=email))
        bot.send_message(chat_id, "Ваше сообщение отправлено в поддержку.")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при отправке сообщения: {str(e)}")

    # Сбросим данные пользователя
    reset_user_state(chat_id)

def dell_messages(chat_id, last_message_id):
    """
    Удаляем передувшее сообщение
    """
    bot.delete_message(chat_id, last_message_id)
    # обновляем id
    last_message_id = None



def show_animal(chat_id):
    """
    Результаты
    отправляет сообщение с фото животного
    """
    user_state = user_states[chat_id]
    do_result = list(map(lambda x: int(x), user_state["answers"]))

    result = sum(do_result)
    animal = animals[result]

    list_botton = types.InlineKeyboardMarkup()
    botton = types.InlineKeyboardButton("Написать зоопарку ", callback_data="EMAIL")
    list_botton.add(botton)

    bot.send_message(chat_id, "Ииии подводя итоги, ваше тотемное животное:")
    bot.send_photo(chat_id, photo=get_animal_name(f"{animal.split(':')[0]}"), caption=f"{animal}",
                   reply_markup=list_botton)


def share_result():
    """Поделиться результатом
        пока ничего и смысл так такого нет.
        Так как сам телеграм позволяет удобно поделиться куда угодно кому удобно
        Но я всё равно сделаю, но в конце, так как это второсотное.
        А добавил её чтобы не забыть."""
    pass


@bot.message_handler(commands=["test"])
def test(messeng):
    """
    Проверка итогово результата.
    Сделал времена дабы не проходить весь тест занова,
    поэтому когда буду уверен, что система работает так как я хочу, уберу.
    """
    result = 138     # номер животного которое хочу проверить (от 1 до 260)
    animal = animals[result]
    list_botton = types.InlineKeyboardMarkup()
    botton = types.InlineKeyboardButton("Написать зоопарку ", callback_data="EMAIL")
    list_botton.add(botton)

    bot.send_message(messeng.chat.id, "Ииии подводя итоги, ваше тотемное животное:")
    bot.send_photo(messeng.chat.id, photo=get_animal_name(f"{animal.split(':')[0]}"), caption=f"{animal}",
                   reply_markup=list_botton)


bot.polling(non_stop=True)