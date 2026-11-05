# ============================================================
# OpenAlex API Communication Service
# ============================================================

import re

from typing import Any
from urllib.parse import urlsplit

import httpx

from app.config import Settings


# 1. CUSTOM OPENALEX SERVICE ERROR
class OpenAlexServiceError(Exception):
    """Custom exception for OpenAlex API errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
    ):
        self.status_code = status_code
        self.detail = detail

        super().__init__(detail)


# 2. NORMALIZE OPENALEX AUTHOR ID
def normalize_author_id(author_id: str) -> str:
    """
    Validate and normalize an OpenAlex Author ID.

    Accepted:
        A5023888391
        https://openalex.org/A5023888391
        http://openalex.org/A5023888391

    Returns:
        A5023888391
    """

    if not isinstance(author_id, str):
        raise ValueError("Author ID must be a string.")

    author_id = author_id.strip()

    if not author_id:
        raise ValueError("Author ID cannot be empty.")

    # Handle complete OpenAlex URLs.
    if "://" in author_id:

        try:
            parsed_url = urlsplit(author_id)

        except ValueError as exc:
            raise ValueError("Invalid OpenAlex Author URL.") from exc

        if (
            parsed_url.scheme not in {"http", "https"}
            or parsed_url.hostname != "openalex.org"
            or parsed_url.query
            or parsed_url.fragment
        ):
            raise ValueError("Invalid OpenAlex Author URL.")

        author_id = parsed_url.path.strip("/")

    # Handle trailing slash and whitespace.
    author_id = author_id.strip().rstrip("/")

    # Validate OpenAlex Author ID format.
    if not re.fullmatch(r"A\d+", author_id):

        raise ValueError(
            "Invalid OpenAlex Author ID. "
            "Expected format: A123456789."
        )

    return author_id


# 3. BUILD OPENALEX REQUEST PARAMETERS
def _build_params(settings: Settings) -> dict:
    """
    Build OpenAlex API request parameters.

    The API key is retrieved from application settings.
    """

    params = {}

    if settings.OPENALEX_API_KEY:
        params["api_key"] = settings.OPENALEX_API_KEY

    return params


# 4. SEND REQUEST AND PROCESS RESPONSE
async def _request_json(
    client: httpx.AsyncClient,
    url: str,
    params: dict | None = None,
) -> dict[str, Any]:
    """
    Send an asynchronous GET request to OpenAlex.

    Handle:
        - Timeout errors
        - Connection errors
        - HTTP errors
        - Invalid JSON responses
        - Unexpected response structures
    """

    try:

        response = await client.get(
            url,
            params=params,
        )

    except httpx.TimeoutException as exc:

        raise OpenAlexServiceError(
            status_code=504,
            detail="OpenAlex API request timed out.",
        ) from exc

    except httpx.RequestError as exc:

        raise OpenAlexServiceError(
            status_code=502,
            detail="Unable to communicate with OpenAlex.",
        ) from exc


    # HTTP STATUS HANDLING
    if response.status_code == 404:

        raise OpenAlexServiceError(
            status_code=404,
            detail="The requested OpenAlex author was not found.",
        )

    if response.status_code == 401:

        raise OpenAlexServiceError(
            status_code=401,
            detail="OpenAlex authentication failed.",
        )

    if response.status_code == 403:

        raise OpenAlexServiceError(
            status_code=403,
            detail="OpenAlex API key is invalid or not authorized.",
        )

    if response.status_code == 429:

        raise OpenAlexServiceError(
            status_code=429,
            detail="OpenAlex API rate limit exceeded. Retry later.",
        )

    if response.is_error:

        raise OpenAlexServiceError(
            status_code=502,
            detail=(
                "OpenAlex returned an unsuccessful response: "
                f"HTTP {response.status_code}."
            ),
        )


    # JSON RESPONSE HANDLING
    try:

        data = response.json()

    except ValueError as exc:

        raise OpenAlexServiceError(
            status_code=502,
            detail="OpenAlex returned an invalid JSON response.",
        ) from exc

    if not isinstance(data, dict):

        raise OpenAlexServiceError(
            status_code=502,
            detail="Unexpected response structure received from OpenAlex.",
        )

    return data


# 5. GET AUTHOR BY OPENALEX ID

async def get_author_by_id(
    author_id: str,
    client: httpx.AsyncClient,
    settings: Settings,
) -> dict[str, Any]:
    """
    Retrieve a single author record using OpenAlex Author ID.

    Returns:
        Original OpenAlex author JSON.

    Field extraction is handled separately by
    extraction_service.py.
    """


    # Step 1: Normalize Author ID
    author_id = normalize_author_id(author_id)


    # Step 2: Build API request
    url = f"/authors/{author_id}"

    params = _build_params(settings)


    # Step 3: Retrieve raw author JSON
    data = await _request_json(
        client=client,
        url=url,
        params=params,
    )

    # Step 4: Validate returned author ID
    returned_id = data.get("id")

    if not returned_id:

        raise OpenAlexServiceError(
            status_code=502,
            detail="OpenAlex response does not contain an author ID.",
        )

    try:

        returned_id = normalize_author_id(returned_id)

    except ValueError as exc:

        raise OpenAlexServiceError(
            status_code=502,
            detail="OpenAlex returned an invalid author ID.",
        ) from exc

    if returned_id != author_id:

        raise OpenAlexServiceError(
            status_code=502,
            detail="The returned author ID does not match the requested ID.",
        )

    # Step 5: Return raw author data
    return data