import os
import threading
import requests
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


QURAN_QUOTES = [
    {
        "text": "Albatta, namoz mo‘minlarga vaqtida farz qilingandir.",
        "source": "An-Niso surasi, 103-oyat"
    },
    {
        "text": "Namozlarni va ayniqsa o‘rta namozni saqlanglar.",
        "source": "Baqara surasi, 238-oyat"
    },
    {
        "text": "Meni zikr qilish uchun namozni to‘kis ado et.",
        "source": "Toha surasi, 14-oyat"
    },
    {
        "text": "Albatta, namoz fahsh va munkar ishlardan qaytaradi.",
        "source": "Ankabut surasi, 45-oyat"
    },
    {
        "text": "Robbingizdan yordamni sabr va namoz bilan so‘ranglar.",
        "source": "Baqara surasi, 45-oyat"
    }
]


@app.route("/")
def home():
    return "IslamTimeWorldBot is running!"


def get_location_name(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "accept-language": "en"
        }
        headers = {
            "User-Agent": "IslamTimeWorldBot/1.0"
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        address = data.get("address", {})

        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or address.get("county")
            or "Aniqlanmagan shahar"
        )

        country = address.get("country", "")

        if country:
            return f"{city}, {country}"

        return city

    except Exception:
        return "Siz yuborgan lokatsiya"


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

    try:
        prayer_url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=2"
        response = requests.get(prayer_url, timeout=10)
        data = response.json()

        timings = data["data"]["timings"]
        date = data["data"]["date"]["readable"]
        timezone_name = data["data"]["meta"]["timezone"]

        location_name = get_location_name(lat, lon)

        tz = ZoneInfo(timezone_name)
        now = datetime.now(tz)

        prayers = [
            ("Bomdod", "🌅", timings["Fajr"]),
            ("Peshin", "🕛", timings["Dhuhr"]),
            ("Asr", "🌇", timings["Asr"]),
            ("Shom", "🌆", timings["Maghrib"]),
            ("Xufton", "🌙", timings["Isha"]),
        ]

        next_prayer_name = "Bomdod"
        next_prayer_emoji = "🌅"
        time_left_text = ""

        for name, emoji, prayer_time in prayers:
            hour, minute = map(int, prayer_time.split(":")[:2])
            prayer_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if prayer_datetime > now:
                diff = prayer_datetime - now
                hours = diff.seconds // 3600
                minutes = (diff.seconds % 3600) // 60

                next_prayer_name = name
                next_prayer_emoji = emoji
                time_left_text = f"{hours} soat {minutes} daqiqadan so‘ng"
                break

        if time_left_text == "":
            hour, minute = map(int, timings["Fajr"].split(":")[:2])
            prayer_datetime = (now + timedelta(days=1)).replace(
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0
            )
            diff = prayer_datetime - now
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            time_left_text = f"{hours} soat {minutes} daqiqadan so‘ng"

        quote = random.choice(QURAN_QUOTES)

        text = f"""
🕌 <b>BUGUNGI NAMOZ VAQTLARI</b>

📍 <b>{location_name}</b>
📅 <b>{date}</b>

🌅 <b>Bomdod:</b> {timings["Fajr"]}
🌄 <b>Quyosh:</b> {timings["Sunrise"]}
🕛 <b>Peshin:</b> {timings["Dhuhr"]}
🌇 <b>Asr:</b> {timings["Asr"]}
🌆 <b>Shom:</b> {timings["Maghrib"]}
🌙 <b>Xufton:</b> {timings["Isha"]}

⏳ <b>Keyingi namoz:</b>
{next_prayer_emoji} <b>{next_prayer_name}</b> — {time_left_text}

━━━━━━━━━━━━━━

📖 <b>QUR'ONDAN OYAT</b>

<b>"{quote["text"]}"</b>

<b>{quote["source"]}</b>

🤲 Alloh namozlaringizni qabul qilsin.
"""

        bot.send_message(
            message.chat.id,
            text,
            parse_mode="HTML"
        )

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Kechirasiz, namoz vaqtlarini olishda xatolik yuz berdi.\n\nXato: {e}"
        )


@bot.message_handler(func=lambda message: message.text == "🧭 Qibla")
def qibla(message):
    bot.send_message(message.chat.id, "🧭 Qibla moduli keyingi bosqichda qo‘shiladi.")


@bot.message_handler(func=lambda message: message.text == "📍 Yaqin masjidlar")
def nearby_mosques(message):
    bot.send_message(message.chat.id, "📍 Yaqin masjidlar moduli keyingi bosqichda qo‘shiladi.")


@bot.message_handler(func=lambda message: message.text == "📖 Qur'on")
def quran(message):
    bot.send_message(message.chat.id, "📖 Qur'on moduli keyingi bosqichda qo‘shiladi.")


@bot.message_handler(func=lambda message: message.text == "📚 Hadislar")
def hadith(message):
    bot.send_message(message.chat.id, "📚 Hadislar moduli keyingi bosqichda qo‘shiladi.")


@bot.message_handler(func=lambda message: message.text == "⚙️ Sozlamalar")
def settings(message):
    bot.send_message(message.chat.id, "⚙️ Sozlamalar moduli keyingi bosqichda qo‘shiladi.")


def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling(skip_pending=True)
