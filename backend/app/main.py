
"""
FastAPI application entry point
Author Misattribution Detection System
"""

from contextlib import asynccontextmanager

import httpx

from fastapi import FastAPI

from app import __version__
from app.api.routes import authors, validation
from app.config import get_settings


# 1. APPLICATION LIFESPAN

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.

    Startup:
        1. Load application settings.
        2. Initialize shared HTTPX AsyncClient.
        3. Store resources in application state.

    Shutdown:
        1. Close the shared HTTPX client.
    """

    settings = get_settings()

    # OpenAlex API configuration
    base_url = settings.OPENALEX_BASE_URL.rstrip("/")

    timeout = httpx.Timeout(
        settings.REQUEST_TIMEOUT_SECONDS
    )

    # Initialize shared asynchronous HTTP client
    async with httpx.AsyncClient(
        base_url=base_url,
        timeout=timeout,
        headers={
            "User-Agent": (
                "Author-Misattribution-Detection-System/1.0"
            )
        },
        follow_redirects=True,
    ) as http_client:

        app.state.settings = settings
        app.state.http_client = http_client

        yield


# ============================================================
# 2. CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Author Misattribution Detection System",

    description=(
        "A backend system for retrieving OpenAlex author metadata, "
        "evaluating author misattribution signals, and calculating "
        "a weighted suspiciousness score."
    ),

    version=__version__,

    lifespan=lifespan,

    docs_url="/docs",
    redoc_url=None,
)



# 3. REGISTER API ROUTERS

# Author retrieval API
app.include_router(authors.router)

# Author validation API
app.include_router(validation.router)
