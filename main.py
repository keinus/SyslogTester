#!/usr/bin/env python3
"""
Main entry point for the RFC 3164/5424 Syslog Parser application.
"""

import uvicorn
from app.core import settings
from app.main import app


if __name__ == "__main__":
    print(f"Starting {settings.app_name} v{settings.version}...")
    print(f"API available at: http://localhost:{settings.port}")
    print(f"API documentation at: http://localhost:{settings.port}/docs")
    print(f"Frontend available at: http://localhost:{settings.port}")

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
