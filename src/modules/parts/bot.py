import os
import telebot
from dotenv import load_dotenv
from telebot import types

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

keyboards = {
    "/start": types.InlineKeyboardMarkup(),
    "/grm": types.InlineKeyboardMarkup(),
}
