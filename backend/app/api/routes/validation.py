import logging
import httpx

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.api.dependencies import (
    get_http_client,
    get_settings as get_app_settings,
)

from app.config import Settings
from app.schemas.validation import ValidationResponse

from app.services.openalex_service import get_author_by_id
from app.services.extraction_service import extract_author_data
from app.services.validation_service import run_author_validation


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/validation",
    tags=["Validation"],
)


# ============================================================
# POST: RUN AUTHOR VALIDATION
# ============================================================

@router.post(
    "/{author_id}",
    response_model=ValidationResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Run Author Misattribution Validation",
    description=(
        "Fetch author data from OpenAlex, extract author details, "
        "execute all validation problems, and calculate the "
        "suspiciousness score."
    ),
)
async def run_validation(
    author_id: str,
    client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_app_settings),
) -> ValidationResponse:

    try:
        # 1. Fetch author data from OpenAlex
        raw_author = await get_author_by_id(
            author_id=author_id,
            client=client,
            settings=settings,
        )

        # 2. Extract normalized author data
        author_response = extract_author_data(raw_author)

        author_data = author_response.model_dump(
            mode="python"
        )

        # 3. Execute validation and scoring
        result = run_author_validation(
            author_data=author_data,
        )

        # 4. Return final response
        return result

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Author validation failed for %s.",
            author_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to complete author validation.",
        ) from exc