from telebot import types
from .bot import bot, keyboards


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Отладочный Привет, @{message.from_user.username}\nВыбирай команлу:",
        reply_markup=keyboards["/start"],
    )


@bot.callback_query_handler(func=lambda call: True)
def inlineButtonsCallback(call):
    bot.answer_callback_query(call.id)

    fake_message = types.Message(
        message_id=call.message.message_id,
        from_user=call.from_user,
        chat=call.message.chat,
        date=call.message.date,
        content_type="text",
        options={},
        json_string={},
    )

    fake_message.text = call.data
    bot.process_new_messages([fake_message])


@bot.message_handler(commands=["grm"])
def getRandomMenu(message):
    bot.send_message(
        message.chat.id,
        "Тут будет функционал рандомизирования меню!",
        reply_markup=keyboards["/grm"],
    ),


@bot.message_handler(commands=["info"])
def getInfo(message):
    bot.send_message(
        message.chat.id, "Arhy’s Tiny Helper Unit is still in development..."
    )
    finish_interaction(message.chat.id)


def finish_interaction(chat_id):
    bot.send_message(
        chat_id,
        "Чем я могу ещё помочь?",
        reply_markup=keyboards["/start"],
    )
