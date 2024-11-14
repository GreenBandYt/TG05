import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import random
import requests
from datetime import datetime, timedelta
from config import TOKEN, NASA_API_KEY, THE_CAT_API_KEY
from googletrans import Translator

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализация переводчика
translator = Translator()

# Хранение использованных URL для NASA APOD
used_urls = set()

# Главное меню
def main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📜 Список пород"), KeyboardButton(text="🐾 Введите породу")],
            [KeyboardButton(text="🔄 Старт"), KeyboardButton(text="🚀 Космос")]
        ],
        resize_keyboard=True
    )
    return keyboard

# Получить данные NASA APOD
def get_random_apod():
    global used_urls
    end_date = datetime.now()
    start_date = datetime.now() - timedelta(days=365)

    while True:
        random_days = random.randint(0, 365)
        random_date = start_date + timedelta(days=random_days)
        date_str = random_date.strftime('%Y-%m-%d')

        url = f'https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={date_str}'
        response = requests.get(url).json()

        if response['url'] not in used_urls:
            used_urls.add(response['url'])
            return response

# Получить список пород котов
def get_cat_breeds():
    url = 'https://api.thecatapi.com/v1/breeds'
    headers = {'x-api-key': THE_CAT_API_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

# Получить изображение кота по породе
def get_cat_image_by_breed(breed_id):
    url = f'https://api.thecatapi.com/v1/images/search?breed_ids={breed_id}'
    headers = {'x-api-key': THE_CAT_API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data[0]['url']

# Получить информацию о породе
def get_breed_info(breed_name):
    breeds = get_cat_breeds()
    for breed in breeds:
        if breed_name.lower() in (breed['name'].lower(), breed.get('alt_names', '').lower()):
            return breed
    return None

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! Выберите действие:",
        reply_markup=main_menu()
    )

@dp.message(lambda message: message.text == "📜 Список пород")
async def list_breeds(message: Message):
    breeds = get_cat_breeds()
    breed_list = "\n".join([f"{breed['name']} / {translator.translate(breed['name'], src='en', dest='ru').text}" for breed in breeds])
    await message.answer(f"Список пород котов:\n\n{breed_list}")

@dp.message(lambda message: message.text == "🐾 Введите породу")
async def prompt_breed_input(message: Message):
    await message.answer("Введите название породы на русском или английском языке:")

@dp.message(lambda message: message.text not in ["📜 Список пород", "🐾 Введите породу", "🔄 Старт", "🚀 Космос"])
async def send_cat_info(message: Message):
    breed_name = message.text
    breed_info = get_breed_info(breed_name)
    if breed_info:
        cat_image_url = get_cat_image_by_breed(breed_info['id'])
        description_ru = translator.translate(breed_info['description'], src='en', dest='ru').text
        temperament_ru = translator.translate(breed_info['temperament'], src='en', dest='ru').text
        info = (
            f"Название породы: {breed_info['name']} / {translator.translate(breed_info['name'], src='en', dest='ru').text}\n"
            f"Описание: {description_ru}\n"
            f"Продолжительность жизни: {breed_info['life_span']} лет\n"
            f"Темперамент: {temperament_ru}\n"
        )
        await message.answer_photo(cat_image_url, caption=info)
    else:
        await message.answer("Кот с такой породой не найден.")

@dp.message(lambda message: message.text == "🚀 Космос")
async def send_random_apod(message: Message):
    apod = get_random_apod()
    photo_url = apod.get('url', '')
    title = apod.get('title', 'Нет названия')

    # Переводим заголовок на русский язык
    translated_title = translator.translate(title, src='en', dest='ru').text

    # Отправляем фото с переводом
    await message.answer_photo(photo_url, caption=f"{translated_title}")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
