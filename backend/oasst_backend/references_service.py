"""
Think of this as a service layer for business logic. 
"""

from sqlmodel import Session

from oasst_shared.exceptions.oasst_api_error import OasstError
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

# TODO this is just for dev purposes to get the routing correct...
LOCAL_MODEL_PATH = "/Users/einar/git/Open-Assistant-g11/_notebooks/RAG/multilingual-e5-large-instruct_local"
TEST_CITATION_DATA_PATH = "/Users/einar/git/Open-Assistant-g11/_notebooks/RAG/citations_and_embeddings.pkl"


model = SentenceTransformer(LOCAL_MODEL_PATH, local_files_only=True)

with open(TEST_CITATION_DATA_PATH, "rb") as f:
    all_docs = pickle.load(f)

embeddings = [doc["embeddings"] for doc in all_docs]
embeddings = np.array(embeddings).astype('float32')


# index = faiss.IndexFlatL2(1024)
index = faiss.IndexFlatIP(1024)
index.add(embeddings)

def vector_search(query, k=5):
    query_vector = model.encode(query)
    query_vector = np.array(query_vector).astype('float32')
    # Reshape the query_vector to be a 2D matrix with 1 row
    query_vector = query_vector.reshape(1, -1)

    D, I = index.search(query_vector, k)
    return D, I

def similarity_search(query, k=5):
    D, I = vector_search(query, k)
    # return [(all_docs[i], d) for i, d in zip(I[0], D[0])]

    return [all_docs[i]["chunk"] for i in I[0]]  # return just chunks
    # return [all_docs[i] for i in I[0]]  # return the whole doc  




class ReferencesService:
    def __init__(self, db: Session):
        self.db = db

    async def get_references(self, query: str, lang: str) -> list[dict]:
        """
        Find the references that have the closest match to the query.
        """

        similar_docs = similarity_search(query)
        # convert list of strings to dict for dev purposes
        similar_docs = [{"id": str(i), "text": doc} for i, doc in enumerate(similar_docs)]
        return similar_docs

        # try:
        #     return [
        #         {
        #             "id": "1",
        #             "title": "Reference 1",
        #             "text": "This is the text of reference 1."
        #         },
        #         {
        #             "id": "2",
        #             "title": "Reference 2",
        #             "text": "This is the text of reference 2."
        #         }
        #     ]
            
        # except OasstError:
        #     pass
