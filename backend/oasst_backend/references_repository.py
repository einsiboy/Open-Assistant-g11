"""
Following the pattern already established in OA, 
this module will handle the interaction with the database 
and vector search for the references service.

It seems that the routers usually handle high-level logic, 
with the details implemented in the repository classes. 
"""

from oasst_backend.embedding_model import model as embedding_model
from oasst_backend.milvus_datastore import MilvusDatastore
from sqlmodel import Session


class ReferencesRepository:
    def __init__(
        self,
        db: Session,
        vector_db: MilvusDatastore,
        #  client_user: protocol_schema.User,  # used when inserting data into the database
    ):

        self.db = db
        self.vector_db = vector_db
        # self.client_user = client_user

    async def get_references(self, query: str, lang: str) -> list[dict]:
        """
        Fetch references from the backend.

        Note: if needed we could do something like:
        asyncio.to_thread(embedding_model.encode, query)..
        or asyncio.get_event_loop().run_in_executor(None, embedding_model.encode, query)

        Look into if needed
        """
        query_vector = embedding_model.encode(query)

        res = self.vector_db.search_single_vector(collection=lang, vectors=query_vector, top_k=5)
        return res
