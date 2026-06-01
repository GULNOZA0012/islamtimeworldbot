import os
import threading
from flask import Flask
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "IslamTimeWorldBot is running!"

@bot.message_handler(commands=["start"])
def start(message):
    text = """
🌍 Welcome to Islam Time World

Please select your language:
"""

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        "🇺🇿 O'zbekcha", "🇷🇺 Русский",
        "🇬🇧 English", "🇸🇦 العربية",
        "🇹🇷 Türkçe", "🇩🇪 Deutsch",
        "🇫🇷 Français", "🇪🇸 Español",
        "🇮🇹 Italiano", "🇰🇿 Қазақша",
        "🇰🇬 Кыргызча", "🇹🇯 Тоҷикӣ"
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )
@bot.message_handler(func=lambda message: message.text == "🇺🇿 O'zbekcha")
def uzbek(message):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        "🕌 Namoz vaqtlari",
        "🧭 Qibla",
        "📍 Yaqin masjidlar",
        "📖 Qur'on",
        "📚 Hadislar",
        "⚙️ Sozlamalar"
    )

    bot.send_message(
        message.chat.id,
        "🇺🇿 O'zbek tili tanlandi.\n\nKerakli bo'limni tanlang:",
        reply_markup=markup
    )
    @bot.message_handler(func=lambda message: message.text == "🕌 Namoz vaqtlari")
def prayer_times(message):
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

    location_btn = types.KeyboardButton(
        "📍 Lokatsiyani yuborish",
        request_location=True
    )

    markup.add(location_btn)

    bot.send_message(
        message.chat.id,
        "📍 Namoz vaqtlarini hisoblash uchun hozirgi lokatsiyangizni yuboring.",
        reply_markup=markup
    )


@bot.message_handler(content_types=["location"])
def location_handler(message):
    lat = message.location.latitude
    lon = message.location.longitude

    bot.send_message(
        message.chat.id,
        f"✅ Lokatsiya qabul qilindi.\n\nLatitude: {lat}\nLongitude: {lon}"
    )
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling(skip_pending=True)
