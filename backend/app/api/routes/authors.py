from fastapi import APIRouter, Depends, HTTPException, status
import httpx

from app.api.dependencies import (
    get_http_client,
    get_settings,
)

from app.config import Settings

from app.schemas.author import AuthorResponse

from app.services.openalex_service import (
    get_author_by_id,
    OpenAlexServiceError,
)

from app.services.extraction_service import extract_author_data



# Authors API Router
router = APIRouter(
    prefix="/api/authors",
    tags=["Authors"],
)



# GET: Fetch Author By OpenAlex ID
@router.get(
    "/{author_id}",
    response_model=AuthorResponse,
    status_code=status.HTTP_200_OK,
    summary="Fetch Author by OpenAlex ID",
    description=(
        "Retrieve an author from OpenAlex using their Author ID, "
        "extract the required information, and return structured data."
    ),
)
async def fetch_author(
    author_id: str,
    client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    """
    Fetch an author using their OpenAlex Author ID.

    Steps:
        1. Validate the supplied Author ID.
        2. Retrieve raw author data from OpenAlex.
        3. Extract the required author information.
        4. Validate the extracted response structure.
        5. Return structured author information.
    """

    # Step 1: Retrieve raw author data from OpenAlex
    try:

        raw_author_data = await get_author_by_id(
            author_id=author_id,
            client=client,
            settings=settings,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except OpenAlexServiceError as exc:

        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.detail,
        ) from exc

    # Step 2: Extract required author information
    try:

        author_data = extract_author_data(
            raw_author_data
        )

    except (ValueError, KeyError, TypeError) as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Unable to extract author information "
                "from the OpenAlex response."
            ),
        ) from exc

    # Step 3: Return structured author information
    return author_data