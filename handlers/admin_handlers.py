"""
Обработчики для администраторов
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta

from database import get_bookings_by_date
from utils import is_admin

router = Router()


# ========== КОМАНДА /bookings (только для админов) ==========

@router.message(Command("bookings"))
async def cmd_bookings(message: Message):
    """Показать записи на выбранный день"""
    user_id = message.from_user.id

    # Проверка прав админа
    if not is_admin(user_id):
        await message.answer("❌ Доступ запрещён.")
        return

    # Показываем выбор даты
    await show_date_selection(message)


async def show_date_selection(message: Message):
    """Показать выбор даты для просмотра записей"""
    builder = InlineKeyboardBuilder()

    # Сегодня
    today = datetime.now().date()
    builder.button(
        text=f"Сегодня ({today.strftime('%d.%m')})",
        callback_data=f"admin_date:{today.isoformat()}"
    )

    # Следующие 6 дней
    for i in range(1, 7):
        date = today + timedelta(days=i)
        weekday_names = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
        weekday = weekday_names[date.weekday()]
        builder.button(
            text=f"{weekday} {date.strftime('%d.%m')}",
            callback_data=f"admin_date:{date.isoformat()}"
        )

    builder.adjust(2)

    await message.answer(
        "📅 Выберите дату для просмотра записей:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.startswith("admin_date:"))
async def show_bookings_for_date(callback: CallbackQuery):
    """Показать записи на выбранную дату"""
    user_id = callback.from_user.id

    # Дополнительная проверка прав
    if not is_admin(user_id):
        await callback.answer("❌ Доступ запрещён.", show_alert=True)
        return

    date_str = callback.data.split(":")[1]
    bookings = get_bookings_by_date(date_str)

    # Форматируем дату для отображения
    date_obj = datetime.fromisoformat(date_str)
    date_display = date_obj.strftime("%d.%m.%Y (%A)")

    if not bookings:
        await callback.message.edit_text(
            f"📅 Записи на {date_display}:\n\n"
            "Записей нет."
        )
        await callback.answer()
        return

    # Формируем список записей
    text = f"📅 <b>Записи на {date_display}:</b>\n\n"

    for booking in bookings:
        time_str = booking['booking_time'].strftime('%H:%M')
        username_display = f"@{booking['username']}" if booking['username'] else f"ID: {booking['user_id']}"

        text += (
            f"🕐 <b>{time_str}</b> | {booking['master']}\n"
            f"   📋 {booking['service_name']}\n"
            f"   👤 {username_display}\n\n"
        )

    text += f"<i>Всего записей: {len(bookings)}</i>"

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()
