"""
Вспомогательные функции
"""
from datetime import datetime, timedelta, time
from config import MASTERS_SCHEDULE, BOOKING_DAYS_AHEAD, SLOT_DURATION_MINUTES, ADMIN_IDS
from database.models import get_bookings_by_master_date_time


def get_available_masters() -> list:
    """Получить список всех мастеров"""
    return list(MASTERS_SCHEDULE.keys())


def get_available_dates(master: str) -> list:
    """Получить доступные даты для мастера (сегодня + N дней)"""
    schedule = MASTERS_SCHEDULE.get(master)
    if not schedule:
        return []

    available_dates = []
    today = datetime.now().date()

    for i in range(BOOKING_DAYS_AHEAD + 1):
        date = today + timedelta(days=i)
        weekday = date.weekday()

        if weekday in schedule['days']:
            # Форматируем дату для отображения
            if i == 0:
                display = f"Сегодня ({date.strftime('%d.%m')})"
            elif i == 1:
                display = f"Завтра ({date.strftime('%d.%m')})"
            else:
                weekday_names = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
                display = f"{weekday_names[weekday]} {date.strftime('%d.%m')}"

            available_dates.append({
                'display': display,
                'value': date.isoformat()
            })

    return available_dates


def get_available_time_slots(master: str, date_str: str) -> list:
    """Получить свободные временные слоты для мастера на дату"""
    schedule = MASTERS_SCHEDULE.get(master)
    if not schedule:
        return []

    # Парсим время работы
    start_time = datetime.strptime(schedule['start'], '%H:%M').time()
    end_time = datetime.strptime(schedule['end'], '%H:%M').time()

    # Генерируем все возможные слоты
    slots = []
    current_time = datetime.combine(datetime.today(), start_time)
    end_datetime = datetime.combine(datetime.today(), end_time)

    while current_time < end_datetime:
        slot_time = current_time.strftime('%H:%M')

        # Проверяем, занят ли слот
        is_booked = get_bookings_by_master_date_time(master, date_str, slot_time)

        # Если слот свободен, добавляем
        if not is_booked:
            # Дополнительная проверка: если дата сегодня, не показываем прошедшие слоты
            date_obj = datetime.fromisoformat(date_str).date()
            if date_obj == datetime.now().date():
                slot_datetime = datetime.strptime(slot_time, '%H:%M').time()
                current_now = datetime.now().time()
                if slot_datetime <= current_now:
                    current_time += timedelta(minutes=SLOT_DURATION_MINUTES)
                    continue

            slots.append(slot_time)

        current_time += timedelta(minutes=SLOT_DURATION_MINUTES)

    return slots


def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь администратором"""
    return user_id in ADMIN_IDS
