# ═══════════════════════════════════════════════════════════════
#  ISLAM TIME WORLD BOT  —  v2.1 (mukammal versiya)
#  Namoz vaqtlari • Qibla • Masjidlar • Qur'on • Hadislar
#  Duolar • Zikr • 99 ism • Hijriy taqvim • Sozlamalar
# ═══════════════════════════════════════════════════════════════
import os
import math
import random
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

# ═══════════════════════════════════════════════════════════════
#  MA'LUMOTLAR BAZASI
# ═══════════════════════════════════════════════════════════════
KAABA_LAT = 21.422487
KAABA_LON = 39.826206

HIJRI_MONTHS_UZ = {
    "Muharram": "Muharram", "Safar": "Safar",
    "Rabi' al-Awwal": "Robiul-avval", "Rabi' al-Thani": "Robius-soniy",
    "Jumada al-Ula": "Jumodul-avval", "Jumada al-Akhirah": "Jumodus-soniy",
    "Rajab": "Rajab", "Sha'ban": "Sha'bon", "Ramadan": "Ramazon",
    "Shawwal": "Shavvol", "Dhu al-Qa'dah": "Zul-Qa'da",
    "Dhu al-Hijjah": "Zul-Hijja", "Dhū al-Ḥijjah": "Zul-Hijja",
}
UZ_WEEKDAYS = {
    "Monday": "Dushanba", "Tuesday": "Seshanba", "Wednesday": "Chorshanba",
    "Thursday": "Payshanba", "Friday": "Juma", "Saturday": "Shanba", "Sunday": "Yakshanba",
}
IMPORTANT_HIJRI_DATES = [
    {"title": "🌙 Yangi Hijriy yil",      "h_month": 1,  "h_day": 1},
    {"title": "📖 Ashuro kuni",            "h_month": 1,  "h_day": 10},
    {"title": "🌙 Isro va Me'roj kechasi", "h_month": 7,  "h_day": 27},
    {"title": "🌙 Barot kechasi",          "h_month": 8,  "h_day": 15},
    {"title": "🌙 Ramazon boshlanishi",    "h_month": 9,  "h_day": 1},
    {"title": "🎉 Iydul-Fitr",             "h_month": 10, "h_day": 1},
    {"title": "🤲 Arafa kuni",             "h_month": 12, "h_day": 9},
    {"title": "🐑 Qurbon Hayit",           "h_month": 12, "h_day": 10},
]

# ═══════════════════════════════════════════════════════════════
#  QURON OYATLARI (namoz vaqtida chiqadi)
# ═══════════════════════════════════════════════════════════════
QURAN_QUOTES = [
    {"text": "Albatta, namoz mo'minlarga vaqtida farz qilingandir.", "source": "An-Niso, 103"},
    {"text": "Namozlarni va ayniqsa o'rta namozni saqlanglar.", "source": "Baqara, 238"},
    {"text": "Meni zikr qilish uchun namozni to'kis ado et.", "source": "Toha, 14"},
    {"text": "Albatta, namoz fahsh va munkar ishlardan qaytaradi.", "source": "Ankabut, 45"},
    {"text": "Robbingizdan yordamni sabr va namoz bilan so'ranglar.", "source": "Baqara, 45"},
    {"text": "Faqat Allohni zikr qilish bilan qalblar taskin topadi.", "source": "Ra'd, 28"},
    {"text": "Kim Allohga tavakkal qilsa, U unga kifoya qiladi.", "source": "Taloq, 3"},
    {"text": "Allohning rahmatidan noumid bo'lmanglar.", "source": "Zumar, 53"},
    {"text": "Duo qilinglar, Men ijobat qilaman.", "source": "G'ofir, 60"},
    {"text": "Albatta, qiyinchilik bilan birga yengillik bordir.", "source": "Sharh, 6"},
]
HADITH_QUOTES = [
    {"text": "Kim bomdod namozini o'qisa, Allohning himoyasida bo'ladi.", "source": "Muslim, 657"},
    {"text": "Amallar niyatlarga bog'liqdir.", "source": "Buxoriy, 1"},
    {"text": "Poklik iymonning yarmidir.", "source": "Muslim, 223"},
    {"text": "Jamoat bilan o'qilgan namoz yolg'iz o'qilgandan 27 daraja afzal.", "source": "Buxoriy, 645"},
    {"text": "Allohga eng sevimli amal — oz bo'lsa ham davomli bo'lgan amaldir.", "source": "Buxoriy, 6464"},
]

# ═══════════════════════════════════════════════════════════════
#  ALLOHNING 99 ISMI (to'liq)
# ═══════════════════════════════════════════════════════════════
ALLAH_NAMES = [
    {"arabic":"اللّٰه","latin":"Alloh","meaning":"Barcha go'zal sifatlarni jamlagan yagona haq iloh.","zikr":"Alloh"},
    {"arabic":"الرَّحْمٰنُ","latin":"Ar-Rahman","meaning":"Cheksiz mehribon, rahmati barcha maxluqotlarni qamrab olgan Zot.","zikr":"Ya Rahman"},
    {"arabic":"الرَّحِيمُ","latin":"Ar-Rahim","meaning":"Bandalariga nihoyatda rahm qiluvchi Zot.","zikr":"Ya Rahim"},
    {"arabic":"الْمَلِكُ","latin":"Al-Malik","meaning":"Barcha olamlarning haqiqiy Podshohi.","zikr":"Ya Malik"},
    {"arabic":"الْقُدُّوسُ","latin":"Al-Quddus","meaning":"Har qanday nuqsondan pok Zot.","zikr":"Ya Quddus"},
    {"arabic":"السَّلَامُ","latin":"As-Salam","meaning":"Tinchlik va omonlik beruvchi Zot.","zikr":"Ya Salam"},
    {"arabic":"الْمُؤْمِنُ","latin":"Al-Mu'min","meaning":"Omonlik va ishonch beruvchi Zot.","zikr":"Ya Mu'min"},
    {"arabic":"الْمُهَيْمِنُ","latin":"Al-Muhaymin","meaning":"Har narsani kuzatib turuvchi Zot.","zikr":"Ya Muhaymin"},
    {"arabic":"الْعَزِيزُ","latin":"Al-Aziz","meaning":"Mutlaq qudrat egasi.","zikr":"Ya Aziz"},
    {"arabic":"الْجَبَّارُ","latin":"Al-Jabbar","meaning":"Barcha ishlarni irodasi bilan amalga oshiruvchi Zot.","zikr":"Ya Jabbar"},
    {"arabic":"الْمُتَكَبِّرُ","latin":"Al-Mutakabbir","meaning":"Ulug'lik va buyuklik egasi.","zikr":"Ya Mutakabbir"},
    {"arabic":"الْخَالِقُ","latin":"Al-Khaliq","meaning":"Yaratuvchi Zot.","zikr":"Ya Khaliq"},
    {"arabic":"الْبَارِئُ","latin":"Al-Bari","meaning":"Yo'qdan bor qiluvchi Zot.","zikr":"Ya Bari"},
    {"arabic":"الْمُصَوِّرُ","latin":"Al-Musawwir","meaning":"Har bir narsaga surat beruvchi Zot.","zikr":"Ya Musawwir"},
    {"arabic":"الْغَفَّارُ","latin":"Al-Ghaffar","meaning":"Ko'p mag'firat qiluvchi Zot.","zikr":"Ya Ghaffar"},
    {"arabic":"الْقَهَّارُ","latin":"Al-Qahhar","meaning":"Hammani bo'ysundiruvchi Zot.","zikr":"Ya Qahhar"},
    {"arabic":"الْوَهَّابُ","latin":"Al-Wahhab","meaning":"Cheksiz ne'matlar beruvchi Zot.","zikr":"Ya Wahhab"},
    {"arabic":"الرَّزَّاقُ","latin":"Ar-Razzaq","meaning":"Rizq beruvchi Zot.","zikr":"Ya Razzaq"},
    {"arabic":"الْفَتَّاحُ","latin":"Al-Fattah","meaning":"Yaxshilik eshiklarini ochuvchi Zot.","zikr":"Ya Fattah"},
    {"arabic":"اَلْعَلِيمُ","latin":"Al-Alim","meaning":"Har narsani biluvchi Zot.","zikr":"Ya Alim"},
    {"arabic":"الْقَابِضُ","latin":"Al-Qabid","meaning":"Rizqni toraytiruvchi Zot.","zikr":"Ya Qabid"},
    {"arabic":"الْبَاسِطُ","latin":"Al-Basit","meaning":"Rizqni kengaytiruvchi Zot.","zikr":"Ya Basit"},
    {"arabic":"الْخَافِضُ","latin":"Al-Khafid","meaning":"Pasaytiruvchi Zot.","zikr":"Ya Khafid"},
    {"arabic":"الرَّافِعُ","latin":"Ar-Rafi","meaning":"Yuksaltiruvchi Zot.","zikr":"Ya Rafi"},
    {"arabic":"الْمُعِزُّ","latin":"Al-Mu'izz","meaning":"Aziz qiluvchi Zot.","zikr":"Ya Mu'izz"},
    {"arabic":"الْمُذِلُّ","latin":"Al-Muzill","meaning":"Xor qiluvchi Zot.","zikr":"Ya Muzill"},
    {"arabic":"السَّمِيعُ","latin":"As-Sami","meaning":"Barcha narsani eshituvchi Zot.","zikr":"Ya Sami"},
    {"arabic":"الْبَصِيرُ","latin":"Al-Basir","meaning":"Barcha narsani ko'ruvchi Zot.","zikr":"Ya Basir"},
    {"arabic":"الْحَكَمُ","latin":"Al-Hakam","meaning":"Adolat bilan hukm qiluvchi Zot.","zikr":"Ya Hakam"},
    {"arabic":"الْعَدْلُ","latin":"Al-Adl","meaning":"Mutlaq adolat egasi.","zikr":"Ya Adl"},
    {"arabic":"اللَّطِيفُ","latin":"Al-Latif","meaning":"Bandalariga lutf ko'rsatuvchi Zot.","zikr":"Ya Latif"},
    {"arabic":"الْخَبِيرُ","latin":"Al-Khabir","meaning":"Har narsaning ichki sirlaridan xabardor Zot.","zikr":"Ya Khabir"},
    {"arabic":"الْحَلِيمُ","latin":"Al-Halim","meaning":"Shoshilmay jazo bermaydigan Zot.","zikr":"Ya Halim"},
    {"arabic":"الْعَظِيمُ","latin":"Al-Azim","meaning":"Buyuk va ulug' Zot.","zikr":"Ya Azim"},
    {"arabic":"الْغَفُورُ","latin":"Al-Ghafur","meaning":"Ko'p kechiruvchi Zot.","zikr":"Ya Ghafur"},
    {"arabic":"الشَّكُورُ","latin":"Ash-Shakur","meaning":"Oz amal uchun ham ko'p mukofot beruvchi Zot.","zikr":"Ya Shakur"},
    {"arabic":"الْعَلِيُّ","latin":"Al-Aliyy","meaning":"Eng oliy martaba egasi.","zikr":"Ya Aliyy"},
    {"arabic":"الْكَبِيرُ","latin":"Al-Kabir","meaning":"Eng buyuk Zot.","zikr":"Ya Kabir"},
    {"arabic":"الْحَفِيظُ","latin":"Al-Hafiz","meaning":"Asrovchi va saqlovchi Zot.","zikr":"Ya Hafiz"},
    {"arabic":"الْمُقِيتُ","latin":"Al-Muqit","meaning":"Barcha mavjudotlarga rizq yetkazuvchi Zot.","zikr":"Ya Muqit"},
    {"arabic":"الْحسِيبُ","latin":"Al-Hasib","meaning":"Hisob-kitob qiluvchi Zot.","zikr":"Ya Hasib"},
    {"arabic":"الْجَلِيلُ","latin":"Al-Jalil","meaning":"Ulug'vorlik egasi.","zikr":"Ya Jalil"},
    {"arabic":"الْكَرِيمُ","latin":"Al-Karim","meaning":"Saxovatli va karamli Zot.","zikr":"Ya Karim"},
    {"arabic":"الرَّقِيبُ","latin":"Ar-Raqib","meaning":"Har narsani kuzatib turuvchi Zot.","zikr":"Ya Raqib"},
    {"arabic":"الْمُجِيبُ","latin":"Al-Mujib","meaning":"Duolarga javob beruvchi Zot.","zikr":"Ya Mujib"},
    {"arabic":"الْوَاسِعُ","latin":"Al-Wasi","meaning":"Rahmati va ilmi keng Zot.","zikr":"Ya Wasi"},
    {"arabic":"الْحَكِيمُ","latin":"Al-Hakim","meaning":"Hikmat egasi Zot.","zikr":"Ya Hakim"},
    {"arabic":"الْوَدُودُ","latin":"Al-Wadud","meaning":"Bandalarini sevuvchi Zot.","zikr":"Ya Wadud"},
    {"arabic":"الْمَجِيدُ","latin":"Al-Majid","meaning":"Sharaf va ulug'lik egasi.","zikr":"Ya Majid"},
    {"arabic":"الْبَاعِثُ","latin":"Al-Baith","meaning":"Tirilitiruvchi Zot.","zikr":"Ya Baith"},
    {"arabic":"الشَّهِيدُ","latin":"Ash-Shahid","meaning":"Har narsaga guvoh Zot.","zikr":"Ya Shahid"},
    {"arabic":"الْحَقُّ","latin":"Al-Haqq","meaning":"Mutlaq Haqiqat Zot.","zikr":"Ya Haqq"},
    {"arabic":"الْوَكِيلُ","latin":"Al-Wakil","meaning":"Ishlarni boshqaruvchi vakil Zot.","zikr":"Ya Wakil"},
    {"arabic":"الْقَوِيُّ","latin":"Al-Qawiyy","meaning":"Cheksiz qudrat egasi.","zikr":"Ya Qawiyy"},
    {"arabic":"الْمَتِينُ","latin":"Al-Matin","meaning":"Juda mustahkam va qudratli Zot.","zikr":"Ya Matin"},
    {"arabic":"الْوَلِيُّ","latin":"Al-Waliyy","meaning":"Mo'minlarning do'sti va yordamchisi.","zikr":"Ya Waliyy"},
    {"arabic":"الْحَمِيدُ","latin":"Al-Hamid","meaning":"Hamd va maqtovga loyiq Zot.","zikr":"Ya Hamid"},
    {"arabic":"الْمُحْصِي","latin":"Al-Muhsi","meaning":"Har narsani sanab biluvchi Zot.","zikr":"Ya Muhsi"},
    {"arabic":"الْمُبْدِئُ","latin":"Al-Mubdi","meaning":"Yaratishni boshlovchi Zot.","zikr":"Ya Mubdi"},
    {"arabic":"الْمُعِيدُ","latin":"Al-Muid","meaning":"Qayta tiriltiruvchi Zot.","zikr":"Ya Muid"},
    {"arabic":"الْمُحْيِي","latin":"Al-Muhyi","meaning":"Hayot beruvchi Zot.","zikr":"Ya Muhyi"},
    {"arabic":"اَلْمُمِيتُ","latin":"Al-Mumit","meaning":"O'lim beruvchi Zot.","zikr":"Ya Mumit"},
    {"arabic":"الْحَيُّ","latin":"Al-Hayy","meaning":"Abadiy tirik Zot.","zikr":"Ya Hayy"},
    {"arabic":"الْقَيُّومُ","latin":"Al-Qayyum","meaning":"Borliqni tutib turuvchi Zot.","zikr":"Ya Qayyum"},
    {"arabic":"الْوَاجِدُ","latin":"Al-Wajid","meaning":"Istagan narsasini topuvchi Zot.","zikr":"Ya Wajid"},
    {"arabic":"اَلاَحَدُ","latin":"Al-Ahad","meaning":"Yakkayu yagona Zot.","zikr":"Ya Ahad"},
    {"arabic":"الْواحِدُ","latin":"Al-Wahid","meaning":"Yagona Zot.","zikr":"Ya Wahid"},
    {"arabic":"الصَّمَدُ","latin":"As-Samad","meaning":"Barcha muhtoj, O'zi hech kimga muhtoj bo'lmagan Zot.","zikr":"Ya Samad"},
    {"arabic":"الْقَادِرُ","latin":"Al-Qadir","meaning":"Har narsaga qodir Zot.","zikr":"Ya Qadir"},
    {"arabic":"الْمُقْتَدِرُ","latin":"Al-Muqtadir","meaning":"Cheksiz qudrat egasi.","zikr":"Ya Muqtadir"},
    {"arabic":"الْمُقَدِّمُ","latin":"Al-Muqaddim","meaning":"Oldinga suruvchi Zot.","zikr":"Ya Muqaddim"},
    {"arabic":"الْمُؤَخِّرُ","latin":"Al-Muakhkhir","meaning":"Orqaga qoldiruvchi Zot.","zikr":"Ya Muakhkhir"},
    {"arabic":"الأوَّلُ","latin":"Al-Awwal","meaning":"Avvalgi Zot, boshlanishsiz.","zikr":"Ya Awwal"},
    {"arabic":"الآخِرُ","latin":"Al-Akhir","meaning":"Oxirgi Zot, tugashsiz.","zikr":"Ya Akhir"},
    {"arabic":"الظَّاهِرُ","latin":"Az-Zahir","meaning":"Alomatlari bilan zohir bo'lgan Zot.","zikr":"Ya Zahir"},
    {"arabic":"الْبَاطِنُ","latin":"Al-Batin","meaning":"Yashirin narsalardan ham xabardor Zot.","zikr":"Ya Batin"},
    {"arabic":"الْوَالِي","latin":"Al-Wali","meaning":"Borliqni boshqaruvchi Zot.","zikr":"Ya Wali"},
    {"arabic":"الْمُتَعَالِي","latin":"Al-Muta'ali","meaning":"Har narsadan yuksak Zot.","zikr":"Ya Muta'ali"},
    {"arabic":"الْبَرُّ","latin":"Al-Barr","meaning":"Bandalariga yaxshilik qiluvchi Zot.","zikr":"Ya Barr"},
    {"arabic":"التَّوَّابُ","latin":"At-Tawwab","meaning":"Tavbalarni qabul qiluvchi Zot.","zikr":"Ya Tawwab"},
    {"arabic":"الْمُنْتَقِمُ","latin":"Al-Muntaqim","meaning":"Adolat bilan jazolovchi Zot.","zikr":"Ya Muntaqim"},
    {"arabic":"العَفُوُّ","latin":"Al-Afuww","meaning":"Kechiruvchi Zot.","zikr":"Ya Afuww"},
    {"arabic":"الرَّؤُوفُ","latin":"Ar-Ra'uf","meaning":"Nihoyatda mehribon Zot.","zikr":"Ya Ra'uf"},
    {"arabic":"مَالِكُ الْمُلْكِ","latin":"Malikul-Mulk","meaning":"Butun mulk egasi Zot.","zikr":"Ya Malikul-Mulk"},
    {"arabic":"ذُوالْجَلاَلِ وَالإكْرَامِ","latin":"Dhul-Jalali wal-Ikram","meaning":"Ulug'lik va karam egasi Zot.","zikr":"Ya Dhul-Jalali wal-Ikram"},
    {"arabic":"الْمُقْسِطُ","latin":"Al-Muqsit","meaning":"Adolat bilan hukm qiluvchi Zot.","zikr":"Ya Muqsit"},
    {"arabic":"الْجَامِعُ","latin":"Al-Jami","meaning":"Barcha mavjudotni jamlovchi Zot.","zikr":"Ya Jami"},
    {"arabic":"الْغَنِيُّ","latin":"Al-Ghani","meaning":"Hech kimga muhtoj bo'lmagan Zot.","zikr":"Ya Ghani"},
    {"arabic":"الْمُغْنِي","latin":"Al-Mughni","meaning":"Boy qiluvchi Zot.","zikr":"Ya Mughni"},
    {"arabic":"الْمَانِعُ","latin":"Al-Mani","meaning":"To'suvchi Zot.","zikr":"Ya Mani"},
    {"arabic":"الضَّارُّ","latin":"Ad-Darr","meaning":"Zarar yetkazishga qodir Zot.","zikr":"Ya Darr"},
    {"arabic":"النَّافِعُ","latin":"An-Nafi","meaning":"Foyda beruvchi Zot.","zikr":"Ya Nafi"},
    {"arabic":"النُّورُ","latin":"An-Nur","meaning":"Nur beruvchi Zot.","zikr":"Ya Nur"},
    {"arabic":"الْهَادِي","latin":"Al-Hadi","meaning":"Hidoyat beruvchi Zot.","zikr":"Ya Hadi"},
    {"arabic":"الْبَدِيعُ","latin":"Al-Badi","meaning":"O'xshashi yo'q yaratuvchi Zot.","zikr":"Ya Badi"},
    {"arabic":"الْبَاقِي","latin":"Al-Baqi","meaning":"Abadiy qoluvchi Zot.","zikr":"Ya Baqi"},
    {"arabic":"الْوَارِثُ","latin":"Al-Warith","meaning":"Barcha narsaning merosxo'ri Zot.","zikr":"Ya Warith"},
    {"arabic":"الرَّشِيدُ","latin":"Ar-Rashid","meaning":"To'g'ri yo'l ko'rsatuvchi Zot.","zikr":"Ya Rashid"},
    {"arabic":"الصَّبُورُ","latin":"As-Sabur","meaning":"Juda sabrli Zot.","zikr":"Ya Sabur"},
]

# ═══════════════════════════════════════════════════════════════
#  HADISLAR (bo'limlar bo'yicha)
# ═══════════════════════════════════════════════════════════════
HADITH_SECTIONS = {
    "odob":    {"label": "🌸 Odob-axloq",       "hadiths": [
        {"text": "Amallar niyatlarga bog'liqdir.", "source": "Buxoriy, 1"},
        {"text": "Haqiqiy kuchli kishi g'azab paytida o'zini tutgan kishidir.", "source": "Buxoriy, 6114"},
        {"text": "Hayoning hammasi yaxshilikdir.", "source": "Buxoriy, 6117"},
        {"text": "Alloh go'zaldir va go'zallikni sevadi.", "source": "Muslim, 91"},
        {"text": "Tabassum qilishingiz sadaqadir.", "source": "Buxoriy, 2989"},
        {"text": "Yaxshi so'z ham sadaqadir.", "source": "Buxoriy, 2989"},
        {"text": "Odamlarning eng yaxshisi — odamlarga eng foydali bo'lganidir.", "source": "Tabaroniy, 6026"},
        {"text": "Doim haqni gapiring — haqiqat yaxshilikka, yaxshilik jannatga olib boradi.", "source": "Muslim, 2607"},
        {"text": "Yolg'ondan saqlaning — yolg'on buzuqlikka, buzuqlik jahannamga olib boradi.", "source": "Muslim, 2607"},
        {"text": "Kishi sevgan odami bilan birga bo'ladi (oxiratda).", "source": "Buxoriy, 6169"},
        {"text": "Alloh mehribon va yumshoqlikni sevadi.", "source": "Muslim, 2593"},
        {"text": "Rahm qilmagan kishiga rahm qilinmaydi.", "source": "Buxoriy, 5997"},
    ]},
    "ota_ona": {"label": "👨‍👩‍👧 Ota-ona va oila", "hadiths": [
        {"text": "Eng katta gunoh — Allohga sherik qo'shish va ota-onaga oq bo'lish.", "source": "Buxoriy, 2654"},
        {"text": "Jannat onaning oyog'i ostidadir.", "source": "Nasaiy, 3104"},
        {"text": "Ota-onaning roziligida Allohning roziligi bor.", "source": "Tirmiziy, 1899"},
        {"text": "Rizq kengayishini istagan kishi qarindoshlik aloqasini bog'lasin.", "source": "Buxoriy, 5986"},
        {"text": "Eng yaxshi farzand — vafot etgan ota-onasi uchun duo qiladigan farzanddir.", "source": "Muslim, 1631"},
        {"text": "Ota-onaga yaxshilik qil — jannat ularning oyog'i ostidadir.", "source": "Nasaiy, 3104"},
        {"text": "Bir kishi ota-onasiga xizmat qilishini aytdi. Rasululloh: 'Bu jihod' — dedi.", "source": "Buxoriy, 3004"},
        {"text": "Alloh sizlarning suratlaringizga emas, qalblaringizga qaraydi.", "source": "Muslim, 2564"},
    ]},
    "ilm":     {"label": "📚 Ilm va hikmat",     "hadiths": [
        {"text": "Kim ilm izlash yo'liga kirsa, Alloh unga jannat yo'lini oson qiladi.", "source": "Muslim, 2699"},
        {"text": "Ilm o'rganish — har bir musulmonga farzdir.", "source": "Ibn Moja, 224"},
        {"text": "Sizlarning eng yaxshilaringiz Qur'onni o'rganib, boshqalarga o'rgatganlaringizdir.", "source": "Buxoriy, 5027"},
        {"text": "Alloh kimga yaxshilik qilmoqchi bo'lsa, uni dinda faqih qiladi.", "source": "Buxoriy, 71"},
        {"text": "Oxirgi zamon kelganda ilm ko'tariladi, jaholat ko'payadi.", "source": "Muslim, 157"},
        {"text": "Bir olim — ming obiddan yaxshiroqdir.", "source": "Tirmiziy, 2682"},
        {"text": "Ilm amal bilan, amal ikhlos bilan kamolga yetadi.", "source": "Hikmatul Islom"},
        {"text": "Bemorni ziyorat qiling, och kishini to'ydiring, asirni ozod qiling.", "source": "Buxoriy, 5373"},
    ]},
    "namoz":   {"label": "🕌 Namoz va ibodat",   "hadiths": [
        {"text": "Kim bomdod namozini o'qisa, Allohning himoyasida bo'ladi.", "source": "Muslim, 657"},
        {"text": "Jamoat bilan o'qilgan namoz yolg'iz o'qilgandan 27 daraja afzal.", "source": "Buxoriy, 645"},
        {"text": "Namoz — dinning ustuni. Kim uni tark etsa, dinini buzgan bo'ladi.", "source": "Bayhaqiy, 2/14"},
        {"text": "Poklik iymonning yarmidir.", "source": "Muslim, 223"},
        {"text": "Qiyomat kuni bandadan birinchi so'raladigan narsa namozdir.", "source": "Abu Dovud, 864"},
        {"text": "Allohga eng sevimli amal — oz bo'lsa ham davomli bo'lgan amaldir.", "source": "Buxoriy, 6464"},
        {"text": "Kim Ramazon oyida imon bilan ro'za tutsa, gunohlarining hammasi kechiriladi.", "source": "Buxoriy, 38"},
        {"text": "Besh vaqt namoz gunohlarni kaffarat qiladi, agar katta gunohlardan saqlanilsa.", "source": "Muslim, 233"},
    ]},
    "sahovat": {"label": "💛 Sahovat va sadaqa", "hadiths": [
        {"text": "Eng yaxshi sadaqa — mol-mulk ko'p ekan berilgan sadaqadir.", "source": "Buxoriy, 1427"},
        {"text": "Kim birodarining hojatini chiqarsa, Alloh uning hojatini chiqaradi.", "source": "Buxoriy, 2442"},
        {"text": "Kim qiynalgan kishiga yengillik qilsa, Alloh unga dunyo va oxiratda yengillik qiladi.", "source": "Muslim, 2699"},
        {"text": "Insonga o'lganidan keyin uch narsa savob keltiradi: sadaqa, ilm va solih farzand.", "source": "Muslim, 1631"},
        {"text": "Yuqori qo'l quyi qo'ldan yaxshiroqdir.", "source": "Buxoriy, 1427"},
        {"text": "Qo'shnisi och yotganini bilib, to'q yotgan kishi mo'min emas.", "source": "Al-Adab, 112"},
        {"text": "Kim bir musulmonning aybini yopsa, Alloh qiyomat kuni uning aybini yopadi.", "source": "Buxoriy, 2442"},
    ]},
    "birlik":  {"label": "🤝 Birlik va birodarlik","hadiths": [
        {"text": "Musulmon musulmonning birodaridir. Unga zulm qilmaydi, uni tashlab ketmaydi.", "source": "Buxoriy, 2442"},
        {"text": "Sizlardan hech biringiz o'zi uchun yaxshi ko'rganni birodari uchun ham yaxshi ko'rmaguncha to'liq mo'min bo'la olmaydi.", "source": "Buxoriy, 13"},
        {"text": "Bir-biringizga hasad qilmanglar, bir-biringizni sevib qoling.", "source": "Muslim, 2559"},
        {"text": "Mo'minning ishi ajablanarlidir: uning har bir holatida yaxshilik bor.", "source": "Muslim, 2999"},
        {"text": "Kuchli mo'min Allohga zaif mo'mindan ko'ra yaxshiroq va suyukliroqdir.", "source": "Muslim, 2664"},
        {"text": "Alloh rahm-shafqat qiluvchilarga rahm qiladi.", "source": "Abu Dovud, 4941"},
        {"text": "Siz mo'min bo'lmasangiz, jannatga kira olmaysiz. Bir-biringizni sevmasangiz, to'liq mo'min bo'la olmaysiz.", "source": "Muslim, 54"},
    ]},
    "tavba":   {"label": "🌿 Tavba va istig'for", "hadiths": [
        {"text": "Alloh tavbalarni tongdan avval qabul qiladi.", "source": "Muslim, 2759"},
        {"text": "Alloh bandasi tavba qilganda, cho'lda tuyasini yo'qotib topgan odamdan ham ko'proq xursand bo'ladi.", "source": "Buxoriy, 6309"},
        {"text": "Barcha odamlar xato qiladi. Xato qiluvchilarning eng yaxshisi — tavba qiluvchisidir.", "source": "Tirmiziy, 2499"},
        {"text": "Kim 'Subhanallahi wa bihamdihi'ni bir kunda yuz marta aytsa, gunohlarining hammasi kechiriladi.", "source": "Muslim, 2691"},
        {"text": "Allohdan avf va afiyat so'ranglar.", "source": "Tirmiziy, 3514"},
        {"text": "Ulug' savob ulug' sinov bilan birga keladi. Alloh bir qavmni sevsa, uni sinaydi.", "source": "Tirmiziy, 2396"},
    ]},
    "dunyo":   {"label": "🌍 Dunyo va oxirat",   "hadiths": [
        {"text": "Dunyo mo'minning zindoni, kofirning jannatidir.", "source": "Muslim, 2956"},
        {"text": "Aqlliroq kishi — o'limni ko'p eslaydigan va unga yaxshi tayyorgarlik ko'radigan kishidir.", "source": "Tirmiziy, 2459"},
        {"text": "Ikki ne'mat bor — ko'p odamlar ularni bekor ketkazadi: sog'lik va bo'sh vaqt.", "source": "Buxoriy, 6412"},
        {"text": "Kim shahid bo'lishni samimiy qalb bilan so'rasa, to'shagida vafot etsa ham shahid darajasiga yetadi.", "source": "Muslim, 1909"},
        {"text": "Insonga o'lganidan keyin uch narsa savob keltiradi: jariya sadaqa, ilm va solih farzand.", "source": "Muslim, 1631"},
        {"text": "Kishi biror narsada shubhalanib, uni tark etsa — bu unga savob bo'ladi.", "source": "Nasaiy, 5711"},
    ]},
}

# ═══════════════════════════════════════════════════════════════
#  DUOLAR (bo'limlar bo'yicha)
# ═══════════════════════════════════════════════════════════════
DUA_SECTIONS = {
    "ertalab":   {"label": "🌅 Ertalabki duolar",   "duas": [
        {"name": "Uyg'onganda", "arabic": "اَلْحَمْدُ لِلَّهِ الَّذِي أَحْيَانَا بَعْدَ مَا أَمَاتَنَا وَإِلَيْهِ النُّشُورُ", "latin": "Alhamdulillahil-lazii ahyaanaa ba'da maa amaatanaa wa ilayhin-nushuur.", "mazmun": "Bizni o'ldirgandan keyin tiriltirgani va qaytish Unga ekaniga hamd bo'lsin.", "manba": "Buxoriy, 6312"},
        {"name": "Sabah zikri", "arabic": "أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ وَالْحَمْدُ لِلَّهِ", "latin": "Asbahna wa asbahal mulku lillah, walhamdulillah.", "mazmun": "Biz tong otdik, mulk Allohniki, hamd Allohga.", "manba": "Muslim, 2723"},
        {"name": "Sabah himoya duosi", "arabic": "اَللّٰهُمَّ بِكَ أَصْبَحْنَا وَبِكَ أَمْسَيْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ", "latin": "Allahumma bika asbahna wa bika amsayna wa bika nahya wa bika namuut.", "mazmun": "Allohim, Sen bilan tong otdik, Sen bilan kechga yetdik, Sen bilan yashaymiz va o'lamiz.", "manba": "Tirmiziy, 3391"},
        {"name": "Sabah tasbeh", "arabic": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ", "latin": "Subhanallahi wa bihamdih. (100 marta)", "mazmun": "Alloh pokdir va hamdu sanoga loyiqdir. 100 marta aytilsa katta savob.", "manba": "Muslim, 2692"},
        {"name": "Ayatul Kursi", "arabic": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ...", "latin": "Allahu laa ilaaha illaa huwal hayyul qayyuum...", "mazmun": "Alloh — Undan boshqa iloh yo'q. Har ertalab o'qilsa kechgacha Alloh himoyasida bo'linadi.", "manba": "Baqara, 255"},
    ]},
    "kechki":    {"label": "🌙 Kechki duolar",      "duas": [
        {"name": "Kechki zikr", "arabic": "أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ وَالْحَمْدُ لِلَّهِ", "latin": "Amsayna wa amsal mulku lillah, walhamdulillah.", "mazmun": "Biz kechga yetdik, mulk Allohniki, hamd Allohga.", "manba": "Muslim, 2723"},
        {"name": "Uxlashdan oldin — Tasbeh", "arabic": "سُبْحَانَ اللَّهِ (٣٣) اَلْحَمْدُ لِلَّهِ (٣٣) اَللَّهُ أَكْبَرُ (٣٤)", "latin": "Subhanallah (33), Alhamdulillah (33), Allahu Akbar (34).", "mazmun": "Uxlashdan avval o'qilsa katta savob.", "manba": "Buxoriy, 5362"},
        {"name": "Uxlashdan oldin — 3 sura", "arabic": "قُلْ هُوَ اللَّهُ أَحَدٌ ۝ قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ ۝ قُلْ أَعُوذُ بِرَبِّ النَّاسِ", "latin": "Al-Ikhlos, Al-Falaq va An-Nas suralarini o'qib kafti bilan badanini silash.", "mazmun": "Rasululloh har kechasi shu suralarni o'qir edi.", "manba": "Buxoriy, 5017"},
        {"name": "Uxlashdan oldin duo", "arabic": "بِسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا", "latin": "Bismikallaahumma amuutu wa ahyaa.", "mazmun": "Allohim, Sening isming bilan o'laman va yashaman.", "manba": "Buxoriy, 6324"},
        {"name": "Kechki Ayatul Kursi", "arabic": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ...", "latin": "Allahu laa ilaaha illaa huwal hayyul qayyuum...", "mazmun": "Kechqurun o'qilsa, tongga qadar Alloh himoyasida bo'linadi.", "manba": "Buxoriy, 2311"},
    ]},
    "namoz":     {"label": "🕌 Namoz duolari",      "duas": [
        {"name": "Sano", "arabic": "سُبْحَانَكَ اللَّهُمَّ وَبِحَمْدِكَ وَتَبَارَكَ اسْمُكَ وَتَعَالَى جَدُّكَ وَلَا إِلَهَ غَيْرُكَ", "latin": "Subhanakallahumma wa bihamdika wa tabaarakasmuka wa ta'aalaa jadduka wa laa ilaaha ghayruk.", "mazmun": "Allohim, Seni poklaymen va Senga hamd aytaman, Sening isming muborak va ulug'vorliging yuksak.", "manba": "Abu Dovud, 775"},
        {"name": "Ruku' duosi", "arabic": "سُبْحَانَ رَبِّيَ الْعَظِيمِ", "latin": "Subhaana rabbiyal aziim. (3 marta)", "mazmun": "Buyuk Rabbim pok va muqaddasdir.", "manba": "Muslim, 772"},
        {"name": "Sajda duosi", "arabic": "سُبْحَانَ رَبِّيَ الْأَعْلَى", "latin": "Subhaana rabbiyal a'laa. (3 marta)", "mazmun": "Eng Oliy Rabbim pok va muqaddasdir.", "manba": "Muslim, 772"},
        {"name": "Attahiyyat", "arabic": "التَّحِيَّاتُ لِلَّهِ وَالصَّلَوَاتُ وَالطَّيِّبَاتُ، السَّلَامُ عَلَيْكَ أَيُّهَا النَّبِيُّ...", "latin": "Attahiyyaatu lillaahi wassalawaatu wattayyibaat. Assalaamu alayka ayyuhan-nabiyyu wa rahmatullaahi wa barakaatuh...", "mazmun": "Barcha ta'zimlar, ibodat va yaxshiliklar Alloh uchundir. Ey Nabiy, salom, Allohning rahmati va barakoti senga bo'lsin.", "manba": "Buxoriy, 831"},
        {"name": "Salavot (Ibrohimiy)", "arabic": "اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ وَعَلَى آلِ مُحَمَّدٍ...", "latin": "Allahumma salli alaa Muhammadin wa alaa aali Muhammad...", "mazmun": "Allohim, Muhammadga va uning oilasiga rahmat yubor.", "manba": "Buxoriy, 3370"},
        {"name": "Namoz oxirida (4 narsadan)", "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ عَذَابِ الْقَبْرِ...", "latin": "Allahumma inni a'uuzu bika min azaabil qabri wa min azaabinnaari...", "mazmun": "Allohim, qabr azobidan, do'zax azobidan, hayot va o'lim fitnasidan, Dajjol fitnasidan panoh so'rayman.", "manba": "Muslim, 588"},
        {"name": "Namozdan keyin zikr", "arabic": "سُبْحَانَ اللَّهِ (٣٣) اَلْحَمْدُ لِلَّهِ (٣٣) اَللَّهُ أَكْبَرُ (٣٣) لَا إِلٰهَ إِلَّا اللّٰهُ وَحْدَهُ لَا شَرِيكَ لَهُ", "latin": "Subhanallah (33), Alhamdulillah (33), Allahu Akbar (33), La ilaha illallahu wahdahu la sharika lah.", "mazmun": "Namozdan keyin o'qiladi.", "manba": "Muslim, 597"},
    ]},
    "dasturxon": {"label": "🍽 Dasturxon duolari", "duas": [
        {"name": "Ovqatdan oldin", "arabic": "بِسْمِ اللَّهِ", "latin": "Bismillah.", "mazmun": "Allohning ismi bilan. Ovqat yeyishdan avval aytiladi.", "manba": "Buxoriy, 5376"},
        {"name": "Unutilsa", "arabic": "بِسْمِ اللَّهِ أَوَّلَهُ وَآخِرَهُ", "latin": "Bismillahi awwalahu wa aakhirah.", "mazmun": "Allohning ismi bilan — boshida ham, oxirida ham.", "manba": "Abu Dovud, 3767"},
        {"name": "Ovqatdan keyin", "arabic": "اَلْحَمْدُ لِلَّهِ الَّذِي أَطْعَمَنَا وَسَقَانَا وَجَعَلَنَا مُسْلِمِينَ", "latin": "Alhamdulillahil-lazii at'amanaa wa saqaanaa wa ja'alanaa muslimiin.", "mazmun": "Bizni yedirgan, ichirgan va muslimlardan qilgan Allohga hamd bo'lsin.", "manba": "Abu Dovud, 3850"},
        {"name": "Taom bergan kishiga duo", "arabic": "اللَّهُمَّ أَطْعِمْ مَنْ أَطْعَمَنِي وَاسْقِ مَنْ سَقَانِي", "latin": "Allahumma at'im man at'amani wasqi man saqaani.", "mazmun": "Allohim, meni yedirgan kishini yedir, ichirgan kishini ichlir.", "manba": "Muslim, 2055"},
        {"name": "Mezbonga duo", "arabic": "اللَّهُمَّ بَارِكْ لَهُمْ فِيمَا رَزَقْتَهُمْ", "latin": "Allahumma baarik lahum fiimaa razaqtahum waghfir lahum warhamhum.", "mazmun": "Allohim, ularga bergan rizqingni barakali qil, ularni kechir va rahm qil.", "manba": "Muslim, 2042"},
    ]},
    "kocha":     {"label": "🚶 Ko'cha va safar",    "duas": [
        {"name": "Uydan chiqishda", "arabic": "بِسْمِ اللَّهِ تَوَكَّلْتُ عَلَى اللَّهِ وَلَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ", "latin": "Bismillahi tawakkaltu alallahi wa laa hawla wa laa quwwata illaa billaah.", "mazmun": "Allohning ismi bilan, Allohga tavakkal qildim, kuch-quvvat faqat Allohdan.", "manba": "Abu Dovud, 5095"},
        {"name": "Uyga kirishda", "arabic": "بِسْمِ اللَّهِ وَلَجْنَا وَبِسْمِ اللَّهِ خَرَجْنَا", "latin": "Bismillahi walajna wa bismillahi kharajna wa alallahi rabbina tawakkalna.", "mazmun": "Allohning ismi bilan kirdik, Allohning ismi bilan chiqdik, Rabbimiz Allohga tavakkal qildik.", "manba": "Abu Dovud, 5096"},
        {"name": "Transport duosi", "arabic": "سُبْحَانَ الَّذِي سَخَّرَ لَنَا هَذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ", "latin": "Allahu Akbar (3x). Subhaanal-lazii sakhkhara lanaa haazaa wa maa kunnaa lahu muqriniin.", "mazmun": "Alloh Ulug'. Buni bizga bo'ysundirgan Zot pok — biz uni o'zimiz bo'ysundira olmasdik.", "manba": "Muslim, 1342"},
        {"name": "Yangi joyga kelganda", "arabic": "أَعُوذُ بِكَلِمَاتِ اللَّهِ التَّامَّاتِ مِنْ شَرِّ مَا خَلَقَ", "latin": "A'uuzu bikalimaatillaahit-taammaati min sharri maa khalaq.", "mazmun": "Allohning mukammal so'zlari bilan yaratiqlarining yomonligidan panoh so'rayman.", "manba": "Muslim, 2708"},
        {"name": "Masjidga kirishda", "arabic": "اللَّهُمَّ افْتَحْ لِي أَبْوَابَ رَحْمَتِكَ", "latin": "Allahummaf-tah li abwaaba rahmatik.", "mazmun": "Allohim, menga rahmat eshiklarini och.", "manba": "Muslim, 713"},
        {"name": "Masjiddan chiqqanda", "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ مِنْ فَضْلِكَ", "latin": "Allahumma inni as'aluka min fadlik.", "mazmun": "Allohim, Sening fazlingdan so'rayman.", "manba": "Muslim, 713"},
        {"name": "Hojatxonaga kirishda", "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْخُبُثِ وَالْخَبَائِثِ", "latin": "Allahumma inni a'uuzu bika minal khubuthi wal khabaaith.", "mazmun": "Allohim, erkak va urg'ochi jinlardan Sening panohing'da bo'lishni so'rayman.", "manba": "Buxoriy, 142"},
    ]},
    "maxsus":    {"label": "🤲 Maxsus duolar",      "duas": [
        {"name": "Sayyidul Istig'for", "arabic": "اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ خَلَقْتَنِي وَأَنَا عَبْدُكَ...", "latin": "Allahumma anta rabbi laa ilaaha illaa anta, khalaqtani wa ana abduk...", "mazmun": "Allohim, Sen mening Rabbimsan, Sendan boshqa iloh yo'q. Sen meni yaratding, men Sening bandangman. Meni kechir — gunohlarni Sen'dan boshqasi kechirmaydi.", "manba": "Buxoriy, 6306"},
        {"name": "Yunus alayhissalom duosi", "arabic": "لَا إِلَهَ إِلَّا أَنْتَ سُبْحَانَكَ إِنِّي كُنْتُ مِنَ الظَّالِمِينَ", "latin": "Laa ilaaha illaa anta subhaanaka innii kuntu minaz-zaalimiin.", "mazmun": "Sendan boshqa iloh yo'q, Seni poklaymen — albatta men zolimlardan bo'ldim.", "manba": "Quron, Anbiyo 87"},
        {"name": "Rizq uchun duo", "arabic": "اللَّهُمَّ اكْفِنِي بِحَلَالِكَ عَنْ حَرَامِكَ", "latin": "Allahummak-fini bihalaalika an haraamika wa aghnini bifadlika amman siwaak.", "mazmun": "Allohim, Sening halolingni haromingdan kifoya qil.", "manba": "Tirmiziy, 3563"},
        {"name": "Kasallik vaqtida", "arabic": "اللَّهُمَّ رَبَّ النَّاسِ أَذْهِبِ الْبَأْسَ اشْفِ أَنْتَ الشَّافِي", "latin": "Allahumma rabban-naas, az-hibil-ba's, ishfi antash-shaafi, laa shifaa'a illaa shifaa'uk.", "mazmun": "Allohim, odamlarning Rabbisi, azobni ket, shifo ber — Shifo beruvchi Sen'san.", "manba": "Buxoriy, 5742"},
        {"name": "Qalb sobitligi", "arabic": "يَا مُقَلِّبَ الْقُلُوبِ ثَبِّتْ قَلْبِي عَلَى دِينِكَ", "latin": "Yaa muqallibal quluub, thabbit qalbi alaa dinik.", "mazmun": "Ey qalblarni o'zgartiruvchi, qalbimni Sening diningda sobit qil.", "manba": "Tirmiziy, 2140"},
        {"name": "Ota-ona uchun", "arabic": "رَبِّ اغْفِرْ لِي وَلِوَالِدَيَّ وَارْحَمْهُمَا", "latin": "Rabbighfir lii wa liwaalidayya warhamhumaa kamaa rabbayaani saghiiraa.", "mazmun": "Rabbim, menga va ota-onamga mag'firat qil va ular meni tarbiyalaganidek ularga rahm qil.", "manba": "Quron, Isro 24"},
        {"name": "Ilm uchun", "arabic": "رَبِّ زِدْنِي عِلْمًا", "latin": "Rabbi zidni ilmaa.", "mazmun": "Rabbim, ilmimni oshir.", "manba": "Quron, Toha 114"},
        {"name": "Jannat uchun", "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْجَنَّةَ وَأَعُوذُ بِكَ مِنَ النَّارِ", "latin": "Allahumma inni as'alukal jannata wa a'uuzu bika minan-naar.", "mazmun": "Allohim, Sendan jannatni so'rayman va do'zaxdan Sening panohing'da bo'lishni tilayman.", "manba": "Abu Dovud, 792"},
        {"name": "Qiyinchilikda", "arabic": "لَا إِلَهَ إِلَّا اللَّهُ الْعَظِيمُ الْحَلِيمُ", "latin": "Laa ilaaha illallaahul aziimul haliim. Laa ilaaha illallaahu rabbul arshil aziim.", "mazmun": "Ulug' va Halim Allohdan boshqa iloh yo'q. Ulug' Arsh Rabbisidan boshqa iloh yo'q.", "manba": "Buxoriy, 6346"},
        {"name": "Zikr & Tasbeh", "arabic": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ سُبْحَانَ اللَّهِ الْعَظِيمِ", "latin": "Subhanallahi wa bihamdihi, Subhanallahil azim.", "mazmun": "Tilga yengil, tarozida og'ir va Rahmonga suyukli ikki kalima.", "manba": "Buxoriy, 6682"},
    ]},
}

# ═══════════════════════════════════════════════════════════════
#  QUR'ON SURALAR (114 ta)
# ═══════════════════════════════════════════════════════════════
QURAN_SURAHS = [
    (1,"Al-Fotiha",7),(2,"Al-Baqara",286),(3,"Oli Imron",200),(4,"An-Niso",176),
    (5,"Al-Moida",120),(6,"Al-An'om",165),(7,"Al-A'rof",206),(8,"Al-Anfol",75),
    (9,"At-Tavba",129),(10,"Yunus",109),(11,"Hud",123),(12,"Yusuf",111),
    (13,"Ar-Ra'd",43),(14,"Ibrohim",52),(15,"Al-Hijr",99),(16,"An-Nahl",128),
    (17,"Al-Isro",111),(18,"Al-Kahf",110),(19,"Maryam",98),(20,"Toha",135),
    (21,"Al-Anbiyo",112),(22,"Al-Haj",78),(23,"Al-Mo'minun",118),(24,"An-Nur",64),
    (25,"Al-Furqon",77),(26,"Ash-Shuaro",227),(27,"An-Naml",93),(28,"Al-Qasas",88),
    (29,"Al-Ankabut",69),(30,"Ar-Rum",60),(31,"Luqmon",34),(32,"As-Sajda",30),
    (33,"Al-Ahzob",73),(34,"Sabo",54),(35,"Fotir",45),(36,"Yosin",83),
    (37,"As-Soffot",182),(38,"Sod",88),(39,"Az-Zumar",75),(40,"G'ofir",85),
    (41,"Fussilat",54),(42,"Ash-Shuro",53),(43,"Az-Zuxruf",89),(44,"Ad-Duxon",59),
    (45,"Al-Josiya",37),(46,"Al-Ahqof",35),(47,"Muhammad",38),(48,"Al-Fath",29),
    (49,"Al-Hujurot",18),(50,"Qof",45),(51,"Az-Zoriyot",60),(52,"At-Tur",49),
    (53,"An-Najm",62),(54,"Al-Qamar",55),(55,"Ar-Rahman",78),(56,"Al-Voqia",96),
    (57,"Al-Hadid",29),(58,"Al-Mujodala",22),(59,"Al-Hashr",24),(60,"Al-Mumtahana",13),
    (61,"As-Sof",14),(62,"Al-Juma",11),(63,"Al-Munofiqun",11),(64,"At-Tag'obun",18),
    (65,"At-Taloq",12),(66,"At-Tahrim",12),(67,"Al-Mulk",30),(68,"Al-Qalam",52),
    (69,"Al-Haqqa",52),(70,"Al-Maarij",44),(71,"Nuh",28),(72,"Al-Jin",28),
    (73,"Al-Muzzammil",20),(74,"Al-Muddassir",56),(75,"Al-Qiyoma",40),(76,"Al-Inson",31),
    (77,"Al-Mursalot",50),(78,"An-Naba",40),(79,"An-Noziot",46),(80,"Abasa",42),
    (81,"At-Takwir",29),(82,"Al-Infitor",19),(83,"Al-Mutaffifin",36),(84,"Al-Inshiqoq",25),
    (85,"Al-Buruj",22),(86,"At-Toriq",17),(87,"Al-A'lo",19),(88,"Al-G'oshiya",26),
    (89,"Al-Fajr",30),(90,"Al-Balad",20),(91,"Ash-Shams",15),(92,"Al-Layl",21),
    (93,"Ad-Duho",11),(94,"Ash-Sharh",8),(95,"At-Tin",8),(96,"Al-Alaq",19),
    (97,"Al-Qadr",5),(98,"Al-Bayyina",8),(99,"Az-Zilzol",8),(100,"Al-Odiyot",11),
    (101,"Al-Qoria",11),(102,"At-Takosur",8),(103,"Al-Asr",3),(104,"Al-Humaza",9),
    (105,"Al-Fil",5),(106,"Quraysh",4),(107,"Al-Mo'un",7),(108,"Al-Kavsar",3),
    (109,"Al-Kofirun",6),(110,"An-Nasr",3),(111,"Al-Masad",5),(112,"Al-Ixlos",4),
    (113,"Al-Falaq",5),(114,"An-Nos",6),
]


# ═══════════════════════════════════════════════════════════════
#  USER STATE (xotirada saqlanadi)
# ═══════════════════════════════════════════════════════════════
user_mode       = {}   # prayer | qibla | masjid
user_hijri_date = {}
user_name_idx   = {}
user_hadith_sec = {}
user_hadith_idx = {}
user_dua_sec    = {}
user_dua_idx    = {}
user_quran_page = {}
user_zikr_count = {}
user_zikr_type  = {}

# ═══════════════════════════════════════════════════════════════
#  MENYULAR  (rasmda ko'rsatilgan ko'rinish)
# ═══════════════════════════════════════════════════════════════
def main_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(
        "🕌 Namoz vaqtlari", "🧭 Qibla",
        "📍 Yaqin masjidlar", "📖 Qur'on",
        "📚 Hadislar", "🤲 Duolar",
        "📿 Zikr & Salovatlar", "📅 Hijriy taqvim",
        "🕋 Allohning 99 ismi", "⚙️ Sozlamalar",
    )
    return m

def loc_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add(types.KeyboardButton("📍 Lokatsiyani yuborish", request_location=True))
    m.add("🏠 Asosiy menyu")
    return m

def hijri_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("📌 Muhim islomiy sanalar")
    m.add("🏠 Asosiy menyu")
    return m

def names_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("⬅️ Oldingi", "➡️ Keyingi")
    m.add("🏠 Asosiy menyu")
    return m

def hadith_sections_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🌸 Odob-axloq", "👨‍👩‍👧 Ota-ona va oila",
          "📚 Ilm va hikmat", "🕌 Namoz va ibodat",
          "💛 Sahovat", "🤝 Birlik",
          "🌿 Tavba", "🌍 Dunyo va oxirat")
    m.add("🏠 Asosiy menyu")
    return m

def hadith_nav_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("⬅️ Oldingi hadis", "➡️ Keyingi hadis")
    m.add("📋 Hadis bo'limlari", "🏠 Asosiy menyu")
    return m

def dua_sections_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🌅 Ertalabki duolar", "🌙 Kechki duolar",
          "🕌 Namoz duolari", "🍽 Dasturxon duolari",
          "🚶 Ko'cha va safar", "🤲 Maxsus duolar")
    m.add("🏠 Asosiy menyu")
    return m

def dua_nav_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("⬅️ Oldingi duo", "➡️ Keyingi duo")
    m.add("📋 Duo bo'limlari", "🏠 Asosiy menyu")
    return m

def zikr_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("📿 Istig'for", "🤲 Salavot")
    m.add("🌟 Kalimalar", "📖 Tasbeh")
    m.add("🏠 Asosiy menyu")
    return m

def settings_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🌐 Tilni o'zgartirish", "🔔 Namoz eslatmalari",
          "📍 Lokatsiyani yangilash", "🎧 Qori tanlash",
          "ℹ️ Bot haqida", "📞 Murojaat")
    m.add("🏠 Asosiy menyu")
    return m

def language_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🇺🇿 O'zbekcha", "🇷🇺 Русский",
          "🇬🇧 English", "🇸🇦 العربية",
          "🇹🇷 Türkçe", "🇩🇪 Deutsch",
          "🇫🇷 Français", "🇪🇸 Español",
          "🇮🇹 Italiano", "🇰🇿 Қазақша",
          "🇰🇬 Кыргызча", "🇹🇯 Тоҷикӣ")
    m.add("🏠 Asosiy menyu")
    return m

# ═══════════════════════════════════════════════════════════════
#  YORDAMCHI FUNKSIYALAR
# ═══════════════════════════════════════════════════════════════
def calc_qibla(lat, lon):
    la1, lo1 = math.radians(lat), math.radians(lon)
    la2, lo2 = math.radians(KAABA_LAT), math.radians(KAABA_LON)
    d = lo2 - lo1
    x = math.sin(d)
    y = math.cos(la1) * math.tan(la2) - math.sin(la1) * math.cos(d)
    return (math.degrees(math.atan2(x, y)) + 360) % 360

def compass(angle):
    dirs = ["Shimol ⬆️", "Shimol-Sharq ↗️", "Sharq ➡️", "Janub-Sharq ↘️",
            "Janub ⬇️", "Janub-G'arb ↙️", "G'arb ⬅️", "Shimol-G'arb ↖️"]
    return dirs[int((angle + 22.5) / 45) % 8]

def haversine(la1, lo1, la2, lo2):
    R = 6371000; p = math.pi / 180
    a = (math.sin((la2 - la1) * p / 2) ** 2 +
         math.cos(la1 * p) * math.cos(la2 * p) * math.sin((lo2 - lo1) * p / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))

def get_city(lat, lon):
    try:
        r = requests.get("https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json", "accept-language": "uz,en"},
            headers={"User-Agent": "IslamTimeWorldBot/2.1"}, timeout=8).json()
        a = r.get("address", {})
        city = a.get("city") or a.get("town") or a.get("village") or a.get("county") or "Noma'lum"
        return f"{city}, {a.get('country', '')}"
    except Exception:
        return "Joylashuv aniqlandi"

def get_hijri(date_obj):
    try:
        ds = date_obj.strftime("%d-%m-%Y")
        d = requests.get(f"https://api.aladhan.com/v1/gToH?date={ds}", timeout=10).json()["data"]
        h = d["hijri"]; g = d["gregorian"]
        return {"h_day": h["day"],
                "h_month": HIJRI_MONTHS_UZ.get(h["month"]["en"], h["month"]["en"]),
                "h_year": h["year"], "g_date": g["date"],
                "weekday": UZ_WEEKDAYS.get(g["weekday"]["en"], g["weekday"]["en"])}
    except Exception:
        return {"h_day": "—", "h_month": "Xatolik", "h_year": "—", "g_date": "—", "weekday": "—"}

def h_to_g(hd, hm, hy):
    try:
        d = requests.get(f"https://api.aladhan.com/v1/hToG?date={hd}-{hm}-{hy}", timeout=10).json()["data"]["gregorian"]["date"]
        return datetime.strptime(d, "%d-%m-%Y").date()
    except Exception:
        return datetime.now().date()

def next_dates(today):
    info = get_hijri(today)
    try:
        cy = int(info.get("h_year", "1446"))
    except (ValueError, TypeError):
        cy = 1446
    res = []
    for item in IMPORTANT_HIJRI_DATES:
        for yr in [cy, cy + 1]:
            gd = h_to_g(item["h_day"], item["h_month"], yr)
            dl = (gd - today.date()).days
            if dl >= 0:
                res.append({**item, "h_year": yr, "g_date": gd, "days_left": dl})
                break
    res.sort(key=lambda x: x["days_left"])
    return res

# ═══════════════════════════════════════════════════════════════
#  SHOW FUNKSIYALARI
# ═══════════════════════════════════════════════════════════════
def show_name(cid, idx):
    n = ALLAH_NAMES[idx]; total = len(ALLAH_NAMES)
    bot.send_message(cid,
        f"🕋 <b>ASMAUL HUSNA</b>\n<i>Allohning 99 go'zal ismi</i>\n\n"
        f"<b>{idx+1}/{total}</b>\n\n"
        f"<b>{n['arabic']}</b>\n\n"
        f"🔤 <b>{n['latin']}</b>\n\n"
        f"💡 <b>Ma'nosi:</b>\n{n['meaning']}\n\n"
        f"📿 <b>Zikr:</b> <i>{n['zikr']}</i>\n\n"
        f"🤲 <i>Allohni zikr qiling va ma'nosini tafakkur qiling.</i>",
        parse_mode="HTML", reply_markup=names_menu())

def show_hijri(cid, date_obj):
    user_hijri_date[cid] = date_obj
    info = get_hijri(date_obj)
    dates = next_dates(date_obj)
    nxt = dates[0] if dates else None
    nxt_text = f"\n⏳ <b>Keyingi muhim sana:</b>\n{nxt['title']} — {nxt['days_left']} kun qoldi" if nxt else ""
    bot.send_message(cid,
        f"📅 <b>HIJRIY TAQVIM</b>\n\n"
        f"🌙 <b>Hijriy:</b>  {info['h_day']} {info['h_month']} {info['h_year']}\n"
        f"🗓 <b>Milodiy:</b> {info['g_date']}\n"
        f"📆 <b>Kun:</b>     {info['weekday']}"
        f"{nxt_text}\n\n"
        f"🤲 <i>Alloh bugungi kuningizni barakali qilsin.</i>",
        parse_mode="HTML", reply_markup=hijri_menu())

def show_hadith(cid, sec_key, idx):
    sec = HADITH_SECTIONS[sec_key]; lst = sec["hadiths"]
    idx = max(0, min(idx, len(lst) - 1)); user_hadith_idx[cid] = idx
    h = lst[idx]
    bot.send_message(cid,
        f"{sec['label']}\n\n"
        f"<b>{idx+1}/{len(lst)}</b>\n\n"
        f"❝ {h['text']} ❞\n\n"
        f"📖 <b>{h['source']}</b>\n\n"
        f"🤲 <i>Alloh bu hadisdan bahra olishimizni nasib etsin.</i>",
        parse_mode="HTML", reply_markup=hadith_nav_menu())

def show_dua(cid, sec_key, idx):
    sec = DUA_SECTIONS[sec_key]; lst = sec["duas"]
    idx = max(0, min(idx, len(lst) - 1)); user_dua_idx[cid] = idx
    d = lst[idx]
    bot.send_message(cid,
        f"{sec['label']}\n\n"
        f"<b>{idx+1}/{len(lst)}</b> — <b>{d['name']}</b>\n\n"
        f"🔤 <b>Arabcha:</b>\n{d['arabic']}\n\n"
        f"📢 <b>Talaffuz:</b>\n<i>{d['latin']}</i>\n\n"
        f"💬 <b>Ma'nosi:</b>\n{d['mazmun']}\n\n"
        f"📖 <b>Manba:</b> {d['manba']}\n\n"
        f"🤲 <i>Alloh duolarimizni ijobat qilsin!</i>",
        parse_mode="HTML", reply_markup=dua_nav_menu())

QPAGE = 10
def show_quran(cid, page):
    user_quran_page[cid] = page
    total = (len(QURAN_SURAHS) + QPAGE - 1) // QPAGE
    start = page * QPAGE; slist = QURAN_SURAHS[start:start + QPAGE]
    lines = [f"📖 <b>QUR'ON KARIM — SURALAR</b>\n<i>Sahifa {page+1}/{total}</i>\n"]
    for num, name, ayats in slist:
        lines.append(f"<b>{num}.</b> {name}  <i>({ayats} oyat)</i>")
    lines.append("\n⬇️ <i>O'qish uchun tugmani bosing:</i>")

    mk = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(f"{num}. {name}", url=f"https://quran.com/uz/{num}") for num, name, _ in slist]
    mk.add(*btns)

    nav = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if page > 0 and page < total - 1:
        nav.add("⬅️ Oldingi sahifa", "➡️ Keyingi sahifa")
    elif page == 0:
        nav.add("➡️ Keyingi sahifa")
    else:
        nav.add("⬅️ Oldingi sahifa")
    nav.add("🏠 Asosiy menyu")

    bot.send_message(cid, "\n".join(lines), parse_mode="HTML", reply_markup=nav)
    bot.send_message(cid,
        "👆 <b>Sura nomini bosing</b> — Quran.com da arabcha matn,\n"
        "Muhammad Sodiq Muhammad Yusuf tarjimasi va\nMishary Rashid tilovati ochiladi.",
        parse_mode="HTML", reply_markup=mk)

# ═══════════════════════════════════════════════════════════════
#  FLASK (Render/Heroku uchun)
# ═══════════════════════════════════════════════════════════════
@app.route("/")
def home():
    return "IslamTimeWorldBot v2.1 running!"

# ═══════════════════════════════════════════════════════════════
#  HANDLERS
# ═══════════════════════════════════════════════════════════════

# ── /start ───────────────────────────────────────────────────
@bot.message_handler(commands=["start"])
def cmd_start(msg):
    bot.send_message(msg.chat.id,
        "🌙 <b>Bismillahir Rohmanir Rohiym</b>\n\n"
        "Assalomu alaykum! <b>Islam Time World</b> botiga xush kelibsiz!\n\n"
        "Kerakli bo'limni tanlang 👇",
        parse_mode="HTML", reply_markup=main_menu())

# ── Asosiy menyu / Ortga ──────────────────────────────────────
@bot.message_handler(func=lambda m: m.text in ["🏠 Asosiy menyu", "⬅️ Ortga", "⬅️ Orqaga"])
def go_home(msg):
    bot.send_message(msg.chat.id, "🏠 Asosiy menyu", reply_markup=main_menu())

# ── Til tanlash (har qanday til) ──────────────────────────────
@bot.message_handler(func=lambda m: m.text in [
    "🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇬🇧 English", "🇸🇦 العربية",
    "🇹🇷 Türkçe", "🇩🇪 Deutsch", "🇫🇷 Français", "🇪🇸 Español",
    "🇮🇹 Italiano", "🇰🇿 Қазақша", "🇰🇬 Кыргызча", "🇹🇯 Тоҷикӣ"])
def lang_selected(msg):
    bot.send_message(msg.chat.id,
        f"✅ {msg.text} tanlandi!\n\n"
        "🔜 Ko'p tilli tizim tez orada to'liq ishga tushadi.\n"
        "Hozircha bot O'zbek tilida ishlaydi.",
        reply_markup=main_menu())

# ── Namoz vaqtlari ───────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text == "🕌 Namoz vaqtlari")
def prayer_req(msg):
    user_mode[msg.chat.id] = "prayer"
    bot.send_message(msg.chat.id,
        "📍 <b>Namoz vaqtlarini hisoblash uchun</b>\nJoylashuvingizni yuboring:",
        parse_mode="HTML", reply_markup=loc_menu())

# ── Qibla ────────────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text == "🧭 Qibla")
def qibla_req(msg):
    user_mode[msg.chat.id] = "qibla"
    bot.send_message(msg.chat.id,
        "🧭 <b>Qibla yo'nalishi</b>\n\nJoylashuvingizni yuboring:",
        parse_mode="HTML", reply_markup=loc_menu())

# ── Yaqin masjidlar ──────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text == "📍 Yaqin masjidlar")
def masjid_req(msg):
    user_mode[msg.chat.id] = "masjid"
    bot.send_message(msg.chat.id,
        "🕌 <b>Yaqin masjidlarni topish</b>\n\nJoylashuvingizni yuboring:",
        parse_mode="HTML", reply_markup=loc_menu())

# ── Lokatsiya handler ─────────────────────────────────────────
@bot.message_handler(content_types=["location"])
def loc_handler(msg):
    cid = msg.chat.id
    lat = msg.location.latitude
    lon = msg.location.longitude
    mode = user_mode.get(cid)

    # QIBLA
    if mode == "qibla":
        try:
            angle = calc_qibla(lat, lon); direction = compass(angle)
            mk = types.InlineKeyboardMarkup()
            mk.add(types.InlineKeyboardButton("🗺 Google Mapda ko'rish",
                url=f"https://www.google.com/maps/dir/{lat},{lon}/{KAABA_LAT},{KAABA_LON}"))
            bot.send_message(cid,
                f"🧭 <b>QIBLA YO'NALISHI</b>\n\n"
                f"📐 Burchak: <b>{angle:.1f}°</b>\n"
                f"🧭 Yo'nalish: <b>{direction}</b>\n\n"
                f"<i>Kompas ilovasida {angle:.0f}° tomonga qarang.</i>",
                parse_mode="HTML", reply_markup=mk)
        except Exception:
            bot.send_message(cid, "❌ Qiblani hisoblashda xatolik.")
        bot.send_message(cid, "🏠 Asosiy menyu", reply_markup=main_menu())
        user_mode.pop(cid, None)
        return

    # MASJIDLAR
    if mode == "masjid":
        bot.send_message(cid, "🔍 Yaqin masjidlar qidirilmoqda...")
        try:
            r = requests.get("https://overpass-api.de/api/interpreter",
                params={"data": f"""[out:json][timeout:15];
                    (node["amenity"="place_of_worship"]["religion"="muslim"](around:3000,{lat},{lon});
                     way["amenity"="place_of_worship"]["religion"="muslim"](around:3000,{lat},{lon}););
                    out center 10;"""}, timeout=20)
            els = r.json().get("elements", [])
            if not els:
                raise ValueError("not found")
            txt = "🕌 <b>YAQIN MASJIDLAR</b>\n\n"
            mk = types.InlineKeyboardMarkup(row_width=1)
            for i, el in enumerate(els[:8], 1):
                elat = el.get("lat") or el.get("center", {}).get("lat")
                elon = el.get("lon") or el.get("center", {}).get("lon")
                if elat is None or elon is None:
                    continue
                name = el.get("tags", {}).get("name") or f"Masjid {i}"
                dist = haversine(lat, lon, elat, elon)
                txt += f"<b>{i}.</b> {name}\n📏 {dist:.0f} m\n\n"
                mk.add(types.InlineKeyboardButton(f"🗺 {i}. {name[:28]}",
                    url=f"https://www.google.com/maps/dir/{lat},{lon}/{elat},{elon}"))
            bot.send_message(cid, txt, parse_mode="HTML")
            bot.send_message(cid, "👆 Masjid nomini bosib yo'l olishingiz mumkin:", reply_markup=mk)
        except Exception:
            mk = types.InlineKeyboardMarkup()
            mk.add(types.InlineKeyboardButton("🗺 Google Mapsda qidirish",
                url=f"https://www.google.com/maps/search/masjid/@{lat},{lon},14z"))
            bot.send_message(cid, "🕌 <b>Yaqin masjidlar:</b>", parse_mode="HTML", reply_markup=mk)
        bot.send_message(cid, "🏠 Asosiy menyu", reply_markup=main_menu())
        user_mode.pop(cid, None)
        return

    # NAMOZ VAQTLARI
    if mode == "prayer":
        try:
            r = requests.get(f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=3", timeout=10)
            d = r.json()["data"]; t = d["timings"]
            city = get_city(lat, lon)
            tz = ZoneInfo(d["meta"]["timezone"]); now = datetime.now(tz)
            prayers = [("Bomdod", "🌅", t["Fajr"]), ("Peshin", "🕛", t["Dhuhr"]),
                       ("Asr", "🌇", t["Asr"]), ("Shom", "🌆", t["Maghrib"]), ("Xufton", "🌙", t["Isha"])]
            nname, nemoji, nleft = "Bomdod", "🌅", ""
            for pn, pe, pt in prayers:
                h, mn = map(int, pt.split(":")[:2])
                pdt = now.replace(hour=h, minute=mn, second=0, microsecond=0)
                if pdt > now:
                    diff = pdt - now; hrs = diff.seconds // 3600; mins = (diff.seconds % 3600) // 60
                    nname, nemoji, nleft = pn, pe, f"{hrs} soat {mins} daqiqa"
                    break
            if not nleft:
                h, mn = map(int, t["Fajr"].split(":")[:2])
                tom = (now + timedelta(days=1)).replace(hour=h, minute=mn, second=0, microsecond=0)
                diff = tom - now; hrs = diff.seconds // 3600; mins = (diff.seconds % 3600) // 60
                nleft = f"{hrs} soat {mins} daqiqa (ertaga)"
            q = random.choice(QURAN_QUOTES); hd = random.choice(HADITH_QUOTES)
            bot.send_message(cid,
                f"🕌 <b>NAMOZ VAQTLARI</b>\n\n"
                f"📍 <b>{city}</b>\n"
                f"📅 <b>{d['date']['readable']}</b>\n\n"
                f"🌅 Bomdod  — <b>{t['Fajr']}</b>\n"
                f"🌄 Quyosh  — <b>{t['Sunrise']}</b>\n"
                f"🕛 Peshin  — <b>{t['Dhuhr']}</b>\n"
                f"🌇 Asr     — <b>{t['Asr']}</b>\n"
                f"🌆 Shom    — <b>{t['Maghrib']}</b>\n"
                f"🌙 Xufton  — <b>{t['Isha']}</b>\n\n"
                f"⏳ <b>Keyingi namoz:</b>\n"
                f"{nemoji} <b>{nname}</b> — {nleft} qoldi\n\n"
                f"━━━━━━━━━━━━━━\n"
                f"📖 <b>BUGUNGI OYAT</b>\n"
                f"❝ {q['text']} ❞\n"
                f"<b>{q['source']}</b>\n\n"
                f"━━━━━━━━━━━━━━\n"
                f"📚 <b>BUGUNGI HADIS</b>\n"
                f"❝ {hd['text']} ❞\n"
                f"<b>{hd['source']}</b>\n\n"
                f"🤲 <i>Alloh namozlaringizni qabul qilsin.</i>",
                parse_mode="HTML", reply_markup=main_menu())
        except Exception:
            bot.send_message(cid, "❌ Namoz vaqtlarini olishda xatolik. Internetni tekshiring.", reply_markup=main_menu())
        user_mode.pop(cid, None)
        return

    bot.send_message(cid, "Iltimos, avval menyudan bo'limni tanlang.", reply_markup=main_menu())

# ── Qur'on ───────────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text == "📖 Qur'on")
def quran_h(msg):
    show_quran(msg.chat.id, 0)

@bot.message_handler(func=lambda m: m.text == "➡️ Keyingi sahifa")
def quran_next(msg):
    cid = msg.chat.id; p = user_quran_page.get(cid, 0)
    total = (len(QURAN_SURAHS) + QPAGE - 1) // QPAGE
    if p + 1 < total:
        show_quran(cid, p + 1)

@bot.message_handler(func=lambda m: m.text == "⬅️ Oldingi sahifa")
def quran_prev(msg):
    cid = msg.chat.id; p = user_quran_page.get(cid, 0)
    if p > 0:
        show_quran(cid, p - 1)

# ── Hadislar ─────────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text == "📚 Hadislar")
def hadislar(msg):
    bot.send_message(msg.chat.id,
        "📚 <b>HADISLAR TO'PLAMI</b>\n\nBo'limni tanlang:",
        parse_mode="HTML", reply_markup=hadith_sections_menu())

@bot.message_handler(func=lambda m: m.text in [
    "🌸 Odob-axloq", "👨‍👩‍👧 Ota-ona va oila", "📚 Ilm va hikmat", "🕌 Namoz va ibodat",
    "💛 Sahovat", "🤝 Birlik", "🌿 Tavba", "🌍 Dunyo va oxirat"])
def hadith_sec(msg):
    mp = {"🌸 Odob-axloq": "odob", "👨‍👩‍👧 Ota-ona va oila": "ota_ona",
          "📚 Ilm va hikmat": "ilm", "🕌 Namoz va ibodat": "namoz",
          "💛 Sahovat": "sahovat", "🤝 Birlik": "birlik",
          "🌿 Tavba": "tavba", "🌍 Dunyo va oxirat": "dunyo"}
    k = mp[msg.text]; user_hadith_sec[msg.chat.id] = k; user_hadith_idx[msg.chat.id] = 0
    show_hadith(msg.chat.id, k, 0)

@bot.message_handler(func=lambda m: m.text == "➡️ Keyingi hadis")
def hn(msg):
    cid = msg.chat.id; k = user_hadith_sec.get(cid, "odob")
    idx = user_hadith_idx.get(cid, 0) + 1
    if idx >= len(HADITH_SECTIONS[k]["hadiths"]):
        idx = 0
    show_hadith(cid, k, idx)

@bot.message_handler(func=lambda m: m.text == "⬅️ Oldingi hadis")
def hp(msg):
    cid = msg.chat.id; k = user_hadith_sec.get(cid, "odob")
    idx = user_hadith_idx.get(cid, 0) - 1
    if idx < 0:
        idx = len(HADITH_SECTIONS[k]["hadiths"]) - 1
    show_hadith(cid, k, idx)

@bot.message_handler(func=lambda m: m.text == "📋 Hadis bo'limlari")
def hback(msg):
    bot.send_message(msg.chat.id, "📚 Bo'limni tanlang:", reply_markup=hadith_sections_menu())

# ── Duolar ───────────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text == "🤲 Duolar")
def duolar(msg):
    bot.send_message(msg.chat.id,
        "📿 <b>DUOLAR TO'PLAMI</b>\n\nBo'limni tanlang:",
        parse_mode="HTML", reply_markup=dua_sections_menu())

@bot.message_handler(func=lambda m: m.text in [
    "🌅 Ertalabki duolar", "🌙 Kechki duolar", "🕌 Namoz duolari",
    "🍽 Dasturxon duolari", "🚶 Ko'cha va safar", "🤲 Maxsus duolar"])
def dua_sec(msg):
    mp = {"🌅 Ertalabki duolar": "ertalab", "🌙 Kechki duolar": "kechki",
          "🕌 Namoz duolari": "namoz", "🍽 Dasturxon duolari": "dasturxon",
          "🚶 Ko'cha va safar": "kocha", "🤲 Maxsus duolar": "maxsus"}
    k = mp[msg.text]; user_dua_sec[msg.chat.id] = k; user_dua_idx[msg.chat.id] = 0
    show_dua(msg.chat.id, k, 0)

@bot.message_handler(func=lambda m: m.text == "➡️ Keyingi duo")
def dn(msg):
    cid = msg.chat.id; k = user_dua_sec.get(cid, "ertalab")
    idx = user_dua_idx.get(cid, 0) + 1
    if idx >= len(DUA_SECTIONS[k]["duas"]):
        idx = 0
    show_dua(cid, k, idx)

@bot.message_handler(func=lambda m: m.text == "⬅️ Oldingi duo")
def dp(msg):
    cid = msg.chat.id; k = user_dua_sec.get(cid, "ertalab")
    idx = user_dua_idx.get(cid, 0) - 1
    if idx < 0:
        idx = len(DUA_SECTIONS[k]["duas"]) - 1
    show_dua(cid, k, idx)

@bot.message_handler(func=lambda m: m.text == "📋 Duo bo'limlari")
def dback(msg):
    bot.send_message(msg.chat.id, "📿 Bo'limni tanlang:", reply_markup=dua_sections_menu())

# ── Zikr & Salovatlar ────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text == "📿 Zikr & Salovatlar")
def zikr_h(msg):
    bot.send_message(msg.chat.id, "📿 <b>ZIKR & SALOVATLAR</b>\n\nBo'limni tanlang:",
        parse_mode="HTML", reply_markup=zikr_menu())

@bot.message_handler(func=lambda m: m.text == "📿 Istig'for")
def istigfor(msg):
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("📿 Bosing — 0", callback_data="zk_click"))
    mk.add(types.InlineKeyboardButton("🔄 Nolga", callback_data="zk_reset"))
    user_zikr_count[msg.chat.id] = 0; user_zikr_type[msg.chat.id] = "istigfor"
    bot.send_message(msg.chat.id,
        "📿 <b>ISTIG'FOR TASBEH</b>\n\n"
        "<b>أَسْتَغْفِرُ اللّٰهَ</b>\n\n"
        "✍️ <i>Astagfirulloh</i>\n\n"
        "💡 Allohdan gunohlarimni kechirishini so'rayman.\n\n"
        "👇 Bosib hisoblang:",
        parse_mode="HTML", reply_markup=mk)

@bot.message_handler(func=lambda m: m.text == "🤲 Salavot")
def salavot(msg):
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🤲 Bosing — 0", callback_data="zk_click"))
    mk.add(types.InlineKeyboardButton("🔄 Nolga", callback_data="zk_reset"))
    user_zikr_count[msg.chat.id] = 0; user_zikr_type[msg.chat.id] = "salavot"
    bot.send_message(msg.chat.id,
        "🤲 <b>SALAVOT TASBEH</b>\n\n"
        "<b>اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ</b>\n\n"
        "✍️ <i>Allohumma solli ala Muhammad</i>\n\n"
        "💡 Allohim, Muhammad alayhissalomga salovat yubor.\n\n"
        "👇 Bosib hisoblang:",
        parse_mode="HTML", reply_markup=mk)

@bot.message_handler(func=lambda m: m.text == "🌟 Kalimalar")
def kalimalar(msg):
    bot.send_message(msg.chat.id,
        "🌟 <b>KALIMAI TOYYIBA</b>\n\n"
        "<b>لَا إِلٰهَ إِلَّا اللّٰهُ مُحَمَّدٌ رَسُولُ اللّٰهِ</b>\n\n"
        "✍️ <i>La ilaha illalloh Muhammadur rasululloh</i>\n\n"
        "💡 <b>Ma'nosi:</b>\nAllohdan o'zga iloh yo'q va Muhammad Uning elchisidir.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "🌟 <b>KALIMAI SHAHODAT</b>\n\n"
        "<b>أَشْهَدُ أَنْ لَا إِلٰهَ إِلَّا اللّٰهُ وَأَشْهَدُ أَنَّ مُحَمَّدًا عَبْدُهُ وَرَسُولُهُ</b>\n\n"
        "✍️ <i>Ashhadu alla ilaha illalloh va ashhadu anna Muhammadan abduhu va rasuluh</i>\n\n"
        "💡 Allohdan o'zga haq iloh yo'qligiga va Muhammad Uning bandasi va elchisi ekanligiga guvohlik beraman.\n\n"
        "🤲 <i>Alloh bizni kalimada sobit qilsin!</i>",
        parse_mode="HTML", reply_markup=zikr_menu())

@bot.message_handler(func=lambda m: m.text == "📖 Tasbeh")
def tasbeh(msg):
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("📿 Subhanallah — 0", callback_data="zk_click"))
    mk.add(types.InlineKeyboardButton("🔄 Nolga", callback_data="zk_reset"))
    user_zikr_count[msg.chat.id] = 0; user_zikr_type[msg.chat.id] = "tasbeh"
    bot.send_message(msg.chat.id,
        "📿 <b>TASBEH</b>\n\n"
        "<b>سُبْحَانَ اللَّهِ</b>\n\n"
        "✍️ <i>Subhanalloh</i>\n\n"
        "💡 Alloh pokdir va har qanday nuqsondan uzokdir.\n\n"
        "👇 Bosib hisoblang:",
        parse_mode="HTML", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data in ["zk_click", "zk_reset"])
def zikr_cb(call):
    cid = call.message.chat.id
    if call.data == "zk_reset":
        user_zikr_count[cid] = 0
    else:
        user_zikr_count[cid] = user_zikr_count.get(cid, 0) + 1
    cnt = user_zikr_count[cid]; zt = user_zikr_type.get(cid, "istigfor")
    labels = {"istigfor": ("📿 Istig'for", "أَسْتَغْفِرُ اللّٰهَ", "Astagfirulloh"),
              "salavot": ("🤲 Salavot", "اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ", "Allohumma solli ala Muhammad"),
              "tasbeh": ("📿 Tasbeh", "سُبْحَانَ اللَّهِ", "Subhanalloh")}
    lbl, arabic, latin = labels.get(zt, labels["istigfor"])
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton(f"📿 Bosing — {cnt}", callback_data="zk_click"))
    mk.add(types.InlineKeyboardButton("🔄 Nolga", callback_data="zk_reset"))
    bonus = ""
    if cnt == 33:
        bonus = "\n\n🎉 <b>33 ta to'ldi! Alhamdulillah!</b>"
    elif cnt == 99:
        bonus = "\n\n✨ <b>99 ta to'ldi! Allahu Akbar!</b>"
    elif cnt == 100:
        bonus = "\n\n🌟 <b>100 ta to'ldi! MashAllah!</b>"
    try:
        bot.edit_message_text(
            f"{lbl}\n\n<b>{arabic}</b>\n\n✍️ <i>{latin}</i>\n\n"
            f"📿 <b>Sanoq: {cnt}</b>{bonus}",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=mk)
    except Exception:
        pass

# ── Allohning 99 ismi ────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text == "🕋 Allohning 99 ismi")
def names99(msg):
    user_name_idx[msg.chat.id] = 0
    show_name(msg.chat.id, 0)

@bot.message_handler(func=lambda m: m.text == "➡️ Keyingi")
def nname(msg):
    cid = msg.chat.id; idx = user_name_idx.get(cid, 0)
    if idx < len(ALLAH_NAMES) - 1:
        idx += 1
    user_name_idx[cid] = idx
    show_name(cid, idx)

@bot.message_handler(func=lambda m: m.text == "⬅️ Oldingi")
def pname(msg):
    cid = msg.chat.id; idx = user_name_idx.get(cid, 0)
    if idx > 0:
        idx -= 1
    user_name_idx[cid] = idx
    show_name(cid, idx)

# ── Hijriy taqvim ────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text == "📅 Hijriy taqvim")
def hijri_h(msg):
    try:
        show_hijri(msg.chat.id, datetime.now())
    except Exception:
        bot.send_message(msg.chat.id, "❌ Hijriy taqvimni yuklashda xatolik.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📌 Muhim islomiy sanalar")
def imp_dates(msg):
    try:
        dates = next_dates(datetime.now())
        txt = "📌 <b>MUHIM ISLOMIY SANALAR</b>\n\n"
        for d in dates[:8]:
            txt += f"{d['title']}\n⏳ <b>{d['days_left']}</b> kun qoldi\n\n"
        bot.send_message(msg.chat.id, txt, parse_mode="HTML", reply_markup=hijri_menu())
    except Exception:
        bot.send_message(msg.chat.id, "❌ Xatolik yuz berdi.", reply_markup=main_menu())

# ── Sozlamalar ───────────────────────────────────────────────
@bot.message_handler(func=lambda m: m.text == "⚙️ Sozlamalar")
def soz(msg):
    bot.send_message(msg.chat.id, "⚙️ <b>SOZLAMALAR</b>", parse_mode="HTML", reply_markup=settings_menu())

@bot.message_handler(func=lambda m: m.text == "🌐 Tilni o'zgartirish")
def lang(msg):
    bot.send_message(msg.chat.id, "🌍 Tilni tanlang:", reply_markup=language_menu())

@bot.message_handler(func=lambda m: m.text == "🔔 Namoz eslatmalari")
def reminder(msg):
    bot.send_message(msg.chat.id,
        "🔔 <b>Namoz eslatmalari</b>\n\n"
        "✅ Eslatmalar tizimi tez orada ishga tushadi!\n\n"
        "Hozircha 🕌 Namoz vaqtlari bo'limidan tekshirishingiz mumkin.",
        parse_mode="HTML", reply_markup=settings_menu())

@bot.message_handler(func=lambda m: m.text == "📍 Lokatsiyani yangilash")
def upd_loc(msg):
    user_mode[msg.chat.id] = "prayer"
    bot.send_message(msg.chat.id, "📍 Yangi joylashuvingizni yuboring:", reply_markup=loc_menu())

@bot.message_handler(func=lambda m: m.text == "🎧 Qori tanlash")
def qori(msg):
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🎙 Mishary Rashid Al-Afasy", callback_data="qori_mishary"))
    mk.add(types.InlineKeyboardButton("🎙 Abdulbosit Abdussamad", callback_data="qori_abdulbosit"))
    mk.add(types.InlineKeyboardButton("🎙 Maher Al-Mueaqly", callback_data="qori_maher"))
    bot.send_message(msg.chat.id, "🎧 <b>Qori tanlang:</b>", parse_mode="HTML", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("qori_"))
def qori_cb(call):
    names = {"qori_mishary": "Mishary Rashid Al-Afasy",
             "qori_abdulbosit": "Abdulbosit Abdussamad",
             "qori_maher": "Maher Al-Mueaqly"}
    bot.send_message(call.message.chat.id,
        f"✅ <b>{names.get(call.data, 'Qori')} tanlandi!</b>\n\n"
        "Qur'on bo'limida shu qori ovozida tinglashingiz mumkin.",
        parse_mode="HTML", reply_markup=settings_menu())

@bot.message_handler(func=lambda m: m.text == "ℹ️ Bot haqida")
def about(msg):
    bot.send_message(msg.chat.id,
        "ℹ️ <b>ISLAM TIME WORLD BOT</b>\n\n"
        "📌 Versiya: 2.1\n\n"
        "✅ Namoz vaqtlari (GPS)\n"
        "✅ Qibla yo'nalishi\n"
        "✅ Yaqin masjidlar (Overpass API)\n"
        "✅ Qur'on — 114 sura\n"
        "✅ Hadislar — 8 bo'lim, 60+ hadis\n"
        "✅ Duolar — 6 bo'lim, 39+ duo\n"
        "✅ Zikr tasbeh (interaktiv)\n"
        "✅ Allohning 99 ismi\n"
        "✅ Hijriy taqvim\n"
        "✅ 12 ta til\n\n"
        "🤲 <i>Alloh bu botni barcha uchun foydali qilsin!</i>",
        parse_mode="HTML", reply_markup=settings_menu())

@bot.message_handler(func=lambda m: m.text == "📞 Murojaat")
def contact(msg):
    bot.send_message(msg.chat.id,
        "📞 <b>Murojaat</b>\n\n"
        "Taklif yoki xatoliklar uchun:\n"
        "✉️ @IslamTimeWorldSupport\n\n"
        "🤲 <i>Barcha murojaat va takliflaringiz qabul qilinadi!</i>",
        parse_mode="HTML", reply_markup=settings_menu())

# ── Noma'lum xabar ───────────────────────────────────────────
@bot.message_handler(func=lambda m: True)
def unknown(msg):
    bot.send_message(msg.chat.id, "Iltimos, menyudan kerakli bo'limni tanlang. 👇", reply_markup=main_menu())

# ═══════════════════════════════════════════════════════════════
#  ISHGA TUSHIRISH
# ═══════════════════════════════════════════════════════════════
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ IslamTimeWorldBot v2.1 ishga tushdi!")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
        except Exception as e:
            print(f"⚠️ Polling xatosi: {e}. 5 soniyadan keyin qayta...")
            import time
            time.sleep(5)
