import telebot
from telebot import types

from sekret.key import TOKEN
from animals_and_their_characteristics import animals
from questions import questions

bot = telebot.TeleBot(TOKEN)

last_message_id = None

user_states = {}


commands = {
    "start": "Начать диолог",
    "help": "Помощь"
}


@bot.message_handler(commands=["help", 'start'])
def initial_message(massege):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for cmd in commands:
        button = types.KeyboardButton(f'/{cmd}')
        markup.add(button)

    bot.send_message(massege.chat.id, "Добро пожаловать на викторину «Какое у вас тотемное животное?».", reply_markup= markup)
    bot.send_message(massege.chat.id, "В данной викторине, от Московского зоопарка, вам предстоит пройти опрос \n"
                "какое у вас тотемное животное. И вы даже сможете взять его в опеку! Интересно? Тогда нажми /values?")


@bot.message_handler(commands=["values"])
def start_questions(massage):
    user_states[massage.chat.id] = {"current_question": 0, "answers": []}
    ask_question(massage.chat.id)

def ask_question(chat_id):
    state = user_states[chat_id]
    question_keys = list(questions.keys())

    if state["current_question"] < len(question_keys):
        question = question_keys[state["current_question"]]
        options = questions[question]

        list_botton = types.InlineKeyboardMarkup(row_width=3)
        row = []

        for option in options:
            botton= types.InlineKeyboardButton(option, callback_data= option)
            row.append(botton)

            if len(row) == 3:
                list_botton.add(*row)
                row = []
        if row:
            list_botton.add(*row)

        last_mess = bot.send_message(chat_id, question, reply_markup= list_botton)

        last_message_id = last_mess.message_id

    else:
        show_animal(chat_id)

print(last_message_id)
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    user_state = user_states[chat_id]

    # Сохраняем ответ
    user_state["answers"].append(call.data)

    bot.delete_message(call.message.chat.id, last_message_id)

    # Переходим к следующему вопросу
    user_state["current_question"] += 1
    ask_question(chat_id)



def show_animal(chat_id):
    user_state = user_states[chat_id]
    do_result = user_state["answers"]
    n = 0
    way = None
    while n < len(do_result):
        if n == 0:
            way = animals[do_result[n]]
            n += 1
        else:
            way = way[do_result[n]]
            n += 1
    bot.send_message(chat_id, way)


bot.polling(non_stop=True)

