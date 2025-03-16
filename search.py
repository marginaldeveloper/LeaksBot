
API_TOKEN = '#'
import re
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp
import asyncio
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import os
from sqlalchemy import create_engine, MetaData, Table, select, or_
from sqlalchemy.exc import SQLAlchemyError
import logging
# ДЛЯ ДУШИ  📂💾📊📈🔍🔎🔓🛠️💻🖥️📱📝🗃️📜📑📇📋🔐🔒🧬📌🗂️📁⚙️📉💡🛰️🌐🌍🌏🌎📡🧩💥📣🔊🔔🛡️🧨🕶️🔗🔗📟💳📊⚔️🧲📑📈🖋️🛠️🔍🔐📋📋🔍🗝️📜📈🛡️📈🔗📌🖥️📇📜🗃️📍🔍📉📱🖥️📂📊🔓🔍🔓📊📜🔒🔐🛡️
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

LISTDB = [
    "🔓 Moldova Facebook Leaks",
    "🎥 Кинотеатр тирасполь kinotir.md",
    "🕵️ МВД - Поиск без вести пропавших 2016",
    "🧭 Молдова - Гагаузия - Розыск пропавших без вести 2017",
    "🔍 Молдова - Гагаузия Розыск преступников 2017",
    "📋 Молдова - Генеральный Инспекторат 2017 Поиск пропавших без вести",
    "🛡️ Молдова - Генеральный Инспекторат 2017",
    "🚨 Молдова - Департамент пограничной полиции - Розыск преступников 2017",
    "🌍 Молдова - Интерпол - Розыск преступников 2017",
    "🏙️ Молдова - Кишинев Поиск преступников 2014",
    "🔒 Молдова - МВР Розыск Преступников 2014",
    "⚖️ Молдова - Министерство юстиции - Розыск преступников 2017",
    "📅 Молдова - Розыск Преступников 2004",
    "⚰️ ПМР - Дуббосары - Погибшие и без вести пропавшие 1990-1992",
    "👮‍♂️ ПМР - МВД - Розыск преступников",
    "💼 ПМР - Министерство Юстиции - Генеральная служба исполнения наказаний - Алиментщики в Розыске 2012",
    "📜 ПМР - Министерство Юстиции - Генеральная служба исполнения наказаний 2017",
    "🗂️ ПМР РОЗЫСК 2017",
    "📂 Приднестровье Розыск МВД",
    "🌐 George Standard Кишинев 2023                      ",
    "📁 pmr_users (источник не определен)                        ",
    "📟 Владельцы отелей Молдовы                        ",
    "🧬 API LEAK OSINT                       ",
    "                       ", #ПУСТУЮ ОСТАВЬ для эсстетики
    "⋆｡ﾟ☁︎｡⋆｡ ﾟ☾ ﾟ｡⋆ Всего Строк: 58027(ПМР/МД) ",
    "Вернуться назад - /start                          ",
]

DB_FOLDER_PATH = 'F:\\fordatabase'
API_LEAK_OSINT = "#"  
LEAK_OSINT_URL = "https://leakosintapi.com/"

async def search_leak_osint(query):
    async with aiohttp.ClientSession() as session:
        data = {
            "token": API_LEAK_OSINT,
            "request": query,
            "limit": 100,  
            "lang": "ru",  
            "type": "json"  
        }
        try:
            async with session.post(LEAK_OSINT_URL, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result:
                        return format_osint_results(result)
                    else:
                        return ["❗ Нет данных по запросу в Leak OSINT."]
                else:
                    return [f"⚠ Ошибка API Leak OSINT: {response.status}"]
        except Exception as e:
            logger.error(f"Ошибка при запросе к API Leak OSINT: {e}")
            return ["❗ Произошла ошибка при обращении к API."]


def format_osint_results(results):
    messages = []
    chunk_size = 4000  
    formatted_result = "\n".join([f"🔹 {key}: {value}" for key, value in results.items()])
    
    for i in range(0, len(formatted_result), chunk_size):
        messages.append(formatted_result[i:i+chunk_size])
    
    return messages


def is_phone_number(input_string):
    phone_pattern = re.compile(r"^\+?\d{7,15}$")
    match = phone_pattern.match(input_string)
    logger.debug(f"is_phone_number: {input_string} -> {bool(match)}")
    return match is not None

def is_ip_address(input_string):
    ip_pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    match = ip_pattern.match(input_string)
    logger.debug(f"is_ip_address: {input_string} -> {bool(match)}")
    return match is not None

# чтобы не путало почту с юзернеймом, уже лишнее т.к переделал на команду /user
def is_username(input_string):
    username_check = not any(input_string.lower().endswith(domain) for domain in [
        "@mail.ru", "@gmail.com", "@bk.ru", "@vk.com", "@inbox.ru", "@list.ru", "@internet.ru", "@rambler.ru", "@yahoo.com"
    ]) and "@" not in input_string
    logger.debug(f"is_username: {input_string} -> {username_check}")
    return username_check

async def notify_admin(user_id: int, query: str, user_info: str):
    try:
        message = f"🔔 Новый запрос!\n\nПользователь: {user_info}\nЗапрос: {query}"
        await bot.send_message(user_id, message)
        logger.debug(f"Отправлено уведомление администратору: {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления: {e}")


def create_main_menu():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Базы данных 🗃️")]],
        resize_keyboard=True
    )
    return keyboard



@router.message(F.text == "Базы данных 🗃️")
async def show_databases(message: types.Message):
    if LISTDB:
        db_list = "\n".join(LISTDB)
        await message.reply(f"Доступные базы данных:\n{db_list}", reply_markup=create_main_menu())
    else:
        await message.reply("❗ Нет доступных баз данных.", reply_markup=create_main_menu())
def find_matches_in_db(engine, search_term):
    metadata = MetaData()
    metadata.reflect(bind=engine)
    results = []

    logger.debug(f"🕵🏻 Поиск в базе данных по термину: {search_term}")

    for table in metadata.sorted_tables:
        try:
            conditions = []
            for column in table.columns:
                if column.type.python_type == str:
                    conditions.append(table.c[column.name].like(f'%{search_term}%'))
            if conditions:
                query = select(table).where(or_(*conditions))
                with engine.connect() as connection:
                    result = connection.execute(query)
                    rows = result.fetchall()
                    if rows:
                        logger.debug(f"✔️  Найдены совпадения в таблице {table.name}")
                        results.append((table.name, rows))
        except SQLAlchemyError as e:
            logger.error(f"❗ Ошибка при выполнении запроса к таблице {table.name}: {e}")

    return results

def search_all_databases(search_term):
    logger.debug(f"🕵🏻 Запуск поиска по всем базам данных для: {search_term}")
    databases = [f for f in os.listdir(DB_FOLDER_PATH) if f.endswith('.db')]
    
    all_matches = []
    for db in databases:
        db_path = os.path.join(DB_FOLDER_PATH, db)
        engine = create_engine(f'sqlite:///{db_path}')
        matches = find_matches_in_db(engine, search_term)
        
        if matches:
            for table_name, rows in matches:
                match_text = f"🗂️ База данных: {db}, 📅Таблица: {table_name}\n"
                for row in rows:
                    row_dict = dict(row._mapping)  
                    for column, value in row_dict.items(): 
                        match_text += f"{column}┃ {value}\n"
                    match_text += "\n" 
                all_matches.append(match_text)
    
    return all_matches



def phoneinfo(phone):
    try:
        logger.debug(f"Начинаем обработку номера телефона: {phone}")
        if phone.startswith('+'):
            parsed_phone = phonenumbers.parse(phone, None)
        else:
            logger.warning(f"❗ Неверный формат телефона: {phone}")
            return None
        
        if not phonenumbers.is_valid_number(parsed_phone):
            logger.warning(f"Недействительный номер телефона: {phone}")
            return f"Недействительный номер телефона: {phone}"
        
        carrier_info = carrier.name_for_number(parsed_phone, "ru")
        country = geocoder.description_for_number(parsed_phone, "en")
        region = geocoder.description_for_number(parsed_phone, "ru")
        location = geocoder.description_for_number(parsed_phone, "en")
        formatted_number = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        is_valid = phonenumbers.is_valid_number(parsed_phone)
        is_possible = phonenumbers.is_possible_number(parsed_phone)
        timezones = ', '.join(timezone.time_zones_for_number(parsed_phone))
        
        phone_info = f"""\n  [+] Номер телефона -> {formatted_number}
    🌍 [+] Страна -> {country}
    📍  [+] Локация -> {location}
    🏙️ [+] Регион -> {region}
    💻 [+] Интернет-провайдер -> {carrier_info}
    🟢 [+] Активен -> {is_possible}
    ✅ [+] Валид -> {is_valid}
    🕒 [+] Таймзона -> {timezones}
    ✈️ [+] Telegram -> https://t.me/{phone}
    📲 [+] Whatsapp -> https://wa.me/{phone}
    📞 [+] Viber -> https://viber.click/{phone}\n"""

        logger.debug(f"Информация по телефону {phone}: {phone_info}")
        return phone_info
    except Exception as e:
        logger.error(f"❗ Ошибка в phoneinfo для {phone}: {e}")
        return f"⚠ Произошла ошибка: {str(e)}"

async def search_usernames(username):
    urls = [
        ("Дисклеймер ✧*:･ﾟ", f"Да, возможно, некоторые ссылки будут не действительны! Бот отображает результаты с вероятностью 70%, если такой юзернейм существует. В случае, если он не смог точно распознать, но соцсети с таким юзером присутствуют, они также будут выведены.", "❓"),
        ("Instagram", f"https://www.instagram.com/{username}", "📷"),
        ("TikTok", f"https://www.tiktok.com/@{username}", "🎵"),
        ("Twitter", f"https://twitter.com/{username}", "🐦"),
        ("Facebook", f"https://www.facebook.com/{username}", "📘"),
        ("YouTube", f"https://www.youtube.com/@{username}", "▶️"),
        ("SoundCloud", f"https://soundcloud.com/{username}", "🎶"),
        ("Telegram", f"https://t.me/{username}", "📱"),
        ("VK", f"https://vk.com/{username}", "🔵"),
        ("Roblox", f"https://www.roblox.com/user.aspx?username={username}", "🎮"),
        ("Twitch", f"https://www.twitch.tv/{username}", "🎥"),
        ("Pinterest", f"https://www.pinterest.com/{username}", "📌"),
        ("GitHub", f"https://www.github.com/{username}", "💻"),
        ("Reddit", f"https://www.reddit.com/u/{username}/", "❓"),
        
    ]

    found_accounts = []
    logger.debug(f"Начинается поиск юзернеймов: {username}")
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url, timeout=10) for _, url, _ in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for (resource_name, url, emoji), response in zip(urls, responses):
            if isinstance(response, aiohttp.ClientResponse) and response.status == 200:
                found_accounts.append(f"{emoji} {resource_name}: {url}")
                logger.debug(f"✔️ Найден аккаунт: {resource_name} -> {url}")
            else:
                logger.debug(f"Не удалось найти аккаунт: {resource_name} -> {url}")
    
    return found_accounts


async def trace_ip(target_ip):
    try:
        logger.debug(f"Запрос на поиск IP-адреса: {target_ip}")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://ip-api.com/json/{target_ip}") as response:
                r = await response.json()
                if r['status'] == 'success':
                    return {
                        '✅ Статус': r['status'],
                        '🌐 IP Цели': r['query'],
                        '🏳️‍🌈 Страна': r['country'],
                        '🔢 Код страны': r['countryCode'],
                        '🏙️ Город': r['city'],
                        '⏰ Часовой пояс': r['timezone'],
                        '🌍 Название региона': r['regionName'],
                        '🏞️ Регион': r['region'],
                        '📮 ZIP Код': r['zip'],
                        '🌍 Широта': r['lat'],
                        '🌍 Долгота': r['lon'],
                        '🖥️ ISP': r['isp'],
                        '🖥️ Провайдер': r['org'],
                        '📡 AS': r['as'],
                        '📍 Локация': f"{r['lat']},{r['lon']}",
                        '🗺️ Google Карты': f"https://maps.google.com/?q={r['lat']},{r['lon']}"
                    }
                else:
                    logger.error(f"Ошибка IP: {r['message']}")
                    return {
                        'Status': r['status'],
                        'Message': r['message']
                    }
    except Exception as e:
        logger.error(f"Ошибка в trace_ip для {target_ip}: {e}")
        return {'Status': 'fail', 'Message': str(e)}
    
@router.message(Command("user"))
async def search_by_username(message: types.Message):
    try:

        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply("❗ Пожалуйста, укажите юзернейм после команды /user. Пример: /user john_doe")
            return

        username = command_parts[1].strip()
        usernames_info = await search_usernames(username)
        if usernames_info:
            await message.reply("\n".join(usernames_info))
        else:
            await message.reply("🛡️ Юзернеймы не найдены.")
    except Exception as e:
        logger.error(f"Ошибка при поиске юзернейма: {e}")
        await message.reply("⚠ Произошла ошибка при обработке команды.")



async def handle_search(search_term, message):
    user_info = f"ID: {message.from_user.id}, Имя: {message.from_user.first_name}, Username: @{message.from_user.username or 'Не указан'}"
    logger.debug(f"Начинается обработка запроса: {search_term}")
    loading_message = await message.reply("🔍 Выполняю поиск...")

    await notify_admin(7516159378, search_term, user_info)


    leak_osint_result = await search_leak_osint(search_term)

    if isinstance(leak_osint_result, list):  
        for chunk in leak_osint_result:
            await message.reply(f"📡 From Leak OSINT:\n{chunk}")
    else:
        await message.reply("❗ Ошибка обработки данных из Leak OSINT.")



    if is_phone_number(search_term):
        phone_info = phoneinfo(search_term)
        if phone_info:
            await message.reply(phone_info)


    elif is_ip_address(search_term):
        ip_info = await trace_ip(search_term)
        if 'Message' not in ip_info:
            ip_info_text = "\n".join([f"{key}: {value}" for key, value in ip_info.items()])
            await message.reply(ip_info_text)
        else:
            await message.reply(f"Ошибка: {ip_info['Message']}")


    db_matches = search_all_databases(search_term)
    if db_matches:
        for match in db_matches:
            await message.reply(match)
    else:
        await message.reply("🛡️ Совпадений в базах данных не найдено.")

    
@router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply('''
˖⁺‧₊˚🔭˚₊‧⁺˖ Приветствую!

Мой создатель @theFatR4t не несет ответственности за ваши действия. 

🔍 Введите один из следующих данных для поиска:
• Номер телефона: Укажите номер (например, +37377123456 или 37377123456 )
                        
• IP-адрес Например 62.431.76.241
• Юзернейм: Введите в формате /user username.
• Электронная почта: Например, test@gmail.com.             
• ФИО: Иванов Иван Иванович или Иванов Иван.
• Термин для поиска.
                        
В боте собраны утечки по ПМР/Молдове 🇲🇩.

По кнопке 📚 Базы данных можно узнать все базы.
                        ''', reply_markup=create_main_menu())

@router.message()
async def handle_message(message: types.Message):
    search_term = message.text
    await handle_search(search_term, message)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
