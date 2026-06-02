import os
import threading
import requests
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

    bot.send_message(message.chat.id, text, reply_markup=markup)


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

    url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=3"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        timings = data["data"]["timings"]
        date = data["data"]["date"]["readable"]

        text = f"""
🕌 <b>BUGUNGI NAMOZ VAQTLARI</b>

📍 <b>Joylashuv:</b> Siz yuborgan lokatsiya
📅 <b>Sana:</b> {date}

🌅 <b>Bomdod:</b> {timings["Fajr"]}
🌄 <b>Quyosh:</b> {timings["Sunrise"]}
🕛 <b>Peshin:</b> {timings["Dhuhr"]}
🌇 <b>Asr:</b> {timings["Asr"]}
🌆 <b>Shom:</b> {timings["Maghrib"]}
🌙 <b>Xufton:</b> {timings["Isha"]}

━━━━━━━━━━━━━━

📖 <b>QUR'ONDAN OYAT</b>

<b>"Albatta, namoz mo‘minlarga vaqtida farz qilingandir."</b>

<b>An-Niso surasi, 103-oyat</b>

🤲 Alloh namozlaringizni qabul qilsin.
"""

        bot.send_message(
            message.chat.id,
            text,
            parse_mode="HTML"
        )

    except Exception:
        bot.send_message(
            message.chat.id,
            "❌ Kechirasiz, namoz vaqtlarini olishda xatolik yuz berdi. Iltimos, qayta urinib ko‘ring."
        )


def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling(skip_pending=True)
