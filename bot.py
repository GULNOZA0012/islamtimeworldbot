import os
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


QURAN_QUOTES = [
    {"text": "Albatta, namoz mo'minlarga vaqtida farz qilingandir.", "source": "An-Niso, 103-oyat", "note": "Qisqa mazmun"},
    {"text": "Namozlarni va ayniqsa o'rta namozni saqlanglar.", "source": "Baqara, 238-oyat", "note": "Qisqa mazmun"},
    {"text": "Meni zikr qilish uchun namozni to'kis ado et.", "source": "Toha, 14-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, namoz fahsh va munkar ishlardan qaytaradi.", "source": "Ankabut, 45-oyat", "note": "Qisqa mazmun"},
    {"text": "Robbingizdan yordamni sabr va namoz bilan so'ranglar.", "source": "Baqara, 45-oyat", "note": "Qisqa mazmun"},
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
    {"text": "Har bir jon o'limni totuvchidir.", "source": "Oli Imron, 185-oyat", "note": "Qisqa mazmun"},
    {"text": "Yaxshilik va taqvoda hamkorlik qilinglar.", "source": "Moida, 2-oyat", "note": "Qisqa mazmun"},
    {"text": "Alloh bilan birga bo'linglar.", "source": "Tavba, 119-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, Alloh shukr qiluvchilarni mukofotlaydi.", "source": "Oli Imron, 144-oyat", "note": "Qisqa mazmun"},
    {"text": "Kim bir yaxshilik qilsa, o'n barobar mukofot oladi.", "source": "An'om, 160-oyat", "note": "Qisqa mazmun"},
    {"text": "Allohning rahmatidan noumid bo'lmanglar.", "source": "Zumar, 53-oyat", "note": "Qisqa mazmun"},
    {"text": "Rabbingiz mag'firati tomon shoshilinglar.", "source": "Oli Imron, 133-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, Alloh mo'minlarning do'stidir.", "source": "Oli Imron, 68-oyat", "note": "Qisqa mazmun"},
    {"text": "Albatta, Alloh bilan bo'lganlar g'olib bo'ladilar.", "source": "Moida, 56-oyat", "note": "Qisqa mazmun"},
]


HADITH_QUOTES = [
    {"text": "Kim bomdod namozini o'qisa, Allohning himoyasida bo'ladi.", "source": "Sahih Muslim, 657a"},
    {"text": "Amallar niyatlarga bog'liqdir.", "source": "Sahih Buxoriy, 1"},
    {"text": "Musulmon — boshqa musulmonlar uning tili va qo'lidan omonda bo'lgan kishidir.", "source": "Sahih Buxoriy, 10"},
    {"text": "Sizlardan hech biringiz o'zi uchun yaxshi ko'rgan narsani birodari uchun ham yaxshi ko'rmaguncha to'liq mo'min bo'la olmaydi.", "source": "Sahih Buxoriy, 13"},
    {"text": "Kim Allohga va oxirat kuniga iymon keltirgan bo'lsa, yaxshi gapirsin yoki sukut qilsin.", "source": "Sahih Buxoriy, 6018"},
    {"text": "Poklik iymonning yarmidir.", "source": "Sahih Muslim, 223"},
    {"text": "Namoz nurdir.", "source": "Sahih Muslim, 223"},
    {"text": "Sabr ziyodir.", "source": "Sahih Muslim, 223"},
    {"text": "Qur'on sening foydangga yoki zararingga hujjat bo'ladi.", "source": "Sahih Muslim, 223"},
    {"text": "Sizlarning eng yaxshilaringiz Qur'onni o'rganib, uni boshqalarga o'rgatganlaringizdir.", "source": "Sahih Buxoriy, 5027"},
    {"text": "Jamoat bilan o'qilgan namoz yolg'iz o'qilgan namozdan yigirma yetti daraja afzaldir.", "source": "Sahih Buxoriy, 645"},
    {"text": "Rahm qilmagan kishiga rahm qilinmaydi.", "source": "Sahih Buxoriy, 5997"},
    {"text": "Alloh go'zaldir va go'zallikni sevadi.", "source": "Sahih Muslim, 91a"},
    {"text": "Alloh mehribon va yumshoqlikni sevadi.", "source": "Sahih Muslim, 2593"},
    {"text": "Alloh sizlarning suratlaringizga va mol-dunyolaringizga emas, qalblaringiz va amallaringizga qaraydi.", "source": "Sahih Muslim, 2564"},
    {"text": "Halol aniq, harom ham aniqdir.", "source": "Sahih Buxoriy, 52"},
    {"text": "Musulmon musulmonning birodaridir.", "source": "Sahih Buxoriy, 2442"},
    {"text": "Kim birodarining hojatini chiqarsa, Alloh uning hojatini chiqaradi.", "source": "Sahih Buxoriy, 2442"},
    {"text": "Kim musulmonning bir g'amini ketkazsa, Alloh qiyomat kuni uning g'amlaridan birini ketkazadi.", "source": "Sahih Buxoriy, 2442"},
    {"text": "Kim bir musulmonning aybini yopsa, Alloh qiyomat kuni uning aybini yopadi.", "source": "Sahih Buxoriy, 2442"},
    {"text": "Kim ilm izlash yo'liga kirsa, Alloh unga jannat yo'lini oson qiladi.", "source": "Sahih Muslim, 2699"},
    {"text": "Kim bir mo'minning dunyo g'amlaridan birini yengillatsa, Alloh uning qiyomat kunidagi g'amlaridan birini yengillatadi.", "source": "Sahih Muslim, 2699"},
    {"text": "Kim qiynalgan kishiga yengillik qilsa, Alloh unga dunyo va oxiratda yengillik qiladi.", "source": "Sahih Muslim, 2699"},
    {"text": "Alloh banda birodariga yordam berar ekan, bandaga yordam berishda davom etadi.", "source": "Sahih Muslim, 2699"},
    {"text": "Qarindoshlik aloqasini bog'lagan kishining rizqi kengayadi va umri barakali bo'ladi.", "source": "Sahih Buxoriy, 5986"},
    {"text": "Kim menga ikki jag'i orasidagi narsani va ikki oyog'i orasidagi narsani kafolat qilsa, men unga jannatni kafolat qilaman.", "source": "Sahih Buxoriy, 6474"},
    {"text": "Allohga eng sevimli amal oz bo'lsa ham davomli bo'lgan amaldir.", "source": "Sahih Buxoriy, 6464"},
    {"text": "Mo'minning ishi ajablanarlidir: uning har bir holatida yaxshilik bor.", "source": "Sahih Muslim, 2999"},
    {"text": "Kuchli mo'min Allohga zaif mo'mindan ko'ra yaxshiroq va suyukliroqdir.", "source": "Sahih Muslim, 2664"},
    {"text": "Haqiqiy kuchli kishi kurashda yenggan emas, g'azab paytida o'zini tutgan kishidir.", "source": "Sahih Buxoriy, 6114"},
    {"text": "Ikki kalima bor: tilga yengil, tarozida og'ir va Rahmonga suyuklidir.", "source": "Sahih Buxoriy, 6682; Sahih Muslim, 2694"},
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
    {"arabic": "الْبَارِئُ", "latin": "Al-Bari", "meaning": "Yo'qdan bor qiluvchi Zot.", "zikr": "Ya Bari"},
    {"arabic": "الْمُصَوِّرُ", "latin": "Al-Musawwir", "meaning": "Har bir narsaga surat beruvchi Zot.", "zikr": "Ya Musawwir"},
    {"arabic": "الْغَفَّارُ", "latin": "Al-Ghaffar", "meaning": "Ko'p mag'firat qiluvchi Zot.", "zikr": "Ya Ghaffar"},
    {"arabic": "الْقَهَّارُ", "latin": "Al-Qahhar", "meaning": "Hammani bo'ysundiruvchi Zot.", "zikr": "Ya Qahhar"},
    {"arabic": "الْوَهَّابُ", "latin": "Al-Wahhab", "meaning": "Cheksiz ne'matlar beruvchi Zot.", "zikr": "Ya Wahhab"},
    {"arabic": "الرَّزَّاقُ", "latin": "Ar-Razzaq", "meaning": "Rizq beruvchi Zot.", "zikr": "Ya Razzaq"},
    {"arabic": "الْفَتَّاحُ", "latin": "Al-Fattah", "meaning": "Yaxshilik eshiklarini ochuvchi Zot.", "zikr": "Ya Fattah"},
    {"arabic": "اَلْعَلِيمُ", "latin": "Al-Alim", "meaning": "Har narsani biluvchi Zot.", "zikr": "Ya Alim"},
    {"arabic": "الْقَابِضُ", "latin": "Al-Qabid", "meaning": "Rizqni toraytiruvchi Zot.", "zikr": "Ya Qabid"},
    {"arabic": "الْبَاسِطُ", "latin": "Al-Basit", "meaning": "Rizqni kengaytiruvchi Zot.", "zikr": "Ya Basit"},
    {"arabic": "الْخَافِضُ", "latin": "Al-Khafid", "meaning": "Pasaytiruvchi Zot.", "zikr": "Ya Khafid"},
    {"arabic": "الرَّافِعُ", "latin": "Ar-Rafi", "meaning": "Yuksaltiruvchi Zot.", "zikr": "Ya Rafi"},
    {"arabic": "الْمُعِزُّ", "latin": "Al-Mu'izz", "meaning": "Aziz qiluvchi Zot.", "zikr": "Ya Mu'izz"},
    {"arabic": "الْمُذِلُّ", "latin": "Al-Muzill", "meaning": "Xor qiluvchi Zot.", "zikr": "Ya Muzill"},
    {"arabic": "السَّمِيعُ", "latin": "As-Sami", "meaning": "Barcha narsani eshituvchi Zot.", "zikr": "Ya Sami"},
    {"arabic": "الْبَصِيرُ", "latin": "Al-Basir", "meaning": "Barcha narsani ko'ruvchi Zot.", "zikr": "Ya Basir"},
    {"arabic": "الْحَكَمُ", "latin": "Al-Hakam", "meaning": "Adolat bilan hukm qiluvchi Zot.", "zikr": "Ya Hakam"},
    {"arabic": "الْعَدْلُ", "latin": "Al-Adl", "meaning": "Mutlaq adolat egasi.", "zikr": "Ya Adl"},
    {"arabic": "اللَّطِيفُ", "latin": "Al-Latif", "meaning": "Bandalariga lutf va marhamat ko'rsatuvchi Zot.", "zikr": "Ya Latif"},
    {"arabic": "الْخَبِيرُ", "latin": "Al-Khabir", "meaning": "Har narsaning ichki sirlaridan xabardor Zot.", "zikr": "Ya Khabir"},
    {"arabic": "الْحَلِيمُ", "latin": "Al-Halim", "meaning": "Shoshilmay jazo bermaydigan Zot.", "zikr": "Ya Halim"},
    {"arabic": "الْعَظِيمُ", "latin": "Al-Azim", "meaning": "Buyuk va ulug' Zot.", "zikr": "Ya Azim"},
    {"arabic": "الْغَفُورُ", "latin": "Al-Ghafur", "meaning": "Ko'p kechiruvchi Zot.", "zikr": "Ya Ghafur"},
    {"arabic": "الشَّكُورُ", "latin": "Ash-Shakur", "meaning": "Oz amal uchun ham ko'p mukofot beruvchi Zot.", "zikr": "Ya Shakur"},
    {"arabic": "الْعَلِيُّ", "latin": "Al-Aliyy", "meaning": "Eng oliy martaba egasi.", "zikr": "Ya Aliyy"},
    {"arabic": "الْكَبِيرُ", "latin": "Al-Kabir", "meaning": "Eng buyuk Zot.", "zikr": "Ya Kabir"},
    {"arabic": "الْحَفِيظُ", "latin": "Al-Hafiz", "meaning": "Asrovchi va saqlovchi Zot.", "zikr": "Ya Hafiz"},
    {"arabic": "الْمُقِيتُ", "latin": "Al-Muqit", "meaning": "Barcha mavjudotlarga rizq yetkazuvchi Zot.", "zikr": "Ya Muqit"},
    {"arabic": "الْحسِيبُ", "latin": "Al-Hasib", "meaning": "Hisob-kitob qiluvchi Zot.", "zikr": "Ya Hasib"},
    {"arabic": "الْجَلِيلُ", "latin": "Al-Jalil", "meaning": "Ulug'vorlik egasi.", "zikr": "Ya Jalil"},
    {"arabic": "الْكَرِيمُ", "latin": "Al-Karim", "meaning": "Saxovatli va karamli Zot.", "zikr": "Ya Karim"},
    {"arabic": "الرَّقِيبُ", "latin": "Ar-Raqib", "meaning": "Har narsani kuzatib turuvchi Zot.", "zikr": "Ya Raqib"},
    {"arabic": "الْمُجِيبُ", "latin": "Al-Mujib", "meaning": "Duolarga javob beruvchi Zot.", "zikr": "Ya Mujib"},
    {"arabic": "الْوَاسِعُ", "latin": "Al-Wasi", "meaning": "Rahmati va ilmi keng Zot.", "zikr": "Ya Wasi"},
    {"arabic": "الْحَكِيمُ", "latin": "Al-Hakim", "meaning": "Hikmat egasi Zot.", "zikr": "Ya Hakim"},
    {"arabic": "الْوَدُودُ", "latin": "Al-Wadud", "meaning": "Bandalarini sevuvchi Zot.", "zikr": "Ya Wadud"},
    {"arabic": "الْمَجِيدُ", "latin": "Al-Majid", "meaning": "Sharaf va ulug'lik egasi.", "zikr": "Ya Majid"},
    {"arabic": "الْبَاعِثُ", "latin": "Al-Baith", "meaning": "Tirilitiruvchi Zot.", "zikr": "Ya Baith"},
    {"arabic": "الشَّهِيدُ", "latin": "Ash-Shahid", "meaning": "Har narsaga guvoh Zot.", "zikr": "Ya Shahid"},
    {"arabic": "الْحَقُّ", "latin": "Al-Haqq", "meaning": "Mutlaq Haqiqat Zot.", "zikr": "Ya Haqq"},
    {"arabic": "الْوَكِيلُ", "latin": "Al-Wakil", "meaning": "Ishlarni boshqaruvchi va vakil Zot.", "zikr": "Ya Wakil"},
    {"arabic": "الْقَوِيُّ", "latin": "Al-Qawiyy", "meaning": "Cheksiz qudrat egasi.", "zikr": "Ya Qawiyy"},
    {"arabic": "الْمَتِينُ", "latin": "Al-Matin", "meaning": "Juda mustahkam va qudratli Zot.", "zikr": "Ya Matin"},
    {"arabic": "الْوَلِيُّ", "latin": "Al-Waliyy", "meaning": "Mo'minlarning do'sti va yordamchisi.", "zikr": "Ya Waliyy"},
    {"arabic": "الْحَمِيدُ", "latin": "Al-Hamid", "meaning": "Hamd va maqtovga loyiq Zot.", "zikr": "Ya Hamid"},
    {"arabic": "الْمُحْصِي", "latin": "Al-Muhsi", "meaning": "Har narsani sanab biluvchi Zot.", "zikr": "Ya Muhsi"},
    {"arabic": "الْمُبْدِئُ", "latin": "Al-Mubdi", "meaning": "Yaratishni boshlovchi Zot.", "zikr": "Ya Mubdi"},
    {"arabic": "الْمُعِيدُ", "latin": "Al-Muid", "meaning": "Qayta tiriltiruvchi Zot.", "zikr": "Ya Muid"},
    {"arabic": "الْمُحْيِي", "latin": "Al-Muhyi", "meaning": "Hayot beruvchi Zot.", "zikr": "Ya Muhyi"},
    {"arabic": "اَلْمُمِيتُ", "latin": "Al-Mumit", "meaning": "O'lim beruvchi Zot.", "zikr": "Ya Mumit"},
    {"arabic": "الْحَيُّ", "latin": "Al-Hayy", "meaning": "Abadiy tirik Zot.", "zikr": "Ya Hayy"},
    {"arabic": "الْقَيُّومُ", "latin": "Al-Qayyum", "meaning": "Borliqni tutib turuvchi Zot.", "zikr": "Ya Qayyum"},
    {"arabic": "الْوَاجِدُ", "latin": "Al-Wajid", "meaning": "Istagan narsasini topuvchi Zot.", "zikr": "Ya Wajid"},
    {"arabic": "اَلاَحَدُ", "latin": "Al-Ahad", "meaning": "Yakkayu yagona Zot.", "zikr": "Ya Ahad"},
    {"arabic": "الْواحِدُ", "latin": "Al-Wahid", "meaning": "Yagona Zot.", "zikr": "Ya Wahid"},
    {"arabic": "الصَّمَدُ", "latin": "As-Samad", "meaning": "Barcha muhtoj bo'lgan, O'zi hech kimga muhtoj bo'lmagan Zot.", "zikr": "Ya Samad"},
    {"arabic": "الْقَادِرُ", "latin": "Al-Qadir", "meaning": "Har narsaga qodir Zot.", "zikr": "Ya Qadir"},
    {"arabic": "الْمُقْتَدِرُ", "latin": "Al-Muqtadir", "meaning": "Cheksiz qudrat egasi.", "zikr": "Ya Muqtadir"},
    {"arabic": "الْمُقَدِّمُ", "latin": "Al-Muqaddim", "meaning": "Oldinga suruvchi Zot.", "zikr": "Ya Muqaddim"},
    {"arabic": "الْمُؤَخِّرُ", "latin": "Al-Muakhkhir", "meaning": "Orqaga qoldiruvchi Zot.", "zikr": "Ya Muakhkhir"},
    {"arabic": "الأوَّلُ", "latin": "Al-Awwal", "meaning": "Avvalgi Zot, boshlanishsiz.", "zikr": "Ya Awwal"},
    {"arabic": "الآخِرُ", "latin": "Al-Akhir", "meaning": "Oxirgi Zot, tugashsiz.", "zikr": "Ya Akhir"},
    {"arabic": "الظَّاهِرُ", "latin": "Az-Zahir", "meaning": "Alomatlari bilan zohir bo'lgan Zot.", "zikr": "Ya Zahir"},
    {"arabic": "الْبَاطِنُ", "latin": "Al-Batin", "meaning": "Yashirin narsalardan ham xabardor Zot.", "zikr": "Ya Batin"},
    {"arabic": "الْوَالِي", "latin": "Al-Wali", "meaning": "Borliqni boshqaruvchi Zot.", "zikr": "Ya Wali"},
    {"arabic": "الْمُتَعَالِي", "latin": "Al-Muta'ali", "meaning": "Har narsadan yuksak Zot.", "zikr": "Ya Muta'ali"},
    {"arabic": "الْبَرُّ", "latin": "Al-Barr", "meaning": "Bandalariga yaxshilik qiluvchi Zot.", "zikr": "Ya Barr"},
    {"arabic": "التَّوَّابُ", "latin": "At-Tawwab", "meaning": "Tavbalarni qabul qiluvchi Zot.", "zikr": "Ya Tawwab"},
    {"arabic": "الْمُنْتَقِمُ", "latin": "Al-Muntaqim", "meaning": "Adolat bilan jazolovchi Zot.", "zikr": "Ya Muntaqim"},
    {"arabic": "العَفُوُّ", "latin": "Al-Afuww", "meaning": "Kechiruvchi Zot.", "zikr": "Ya Afuww"},
    {"arabic": "الرَّؤُوفُ", "latin": "Ar-Ra'uf", "meaning": "Nihoyatda mehribon Zot.", "zikr": "Ya Ra'uf"},
    {"arabic": "مَالِكُ الْمُلْكِ", "latin": "Malikul-Mulk", "meaning": "Butun mulk egasi Zot.", "zikr": "Ya Malikul-Mulk"},
    {"arabic": "ذُوالْجَلاَلِ وَالإكْرَامِ", "latin": "Dhul-Jalali wal-Ikram", "meaning": "Ulug'lik va karam egasi Zot.", "zikr": "Ya Dhul-Jalali wal-Ikram"},
    {"arabic": "الْمُقْسِطُ", "latin": "Al-Muqsit", "meaning": "Adolat bilan hukm qiluvchi Zot.", "zikr": "Ya Muqsit"},
    {"arabic": "الْجَامِعُ", "latin": "Al-Jami", "meaning": "Barcha mavjudotni jamlovchi Zot.", "zikr": "Ya Jami"},
    {"arabic": "الْغَنِيُّ", "latin": "Al-Ghani", "meaning": "Hech kimga muhtoj bo'lmagan Zot.", "zikr": "Ya Ghani"},
    {"arabic": "الْمُغْنِي", "latin": "Al-Mughni", "meaning": "Boy qiluvchi Zot.", "zikr": "Ya Mughni"},
    {"arabic": "الْمَانِعُ", "latin": "Al-Mani", "meaning": "To'suvchi Zot.", "zikr": "Ya Mani"},
    {"arabic": "الضَّارُّ", "latin": "Ad-Darr", "meaning": "Zarar yetkazishga qodir Zot.", "zikr": "Ya Darr"},
    {"arabic": "النَّافِعُ", "latin": "An-Nafi", "meaning": "Foyda beruvchi Zot.", "zikr": "Ya Nafi"},
    {"arabic": "النُّورُ", "latin": "An-Nur", "meaning": "Nur beruvchi Zot.", "zikr": "Ya Nur"},
    {"arabic": "الْهَادِي", "latin": "Al-Hadi", "meaning": "Hidoyat beruvchi Zot.", "zikr": "Ya Hadi"},
    {"arabic": "الْبَدِيعُ", "latin": "Al-Badi", "meaning": "O'xshashi yo'q yaratuvchi Zot.", "zikr": "Ya Badi"},
    {"arabic": "الْبَاقِي", "latin": "Al-Baqi", "meaning": "Abadiy qoluvchi Zot.", "zikr": "Ya Baqi"},
    {"arabic": "الْوَارِثُ", "latin": "Al-Warith", "meaning": "Barcha narsaning merosxo'ri Zot.", "zikr": "Ya Warith"},
    {"arabic": "الرَّشِيدُ", "latin": "Ar-Rashid", "meaning": "To'g'ri yo'l ko'rsatuvchi Zot.", "zikr": "Ya Rashid"},
    {"arabic": "الصَّبُورُ", "latin": "As-Sabur", "meaning": "Juda sabrli Zot.", "zikr": "Ya Sabur"},
]


user_name_index = {}
user_hijri_date = {}
user_mode = {}


HIJRI_MONTHS_UZ = {
    "Muharram": "Muharram",
    "Safar": "Safar",
    "Rabi' al-Awwal": "Robiul-avval",
    "Rabi' al-Thani": "Robius-soniy",
    "Jumada al-Ula": "Jumodul-avval",
    "Jumada al-Akhirah": "Jumodus-soniy",
    "Rajab": "Rajab",
    "Sha'ban": "Sha'bon",
    "Ramadan": "Ramazon",
    "Shawwal": "Shavvol",
    "Dhu al-Qa'dah": "Zul-Qa'da",
    "Dhu al-Hijjah": "Zul-Hijja",
    "Dhū al-Ḥijjah": "Zul-Hijja",
}


UZ_WEEKDAYS = {
    "Monday": "Dushanba",
    "Tuesday": "Seshanba",
    "Wednesday": "Chorshanba",
    "Thursday": "Payshanba",
    "Friday": "Juma",
    "Saturday": "Shanba",
    "Sunday": "Yakshanba",
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


KAABA_LAT = 21.422487
KAABA_LON = 39.826206


# ─── Menu helpers ─────────────────────────────────────────────────────────────

def qibla_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    location_btn = types.KeyboardButton("📍 Lokatsiyani yuborish", request_location=True)
    markup.add(location_btn)
    markup.add("🏠 Asosiy menyu")
    return markup


def hijri_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🕌 Muhim sanalar")
    markup.add("🏠 Asosiy menyu")
    return markup


def names_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("⬅️ Oldingi", "➡️ Keyingi")
    markup.add("🏠 Asosiy menyu")
    return markup


def language_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "🇺🇿 O'zbekcha", "🇷🇺 Русский",
        "🇬🇧 English", "🇸🇦 العربية",
        "🇹🇷 Türkçe", "🇩🇪 Deutsch",
        "🇫🇷 Français", "🇪🇸 Español",
        "🇮🇹 Italiano", "🇰🇿 Қазақша",
        "🇰🇬 Кыргызча", "🇹🇯 Тоҷикӣ",
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
        "🕋 Allohning 99 ismi",
        "📅 Hijriy taqvim",
        "⚙️ Sozlamalar",
    )
    return markup


def back_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("⬅️ Orqaga", "🏠 Asosiy menyu")
    return markup


# ─── Helper functions ──────────────────────────────────────────────────────────

def calculate_qibla_angle(user_lat, user_lon):
    import math
    lat1 = math.radians(user_lat)
    lon1 = math.radians(user_lon)
    lat2 = math.radians(KAABA_LAT)
    lon2 = math.radians(KAABA_LON)
    delta_lon = lon2 - lon1
    x = math.sin(delta_lon)
    y = math.cos(lat1) * math.tan(lat2) - math.sin(lat1) * math.cos(delta_lon)
    angle = math.degrees(math.atan2(x, y))
    return (angle + 360) % 360


def get_location_name(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lon, "format": "json", "accept-language": "uz,en,pl"}
        headers = {"User-Agent": "IslamTimeWorldBot/1.0"}
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
        return f"{city}, {country}" if country else city
    except Exception:
        return "Joylashuv aniqlandi"


def get_hijri_info(date_obj):
    date_str = date_obj.strftime("%d-%m-%Y")
    url = f"https://api.aladhan.com/v1/gToH?date={date_str}"
    response = requests.get(url, timeout=10)
    data = response.json()["data"]
    hijri = data["hijri"]
    gregorian = data["gregorian"]
    return {
        "h_day": hijri["day"],
        "h_month": HIJRI_MONTHS_UZ.get(hijri["month"]["en"], hijri["month"]["en"]),
        "h_year": hijri["year"],
        "g_date": gregorian["date"],
        "weekday": UZ_WEEKDAYS.get(gregorian["weekday"]["en"], gregorian["weekday"]["en"]),
    }


def h_to_g(h_day, h_month, h_year):
    url = f"https://api.aladhan.com/v1/hToG?date={h_day}-{h_month}-{h_year}"
    response = requests.get(url, timeout=10)
    data = response.json()["data"]["gregorian"]["date"]
    return datetime.strptime(data, "%d-%m-%Y").date()


def get_next_important_date(today):
    hijri_info = get_hijri_info(today)
    current_h_year = int(hijri_info["h_year"])
    upcoming = []
    for item in IMPORTANT_HIJRI_DATES:
        for year in [current_h_year, current_h_year + 1]:
            g_date = h_to_g(item["h_day"], item["h_month"], year)
            days_left = (g_date - today.date()).days
            if days_left >= 0:
                upcoming.append({
                    "title": item["title"],
                    "h_day": item["h_day"],
                    "h_month": item["h_month"],
                    "h_year": year,
                    "g_date": g_date,
                    "days_left": days_left,
                })
                break
    upcoming.sort(key=lambda x: x["days_left"])
    return upcoming[0], upcoming


def show_hijri_calendar(chat_id, date_obj):
    user_hijri_date[chat_id] = date_obj
    info = get_hijri_info(date_obj)
    next_event, _ = get_next_important_date(date_obj)
    text = f"""
📅 <b>HIJRIY TAQVIM</b>

🌙 <b>Bugungi hijriy sana:</b>
{info["h_day"]} {info["h_month"]} {info["h_year"]}

🗓 <b>Milodiy sana:</b>
{info["g_date"]}

📆 <b>Hafta kuni:</b>
{info["weekday"]}

🕌 <b>Hijriy oy:</b>
{info["h_month"]}

🤲 Alloh bugungi kuningizni barakali qilsin.

━━━━━━━━━━━━━━

⏳ <b>Keyingi muhim sana:</b>
{next_event["title"]}
📅 {next_event["h_day"]}-hijriy oy, {next_event["h_year"]}

{next_event["days_left"]} kun qoldi
"""
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=hijri_menu())


def show_allah_name(chat_id, index):
    name = ALLAH_NAMES[index]
    total = len(ALLAH_NAMES)
    text = f"""
🕋 <b>ASMAUL HUSNA</b>
<i>(Allohning 99 go'zal ismi)</i>

{index + 1}/{total}

<b>{name['arabic']}</b>

<b>{name['latin']}</b>

<b>Ma'nosi:</b>
{name['meaning']}

📿 <b>Zikr:</b>
{name['zikr']}

<b><i>🤲 Allohni zikr qiling va ma'nosini tafakkur qiling.</i></b>
"""
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=names_menu())


# ─── Flask ─────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return "IslamTimeWorldBot is running!"


# ─── Bot handlers ──────────────────────────────────────────────────────────────

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🌍 Welcome to Islam Time World\n\nPlease select your language:",
        reply_markup=language_menu(),
    )


@bot.message_handler(func=lambda m: m.text == "🇺🇿 O'zbekcha")
def uzbek(message):
    bot.send_message(
        message.chat.id,
        "🇺🇿 O'zbek tili tanlandi.\n\nKerakli bo'limni tanlang:",
        reply_markup=main_menu(),
    )


@bot.message_handler(func=lambda m: m.text == "🏠 Asosiy menyu")
def go_main_menu(message):
    bot.send_message(message.chat.id, "🏠 Asosiy menyu", reply_markup=main_menu())


@bot.message_handler(func=lambda m: m.text == "⬅️ Orqaga")
def go_back(message):
    bot.send_message(message.chat.id, "🏠 Asosiy menyu", reply_markup=main_menu())


@bot.message_handler(func=lambda m: m.text == "🕌 Namoz vaqtlari")
def prayer_times(message):
    user_mode[message.chat.id] = "prayer"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📍 Lokatsiyani yuborish", request_location=True))
    markup.add("🏠 Asosiy menyu")
    bot.send_message(
        message.chat.id,
        "📍 Namoz vaqtlarini hisoblash uchun hozirgi lokatsiyangizni yuboring.",
        reply_markup=markup,
    )


@bot.message_handler(content_types=["location"])
def location_handler(message):
    chat_id = message.chat.id
    lat = message.location.latitude
    lon = message.location.longitude
    mode = user_mode.get(chat_id)

    # ── Qibla mode ──
    if mode == "qibla":
        angle = calculate_qibla_angle(lat, lon)
        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🧭 Qibla kompasini ochish", url=maps_url))
        bot.send_message(
            chat_id,
            f"🧭 <b>Qibla yo'nalishi:</b>\n\nKa'ba tomonga burchak: <b>{angle:.2f}°</b>",
            parse_mode="HTML",
            reply_markup=markup,
        )
        user_mode.pop(chat_id, None)
        return

    # ── Prayer mode ──
    if mode == "prayer":
        try:
            prayer_url = (
                f"https://api.aladhan.com/v1/timings?"
                f"latitude={lat}&longitude={lon}&method=3"
            )
            response = requests.get(prayer_url, timeout=10)
            data = response.json()

            timings = data["data"]["timings"]
            date = data["data"]["date"]["readable"]
            location_name = get_location_name(lat, lon) or f"{lat:.4f}, {lon:.4f}"

            timezone_name = data["data"]["meta"]["timezone"]
            tz = ZoneInfo(timezone_name)
            now = datetime.now(tz)

            prayers = [
                ("Bomdod", "🌅", timings["Fajr"]),
                ("Peshin", "🕛", timings["Dhuhr"]),
                ("Asr", "🌇", timings["Asr"]),
                ("Shom", "🌆", timings["Maghrib"]),
                ("Xufton", "🌙", timings["Isha"]),
            ]

            # Find next prayer
            next_prayer_name = "Bomdod"
            next_prayer_emoji = "🌅"
            time_left_text = ""

            for name, emoji, prayer_time in prayers:
                hour, minute = map(int, prayer_time.split(":")[:2])
                prayer_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if prayer_dt > now:
                    diff = prayer_dt - now
                    hours = diff.seconds // 3600
                    minutes = (diff.seconds % 3600) // 60
                    next_prayer_name = name
                    next_prayer_emoji = emoji
                    time_left_text = f"{hours} soat {minutes} daqiqadan so'ng"
                    break

            # If all prayers passed today, next is Fajr tomorrow
            if not time_left_text:
                next_prayer_name = "Bomdod"
                next_prayer_emoji = "🌅"
                hour, minute = map(int, timings["Fajr"].split(":")[:2])
                fajr_tomorrow = (now + timedelta(days=1)).replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )
                diff = fajr_tomorrow - now
                hours = diff.seconds // 3600
                minutes = (diff.seconds % 3600) // 60
                time_left_text = f"{hours} soat {minutes} daqiqadan so'ng (ertaga)"

            # Random quote and hadith
            quote = random.choice(QURAN_QUOTES)
            hadith = random.choice(HADITH_QUOTES)

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

"{quote['text']}"

<b>{quote['source']}</b>
<i>({quote['note']})</i>

━━━━━━━━━━━━━━

📚 <b>BUGUNGI HADIS</b>

"{hadith['text']}"

<b>{hadith['source']}</b>

🤲 Alloh namozlaringizni qabul qilsin.
"""
            bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=main_menu())

        except Exception as e:
            bot.send_message(
                chat_id,
                f"❌ Kechirasiz, namoz vaqtlarini olishda xatolik yuz berdi.\n{e}",
                reply_markup=main_menu(),
            )

        user_mode.pop(chat_id, None)
        return

    # ── Unknown mode ──
    bot.send_message(
        chat_id,
        "Iltimos, avval menyudan kerakli bo'limni tanlang:\n\n🕌 Namoz vaqtlari yoki 🧭 Qibla",
        reply_markup=main_menu(),
    )


@bot.message_handler(func=lambda m: m.text == "🧭 Qibla")
def qibla(message):
    user_mode[message.chat.id] = "qibla"
    bot.send_message(
        message.chat.id,
        "🧭 <b>Qibla yo'nalishini aniqlash</b>\n\n"
        "Iltimos, joylashuvingizni yuboring.\n"
        "Shunda men siz turgan joydan Ka'ba tomonga yo'nalishni hisoblab beraman.",
        parse_mode="HTML",
        reply_markup=qibla_menu(),
    )


@bot.message_handler(func=lambda m: m.text == "📅 Hijriy taqvim")
def hijri_calendar_handler(message):
    show_hijri_calendar(message.chat.id, datetime.now())


@bot.message_handler(func=lambda m: m.text == "⬅️ Kecha")
def hijri_prev_day(message):
    date_obj = user_hijri_date.get(message.chat.id, datetime.now()) - timedelta(days=1)
    show_hijri_calendar(message.chat.id, date_obj)


@bot.message_handler(func=lambda m: m.text == "➡️ Ertaga")
def hijri_next_day(message):
    date_obj = user_hijri_date.get(message.chat.id, datetime.now()) + timedelta(days=1)
    show_hijri_calendar(message.chat.id, date_obj)


@bot.message_handler(func=lambda m: m.text == "🕌 Muhim sanalar")
def important_hijri_dates(message):
    _, upcoming = get_next_important_date(datetime.now())
    text = "🕌 <b>MUHIM ISLOMIY SANALAR</b>\n\n"
    for item in upcoming[:8]:
        text += f"{item['title']}\n⏳ {item['days_left']} kun qoldi\n\n"
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=hijri_menu())


@bot.message_handler(func=lambda m: m.text == "🕋 Allohning 99 ismi")
def names_99(message):
    user_name_index[message.chat.id] = 0
    show_allah_name(message.chat.id, 0)


@bot.message_handler(func=lambda m: m.text == "➡️ Keyingi")
def next_name(message):
    chat_id = message.chat.id
    if chat_id in user_name_index:
        if user_name_index[chat_id] < len(ALLAH_NAMES) - 1:
            user_name_index[chat_id] += 1
        show_allah_name(chat_id, user_name_index[chat_id])


@bot.message_handler(func=lambda m: m.text == "⬅️ Oldingi")
def prev_name(message):
    chat_id = message.chat.id
    if chat_id in user_name_index:
        if user_name_index[chat_id] > 0:
            user_name_index[chat_id] -= 1
        show_allah_name(chat_id, user_name_index[chat_id])


@bot.message_handler(func=lambda m: m.text == "⚙️ Sozlamalar")
def settings(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "🌐 Tilni o'zgartirish",
        "🔔 Namoz eslatmalari",
        "📍 Lokatsiyani yangilash",
        "🎧 Qori tanlash",
        "🏠 Asosiy menyu",
    )
    bot.send_message(message.chat.id, "⚙️ Sozlamalar", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "🌐 Tilni o'zgartirish")
def change_language(message):
    bot.send_message(message.chat.id, "🌍 Tilni tanlang:", reply_markup=language_menu())


@bot.message_handler(func=lambda m: m.text == "🔔 Namoz eslatmalari")
def prayer_reminders(message):
    bot.send_message(
        message.chat.id,
        "🔔 Namoz eslatmalari moduli keyingi bosqichda qo'shiladi.",
        reply_markup=back_menu(),
    )


@bot.message_handler(func=lambda m: m.text == "📍 Lokatsiyani yangilash")
def update_location(message):
    bot.send_message(
        message.chat.id,
        "📍 Lokatsiyani yangilash uchun 🕌 Namoz vaqtlari bo'limiga kiring.",
        reply_markup=back_menu(),
    )


@bot.message_handler(func=lambda m: m.text == "🎧 Qori tanlash")
def choose_qari(message):
    bot.send_message(
        message.chat.id,
        "🎧 Qori tanlash moduli keyingi bosqichda qo'shiladi.",
        reply_markup=back_menu(),
    )


@bot.message_handler(func=lambda m: True)
def unknown(message):
    bot.send_message(
        message.chat.id,
        "Iltimos, menyudan kerakli bo'limni tanlang.",
        reply_markup=main_menu(),
    )


# ─── Run ───────────────────────────────────────────────────────────────────────

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
