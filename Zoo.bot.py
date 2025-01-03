import telebot # импортируем основную библиотеку
from telebot import types

from sekret.key import TOKEN # импортируем токен
from animals_and_their_characteristics import animals # импортируем данные (я бы назвал дерево), о животных
from questions import questions # импортируем вопросы

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

        # создаём кнопки, с условием что по 3 кнопки в ряд
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
    """Делаем так чтобы вопросы по очереди задавались"""
    chat_id = call.message.chat.id
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
    ОСТАЛОСЬ ДОРОБОТАТЬ ЧТОБЫ С ЕГО НАЗВАНИЕМ ВЫХОДИЛО ОПИСАНИЕ И ФОТО
    """
    user_state = user_states[chat_id]
    do_result = list(map(lambda x: int(x), user_state["answers"]))
    result = sum(do_result)

    bot.send_message(chat_id, animals[result])


bot.polling(non_stop=True)

