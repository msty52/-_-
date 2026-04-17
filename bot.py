from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
import json

async def on_fetch(request, env):
    # Используем токен из переменных Cloudflare
    bot = Bot(token=env.BOT_TOKEN)
    dp = Dispatcher()

    @dp.message()
    async def echo(message: types.Message):
        await message.answer("Бот на Cloudflare получил ваше сообщение!")

    if request.method == "POST":
        data = await request.json()
        update = Update.model_validate(data, context={"bot": bot})
        await dp.feed_update(bot, update)
        return Response.new("ok")
    
    return Response.new("Worker is running")
