import httpx

from fastapi import Request

from app.config import Settings


# ============================================================
# 1. GET SHARED HTTP CLIENT
# ============================================================

def get_http_client(
    request: Request,
) -> httpx.AsyncClient:
    """
    Retrieve the shared HTTPX client initialized
    during application startup in main.py.
    """

    client = getattr(
        request.app.state,
        "http_client",
        None,
    )

    if client is None:
        raise RuntimeError(
            "HTTP client has not been initialized."
        )

    return client


# ============================================================
# 2. GET APPLICATION SETTINGS
# ============================================================

def get_settings(
    request: Request,
) -> Settings:
    """
    Retrieve application settings initialized
    during application startup in main.py.
    """

    settings = getattr(
        request.app.state,
        "settings",
        None,
    )

    if settings is None:
        raise RuntimeError(
            "Application settings have not been initialized."
        )

    return settings