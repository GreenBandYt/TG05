import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import requests
from googletrans import Translator

from config import TOKEN, THE_CAT_API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализация переводчика
translator = Translator()

# Главное меню
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Вывести список пород")],
        [KeyboardButton(text="Введите породу")]
    ],
    resize_keyboard=True
)

def get_cat_breeds():
    url = 'https://api.thecatapi.com/v1/breeds'
    headers = {'x-api-key': THE_CAT_API_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

def get_cat_image_by_breed(breed_id):
    url = f'https://api.thecatapi.com/v1/images/search?breed_ids={breed_id}'
    headers = {'x-api-key': THE_CAT_API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data[0]['url']

def get_breed_info(breed_name):
    breeds = get_cat_breeds()
    for breed in breeds:
        if breed['name'].lower() == breed_name.lower():
            return breed
    return None

def is_english(text):
    # Проверяем, состоит ли текст из латинских букв
    return all('a' <= char.lower() <= 'z' or char.isspace() for char in text)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я бот, который показывает информацию о котах.",
        reply_markup=menu
    )

@dp.message(lambda message: message.text == "Вывести список пород")
async def list_breeds(message: Message):
    breeds = get_cat_breeds()
    breed_list = []
    for breed in breeds:
        # Переводим название на русский
        breed_name_ru = translator.translate(breed['name'], src='en', dest='ru').text
        breed_list.append(f"{breed['name']} / {breed_name_ru}")
    breed_text = "\n".join(breed_list)
    await message.answer(f"Список доступных пород:\n\n{breed_text}")

@dp.message(lambda message: message.text == "Введите породу")
async def ask_breed(message: Message):
    await message.answer("Введите название породы на русском или английском языке:")

@dp.message()
async def send_cat_info(message: Message):
    breed_name = message.text.strip()

    # Определяем язык ввода и переводим только если это русский
    if not is_english(breed_name):
        breed_name = translator.translate(breed_name, src='ru', dest='en').text

    breed_info = get_breed_info(breed_name)
    if breed_info:
        cat_image_url = get_cat_image_by_breed(breed_info['id'])

        # Переводим название, описание и темперамент на русский
        breed_name_ru = translator.translate(breed_info['name'], src='en', dest='ru').text
        description_ru = translator.translate(breed_info['description'], src='en', dest='ru').text
        temperament_ru = translator.translate(breed_info['temperament'], src='en', dest='ru').text

        info = (f"Название породы: {breed_info['name']} / {breed_name_ru}\n"
                f"Описание: {description_ru}\n"
                f"Продолжительность жизни: {breed_info['life_span']} лет\n"
                f"Темперамент: {temperament_ru}\n")
        await message.answer_photo(cat_image_url, caption=info)
    else:
        await message.answer("Кот с такой породой не найден.")


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
