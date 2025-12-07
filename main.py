"""
Главный файл бота
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
from database import init_db, close_all_connections, delete_old_bookings
from database.init_data import init_services
from handlers import client_router, admin_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def cleanup_old_bookings():
    """Периодическая очистка старых записей"""
    try:
        deleted_count = delete_old_bookings()
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old bookings")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


async def main():
    """Основная функция запуска бота"""
    # Инициализация БД
    logger.info("Initializing database...")
    init_db()
    init_services()
    logger.info("Database initialized successfully")

    # Создание бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация роутеров
    dp.include_router(client_router)
    dp.include_router(admin_router)

    # Настройка планировщика для очистки старых записей
    scheduler = AsyncIOScheduler()
    # Запускать очистку каждый день в 03:00
    scheduler.add_job(cleanup_old_bookings, 'cron', hour=3, minute=0)
    scheduler.start()
    logger.info("Scheduler started for cleanup task")

    try:
        logger.info("Bot started")
        # Запуск бота
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Закрытие соединений при завершении
        await bot.session.close()
        close_all_connections()
        scheduler.shutdown()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
