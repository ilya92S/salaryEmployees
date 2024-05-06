import asyncio
import json
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

logger = logging.getLogger("bot_loger")

bot_token = "токен от BotFather"

bot = Bot(bot_token)
dp = Dispatcher()

client = AsyncIOMotorClient('mongodb://localhost:27017/')
db = client['sampleDB']
collection = db['sample_collection']


async def aggregate(dt_from, dt_upto, group_type):
    """
    Функция принимает параметры для поиска по БД.
    :param dt_from: начальная дата.
    :param dt_upto: конечная дата.
    :param group_type: группировка.
    :return: список с зарплатами и датами.
    """
    dt_from = datetime.fromisoformat(dt_from)
    dt_upto = datetime.fromisoformat(dt_upto)

    if group_type == 'month':
        group_unit = 'month'
    elif group_type == 'day':
        group_unit = 'day'
    elif group_type == 'hour':
        group_unit = 'hour'
    else:
        raise ValueError("Ошибка. Группировка должна быть по 'hour', 'day', или 'month'.")

    logging.info('Готовим агрегатор и собираем данные для ответа')
    pipeline = [
        {"$match": {"dt": {"$gte": dt_from, "$lte": dt_upto}}},
        {"$group": {
            "_id": {"$dateTrunc": {"date": "$dt", "unit": group_unit}},
            "totalValue": {"$sum": "$value"}
        }},
        {"$sort": {"_id": 1}}
    ]

    cursor = collection.aggregate(pipeline)
    results = await cursor.to_list(length=None)

    logging.info('Собираем данные для ответа')
    dataset = [result['totalValue'] for result in results]
    labels = [result['_id'].isoformat() for result in results]

    return {"dataset": dataset, "labels": labels}


@dp.message(Command('start', 'help'))
async def send_welcome(message: types.Message) -> None:
    """
    Обработчик реагирует на /start и /help, позволяет понять пользователю что от него требуется.
    :param message: собщение начала работы бота и помощь по использованию.
    """
    await message.reply("Привет! Отправь мне данные в формате JSON для агрегации. Например:\n"
                        "{\"dt_from\": \"2022-10-01T00:00:00\", \"dt_upto\": \"2022-11-30T23:59:00\","
                        " \"group_type\": \"day\"}")


@dp.message()
async def handle_input(message: types.Message):
    """
    Обработчик отлавливает и реагирует на любое сообщение от пользователя,
    если сообщение не соответствует типу JSON, отправляет об этом уведомление.
    :param message: любое сообщение от пользователя.
    """
    logging.info('Запустилась функция: handle_input')
    try:
        input_data = json.loads(message.text)
        result = await aggregate(input_data["dt_from"], input_data["dt_upto"], input_data["group_type"])
        await message.answer(f"Результаты: {result}")
    except json.JSONDecodeError:
        logging.error('Введен неправильный формат данных')
        await message.reply("Пожалуйста, отправь данные в правильном JSON формате.")
    except Exception as e:
        await message.reply(str(e))


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
