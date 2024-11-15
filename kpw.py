import asyncio
import requests
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from datetime import datetime, timedelta
from googletrans import Translator
from config import TOKEN, NASA_API_KEY, THE_CAT_API_KEY
from buttoms import main_menu, facts_menu  # Импорт кнопок

bot = Bot(token=TOKEN)
dp = Dispatcher()
translator = Translator()

# Словарь пород
breeds_dict = {}

# Инициализация словаря пород
def init_breeds_dict():
    url = 'https://api.thecatapi.com/v1/breeds'
    headers = {'x-api-key': THE_CAT_API_KEY}
    response = requests.get(url, headers=headers).json()
    for breed in response:
        breeds_dict[breed['name'].lower()] = {
            "id": breed['id'],
            "en": breed['name'],
            # "ru": translator.translate(breed['name'], src="en", dest="ru").text,
            "description": translator.translate(breed['description'], src="en", dest="ru").text,
            "temperament": translator.translate(breed['temperament'], src="en", dest="ru").text,
        }
    print("Словарь пород успешно инициализирован.")

# NASA APOD
def get_random_apod():
    random_date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
    url = f'https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={random_date}'
    response = requests.get(url).json()
    return response

# Факты из Numbers API
def fetch_fact(category, query=""):
    url = f"http://numbersapi.com/{query}/{category}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return "Не удалось получить данные. Попробуйте позже."

# Перевод текста на русский
def translate_to_russian(text):
    try:
        return translator.translate(text, src="en", dest="ru").text
    except Exception:
        return "Ошибка перевода."

# Состояние фактов
user_facts_state = {}

@dp.message(CommandStart())
async def start(message: types.Message):
    init_breeds_dict()  # Инициализация словаря при запуске
    await message.answer("Привет! Выберите действие:", reply_markup=main_menu())

@dp.message(lambda message: message.text == "📜 Список пород")
async def list_breeds(message: types.Message):
    breed_list = "\n".join([f"{breed['en']}" for breed in breeds_dict.values()])
    await message.answer(f"Список пород котов:\n\n{breed_list}")

@dp.message(lambda message: message.text == "🐾 Введите породу")
async def prompt_breed_input(message: types.Message):
    await message.answer("Введите название породы на английском языке:")

@dp.message(lambda message: message.text == "🚀 Космос")
async def send_random_apod(message: types.Message):
    apod = get_random_apod()
    photo_url = apod.get('url', '')
    title = apod.get('title', 'Нет названия')
    description = apod.get('explanation', 'Нет описания')

    # Перевод текста
    translated_title = translate_to_russian(title)
    translated_description = translate_to_russian(description)

    # Ограничение длины текста
    if len(translated_description) > 900:
        translated_description = translated_description[:900] + "..."

    caption = f"{translated_title}\n\n{translated_description}"

    await message.answer_photo(photo_url, caption=caption)

@dp.message(lambda message: message.text == "Факты")
async def facts_menu_handler(message: types.Message):
    await message.answer("Выберите категорию факта:", reply_markup=facts_menu())

@dp.message(lambda message: message.text in ["Факт о числе", "Факт о дате", "Факт о годе", "Случайный факт"])
async def handle_fact_request(message: types.Message):
    user_id = message.from_user.id
    if message.text == "Факт о числе":
        user_facts_state[user_id] = "number"
        await message.answer("Введите число:")
    elif message.text == "Факт о дате":
        user_facts_state[user_id] = "date"
        await message.answer("Введите дату в формате MM-DD (например, 11-14):")
    elif message.text == "Факт о годе":
        user_facts_state[user_id] = "year"
        await message.answer("Введите год (например, 2000):")
    elif message.text == "Случайный факт":
        fact = fetch_fact("random")
        await message.answer(f"Случайный факт:\n{translate_to_russian(fact)}")
        user_facts_state.pop(user_id, None)

@dp.message(lambda message: message.text == "Назад")
async def go_back(message: types.Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu())

@dp.message(lambda message: message.from_user.id in user_facts_state)
async def process_fact_input(message: types.Message):
    user_id = message.from_user.id
    fact_type = user_facts_state.get(user_id)
    fact = None

    if fact_type == "number":
        if message.text.isdigit():
            fact = fetch_fact("trivia", message.text)
    elif fact_type == "date" and "-" in message.text:
        fact = fetch_fact("date", message.text)
    elif fact_type == "year" and message.text.isdigit():
        fact = fetch_fact("year", message.text)

    if fact:
        await message.answer(f"Факт:\n{translate_to_russian(fact)}")
    else:
        await message.answer("Некорректный ввод. Попробуйте снова.")
    user_facts_state.pop(user_id, None)

@dp.message(lambda message: True)
async def handle_breed_input(message: types.Message):
    breed_name = message.text.strip().lower()
    breed_info = breeds_dict.get(breed_name)
    if breed_info:
        url = f"https://api.thecatapi.com/v1/images/search?breed_ids={breed_info['id']}"
        response = requests.get(url).json()
        image_url = response[0].get('url', 'Нет изображения') if response else "Нет изображения"
        info = (
            f"Порода: {breed_info['en']}\n"
            f"Описание: {breed_info['description']}\n"
            f"Темперамент: {breed_info['temperament']}"
        )
        await message.answer_photo(image_url, caption=info)
    else:
        await message.answer("Кот с такой породой не найден или некорректный ввод.")

async def main():
    print("Бот запущен...")
    init_breeds_dict()  # Инициализация словаря при запуске
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
