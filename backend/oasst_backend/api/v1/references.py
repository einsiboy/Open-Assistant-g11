from fastapi import APIRouter, Depends, Query
from fastapi.security.api_key import APIKey
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.milvus_datastore import MilvusDatastore
from oasst_backend.references_repository import ReferencesRepository
from oasst_shared.exceptions import OasstError, OasstErrorCode
from sqlmodel import Session

router = APIRouter()


@router.get("/", response_model=list[dict])
async def get_references(
    *,
    db: Session = Depends(deps.get_db),
    vector_db: MilvusDatastore = Depends(deps.get_vector_db),
    api_key: APIKey = Depends(deps.get_api_key),
    query: str = Query(..., description="The search query string"),
    lang: str = Query("en", description="Language code, e.g. 'is' or 'en"),
) -> list[dict]:
    """
    Fetch references from the backend.
    """

    # This does the actual authentication
    api_client = deps.api_auth(api_key, db)
    try:
        ref_repository = ReferencesRepository(db, vector_db)
        # docs = await ref_repository.get_references(query, "is")  # hardcoded for development
        docs = await ref_repository.get_references(query, lang)
        print("--- docs", docs)
        return docs

    except OasstError:
        raise
    except Exception:
        logger.exception("Failed to fetch references.")
        raise OasstError("Failed to fetch references.", OasstErrorCode.FAILED_REFERENCEC_FETCH)
