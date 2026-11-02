from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from acme_policy_copilot.logger import logger
from acme_policy_copilot.exception import RAGException
import sys

COLLECTION_NAME = "acme_policy_chunks"
VECTOR_SIZE = 384

class QdrantStore:
    def __init__(self):
        try:
            logger.info("Initializing Qdrant")
            self.client = QdrantClient(path="qdrant_data")
            self._create_collection()

        except Exception as e:
            logger.error("Error while initializing Qdrant")
            raise RAGException(e, sys)

    def _create_collection(self):
        collections = self.client.get_collections().collections
        collection_exists = any(
            collection.name == COLLECTION_NAME
            for collection in collections
        )

        if not collection_exists:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )

            logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")
        else:
            logger.info(f"Collection already exists: {COLLECTION_NAME}")

    def add_documents(self, chunks, embeddings):
        try:
            points = []
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                points.append(
                    PointStruct(
                        id=idx,
                        vector=embedding.tolist(),
                        payload={
                            "text": chunk["text"],
                            **chunk["metadata"]
                        }
                    )
                )
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )

            logger.info(f"Inserted {len(points)} chunks into Qdrant")

        except Exception as e:
            logger.error("Error while inserting documents into Qdrant")
            raise RAGException(e, sys)
        
    def search(self, query_embedding, top_k=5):
        try:
            results = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_embedding.tolist(),
                limit=top_k,
                with_payload=True
            ).points

            return results

        except Exception as e:
            logger.error("Error while searching Qdrant")
            raise RAGException(e, sys)