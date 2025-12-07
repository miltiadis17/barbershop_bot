"""
Inline клавиатуры для бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_services_keyboard(services: list) -> InlineKeyboardMarkup:
    """Клавиатура выбора услуги"""
    builder = InlineKeyboardBuilder()
    for service in services:
        builder.button(
            text=service['name'],
            callback_data=f"service:{service['id']}"
        )
    builder.adjust(1)
    return builder.as_markup()


def get_masters_keyboard(masters: list) -> InlineKeyboardMarkup:
    """Клавиатура выбора мастера"""
    builder = InlineKeyboardBuilder()
    for master in masters:
        builder.button(
            text=master,
            callback_data=f"master:{master}"
        )
    builder.adjust(2)
    return builder.as_markup()


def get_dates_keyboard(dates: list) -> InlineKeyboardMarkup:
    """Клавиатура выбора даты"""
    builder = InlineKeyboardBuilder()
    for date_info in dates:
        builder.button(
            text=date_info['display'],
            callback_data=f"date:{date_info['value']}"
        )
    builder.adjust(2)
    return builder.as_markup()


def get_time_slots_keyboard(time_slots: list) -> InlineKeyboardMarkup:
    """Клавиатура выбора времени"""
    builder = InlineKeyboardBuilder()
    for slot in time_slots:
        builder.button(
            text=slot,
            callback_data=f"time:{slot}"
        )
    builder.adjust(3)
    return builder.as_markup()


def get_my_bookings_keyboard(bookings: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком записей пользователя"""
    builder = InlineKeyboardBuilder()
    for booking in bookings:
        date_str = booking['booking_date'].strftime('%d.%m.%Y')
        time_str = booking['booking_time'].strftime('%H:%M')
        text = f"{date_str} {time_str} - {booking['master']}"
        builder.button(
            text=text,
            callback_data=f"view_booking:{booking['id']}"
        )
    builder.adjust(1)
    return builder.as_markup()


def get_cancel_confirmation_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения отмены записи"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Да, отменить",
        callback_data=f"confirm_cancel:{booking_id}"
    )
    builder.button(
        text="❌ Нет, оставить",
        callback_data="cancel_back"
    )
    builder.adjust(1)
    return builder.as_markup()
