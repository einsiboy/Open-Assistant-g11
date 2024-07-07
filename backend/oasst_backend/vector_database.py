"""
Follow the same pattern as exists for the sql db, 
i.e. create an instance of the MilvusDatastore class here, 
and then use the instance with dependency injection in the routers.
"""

from oasst_backend.config import settings
from oasst_backend.milvus_datastore import MilvusDatastore
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode

if settings.MILVUS_HOST is None:
    raise OasstError("MILVUS_HOST is not set", error_code=OasstErrorCode.MILVUS_HOST_NOT_SET)

milvus = MilvusDatastore(
    host=settings.MILVUS_HOST,
    port=settings.MILVUS_PORT,
)
