import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from configuration import config
from database import DataBase
import handlers


async def main():
    db = DataBase()
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage(), db=db)

    dp.include_router(handlers.start_router)
    dp.include_router(handlers.router1)
    dp.include_router(handlers.router2)
    dp.include_router(handlers.router_filter)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())




