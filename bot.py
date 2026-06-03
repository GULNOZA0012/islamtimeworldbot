import os
import threading
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


QURAN_QUOTES = [
    {"text": "Albatta, namoz mo‘minlarga vaqtida farz qilingandir.", "source": "An-Niso, 103-oyat", "note": "Qisqa mazmun"},
    {"text": "Namozlarni va ayniqsa o‘rta namozni saqlanglar.", "source": "Baqara, 238-oyat", "note": "Qisqa mazmun"},
    {"text": "Meni zikr qilish uchun namozni to‘kis ado et.", "source": "Toha, 14-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, namoz fahsh va munkar ishlardan qaytaradi.", "source": "Ankabut, 45-oyat", "note": "Qisqa mazmun"},
    {"text": "Robbingizdan yordamni sabr va namoz bilan so‘ranglar.", "source": "Baqara, 45-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, Alloh sabr qiluvchilar bilan birgadir.", "source": "Baqara, 153-oyat", "note": "Qisqa mazmun"},
    {"text": "Alloh taqvodorlarni sevadi.", "source": "Oli Imron, 76-oyat", "note": "Qisqa mazmun"},
    {"text": "Alloh tavba qiluvchilarni sevadi.", "source": "Baqara, 222-oyat", "note": "Qisqa mazmun"},
    {"text": "Meni eslanglar, Men ham sizlarni eslayman.", "source": "Baqara, 152-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, Alloh yaxshilik qiluvchilarni sevadi.", "source": "Baqara, 195-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, qiyinchilik bilan birga yengillik bordir.", "source": "Sharh, 6-oyat", "note": "Qisqa mazmun"},
    {"text": "Faqat Allohni zikr qilish bilan qalblar taskin topadi.", "source": "Ra'd, 28-oyat", "note": "Qisqa mazmun"},
    {"text": "Kim Allohga tavakkal qilsa, U unga kifoya qiladi.", "source": "Taloq, 3-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, Alloh adolatni va yaxshilikni buyuradi.", "source": "Nahl, 90-oyat", "note": "Qisqa mazmun"},
    {"text": "Alloh isrof qiluvchilarni sevmaydi.", "source": "A'rof, 31-oyat", "note": "Qisqa mazmun"},
    {"text": "Alloh sabr qiluvchilarning ajrini zoye qilmaydi.", "source": "Hud, 115-oyat", "note": "Qisqa mazmun"},
    {"text": "Rahmatim har narsani qamrab olgandir.", "source": "A'rof, 156-oyat", "note": "Qisqa mazmun"},
    {"text": "Yaxshilik qilinglar, shoyad najot topsangizlar.", "source": "Haj, 77-oyat", "note": "Qisqa mazmun"},
    {"text": "Duo qilinglar, Men ijobat qilaman.", "source": "G'ofir, 60-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, Alloh bilan ahd qilganlarga ajr bordir.", "source": "Fath, 10-oyat", "note": "Qisqa mazmun"},
    {"text": "Alloh sizlar uchun yengillikni xohlaydi.", "source": "Baqara, 185-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, Alloh zulm qilmaydi.", "source": "Yunus, 44-oyat", "note": "Qisqa mazmun"},
    {"text": "Har bir jon o‘limni totuvchidir.", "source": "Oli Imron, 185-oyat", "note": "Qisqa mazmun"},
    {"text": "Yaxshilik va taqvoda hamkorlik qilinglar.", "source": "Moida, 2-oyat", "note": "Qisqa mazmun"},
    {"text": "Alloh bilan birga bo‘linglar.", "source": "Tavba, 119-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, Alloh shukr qiluvchilarni mukofotlaydi.", "source": "Oli Imron, 144-oyat", "note": "Qisqa mazmun"},
    {"text": "Kim bir yaxshilik qilsa, o‘n barobar mukofot oladi.", "source": "An'om, 160-oyat", "note": "Qisqa mazmun"},
    {"text": "Allohning rahmatidan noumid bo‘lmanglar.", "source": "Zumar, 53-oyat", "note": "Qisqa mazmun"},
    {"text": "Rabbingiz mag‘firati tomon shoshilinglar.", "source": "Oli Imron, 133-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, Alloh mo‘minlarning do‘stidir.", "source": "Oli Imron, 68-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, Alloh bilan bo‘lganlar g‘olib bo‘ladilar.", "source": "Moida, 56-oyat", "note": "Qisqa mazmun"},
]


HADITH_QUOTES = [
    {"text": "Kim bomdod namozini o‘qisa, Allohning himoyasida bo‘ladi.", "source": "Sahih Muslim, 657a"},
    {"text": "Amallar niyatlarga bog‘liqdir.", "source": "Sahih Buxoriy, 1"},
    {"text": "Musulmon — boshqa musulmonlar uning tili va qo‘lidan omonda bo‘lgan kishidir.", "source": "Sahih Buxoriy, 10"},
    {"text": "Sizlardan hech biringiz o‘zi uchun yaxshi ko‘rgan narsani birodari uchun ham yaxshi ko‘rmaguncha to‘liq mo‘min bo‘la olmaydi.", "source": "Sahih Buxoriy, 13"},
    {"text": "Kim Allohga va oxirat kuniga iymon keltirgan bo‘lsa, yaxshi gapirsin yoki sukut qilsin.", "source": "Sahih Buxoriy, 6018"},
    {"text": "Poklik iymonning yarmidir.", "source": "Sahih Muslim, 223"},
    {"text": "Namoz nurdir.", "source": "Sahih Muslim, 223"},
    {"text": "Sabr ziyodir.", "source": "Sahih Muslim, 223"},
    {"text": "Qur’on sening foydangga yoki zararingga hujjat bo‘ladi.", "source": "Sahih Muslim, 223"},
    {"text": "Sizlarning eng yaxshilaringiz Qur’onni o‘rganib, uni boshqalarga o‘rgatganlaringizdir.", "source": "Sahih Buxoriy, 5027"},
    {"text": "Jamoat bilan o‘qilgan namoz yolg‘iz o‘qilgan namozdan yigirma yetti daraja afzaldir.", "source": "Sahih Buxoriy, 645"},
    {"text": "Rahm qilmagan kishiga rahm qilinmaydi.", "source": "Sahih Buxoriy, 5997"},
    {"text": "Alloh go‘zaldir va go‘zallikni sevadi.", "source": "Sahih Muslim, 91a"},
    {"text": "Alloh mehribon va yumshoqlikni sevadi.", "source": "Sahih Muslim, 2593"},
    {"text": "Alloh sizlarning suratlaringizga va mol-dunyolaringizga emas, qalblaringiz va amallaringizga qaraydi.", "source": "Sahih Muslim, 2564"},
    {"text": "Halol aniq, harom ham aniqdir.", "source": "Sahih Buxoriy, 52"},
    {"text": "Musulmon musulmonning birodaridir.", "source": "Sahih Buxoriy, 2442"},
    {"text": "Kim birodarining hojatini chiqarsa, Alloh uning hojatini chiqaradi.", "source": "Sahih Buxoriy, 2442"},
    {"text": "Kim musulmonning bir g‘amini ketkazsa, Alloh qiyomat kuni uning g‘amlaridan birini ketkazadi.", "source": "Sahih Buxoriy, 2442"},
    {"text": "Kim bir musulmonning aybini yopsa, Alloh qiyomat kuni uning aybini yopadi.", "source": "Sahih Buxoriy, 2442"},
    {"text": "Kim ilm izlash yo‘liga kirsa, Alloh unga jannat yo‘lini oson qiladi.", "source": "Sahih Muslim, 2699"},
    {"text": "Kim bir mo‘minning dunyo g‘amlaridan birini yengillatsa, Alloh uning qiyomat kunidagi g‘amlaridan birini yengillatadi.", "source": "Sahih Muslim, 2699"},
    {"text": "Kim qiynalgan kishiga yengillik qilsa, Alloh unga dunyo va oxiratda yengillik qiladi.", "source": "Sahih Muslim, 2699"},
    {"text": "Alloh banda birodariga yordam berar ekan, bandaga yordam berishda davom etadi.", "source": "Sahih Muslim, 2699"},
    {"text": "Qarindoshlik aloqasini bog‘lagan kishining rizqi kengayadi va umri barakali bo‘ladi.", "source": "Sahih Buxoriy, 5986"},
    {"text": "Kim menga ikki jag‘i orasidagi narsani va ikki oyog‘i orasidagi narsani kafolat qilsa, men unga jannatni kafolat qilaman.", "source": "Sahih Buxoriy, 6474"},
    {"text": "Allohga eng sevimli amal oz bo‘lsa ham davomli bo‘lgan amaldir.", "source": "Sahih Buxoriy, 6464"},
    {"text": "Mo‘minning ishi ajablanarlidir: uning har bir holatida yaxshilik bor.", "source": "Sahih Muslim, 2999"},
    {"text": "Kuchli mo‘min Allohga zaif mo‘mindan ko‘ra yaxshiroq va suyukliroqdir.", "source": "Sahih Muslim, 2664"},
    {"text": "Haqiqiy kuchli kishi kurashda yenggan emas, g‘azab paytida o‘zini tutgan kishidir.", "source": "Sahih Buxoriy, 6114"},
    {"text": "Ikki kalima bor: tilga yengil, tarozida og‘ir va Rahmonga suyuklidir.", "source": "Sahih Buxoriy, 6682; Sahih Muslim, 2694"},
]


ALLAH_NAMES = [
{"arabic":"الرَّحْمٰنُ","latin":"Ar-Rahman","meaning":"Cheksiz mehribon, rahmati barcha maxluqotlarni qamrab olgan Zot.","zikr":"Ya Rahman"},
{"arabic":"الرَّحِيمُ","latin":"Ar-Rahim","meaning":"Bandalariga nihoyatda rahm qiluvchi Zot.","zikr":"Ya Rahim"},
{"arabic":"الْمَلِكُ","latin":"Al-Malik","meaning":"Barcha olamlarning haqiqiy Podshohi.","zikr":"Ya Malik"},
{"arabic":"الْقُدُّوسُ","latin":"Al-Quddus","meaning":"Har qanday nuqsondan pok Zot.","zikr":"Ya Quddus"},
{"arabic":"السَّلَامُ","latin":"As-Salam","meaning":"Tinchlik va omonlik beruvchi Zot.","zikr":"Ya Salam"},
{"arabic":"الْمُؤْمِنُ","latin":"Al-Mu'min","meaning":"Omonlik va ishonch beruvchi Zot.","zikr":"Ya Mu'min"},
{"arabic":"الْمُهَيْمِنُ","latin":"Al-Muhaymin","meaning":"Har narsani kuzatib turuvchi Zot.","zikr":"Ya Muhaymin"},
{"arabic":"الْعَزِيزُ","latin":"Al-Aziz","meaning":"Mutlaq qudrat egasi.","zikr":"Ya Aziz"},
{"arabic":"الْجَبَّارُ","latin":"Al-Jabbar","meaning":"Barcha ishlarni irodasi bilan amalga oshiruvchi Zot.","zikr":"Ya Jabbar"},
{"arabic":"الْمُتَكَبِّرُ","latin":"Al-Mutakabbir","meaning":"Ulug‘lik va buyuklik egasi.","zikr":"Ya Mutakabbir"},
{"arabic":"الْخَالِقُ","latin":"Al-Khaliq","meaning":"Yaratuvchi Zot.","zikr":"Ya Khaliq"},
{"arabic":"الْبَارِئُ","latin":"Al-Bari","meaning":"Yo‘qdan bor qiluvchi Zot.","zikr":"Ya Bari"},
{"arabic":"الْمُصَوِّرُ","latin":"Al-Musawwir","meaning":"Har bir narsaga surat beruvchi Zot.","zikr":"Ya Musawwir"},
{"arabic":"الْغَفَّارُ","latin":"Al-Ghaffar","meaning":"Ko‘p mag‘firat qiluvchi Zot.","zikr":"Ya Ghaffar"},
{"arabic":"الْقَهَّارُ","latin":"Al-Qahhar","meaning":"Hammani bo‘ysundiruvchi Zot.","zikr":"Ya Qahhar"},
{"arabic":"الْوَهَّابُ","latin":"Al-Wahhab","meaning":"Cheksiz ne’matlar beruvchi Zot.","zikr":"Ya Wahhab"},
{"arabic":"الرَّزَّاقُ","latin":"Ar-Razzaq","meaning":"Rizq beruvchi Zot.","zikr":"Ya Razzaq"},
{"arabic":"الْفَتَّاحُ","latin":"Al-Fattah","meaning":"Yaxshilik eshiklarini ochuvchi Zot.","zikr":"Ya Fattah"},
{"arabic":"اَلْعَلِيمُ","latin":"Al-Alim","meaning":"Har narsani biluvchi Zot.","zikr":"Ya Alim"},
{"arabic":"الْقَابِضُ","latin":"Al-Qabid","meaning":"Rizqni toraytiruvchi Zot.","zikr":"Ya Qabid"},
{"arabic":"الْبَاسِطُ","latin":"Al-Basit","meaning":"Rizqni kengaytiruvchi Zot.","zikr":"Ya Basit"},
{"arabic":"الْخَافِضُ","latin":"Al-Khafid","meaning":"Pasaytiruvchi Zot.","zikr":"Ya Khafid"},
{"arabic":"الرَّافِعُ","latin":"Ar-Rafi","meaning":"Yuksaltiruvchi Zot.","zikr":"Ya Rafi"},
{"arabic":"الْمُعِزُّ","latin":"Al-Mu'izz","meaning":"Aziz qiluvchi Zot.","zikr":"Ya Mu'izz"},
{"arabic":"الْمُذِلُّ","latin":"Al-Muzill","meaning":"Xor qiluvchi Zot.","zikr":"Ya Muzill"}
]


user_name_index = {}

def names_menu():
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )
    markup.add("⬅️ Oldingi", "➡️ Keyingi")
    markup.add("🏠 Asosiy menyu")
    return markup


def show_allah_name(chat_id, index):
    name = ALLAH_NAMES[index]
    total = len(ALLAH_NAMES)

    text = f"""
🕋 <b>ASMAUL HUSNA</b>
<i>(99 go'zal ism)</i>

{index + 1}/{total}

<b>{name['arabic']}</b>

<b>{name['latin']}</b>

<b>Ma'nosi:</b>
{name['meaning']}

📿 <b>Zikr:</b>
{name['zikr']}

<b><i>🤲 Allohni zikr qiling va ma'nosini tafakkur qiling.</i></b>
"""

    bot.send_message(
        chat_id,
        text,
        parse_mode="HTML",
        reply_markup=names_menu()
    )


@app.route("/")
def home():
    return "IslamTimeWorldBot is running!"


def language_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "🇺🇿 O'zbekcha", "🇷🇺 Русский",
        "🇬🇧 English", "🇸🇦 العربية",
        "🇹🇷 Türkçe", "🇩🇪 Deutsch",
        "🇫🇷 Français", "🇪🇸 Español",
        "🇮🇹 Italiano", "🇰🇿 Қазақша",
        "🇰🇬 Кыргызча", "🇹🇯 Тоҷикӣ"
    )
    return markup


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "🕌 Namoz vaqtlari",
        "🧭 Qibla",
        "📍 Yaqin masjidlar",
        "📖 Qur'on",
        "📚 Hadislar",
        "📿 Duolar",
        "🕋 Allohning 99 Ismi",
        "📅 Hijriy taqvim",
        "⚙️ Sozlamalar"
    )
    return markup


def back_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("⬅️ Orqaga", "🏠 Asosiy menyu")
    return markup


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
    bot.send_message(
        message.chat.id,
        "🌍 Welcome to Islam Time World\n\nPlease select your language:",
        reply_markup=language_menu()
    )


@bot.message_handler(func=lambda message: message.text == "🇺🇿 O'zbekcha")
def uzbek(message):
    bot.send_message(
        message.chat.id,
        "🇺🇿 O'zbek tili tanlandi.\n\nKerakli bo'limni tanlang:",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda message: message.text == "🏠 Asosiy menyu")
def go_main_menu(message):
    bot.send_message(
        message.chat.id,
        "🏠 Asosiy menyu",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda message: message.text == "⬅️ Orqaga")
def go_back(message):
    bot.send_message(
        message.chat.id,
        "🏠 Asosiy menyu",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda message: message.text == "🕌 Namoz vaqtlari")
def prayer_times(message):
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=1,
        one_time_keyboard=True
    )

    location_btn = types.KeyboardButton(
        "📍 Lokatsiyani yuborish",
        request_location=True
    )

    markup.add(location_btn)
    markup.add("🏠 Asosiy menyu")

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
            prayer_datetime = now.replace(
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0
            )

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

        day_index = (now.day - 1) % 31
        quote = QURAN_QUOTES[day_index]
        hadith = HADITH_QUOTES[day_index]

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

📖 <b>BUGUNGI OYAT</b>

<b>"{quote["text"]}"</b>

<b>{quote["source"]}</b>
<i>({quote["note"]})</i>

━━━━━━━━━━━━━━

📿 <b>BUGUNGI HADIS</b>

<b>"{hadith["text"]}"</b>

<b>{hadith["source"]}</b>

🤲 Alloh namozlaringizni qabul qilsin.
"""

        bot.send_message(
            message.chat.id,
            text,
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Kechirasiz, namoz vaqtlarini olishda xatolik yuz berdi.\n\nXato: {e}",
            reply_markup=main_menu()
        )


@bot.message_handler(func=lambda message: message.text == "🧭 Qibla")
def qibla(message):
    bot.send_message(
        message.chat.id,
        "🧭 Qibla moduli keyingi bosqichda qo‘shiladi.",
        reply_markup=back_menu()
    )


@bot.message_handler(func=lambda message: message.text == "📍 Yaqin masjidlar")
def nearby_mosques(message):
    bot.send_message(
        message.chat.id,
        "📍 Yaqin masjidlar moduli keyingi bosqichda qo‘shiladi.",
        reply_markup=back_menu()
    )


@bot.message_handler(func=lambda message: message.text == "📖 Qur'on")
def quran(message):
    bot.send_message(
        message.chat.id,
        "📖 Qur'on moduli keyingi bosqichda qo‘shiladi.",
        reply_markup=back_menu()
    )


@bot.message_handler(func=lambda message: message.text == "📚 Hadislar")
def hadith(message):
    bot.send_message(
        message.chat.id,
        "📚 Hadislar moduli keyingi bosqichda qo‘shiladi.",
        reply_markup=back_menu()
    )


@bot.message_handler(func=lambda message: message.text == "📿 Duolar")
def duas(message):
    bot.send_message(
        message.chat.id,
        "📿 Duolar moduli keyingi bosqichda qo‘shiladi.",
        reply_markup=back_menu()
    )


@bot.message_handler(func=lambda message: message.text == "🕋 99 Ism")
def names_99(message):
    bot.send_message(
        message.chat.id,
        "🕋 Allohning 99 ismi moduli keyingi bosqichda qo‘shiladi.",
        reply_markup=back_menu()
    )


@bot.message_handler(func=lambda message: message.text == "📅 Hijriy taqvim")
def hijri_calendar(message):
    bot.send_message(
        message.chat.id,
        "📅 Hijriy taqvim moduli keyingi bosqichda qo‘shiladi.",
        reply_markup=back_menu()
    )


@bot.message_handler(func=lambda message: message.text == "⚙️ Sozlamalar")
def settings(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "🌐 Tilni o‘zgartirish",
        "🔔 Namoz eslatmalari",
        "📍 Lokatsiyani yangilash",
        "🎧 Qori tanlash",
        "🏠 Asosiy menyu"
    )

    bot.send_message(
        message.chat.id,
        "⚙️ Sozlamalar",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == "🌐 Tilni o‘zgartirish")
def change_language(message):
    bot.send_message(
        message.chat.id,
        "🌍 Tilni tanlang:",
        reply_markup=language_menu()
    )


@bot.message_handler(func=lambda message: message.text == "🔔 Namoz eslatmalari")
def prayer_reminders(message):
    bot.send_message(
        message.chat.id,
        "🔔 Namoz eslatmalari moduli keyingi bosqichda qo‘shiladi.",
        reply_markup=back_menu()
    )


@bot.message_handler(func=lambda message: message.text == "📍 Lokatsiyani yangilash")
def update_location(message):
    bot.send_message(
        message.chat.id,
        "📍 Lokatsiyani yangilash uchun 🕌 Namoz vaqtlari bo‘limiga kiring.",
        reply_markup=back_menu()
    )


@bot.message_handler(func=lambda message: message.text == "🎧 Qori tanlash")
def choose_qari(message):
    bot.send_message(
        message.chat.id,
        "🎧 Qori tanlash moduli keyingi bosqichda qo‘shiladi.",
        reply_markup=back_menu()
    )


@bot.message_handler(func=lambda message: True)
def unknown(message):
    bot.send_message(
        message.chat.id,
        "Iltimos, menyudan kerakli bo‘limni tanlang.",
        reply_markup=main_menu()
    )


def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling(
        timeout=60,
        long_polling_timeout=60,
        skip_pending=True
)
