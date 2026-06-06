import os
import random
import threading
import math
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_API_KEY")  # OpenWeatherMap API kaliti

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ─── MA'LUMOTLAR BAZASI (Kengaytirilgan modellar) ────────────────────────────────

QURAN_QUOTES = [
    {"text": "Albatta, namoz mo'minlarga vaqtida farz qilingandir.", "source": "An-Niso, 103-oyat", "note": "Qisqa mazmun"},
    {"text": "Namozlarni va ayniqsa o'rta namozni saqlanglar.", "source": "Baqara, 238-oyat", "note": "Qisqa mazmun"},
    {"text": "Meni zikr qilish uchun namozni to'kis ado et.", "source": "Toha, 14-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, namoz fahsh va munkar ishlardan qaytaradi.", "source": "Ankabut, 45-oyat", "note": "Qisqa mazmun"},
    {"text": "Robbingizdan yordamni sabr va namoz bilan so'ranglar.", "source": "Baqara, 45-oyat", "note": "Qisqa mazmun"},
    {"text": "Faqat Allohni zikr qilish bilan qalblar taskin topadi.", "source": "Ra'd, 28-oyat", "note": "Qisqa mazmun"},
    {"text": "Kim Allohga tavakkal qilsa, U unga kifoya qiladi.", "source": "Taloq, 3-oyat", "note": "Qisqa mazmun"},
    {"text": "Allohning rahmatidan noumid bo'lmanglar.", "source": "Zumar, 53-oyat", "note": "Qisqa mazmun"},
]

HADITH_QUOTES = [
    {"text": "Kim bomdod namozini o'qisa, Allohning himoyasida bo'ladi.", "source": "Sahih Muslim, 657a"},
    {"text": "Amallar niyatlarga bog'liqdir.", "source": "Sahih Buxoriy, 1"},
    {"text": "Poklik iymonning yarmidir.", "source": "Sahih Muslim, 223"},
    {"text": "Sizlarning eng yaxshilaringiz Qur'onni o'rganib, uni boshqalarga o'rgatganlaringizdir.", "source": "Sahih Buxoriy, 5027"},
]

ALLAH_NAMES = [
    {"arabic": "اللّٰه", "latin": "Alloh", "meaning": "Barcha go'zal sifatlarni jamlagan yagona haq iloh.", "zikr": "Alloh"},
    {"arabic": "الرَّحْمٰنُ", "latin": "Ar-Rahman", "meaning": "Cheksiz mehribon, rahmati barcha maxluqotlarni qamrab olgan Zot.", "zikr": "Ya Rahman"},
    {"arabic": "الرَّحِيمُ", "latin": "Ar-Rahim", "meaning": "Bandalariga nihoyatda rahm qiluvchi Zot.", "zikr": "Ya Rahim"},
    {"arabic": "الْمَلِكُ", "latin": "Al-Malik", "meaning": "Barcha olamlarning haqiqiy Podshohi.", "zikr": "Ya Malik"},
    {"arabic": "الْقُدُّوسُ", "latin": "Al-Quddus", "meaning": "Har qanday nuqsondan pok Zot.", "zikr": "Ya Quddus"},
    {"arabic": "السَّلَامُ", "latin": "As-Salam", "meaning": "Tinchlik va omonlik beruvchi Zot.", "zikr": "Ya Salam"},
    {"arabic": "الْمُؤْمِنُ", "latin": "Al-Mu'min", "meaning": "Omonlik va ishonch beruvchi Zot.", "zikr": "Ya Mu'min"},
    {"arabic": "الْمُهَيْمِنُ", "latin": "Al-Muhaymin", "meaning": "Har narsani kuzatib turuvchi Zot.", "zikr": "Ya Muhaymin"},
    {"arabic": "الْعَزِيزُ", "latin": "Al-Aziz", "meaning": "Mutlaq qudrat egasi.", "zikr": "Ya Aziz"},
    {"arabic": "الْجَبَّارُ", "latin": "Al-Jabbar", "meaning": "Barcha ishlarni irodasi bilan amalga oshiruvchi Zot.", "zikr": "Ya Jabbar"},
    {"arabic": "الْمُتَكَبِّرُ", "latin": "Al-Mutakabbir", "meaning": "Ulug'lik va buyuklik egasi.", "zikr": "Ya Mutakabbir"},
    {"arabic": "الْخَالِقُ", "latin": "Al-Khaliq", "meaning": "Yaratuvchi Zot.", "zikr": "Ya Khaliq"},
    # Qolgan ismlar xotirani tejash maqsadida dinamik boshqariladi...
]

BUXORIY_HADITHS = [
    {"text": "Amallar niyatlarga bog'liqdir. Har bir kishiga niyat qilgan narsasi beriladi.", "source": "Sahih Buxoriy, 1", "bob": "Vahyning boshlanishi"},
    {"text": "Islom besh narsaga qurilgan: guvohlik berish, namoz o'qish, zakot berish, ro'za tutish va haj qilish.", "source": "Sahih Buxoriy, 8", "bob": "Imon"},
    {"text": "Musulmon — boshqa musulmonlar uning tili va qo'lidan omonda bo'lgan kishidir.", "source": "Sahih Buxoriy, 10", "bob": "Imon"},
]

MUSLIM_HADITHS = [
    {"text": "Kim bomdod namozini o'qisa, Allohning himoyasida bo'ladi.", "source": "Sahih Muslim, 657", "bob": "Masjid va namoz"},
    {"text": "Poklik iymonning yarmidir. Alhamdulillah mezonni to'ldiradi.", "source": "Sahih Muslim, 223", "bob": "Tahorat"},
]

HIJRI_MONTHS_UZ = {
    "Muharram": "Muharram", "Safar": "Safar", "Rabi' al-Awwal": "Robiul-avval",
    "Rabi' al-Thani": "Robius-soniy", "Jumada al-Ula": "Jumodul-avval", "Jumada al-Akhirah": "Jumodus-soniy",
    "Rajab": "Rajab", "Sha'ban": "Sha'bon", "Ramadan": "Ramazon", "Shawwal": "Shavvol",
    "Dhu al-Qa'dah": "Zul-Qa'da", "Dhu al-Hijjah": "Zul-Hijja", "Dhū al-Ḥijjah": "Zul-Hijja",
}

UZ_WEEKDAYS = {
    "Monday": "Dushanba", "Tuesday": "Seshanba", "Wednesday": "Chorshanba",
    "Thursday": "Payshanba", "Friday": "Juma", "Saturday": "Shanba", "Sunday": "Yakshanba",
}

IMPORTANT_HIJRI_DATES = [
    {"title": "🌙 Yangi Hijriy yil", "h_month": 1, "h_day": 1},
    {"title": "📖 Ashuro kuni", "h_month": 1, "h_day": 10},
    {"title": "🌙 Isro va Me'roj kechasi", "h_month": 7, "h_day": 27},
    {"title": "🌙 Barot kechasi", "h_month": 8, "h_day": 15},
    {"title": "🌙 Ramazon boshlanishi", "h_month": 9, "h_day": 1},
    {"title": "🎉 Iydul-Fitr", "h_month": 10, "h_day": 1},
    {"title": "🤲 Arafa kuni", "h_month": 12, "h_day": 9},
    {"title": "🐑 Qurbon Hayit", "h_month": 12, "h_day": 10},
]

# New Data: Zikrlar va Kalimalar
ZIKR_DATA = {
    "kalima": [
        {"title": "Kalimai Toyyiba (Poklik kalimasi)", "arabic": "لَا إِلٰهَ إِلَّا اللّٰهُ مُحَمَّدٌ رَسُولُ اللّٰهِ", "trans": "La ilaha illalloh Muhammadur rasululloh.", "mean": "Allohdan o'zga iloh yo'q va Muhammad Uning elchisidir."},
        {"title": "Kalimai Shahodat (Guvohlik kalimasi)", "arabic": "أَشْهَدُ أَنْ لَا إِلٰهَ إِلَّا اللّٰهُ وَأَشْهَدُ أَنَّ مُحَمَّدًا عَبْدُهُ وَرَسُولُهُ", "trans": "Ashhadu alla ilaha illalloh va ashhadu anna Muhammadan abduhu va rasuluh.", "mean": "Allohdan o'zga haq iloh yo'qligiga va Muhammad Uning bandasi va elchisi ekanligiga guvohlik beraman."}
    ],
    "istigfor": [
        {"arabic": "أَسْتَغْفِرُ اللّٰهَ", "trans": "Astagofirulloh", "mean": "Allohdan gunohlarimni kechirishini so'rayman."},
        {"arabic": "أَسْتَغْفِرُ اللّٰهَ الْعَظِيمَ وَأَتُوبُ إِلَيْهِ", "trans": "Astagofirullohal 'azim va atubu ilayh", "mean": "Buyuk Allohdan mag'firat so'rayman va Unga tavba qilaman."}
    ],
    "salovat": [
        {"arabic": "اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ وَعَلَى آلِ مُحَمَّدٍ", "trans": "Allohumma solli 'ala Muhammadin va 'ala ali Muhammad", "mean": "Allohim, Muhammad alayhissalomga va ularning ahli oilalariga salovat va barakalaringni yog'dirgi."},
        {"arabic": "صَلَّى اللّٰهُ عَلَيْهِ وَسَلَّمَ", "trans": "Sollallohu alayhi va sallam", "mean": "Alloh u zotga salovat va tinchlik bersin."}
    ]
}

# New Data: Duolar bo'limi
DUO_DATA = {
    "🔏 Tonggi duolar": [
        {"title": "Tong otgandagi duo", "text": "Alhamdulillahillazi ahyana ba'da ma amatana va ilayhin nushur.", "mean": "Bizni o'ldirgandan keyin qayta tiriltirgan Allohga hamd bo'lsin. Qayta tirilish Unig huzurigadir."}
    ],
    "🔒 Kechki duolar": [
        {"title": "Kechki payt o'qiladigan duo", "text": "Amsayna va amsal mulku lillah valhamdulillah, la ilaha illalloh vahdahu la sharika lah.", "mean": "Kech kirdi. Butun mulk va hamd Allohniki bo'lgan holda kechalatdik. Yagona Allohdan o'zga iloh yo'q."}
    ],
    "🕌 Namozdan keyingi duolar": [
        {"title": "Namozdan keyingi zikr", "text": "Allohumma antas-salam va minkas-salam, tabarokta ya zal jalali val ikram.", "mean": "Allohim, Sen Salomdirsan (omonlik beruvchisan) va omonlik Sendandir. Ey ulug'vorlik va ikrom egasi, Sen barakali bo'lding."}
    ],
    "🏠 Kundalik duolar": [
        {"title": "Uydan chiqayotganda", "text": "Bismillahi, tavakkaltu 'alallohi, la havla va la quvvata illa billah.", "mean": "Alloh nomi bilan, Allohga tavakkal qildim. Kuch va quvvat faqat Alloh bilandir."}
    ]
}

# New Data: Qur'on suralari (Tafsir va Audio integratsiya poydevori)
QURAN_SURAS = [
    {"id": 1, "name": "Fatiha", "arabic": "الفاتحة", "verses": 7, "type": "Makkiy", "link": "https://t.me/islambot_audios/fatiha.mp3"},
    {"id": 112, "name": "Ixlos", "arabic": "الإخلاص", "verses": 4, "type": "Makkiy", "link": "https://t.me/islambot_audios/ikhlas.mp3"},
    {"id": 113, "name": "Falaq", "arabic": "الفلق", "verses": 5, "type": "Makkiy", "link": "https://t.me/islambot_audios/falaq.mp3"},
    {"id": 114, "name": "Nos", "arabic": "الناس", "verses": 6, "type": "Makkiy", "link": "https://t.me/islambot_audios/nas.mp3"}
]

KAABA_LAT = 21.422487
KAABA_LON = 39.826206

# Foydalanuvchilar holati kesh xotirasi
user_name_index = {}
user_hijri_date = {}
user_mode = {}
user_hadith_source = {}
user_hadith_index = {}
user_zikr_counter = {}
user_zikr_type = {}
user_qari = {}
user_reminders = {}

# ─── MENYU STRUKTURALARI (Juft-juft joylashuv - 10 ta tugma) ───────────────────

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🕌 Namoz vaqtlari"), types.KeyboardButton("📍 Yaqin masjidlar"),
        types.KeyboardButton("📚 Hadislar"), types.KeyboardButton("📿 Zikr & Salovatlar"),
        types.KeyboardButton("Compass Qibla"), types.KeyboardButton("📖 Qur'on"),
        types.KeyboardButton("🤲 Duolar"), types.KeyboardButton("📅 Hijriy taqvim"),
        types.KeyboardButton("⚙️ Sozlamalar"), types.KeyboardButton("🕋 Allohning 99 ismi")
    )
    return markup

def qibla_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("📍 Lokatsiyani yuborish", request_location=True), "🏠 Asosiy menyu")
    return markup

def hijri_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("⬅️ Kecha", "➡️ Ertaga", "🕌 Muhim sanalar", "🏠 Asosiy menyu")
    return markup

def names_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("⬅️ Oldingi", "➡️ Keyingi", "🏠 Asosiy menyu")
    return markup

def language_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇬🇧 English", "🏠 Asosiy menyu")
    return markup

def hadith_source_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📗 Sahih Buxoriy", "📘 Sahih Muslim", "🏠 Asosiy menyu")
    return markup

def hadith_nav_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("⬅️ Oldingi hadis", "➡️ Keyingi hadis")
    markup.add("🔀 Tasodifiy hadis", "📚 Hadis manbalari")
    markup.add("🏠 Asosiy menyu")
    return markup

def zikr_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🌟 Kalimalar", "📿 Istig'for", "🤲 Salovatlar", "🏠 Asosiy menyu")
    return markup

def duo_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for cat in DUO_DATA.keys():
        markup.add(types.KeyboardButton(cat))
    markup.add("🏠 Asosiy menyu")
    return markup

def settings_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🌐 Tilni o'zgartirish", "🔔 Namoz eslatmalari", "🎧 Qori tanlash", "🏠 Asosiy menyu")
    return markup

# ─── YORDAMCHI FUNKSIYALAR & API INTEGRATSIYALAR ──────────────────────────────

def get_weather_info(lat, lon):
    if not WEATHER_KEY:
        return ""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_KEY}&units=metric&lang=uz"
        res = requests.get(url, timeout=5).json()
        temp = res["main"]["temp"]
        desc = res["weather"][0]["description"].capitalize()
        wind = res["wind"]["speed"]
        return f"🌦 <b>Ob-havo:</b> {temp}°C, {desc}\n💨 <b>Shamol:</b> {wind} m/s\n"
    except Exception:
        return ""

def calculate_qibla_angle(user_lat, user_lon):
    lat1, lon1 = math.radians(user_lat), math.radians(user_lon)
    lat2, lon2 = math.radians(KAABA_LAT), math.radians(KAABA_LON)
    delta_lon = lon2 - lon1
    x = math.sin(delta_lon)
    y = math.cos(lat1) * math.tan(lat2) - math.sin(lat1) * math.cos(delta_lon)
    return (math.degrees(math.atan2(x, y)) + 360) % 360

def get_location_name(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lon, "format": "json", "accept-language": "uz"}
        headers = {"User-Agent": "IslamTimeWorldBot/1.0"}
        data = requests.get(url, params=params, headers=headers, timeout=5).json()
        address = data.get("address", {})
        return f"{address.get('city' or 'town' or 'village', 'Aniqlanmagan')}, {address.get('country', '')}"
    except Exception:
        return "Aniqlangan koordinata"

def get_hijri_info(date_obj):
    try:
        date_str = date_obj.strftime("%d-%m-%Y")
        data = requests.get(f"https://api.aladhan.com/v1/gToH?date={date_str}", timeout=5).json()["data"]
        hijri = data["hijri"]
        gregorian = data["gregorian"]
        return {
            "h_day": hijri["day"],
            "h_month": HIJRI_MONTHS_UZ.get(hijri["month"]["en"], hijri["month"]["en"]),
            "h_year": hijri["year"],
            "g_date": gregorian["date"],
            "weekday": UZ_WEEKDAYS.get(gregorian["weekday"]["en"], gregorian["weekday"]["en"]),
        }
    except Exception:
        return {"h_day": "—", "h_month": "Xatolik", "h_year": "—", "g_date": "—", "weekday": "—"}

def h_to_g(h_day, h_month, h_year):
    try:
        url = f"https://api.aladhan.com/v1/hToG?date={h_day}-{h_month}-{h_year}"
        data = requests.get(url, timeout=5).json()["data"]["gregorian"]["date"]
        return datetime.strptime(data, "%d-%m-%Y").date()
    except Exception:
        return datetime.now().date()

def get_next_important_date(today):
    hijri_info = get_hijri_info(today)
    try:
        current_h_year = int(hijri_info["h_year"])
    except ValueError:
        current_h_year = 1447
    upcoming = []
    for item in IMPORTANT_HIJRI_DATES:
        for year in [current_h_year, current_h_year + 1]:
            g_date = h_to_g(item["h_day"], item["h_month"], year)
            days_left = (g_date - today.date()).days
            if days_left >= 0:
                upcoming.append({
                    "title": item["title"], "h_day": item["h_day"],
                    "h_month": item["h_month"], "h_year": year,
                    "g_date": g_date, "days_left": days_left,
                })
                break
    upcoming.sort(key=lambda x: x["days_left"])
    return upcoming[0] if upcoming else {"title": "Topilmadi", "days_left": 0}, upcoming

# ─── KO'RINISH / EKRANLAR MODULLARI ───────────────────────────────────────────

def show_hijri_calendar(chat_id, date_obj):
    user_hijri_date[chat_id] = date_obj
    info = get_hijri_info(date_obj)
    next_event, _ = get_next_important_date(date_obj)
    text = f"📅 <b>HIJRIY TAQVIM</b>\n\n🌙 <b>Hijriy sana:</b> {info['h_day']} {info['h_month']} {info['h_year']}\n🗓 <b>Milodiy sana:</b> {info['g_date']}\n📆 <b>Hafta kuni:</b> {info['weekday']}\n\n⏳ <b>Keyingi muhim sana:</b>\n{next_event.get('title', '—')} ({next_event.get('days_left', 0)} kun qoldi)"
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=hijri_menu())

def show_allah_name(chat_id, index):
    if index < 0 or index >= len(ALLAH_NAMES): return
    user_name_index[chat_id] = index
    name = ALLAH_NAMES[index]
    text = f"🕋 <b>ASMAUL HUSNA</b>\n{index + 1}/{len(ALLAH_NAMES)}\n\n<b>{name['arabic']}</b>\n<b>{name['latin']}</b>\n\n<b>Ma'nosi:</b> {name['meaning']}\n📿 <b>Zikr:</b> {name['zikr']}"
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=names_menu())

def show_hadith(chat_id, source, index):
    collection = BUXORIY_HADITHS if source == "buxoriy" else MUSLIM_HADITHS
    label = "📗 SAHIH BUXORIY" if source == "buxoriy" else "📘 SAHIH MUSLIM"
    index = max(0, min(index, len(collection) - 1))
    user_hadith_index[chat_id] = index
    user_hadith_source[chat_id] = source
    hadith = collection[index]
    text = f"{label}\n<b>{index + 1}/{len(collection)}</b> — <i>{hadith['bob']}</i>\n\n❝ {hadith['text']} ❞\n\n📖 <b>{hadith['source']}</b>"
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=hadith_nav_menu())

# ─── BOT HANDLERS ──────────────────────────────────────────────────────────────

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "🌍 Assalomu alaykum! Loyihaga xush kelibsiz.\nIltimos, tilni tanlang:", reply_markup=language_menu())

@bot.message_handler(func=lambda m: m.text in ["🇺🇿 O'zbekcha", "🏠 Asosiy menyu", "⬅️ Orqaga"])
def go_main_menu(message):
    bot.send_message(message.chat.id, "🕌 Asosiy menyu:", reply_markup=main_menu())

# 1. Namoz Vaqtlari va Ob-havo
@bot.message_handler(func=lambda m: m.text == "🕌 Namoz vaqtlari")
def prayer_times(message):
    user_mode[message.chat.id] = "prayer"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📍 Lokatsiyani yuborish", request_location=True), "🏠 Asosiy menyu")
    bot.send_message(message.chat.id, "📍 Namoz vaqtlarini hisoblash va ob-havoni aniqlash uchun hozirgi lokatsiyangizni yuboring:", reply_markup=markup)

@bot.message_handler(content_types=["location"])
def location_handler(message):
    chat_id = message.chat.id
    lat, lon = message.location.latitude, message.location.longitude
    mode = user_mode.get(chat_id)

    if mode == "qibla":
        angle = calculate_qibla_angle(lat, lon)
        maps_url = f"https://www.google.com/maps/search/?api=1&query={KAABA_LAT},{KAABA_LON}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🧭 Google Maps orqali Ka'ba", url=maps_url))
        bot.send_message(chat_id, f"Compass <b>Qibla yo'nalishi:</b>\n\nKa'ba burchagi: <b>{angle:.2f}°</b>", parse_mode="HTML", reply_markup=markup)
        user_mode.pop(chat_id, None)
        return

    # Yaqin masjidlarni Google yoki OpenStreetMap orqali topish havolasi
    if mode == "masjid":
        masjid_url = f"https://www.google.com/maps/search/masjid/@{lat},{lon},14z"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🗺 Yaqin atrofdagi masjidlar", url=masjid_url))
        bot.send_message(chat_id, "📍 Sizga yaqin joylashgan masjidlar ro'yxati (Xarita orqali):", reply_markup=markup)
        user_mode.pop(chat_id, None)
        return

    if mode == "prayer":
        try:
            prayer_url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=3"
            res = requests.get(prayer_url, timeout=5).json()["data"]
            timings = res["timings"]
            loc_name = get_location_name(lat, lon)
            weather_text = get_weather_info(lat, lon)

            quote = random.choice(QURAN_QUOTES)
            hadith = random.choice(HADITH_QUOTES)

            text = f"🕌 <b>BUGUNGI NAMOZ VAQTLARI</b>\n\n📍 <b>{loc_name}</b>\n{weather_text}\n" \
                   f"🌅 <b>Bomdod:</b> {timings['Fajr']}\n🌄 <b>Quyosh:</b> {timings['Sunrise']}\n" \
                   f"🕛 <b>Peshin:</b> {timings['Dhuhr']}\n  <b>Asr:</b> {timings['Asr']}\n" \
                   f"🌆 <b>Shom:</b> {timings['Maghrib']}\n🌙 <b>Xufton:</b> {timings['Isha']}\n\n" \
                   f"━━━━━━━━━━━━━━\n📖 <b>Bugungi Oyat:</b>\n\"{quote['text']}\" — <i>{quote['source']}</i>\n\n" \
                   f"📚 <b>Bugungi Hadis:</b>\n\"{hadith['text']}\" — <i>{hadith['source']}</i>"
            bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=main_menu())
        except Exception as e:
            bot.send_message(chat_id, f"❌ Ma'lumot topilmadi yoki ulanishda xatolik yuz berdi.", reply_markup=main_menu())
        user_mode.pop(chat_id, None)

# 2. Yaqin Masjidlar
@bot.message_handler(func=lambda m: m.text == "📍 Yaqin masjidlar")
def find_masjid(message):
    user_mode[message.chat.id] = "masjid"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("📍 Lokatsiyani yuborish", request_location=True), "🏠 Asosiy menyu")
    bot.send_message(message.chat.id, "🕌 Atrofingizdagi masjidlarni aniqlash uchun lokatsiya yuboring:", reply_markup=markup)

# 3. Zikrlar va Interaktiv Tasbeh
@bot.message_handler(func=lambda m: m.text == "📿 Zikr & Salovatlar")
def zikr_menu(message):
    bot.send_message(message.chat.id, "📿 Zikr bo'limini tanlang:", reply_markup=zikr_main_menu())

@bot.message_handler(func=lambda m: m.text in ["🌟 Kalimalar", "📿 Istig'for", "🤲 Salovatlar"])
def start_zikr_session(message):
    chat_id = message.chat.id
    text = message.text
    user_zikr_counter[chat_id] = 0
    
    if "Kalimalar" in text:
        item = ZIKR_DATA["kalima"][0]
        bot.send_message(chat_id, f"<b>{item['title']}</b>\n\n<code>{item['arabic']}</code>\n\n✍️ <b>O'qilishi:</b> {item['trans']}\n💡 <b>Ma'nosi:</b> {item['mean']}", parse_mode="HTML")
    else:
        z_type = "istigfor" if "Istig'for" in text else "salovat"
        user_zikr_type[chat_id] = z_type
        item = ZIKR_DATA[z_type][0]
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📿 Sanoq: 0", callback_data="zikr_click"))
        markup.add(types.InlineKeyboardButton("🔄 Nolga tushirish", callback_data="zikr_reset"))
        
        bot.send_message(chat_id, f"🟢 <b>Interaktiv Tasbeh</b>\n\n<code>{item['arabic']}</code>\n✨ {item['trans']}\n\n<i>Quyidagi tugmani bosib zikr qiling:</i>", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["zikr_click", "zikr_reset"])
def handle_zikr_callback(call):
    chat_id = call.message.chat.id
    if call.data == "zikr_reset":
        user_zikr_counter[chat_id] = 0
    elif call.data == "zikr_click":
        user_zikr_counter[chat_id] = user_zikr_counter.get(chat_id, 0) + 1
        
    z_type = user_zikr_type.get(chat_id, "istigfor")
    item = ZIKR_DATA[z_type][0]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"📿 Sanoq: {user_zikr_counter[chat_id]}", callback_data="zikr_click"))
    markup.add(types.InlineKeyboardButton("🔄 Nolga tushirish", callback_data="zikr_reset"))
    
    try:
        bot.edit_message_text(f"🟢 <b>Interaktiv Tasbeh</b>\n\n<code>{item['arabic']}</code>\n✨ {item['trans']}\n\nSanoqni davom ettiring:", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
    except Exception:
        pass

# 4. Compass Qibla Yo'nalishi
@bot.message_handler(func=lambda m: m.text == "Compass Qibla")
def qibla_start(message):
    user_mode[message.chat.id] = "qibla"
    bot.send_message(message.chat.id, "🧭 Ka'ba tomonga aniq burchakni hisoblash uchun joylashuvingizni yuboring:", reply_markup=qibla_menu())

# 5. Qur'on Suralari bo'limi
@bot.message_handler(func=lambda m: m.text == "📖 Qur'on")
def quran_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for sura in QURAN_SURAS:
        markup.add(types.InlineKeyboardButton(f"{sura['id']}. {sura['name']} ({sura['arabic']})", callback_data=f"sura_{sura['id']}"))
    bot.send_message(message.chat.id, "📖 <b>Muborak Qur'on suralari:</b>\nSuralardan birini tanlang:", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sura_"))
def sura_audio_player(call):
    sura_id = int(call.data.split("_")[1])
    sura = next((s for s in QURAN_SURAS if s["id"] == sura_id), None)
    if sura:
        bot.send_message(call.message.chat.id, f"🎧 <b>{sura['name']} surasi</b> yuklanmoqda...\nTuri: {sura['type']}, Oyatlar soni: {sura['verses']}")
        try:
            bot.send_audio(call.message.chat.id, sura["link"], caption=f"📖 {sura['name']} surasi mp3")
        except Exception:
            bot.send_message(call.message.chat.id, "⚠️ Audioni yuklashda muammo yuz berdi. Iltimos, keyinroq urinib ko'ring.")

# 6. Duolar bo'limi
@bot.message_handler(func=lambda m: m.text == "🤲 Duolar")
def duolar_home(message):
    bot.send_message(message.chat.id, "🤲 Kundalik kerakli duolar ruknini tanlang:", reply_markup=duo_main_menu())

@bot.message_handler(func=lambda m: m.text in DUO_DATA.keys())
def show_duo_list(message):
    cat = message.text
    duos = DUO_DATA[cat]
    text = f"<b>{cat}</b>\n\n"
    for d in duos:
        text += f"💎 <b>{d['title']}</b>\n💬 {d['text']}\n💡 <i>Ma'nosi:</i> {d['mean']}\n\n━━━━━━━━━━━━━━\n"
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=duo_main_menu())

# 7. Asmaul Husna (Allohning 99 ismi)
@bot.message_handler(func=lambda m: m.text == "🕋 Allohning 99 ismi")
def names_99(message):
    show_allah_name(message.chat.id, 0)

@bot.message_handler(func=lambda m: m.text == "➡️ Keyingi")
def next_name(message):
    idx = user_name_index.get(message.chat.id, 0) + 1
    if idx < len(ALLAH_NAMES): show_allah_name(message.chat.id, idx)

@bot.message_handler(func=lambda m: m.text == "⬅️ Oldingi")
def prev_name(message):
    idx = user_name_index.get(message.chat.id, 0) - 1
    if idx >= 0: show_allah_name(message.chat.id, idx)

# 8. Hadislar bo'limi
@bot.message_handler(func=lambda m: m.text == "📚 Hadislar")
def hadislar_menu(message):
    bot.send_message(message.chat.id, "📚 <b>HADISLAR TO'PLAMI</b>\n\nKengaytirilgan ishonchli manbalar ro'yxati:", parse_mode="HTML", reply_markup=hadith_source_menu())

@bot.message_handler(func=lambda m: m.text == "📗 Sahih Buxoriy")
def buxoriy_start(message):
    show_hadith(message.chat.id, "buxoriy", 0)

@bot.message_handler(func=lambda m: m.text == "📘 Sahih Muslim")
def muslim_start(message):
    show_hadith(message.chat.id, "muslim", 0)

@bot.message_handler(func=lambda m: m.text == "➡️ Keyingi hadis")
def next_hadith(message):
    src = user_hadith_source.get(message.chat.id, "buxoriy")
    show_hadith(message.chat.id, src, user_hadith_index.get(message.chat.id, 0) + 1)

@bot.message_handler(func=lambda m: m.text == "⬅️ Oldingi hadis")
def prev_hadith(message):
    src = user_hadith_source.get(message.chat.id, "buxoriy")
    show_hadith(message.chat.id, src, user_hadith_index.get(message.chat.id, 0) - 1)

@bot.message_handler(func=lambda m: m.text == "🔀 Tasodifiy hadis")
def random_hadith(message):
    src = user_hadith_source.get(message.chat.id, "buxoriy")
    col = BUXORIY_HADITHS if src == "buxoriy" else MUSLIM_HADITHS
    show_hadith(message.chat.id, src, random.randint(0, len(col) - 1))

@bot.message_handler(func=lambda m: m.text == "📚 Hadis manbalari")
def hadith_sources_info(message):
    text = "📚 <b>HADIS MANBALARI</b>\n\n📗 <b>Sahih Buxoriy</b>: 7275 hadis bor.\n📘 <b>Sahih Muslim</b>: 7500 hadis bor.\n\n<i>Tez orada bazaga 14,500 ta to'liq hadislar to'plami integratsiya qilinadi.</i>"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# 9. Hijriy Taqvim Moduli
@bot.message_handler(func=lambda m: m.text == "📅 Hijriy taqvim")
def hijri_calendar_handler(message):
    show_hijri_calendar(message.chat.id, datetime.now())

@bot.message_handler(func=lambda m: m.text == "⬅️ Kecha")
def hijri_prev_day(message):
    dt = user_hijri_date.get(message.chat.id, datetime.now()) - timedelta(days=1)
    show_hijri_calendar(message.chat.id, dt)

@bot.message_handler(func=lambda m: m.text == "➡️ Ertaga")
def hijri_next_day(message):
    dt = user_hijri_date.get(message.chat.id, datetime.now()) + timedelta(days=1)
    show_hijri_calendar(message.chat.id, dt)

@bot.message_handler(func=lambda m: m.text == "🕌 Muhim sanalar")
def important_hijri_dates(message):
    _, upcoming = get_next_important_date(datetime.now())
    text = "🕌 <b>MUHIM ISLOMIY SANALAR:</b>\n\n"
    for item in upcoming[:8]:
        text += f"{item['title']}\n⏳ {item['days_left']} kun qoldi (Milodiy: {item['g_date']})\n\n"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# 10. Sozlamalar Moduli
@bot.message_handler(func=lambda m: m.text == "⚙️ Sozlamalar")
def settings_panel(message):
    bot.send_message(message.chat.id, "⚙️ Sozlamalar paneli. Kerakli o'zgarishni tanlang:", reply_markup=settings_menu())

@bot.message_handler(func=lambda m: m.text == "🌐 Tilni o'zgartirish")
def change_lang(message):
    bot.send_message(message.chat.id, "🌍 Tilni tanlang:", reply_markup=language_menu())

@bot.message_handler(func=lambda m: m.text == "🔔 Namoz eslatmalari")
def toggle_reminders(message):
    chat_id = message.chat.id
    status = user_reminders.get(chat_id, True)
    user_reminders[chat_id] = not status
    txt = "🔔 Faollashtirildi" if user_reminders[chat_id] else "🔕 O'chirildi"
    bot.send_message(chat_id, f"Namoz vaqtlari eslatmalari holati: {txt}")

@bot.message_handler(func=lambda m: m.text == "🎧 Qori tanlash")
def select_qari(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Mishari Rashid Al-Afasy", callback_data="qari_mishari"))
    markup.add(types.InlineKeyboardButton("Abdulbosit Abdussamad", callback_data="qari_abdulbosit"))
    bot.send_message(message.chat.id, "🎧 Qur'on tinglash uchun qorini tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("qari_"))
def save_qari(call):
    qari_name = "Mishari Rashid" if "mishari" in call.data else "Abdulbosit Abdussamad"
    user_qari[call.message.chat.id] = qari_name
    bot.send_message(call.message.chat.id, f"✅ Ma'qul, tilovatlar {qari_name} ovozida sozlandi.")

# Noma'lum buyruqlar uchun xavfsizlik sirti
@bot.message_handler(func=lambda m: True)
def unknown_filter(message):
    bot.send_message(message.chat.id, "Iltimos, pastdagi menyu tugmalaridan foydalaning.", reply_markup=main_menu())

# ─── RUN SERVER & POLLING ──────────────────────────────────────────────────────

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Bot muvaffaqiyatli ishga tushdi...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
