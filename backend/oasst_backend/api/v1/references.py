from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.security.api_key import APIKey
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.config import settings
from oasst_backend.prompt_repository import PromptRepository, TaskRepository
from oasst_backend.tree_manager import TreeManager
from oasst_backend.user_repository import UserRepository
from oasst_backend.utils.database_utils import CommitMode, async_managed_tx_function
from oasst_shared.exceptions import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT

from oasst_backend import references_service

router = APIRouter()



# TODO: go over the dependencies, APIKey should be enough to fetch the references
#   since that is an authentication from the website, and we do not need user authentication here
@router.get("/", response_model=list[dict])
async def get_references(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    query: str = Query(..., description="The search query string"),  
    lang: str = Query("en", description="Language code, e.g. 'is' or 'en")  
) -> list[dict]:
    """
    Fetch references from the backend.
    """
    # TODO do I neeed this api_client??
    # api_client = deps.api_auth(api_key, db)
    try:
        ref_service = references_service.ReferencesService(None)  
        docs = await ref_service.get_references(query, lang)  
        return docs
        
    except OasstError:
        raise
    except Exception:
        logger.exception("Failed to fetch references.")
        raise OasstError("Failed to fetch references.", OasstErrorCode.FAILED_REFERENCEC_FETCH)
