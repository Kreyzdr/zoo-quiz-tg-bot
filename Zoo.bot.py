import telebot # импортируем основную библиотеку
from telebot import types

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


@bot.message_handler(commands=["help", 'start'])
def initial_message(massege):
    """
    Первые сообщение информирующие о запуске бота и краткая информация о боте.
    Так же запускает кнопки команд, клава находится у сообщения.
    """

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for cmd in commands:
        button = types.KeyboardButton(f'/{cmd}')
        markup.add(button)

    bot.send_message(massege.chat.id, "Добро пожаловать на викторину «Какое у вас тотемное животное?».", reply_markup= markup)
    bot.send_message(massege.chat.id, "В данной викторине, от Московского зоопарка, вам предстоит пройти опрос \n"
                "какое у вас тотемное животное. И вы даже сможете взять его в опеку! Интересно? Тогда нажми /values?")


@bot.message_handler(commands=["values"])
def start_questions(massage):
    """Кориктируем словарь"""
    user_states[massage.chat.id] = {"current_question": 0, "answers": []}
    ask_question(massage.chat.id)



def ask_question(chat_id):
    """Основная функция.
    Задаюм вопросы
    """
    global last_message_id

    state = user_states[chat_id]
    question_keys = list(questions.keys())

    if state["current_question"] < len(question_keys):
        question = question_keys[state["current_question"]]
        options = questions[question]

        # создаём кнопки, с условием, что по 3 кнопки в ряд
        list_botton = types.InlineKeyboardMarkup(row_width=2)
        row = [] # лист с кнопками

        for option in options:
            # каждый вариант с ответами, и их вес добавляем, и добавляем в лист (row)
            botton= types.InlineKeyboardButton(option, callback_data= options[option])
            row.append(botton)

            if len(row) == 2: # если длина уже подходит под длину клав., то добавляем их
                list_botton.add(*row)
                row = []

        if row: # если остались в листе есть ещё варианты ответа, то добавляем их
            list_botton.add(*row)

        last_mess = bot.send_message(chat_id, question, reply_markup= list_botton) # печатаем вопрос и клав., для ответов
        last_message_id = last_mess.message_id # добавляем id сообщения
    else:
        show_animal(chat_id)



@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    """Делаем так, чтобы вопросы по очереди задавались и имели возвожность отправить сообщение"""

    chat_id = call.message.chat.id

    if call.data == "EMAIL":
        user_states["step"] = 0
        bot.send_message(chat_id, "Сначала введи свою почту: ")
        while True:

            if user_states["step"]==0:
                @bot.message_handler(content_types=["text"])
                def EMIL_TEXT(message):

                    EMAIL = message.text
                    if check_emil(EMAIL):
                        user_states["eml"] = EMAIL
                        user_states["step"] += 1
                        bot.send_message(chat_id, "Теперь ведите то что хотите спросить: ")
                    else:
                        bot.send_message(chat_id, "Вы вели не правильную почту.")

            if user_states["step"] == 1:
                @bot.message_handler(content_types=["text"])
                def EMIL_TEXT(message):

                    TEXTS = message.text
                    user_states["text"] = TEXTS
                    user_states["step"] += 1


            if user_states["step"] == 2:
                try:
                    send_mail(msg=user_states["text"], to=user_states["eml"])
                except:
                    bot.send_message(chat_id, "Произошол сбой на сервере")
                    break
                else:
                    bot.send_message(chat_id, "Сообщение успешно отправлено, ждите ответ на свою почту!!")
                    user_states["step"] += 1
                    break

    else:
        user_state = user_states[chat_id]

        # Сохраняем ответ
        user_state["answers"].append(call.data)

        # Переходим к следующему вопросу
        user_state["current_question"] += 1

        # Если есть id сообщения то удаляем
        if last_message_id is not None:
            dell_messages(chat_id, last_message_id)

        ask_question(chat_id)



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