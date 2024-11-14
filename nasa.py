import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import random
import requests
from datetime import datetime, timedelta
from config import TOKEN, NASA_API_KEY
from googletrans import Translator  # Для перевода текста

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализация переводчика
translator = Translator()

# Хранение использованных URL для предотвращения повторов
used_urls = set()

def get_random_apod():
    global used_urls
    # Устанавливаем диапазон дат за последний год
    end_date = datetime.now()
    start_date = datetime.now() - timedelta(days=365)

    # Пытаемся выбрать уникальную дату
    while True:
        random_days = random.randint(0, 365)
        random_date = start_date + timedelta(days=random_days)
        date_str = random_date.strftime('%Y-%m-%d')

        # Формируем запрос к API NASA
        url = f'https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={date_str}'
        response = requests.get(url).json()

        # Проверяем, что URL уникален
        if response['url'] not in used_urls:
            used_urls.add(response['url'])  # Добавляем в список использованных URL
            print(f"Выбрана уникальная дата: {date_str}")  # Для отладки
            return response


@dp.message(Command("random_apod"))
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
