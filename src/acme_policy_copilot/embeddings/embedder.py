from sentence_transformers import SentenceTransformer
from acme_policy_copilot.logger import logger
from acme_policy_copilot.exception import RAGException
import sys

MODEL_NAME = "BAAI/bge-small-en-v1.5"

class Embedder:

    def __init__(self):
        try:
            logger.info(f"Loading embedding model: {MODEL_NAME}")
            self.model = SentenceTransformer(MODEL_NAME)
            logger.info("Embedding model loaded successfully")

        except Exception as e:
            logger.error("Error while loading embedding model")
            raise RAGException(e, sys)

    def embed_documents(self, texts):
        try:
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=True
            )
            return embeddings

        except Exception as e:
            logger.error("Error while generating document embeddings")
            raise RAGException(e, sys)

    def embed_query(self, query):
        try:
            embedding = self.model.encode(
                query,
                normalize_embeddings=True
            )

            return embedding
        except Exception as e:
            logger.error("Error while generating query embedding")
            raise RAGException(e, sys)

if __name__ == "__main__":

    embedder = Embedder()

    texts = [
        "Employees can claim reimbursement for business travel.",
        "Employees must submit travel expenses within 30 days."
    ]

    embeddings = embedder.embed_documents(texts)

    print("Number of embeddings:", len(embeddings))
    print("Embedding dimension:", len(embeddings[0]))

    query = "How can employees get travel expenses reimbursed?"

    query_embedding = embedder.embed_query(query)

    print("Query embedding dimension:", len(query_embedding))