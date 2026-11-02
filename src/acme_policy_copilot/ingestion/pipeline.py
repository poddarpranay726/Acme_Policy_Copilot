from acme_policy_copilot.ingestion.loader import load_pdfs
from acme_policy_copilot.ingestion.chunker import create_chunks
from acme_policy_copilot.embeddings import Embedder
from acme_policy_copilot.vectorstore.qdrant_store import QdrantStore
from acme_policy_copilot.logger import logger
from acme_policy_copilot.exception import RAGException

import sys

from acme_policy_copilot.vectorstore.qdrant_store import QdrantStore


def run_ingestion():
    try:
        logger.info("Starting ingestion pipeline")
        documents = load_pdfs()
        logger.info(f"Loaded {len(documents)} documents")

        chunks = create_chunks(documents)
        logger.info(f"Created {len(chunks)} chunks")

        embedder = Embedder()
        texts = [chunk["text"] for chunk in chunks]
        embeddings = embedder.embed_documents(texts)
        logger.info(f"Generated embeddings for {len(embeddings)} chunks")

        logger.info(f"Initializing Qdrant vector store and adding documents")
        vector_store = QdrantStore()
        vector_store.add_documents(chunks, embeddings)
        logger.info("Ingestion pipeline completed successfully")
        
        return chunks, embeddings

    except Exception as e:
        logger.error("Ingestion pipeline failed")
        raise RAGException(e, sys)


if __name__ == "__main__":
    chunks, embeddings = run_ingestion()

    print("\n===== INGESTION COMPLETE =====")
    print("Total chunks:", len(chunks))
    print("Total embeddings:", len(embeddings))
    print("Embedding dimension:", len(embeddings[0]))

    print("\n===== SAMPLE =====")
    print("Text:")
    print(chunks[0]["text"])

    print("\nMetadata:")
    print(chunks[0]["metadata"])