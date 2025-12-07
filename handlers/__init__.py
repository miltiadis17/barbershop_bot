"""
Handlers module
"""
from .client_handlers import router as client_router
from .admin_handlers import router as admin_router

__all__ = ['client_router', 'admin_router']
