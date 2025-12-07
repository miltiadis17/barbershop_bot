"""
Инициализация начальных данных в БД
"""
from .models import create_service
import logging

logger = logging.getLogger(__name__)


def init_services():
    """Создать начальные услуги"""
    services = [
        "Стрижка",
        "Борода",
        "Комплекс (стрижка + борода)",
    ]

    for service_name in services:
        try:
            service_id = create_service(service_name)
            logger.info(f"Service '{service_name}' created/verified with ID: {service_id}")
        except Exception as e:
            logger.error(f"Error creating service '{service_name}': {e}")
