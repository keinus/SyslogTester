"""
Syslog Generator API

A FastAPI application for generating, parsing and sending syslog messages
according to RFC 3164 & 5424 standards.

This module serves as the main entry point for the Syslog Generator API,
setting up the FastAPI application with appropriate middleware, routers,
and endpoints for interacting with syslog functionality.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core import settings
from app.routers import syslog_router, info_router
from app.routers.examples import router as examples_router

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Generate, parse and send syslog messages according to RFC 3164 & 5424 standards"
)
"""FastAPI 애플리케이션 인스턴스를 생성"""

# Mount static files
app.mount("/static", StaticFiles(directory="./static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(info_router)
app.include_router(syslog_router)
app.include_router(examples_router)


@app.get("/")
async def serve_index() -> FileResponse:
    """메인 페이지를 제공합니다.

    HTML 정적 파일을 클라이언트에게 전송하여 메인 페이지를 렌더링합니다.
    Returns:
        FileResponse: index.html 파일의 응답 객체
    """

    return FileResponse("./static/index.html")


# Health check endpoint
@app.get("/health")
async def health_check() -> dict[str, str]:
    """헬스 체크 엔드포인트.
    Returns:
        dict[str, str]: 상태와 버전 정보를 담은 딕셔너리
    """
    return {"status": "healthy", "version": settings.version}
