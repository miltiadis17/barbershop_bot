"""
Обработчики для клиентов
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from database import (
    get_all_services,
    create_booking,
    get_bookings_by_user,
    delete_booking
)
from keyboards import (
    get_services_keyboard,
    get_masters_keyboard,
    get_dates_keyboard,
    get_time_slots_keyboard,
    get_my_bookings_keyboard,
    get_cancel_confirmation_keyboard
)
from utils import (
    get_available_masters,
    get_available_dates,
    get_available_time_slots
)

router = Router()


# Состояния для FSM
class BookingStates(StatesGroup):
    choosing_service = State()
    choosing_master = State()
    choosing_date = State()
    choosing_time = State()


# ========== КОМАНДА /start ==========

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()

    user_name = message.from_user.first_name or "друг"
    await message.answer(
        f"👋 Привет, {user_name}!\n\n"
        "Добро пожаловать в барбершоп!\n"
        "Я помогу тебе записаться на услугу.\n\n"
        "Доступные команды:\n"
        "/start - начать запись\n"
        "/my_bookings - мои записи"
    )

    # Начинаем процесс записи
    await start_booking(message, state)


async def start_booking(message: Message, state: FSMContext):
    """Начать процесс записи"""
    services = get_all_services()

    if not services:
        await message.answer("К сожалению, услуги временно недоступны. Попробуйте позже.")
        return

    await state.set_state(BookingStates.choosing_service)
    await message.answer(
        "📋 Шаг 1/4: Выберите услугу:",
        reply_markup=get_services_keyboard(services)
    )


# ========== ШАГ 1: ВЫБОР УСЛУГИ ==========

@router.callback_query(F.data.startswith("service:"), BookingStates.choosing_service)
async def process_service_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора услуги"""
    service_id = int(callback.data.split(":")[1])

    # Находим название услуги
    services = get_all_services()
    service_name = next((s['name'] for s in services if s['id'] == service_id), None)

    if not service_name:
        await callback.answer("Ошибка выбора услуги", show_alert=True)
        return

    # Сохраняем выбор
    await state.update_data(service_id=service_id, service_name=service_name)

    # Переходим к выбору мастера
    masters = get_available_masters()
    await state.set_state(BookingStates.choosing_master)

    await callback.message.edit_text(
        f"✅ Услуга: {service_name}\n\n"
        "👨‍💼 Шаг 2/4: Выберите мастера:",
        reply_markup=get_masters_keyboard(masters)
    )
    await callback.answer()


# ========== ШАГ 2: ВЫБОР МАСТЕРА ==========

@router.callback_query(F.data.startswith("master:"), BookingStates.choosing_master)
async def process_master_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора мастера"""
    master = callback.data.split(":")[1]

    # Сохраняем выбор
    await state.update_data(master=master)

    # Получаем доступные даты для мастера
    dates = get_available_dates(master)

    if not dates:
        await callback.answer("У этого мастера нет доступных дней", show_alert=True)
        return

    await state.set_state(BookingStates.choosing_date)

    data = await state.get_data()
    await callback.message.edit_text(
        f"✅ Услуга: {data['service_name']}\n"
        f"✅ Мастер: {master}\n\n"
        "📅 Шаг 3/4: Выберите дату:",
        reply_markup=get_dates_keyboard(dates)
    )
    await callback.answer()


# ========== ШАГ 3: ВЫБОР ДАТЫ ==========

@router.callback_query(F.data.startswith("date:"), BookingStates.choosing_date)
async def process_date_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора даты"""
    date_str = callback.data.split(":")[1]

    # Сохраняем выбор
    await state.update_data(booking_date=date_str)

    # Получаем свободные слоты
    data = await state.get_data()
    master = data['master']
    time_slots = get_available_time_slots(master, date_str)

    if not time_slots:
        await callback.answer("На эту дату нет свободных слотов", show_alert=True)
        return

    await state.set_state(BookingStates.choosing_time)

    # Форматируем дату для отображения
    date_obj = datetime.fromisoformat(date_str)
    date_display = date_obj.strftime("%d.%m.%Y")

    await callback.message.edit_text(
        f"✅ Услуга: {data['service_name']}\n"
        f"✅ Мастер: {master}\n"
        f"✅ Дата: {date_display}\n\n"
        "🕐 Шаг 4/4: Выберите время:",
        reply_markup=get_time_slots_keyboard(time_slots)
    )
    await callback.answer()


# ========== ШАГ 4: ВЫБОР ВРЕМЕНИ И ПОДТВЕРЖДЕНИЕ ==========

@router.callback_query(F.data.startswith("time:"), BookingStates.choosing_time)
async def process_time_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора времени и создание записи"""
    booking_time = callback.data.split(":")[1]

    # Получаем все данные
    data = await state.get_data()
    user_id = callback.from_user.id
    username = callback.from_user.username or f"user_{user_id}"

    # Создаем запись
    success = create_booking(
        user_id=user_id,
        username=username,
        service_id=data['service_id'],
        master=data['master'],
        booking_date=data['booking_date'],
        booking_time=booking_time
    )

    if success:
        # Форматируем дату для отображения
        date_obj = datetime.fromisoformat(data['booking_date'])
        date_display = date_obj.strftime("%d.%m.%Y")

        await callback.message.edit_text(
            "✅ <b>Запись успешно создана!</b>\n\n"
            f"📋 Услуга: {data['service_name']}\n"
            f"👨‍💼 Мастер: {data['master']}\n"
            f"📅 Дата: {date_display}\n"
            f"🕐 Время: {booking_time}\n\n"
            "Ждём вас! 😊\n\n"
            "Чтобы посмотреть свои записи: /my_bookings",
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка при создании записи.\n"
            "Возможно, это время уже занято.\n\n"
            "Попробуйте снова: /start"
        )

    await state.clear()
    await callback.answer()


# ========== КОМАНДА /my_bookings ==========

@router.message(Command("my_bookings"))
async def cmd_my_bookings(message: Message, state: FSMContext):
    """Показать записи пользователя"""
    await state.clear()

    user_id = message.from_user.id
    bookings = get_bookings_by_user(user_id)

    if not bookings:
        await message.answer(
            "У вас пока нет активных записей.\n\n"
            "Чтобы записаться: /start"
        )
        return

    await message.answer(
        "📝 Ваши записи:\n\n"
        "Выберите запись для просмотра:",
        reply_markup=get_my_bookings_keyboard(bookings)
    )


@router.callback_query(F.data.startswith("view_booking:"))
async def view_booking_details(callback: CallbackQuery):
    """Показать детали записи"""
    booking_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    # Получаем записи пользователя
    bookings = get_bookings_by_user(user_id)
    booking = next((b for b in bookings if b['id'] == booking_id), None)

    if not booking:
        await callback.answer("Запись не найдена", show_alert=True)
        return

    date_display = booking['booking_date'].strftime("%d.%m.%Y")
    time_display = booking['booking_time'].strftime("%H:%M")

    await callback.message.edit_text(
        f"📝 <b>Детали записи:</b>\n\n"
        f"📋 Услуга: {booking['service_name']}\n"
        f"👨‍💼 Мастер: {booking['master']}\n"
        f"📅 Дата: {date_display}\n"
        f"🕐 Время: {time_display}\n\n"
        f"Хотите отменить эту запись?",
        parse_mode="HTML",
        reply_markup=get_cancel_confirmation_keyboard(booking_id)
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_back")
async def cancel_back_to_list(callback: CallbackQuery):
    """Вернуться к списку записей"""
    user_id = callback.from_user.id
    bookings = get_bookings_by_user(user_id)

    if not bookings:
        await callback.message.edit_text(
            "У вас больше нет активных записей.\n\n"
            "Чтобы записаться: /start"
        )
    else:
        await callback.message.edit_text(
            "📝 Ваши записи:\n\n"
            "Выберите запись для просмотра:",
            reply_markup=get_my_bookings_keyboard(bookings)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_cancel:"))
async def confirm_cancel_booking(callback: CallbackQuery):
    """Подтверждение отмены записи"""
    booking_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    success = delete_booking(booking_id, user_id)

    if success:
        await callback.message.edit_text(
            "✅ Запись успешно отменена.\n\n"
            "Чтобы записаться снова: /start\n"
            "Ваши записи: /my_bookings"
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка при отмене записи.\n\n"
            "Попробуйте позже."
        )

    await callback.answer()
