"""
Database module
"""
from .connection import init_db, get_connection, close_all_connections
from .models import (
    create_service,
    get_all_services,
    create_booking,
    get_bookings_by_user,
    get_bookings_by_date,
    get_bookings_by_master_date_time,
    delete_booking,
    delete_old_bookings
)

__all__ = [
    'init_db',
    'get_connection',
    'close_all_connections',
    'create_service',
    'get_all_services',
    'create_booking',
    'get_bookings_by_user',
    'get_bookings_by_date',
    'get_bookings_by_master_date_time',
    'delete_booking',
    'delete_old_bookings'
]
