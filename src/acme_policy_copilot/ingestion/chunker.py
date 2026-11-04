from langchain_text_splitters import RecursiveCharacterTextSplitter
from acme_policy_copilot.logger import logger
from acme_policy_copilot.exception import RAGException
from acme_policy_copilot.ingestion.loader import load_pdfs
import sys

def create_chunks(documents):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
        )
        chunks = []
        for document in documents:
            split_texts = text_splitter.split_text(document["text"])

            for local_chunk_id, text in enumerate(split_texts):
                source = document["metadata"]["source"]
                page = document["metadata"]["page"]

                chunk_id = f"{source}_{page}_{local_chunk_id}"

                chunks.append({
                    "text": text,
                    "metadata": {
                        **document["metadata"],
                        "chunk_id": chunk_id
                    }
                })

        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")

        return chunks

    except Exception as e:
        logger.error("Error while creating chunks")
        raise RAGException(e, sys)

if __name__ == "__main__":

    documents = load_pdfs()
    chunks = create_chunks(documents)
    chunk_ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]

    print(chunk_ids)
    print(f"Total chunks: {len(chunks)}")
    print("\nFirst chunk:")
    print(chunks[0])