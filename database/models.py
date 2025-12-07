"""
Модели для работы с базой данных
"""
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
from .connection import get_connection, return_connection
from config import BOOKING_RETENTION_DAYS
import logging

logger = logging.getLogger(__name__)


# ========== УСЛУГИ ==========

def create_service(name: str) -> int:
    """Создать услугу"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO services (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id",
                (name,)
            )
            result = cur.fetchone()
            conn.commit()
            if result:
                return result[0]
            else:
                # Если услуга уже существует
                cur.execute("SELECT id FROM services WHERE name = %s", (name,))
                return cur.fetchone()[0]
    finally:
        return_connection(conn)


def get_all_services() -> list:
    """Получить все услуги"""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name FROM services ORDER BY id")
            return cur.fetchall()
    finally:
        return_connection(conn)


# ========== ЗАПИСИ ==========

def create_booking(user_id: int, username: str, service_id: int,
                   master: str, booking_date: str, booking_time: str) -> bool:
    """Создать запись"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO bookings (user_id, username, service_id, master, booking_date, booking_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, username, service_id, master, booking_date, booking_time))
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating booking: {e}")
        return False
    finally:
        return_connection(conn)


def get_bookings_by_user(user_id: int) -> list:
    """Получить записи пользователя (только будущие и сегодняшние)"""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT b.id, b.user_id, b.username, s.name as service_name,
                       b.master, b.booking_date, b.booking_time, b.created_at
                FROM bookings b
                JOIN services s ON b.service_id = s.id
                WHERE b.user_id = %s
                  AND b.booking_date >= CURRENT_DATE
                ORDER BY b.booking_date, b.booking_time
            """, (user_id,))
            return cur.fetchall()
    finally:
        return_connection(conn)


def get_bookings_by_date(booking_date: str) -> list:
    """Получить все записи на определенную дату"""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT b.id, b.user_id, b.username, s.name as service_name,
                       b.master, b.booking_date, b.booking_time, b.created_at
                FROM bookings b
                JOIN services s ON b.service_id = s.id
                WHERE b.booking_date = %s
                ORDER BY b.booking_time, b.master
            """, (booking_date,))
            return cur.fetchall()
    finally:
        return_connection(conn)


def get_bookings_by_master_date_time(master: str, booking_date: str, booking_time: str) -> bool:
    """Проверить, занят ли слот (возвращает True если занят)"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM bookings
                WHERE master = %s AND booking_date = %s AND booking_time = %s
            """, (master, booking_date, booking_time))
            count = cur.fetchone()[0]
            return count > 0
    finally:
        return_connection(conn)


def delete_booking(booking_id: int, user_id: int) -> bool:
    """Удалить запись (только свою)"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM bookings
                WHERE id = %s AND user_id = %s
            """, (booking_id, user_id))
            deleted = cur.rowcount > 0
            conn.commit()
            return deleted
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting booking: {e}")
        return False
    finally:
        return_connection(conn)


def delete_old_bookings():
    """Удалить записи старше N дней"""
    conn = get_connection()
    try:
        cutoff_date = datetime.now().date() - timedelta(days=BOOKING_RETENTION_DAYS)
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM bookings
                WHERE booking_date < %s
            """, (cutoff_date,))
            deleted_count = cur.rowcount
            conn.commit()
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} old bookings")
            return deleted_count
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting old bookings: {e}")
        return 0
    finally:
        return_connection(conn)
