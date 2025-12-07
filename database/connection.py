"""
Управление подключением к PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
import logging

logger = logging.getLogger(__name__)

# Connection pool
connection_pool = None


def init_db():
    """Инициализация базы данных и создание таблиц"""
    global connection_pool

    try:
        # Создаем connection pool
        connection_pool = SimpleConnectionPool(
            1, 10,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        logger.info("Connection pool created successfully")

        # Создаем таблицы
        conn = connection_pool.getconn()
        try:
            with conn.cursor() as cur:
                # Таблица услуг
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS services (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Таблица записей
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS bookings (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        username VARCHAR(100),
                        service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
                        master VARCHAR(50) NOT NULL,
                        booking_date DATE NOT NULL,
                        booking_time TIME NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(master, booking_date, booking_time)
                    )
                """)

                # Индексы для ускорения запросов
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_bookings_user
                    ON bookings(user_id)
                """)

                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_bookings_date
                    ON bookings(booking_date)
                """)

                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_bookings_master_date
                    ON bookings(master, booking_date)
                """)

                conn.commit()
                logger.info("Database tables created successfully")

        finally:
            connection_pool.putconn(conn)

    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise


def get_connection():
    """Получить соединение из пула"""
    if connection_pool is None:
        raise Exception("Connection pool is not initialized")
    return connection_pool.getconn()


def return_connection(conn):
    """Вернуть соединение в пул"""
    if connection_pool is not None:
        connection_pool.putconn(conn)


def close_all_connections():
    """Закрыть все соединения"""
    if connection_pool is not None:
        connection_pool.closeall()
        logger.info("All database connections closed")
