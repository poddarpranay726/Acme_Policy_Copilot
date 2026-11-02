from acme_policy_copilot.embeddings import Embedder
from acme_policy_copilot.vectorstore.qdrant_store import QdrantStore
from acme_policy_copilot.logger import logger
from acme_policy_copilot.exception import RAGException
import sys

class Retriever:

    def __init__(self):
        try:
            self.embedder = Embedder()
            self.vector_store = QdrantStore()

        except Exception as e:
            logger.error("Error while initializing retriever")
            raise RAGException(e, sys)

    def retrieve(self, query, top_k=5):
        try:
            logger.info(f"Retrieving documents for query: {query}")
            query_embedding = self.embedder.embed_query(query)

            results = self.vector_store.search(
                query_embedding,
                top_k=top_k
            )
            return results

        except Exception as e:
            logger.error("Error while retrieving documents")
            raise RAGException(e, sys)

if __name__ == "__main__":
    retriever = Retriever()
    query = "How can I claim travel expenses?"
    results = retriever.retrieve(
        query,
        top_k=5
    )

    print("\n===== SEARCH RESULTS =====")
    for i, result in enumerate(results, start=1):
        print(f"\nResult {i}")
        print("Score:", result.score)
        print("Payload:", result.payload)