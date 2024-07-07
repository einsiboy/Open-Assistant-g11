from typing import Any

from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from pydantic import BaseModel
from pymilvus import MilvusClient, MilvusException


class InsertResult(BaseModel):
    insert_count: int
    ids: list[Any]
    cost: float


class MilvusDatastore:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.extra_output_fields = ["text"]

        self.client = MilvusClient(host=host, port=port)

    def insert(self, vectors: list[dict]) -> InsertResult:
        result = self.client.insert(self.collection_name, vectors)
        return InsertResult(**result)

    def search_single_vector(self, collection, vectors, top_k=5) -> list[dict]:
        """
        returns list of dict with the keys:
            id, text, distance
        """

        try:
            result = self.client.search(
                collection_name=collection, data=[vectors], limit=top_k, output_fields=self.extra_output_fields
            )
            result = result[0]  # 0 because we only have one vector

            # results is a list of dicts with the keys: ["id, "distance"]
            # all extra_output_fields are also included under a
            # subdict under the key 'entity'
            final_results = []

            for hit in result:
                result_dict = {"id": hit["id"], "distance": hit["distance"]}

                # Add any extra output fields
                if "entity" in hit:
                    for field in self.extra_output_fields:
                        if field in hit["entity"]:
                            result_dict[field] = hit["entity"][field]

                final_results.append(result_dict)

            return final_results

        except MilvusException as e:
            if e.code == 100:
                raise OasstError(f"Collection not found: '{collection}'", OasstErrorCode.COLLECTION_NOT_FOUND)
