import telebot
from telebot import types

from sekret.key import TOKEN
from animals_and_their_characteristics import animals
from questions import questions
bot = telebot.TeleBot(TOKEN)

massege_id = None


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
def first_question(masseng):

    for i in range(0, len(questions)):
        initial_keyboard = types.InlineKeyboardMarkup()
        quest = list(questions)[i]
        for answer in questions[quest]:
            button = types.InlineKeyboardButton(answer)
            initial_keyboard.add(button)
        bot.send_message(masseng.chat.id, text= str(quest), reply_markup= initial_keyboard)



@bot.callback_query_handler()
def handle_query(call):
    global massege_id

    bot.delete_message(call.message.chat.id, massege_id)
    region = call.data
    result = animals[region]
    bot.send_message(call.message.chat.id,  "/продолжить")


@bot.message_handler()
def second(masseng):
    global massege_id
    initial_keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Вода", callback_data="Water")
    button2 = types.InlineKeyboardButton("Воздух", callback_data="Air")
    button3 = types.InlineKeyboardButton("Земля", callback_data="Land")
    initial_keyboard.add(button1, button2, button3)
    sent_message = bot.send_message(masseng.chat.id, "Какая твоя стихия?", reply_markup= initial_keyboard)
    massege_id = sent_message.message_id

bot.polling(non_stop=True)

