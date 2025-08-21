from .syslog import router as syslog_router
from .test import router as test_router
from .info import router as info_router

__all__ = ["syslog_router", "test_router", "info_router"]