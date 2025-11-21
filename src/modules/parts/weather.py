import os
import requests
from dotenv import load_dotenv
from .bot import bot
from .commands import finish_interaction

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru",
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data["cod"] == 200:
            return data
        else:
            return None
    except Exception as error:
        print(f"Ошибка при получении погоды: {error}")
        return None


def format_weather_message(data, city):
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    description = data["weather"][0]["description"].capitalize()
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    pressure = data["main"]["pressure"]

    message = f"🌍 <b>Погода в городе {city}:</b>\n\n"
    message += f"🌡 <b>Температура:</b> {temp}°C\n"
    message += f"🤔 <b>Ощущается как:</b> {feels_like}°C\n"
    message += f"☁️ <b>Описание:</b> {description}\n"
    message += f"💧 <b>Влажность:</b> {humidity}%\n"
    message += f"💨 <b>Ветер:</b> {wind_speed} м/с\n"
    message += f"📊 <b>Давление:</b> {pressure} гПа"

    return message


@bot.message_handler(commands=["weather"])
def get_weather(message):
    bot_reply = bot.reply_to(
        message, "Введи название города для получения прогноза погоды:"
    )
    bot.register_next_step_handler(bot_reply, process_weather_request)


def process_weather_request(message):
    city = message.text.strip()
    wait_message = bot.reply_to(message, "⏳ Получаю данные о погоде...")
    weather_data = get_weather_data(city)

    if weather_data:
        weather_message = format_weather_message(weather_data, city)
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=wait_message.message_id,
            text=weather_message,
            parse_mode="HTML",
        )
        finish_interaction(message.chat.id)
    else:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=wait_message.message_id,
            text=f"❌ Город '{city}' не найден. Проверь правильность написания и попробуй снова.",
        )
        finish_interaction(message.chat.id)
