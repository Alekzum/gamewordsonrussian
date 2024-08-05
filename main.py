from utils.config import BOT_API
from aiogram import Bot, Dispatcher
import handlers.game as r_game
import asyncio
import logging


bot = Bot(BOT_API)
dp = Dispatcher()

dp.include_router(r_game.router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
