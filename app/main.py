from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core import settings
from app.routers import syslog_router, test_router, info_router
from app.routers.examples import router as examples_router

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Generate, parse and send syslog messages according to RFC 3164 & 5424 standards"
)

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
app.include_router(test_router)
app.include_router(examples_router)


@app.get("/")
async def serve_index():
    """Serve the index.html file."""
    return FileResponse("./static/index.html")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.version}