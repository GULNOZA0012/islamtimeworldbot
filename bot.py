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
    bot.send_message(
        message.chat.id,
        "🇺🇿 O'zbek tili tanlandi."
    )
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling(skip_pending=True)
