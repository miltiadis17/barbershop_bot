"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# PostgreSQL настройки
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "barbershop_bot")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Список админов (Telegram user_id)
ADMIN_IDS = [
    123456789,  # Замените на реальные user_id админов
]

# Рабочие графики мастеров
# Формат: {"мастер": {"days": [список дней недели 0=ПН], "start": "ЧЧ:ММ", "end": "ЧЧ:ММ"}}
MASTERS_SCHEDULE = {
    "Иван": {
        "days": [0, 1, 5, 6],  # ПН, ВТ, СБ, ВС
        "start": "12:00",
        "end": "21:00"
    },
    "Глеб": {
        "days": [0, 2, 4, 5],  # ПН, СР, ПТ, СБ
        "start": "12:00",
        "end": "21:00"
    },
    "Руслан": {
        "days": [1, 3, 5],  # ВТ, ЧТ, СБ
        "start": "15:00",
        "end": "21:00"
    },
    "Павел": {
        "days": [4, 5, 6],  # ПТ, СБ, ВС
        "start": "12:00",
        "end": "21:00"
    },
    "Ибрагим": {
        "days": [1, 3, 5, 6],  # ВТ, ЧТ, СБ, ВС
        "start": "12:00",
        "end": "20:00"
    }
}

# Настройки слотов
SLOT_DURATION_MINUTES = 30

# Количество дней для записи (сегодня + N дней)
BOOKING_DAYS_AHEAD = 14

# Срок хранения записей (дней)
BOOKING_RETENTION_DAYS = 3
