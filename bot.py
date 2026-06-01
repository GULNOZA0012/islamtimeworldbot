import os
import threading
from flask import Flask
import telebot

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "IslamTimeWorldBot is running!"

@bot.message_handler(commands=["start"])
def start(message):
    text = """
🕌 Assalomu alaykum!

Islam Time World Botga xush kelibsiz.

1️⃣ Namoz vaqtlari
2️⃣ Qibla yo‘nalishi
3️⃣ Yaqin masjidlar
4️⃣ Qur'on
5️⃣ Hadislar
6️⃣ Til tanlash
"""
    bot.send_message(message.chat.id, text)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling(skip_pending=True)
