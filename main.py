import asyncio
from app.config import TOKEN
from aiogram import Bot, Dispatcher
from app.handlers import router
from app.scheduler import schedule_checker
from app.db_handlers import init_db
from app.db_create import create_database, create_tables

async def main():
    await create_database()
    await create_tables()

    await init_db()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    asyncio.create_task(schedule_checker(bot))

    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        print("bot on")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("bot off")