import random
from .bot import bot
from .commands import finish_interaction


def get_random_int(min, max):
    return random.randint(min, max)


@bot.message_handler(commands=["ntp"])
def check_seor(message):
    result = get_random_int(0, 100)
    if result == 0:
        bot.reply_to(message, f"🎉 Ты не пидор")
    elif result < 30:
        bot.reply_to(message, f"🎉 Ты пидор на {result}%")
    elif 30 <= result < 90:
        bot.reply_to(message, f"🤔 Ты пидор на {result}%")
    elif 90 <= result:
        bot.reply_to(message, f"😱 Ты пидор на {result}%")
    elif result == 100:
        bot.reply_to(message, f"🎉 Здравствуйте, Король Пидорасов 👑")
    finish_interaction(message.chat.id)
