"""
Keyboards module
"""
from .inline_keyboards import (
    get_services_keyboard,
    get_masters_keyboard,
    get_dates_keyboard,
    get_time_slots_keyboard,
    get_my_bookings_keyboard,
    get_cancel_confirmation_keyboard
)

__all__ = [
    'get_services_keyboard',
    'get_masters_keyboard',
    'get_dates_keyboard',
    'get_time_slots_keyboard',
    'get_my_bookings_keyboard',
    'get_cancel_confirmation_keyboard'
]
