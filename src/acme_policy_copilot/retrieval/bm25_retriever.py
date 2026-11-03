import re
from rank_bm25 import BM25Okapi
from acme_policy_copilot.ingestion.loader import load_pdfs
from acme_policy_copilot.ingestion.chunker import create_chunks

class BM25Retriever:

    def __init__(self):
        documents = load_pdfs()
        self.chunks = create_chunks(documents)

        tokenized_corpus = [
            self._tokenize(chunk["text"])
            for chunk in self.chunks
        ]

        self.bm25 = BM25Okapi(tokenized_corpus)

    def _tokenize(self, text):
        return re.findall(r"\b\w+\b", text.lower())

    def retrieve(self, query, top_k=5):

        query_tokens = self._tokenize(query)
        print("*"*50)
        print(f"Query tokens: {query_tokens}")
        print("*"*50)
        scores = self.bm25.get_scores(query_tokens)
        print(len(scores))
        print("*"*50)
        print(f"Scores: {scores}")
        print("*"*50)
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]
        print("*"*50)
        print(f"Top {top_k} indices: {top_indices}")
        print("*"*50)
        results = []

        for index in top_indices:
            chunk = self.chunks[index]
            results.append({
                "score": float(scores[index]),
                "text": chunk["text"],
                "metadata": chunk["metadata"]
            })
        return results

if __name__ == "__main__":
    retriever = BM25Retriever()
    query = "What are the password requirements at Acme Corp?"
    results = retriever.retrieve(
        query,
        top_k=5
    )
    print(results[0])
    for i, result in enumerate(results, start=1):
        print("\n" + "=" * 80)
        print(f"Rank: {i}")
        print(f"Score: {result['score']}")
        print(f"Source: {result['metadata']['source']}")
        print(f"Page: {result['metadata']['page']}")
        print(f"Chunk: {result['metadata']['chunk_id']}")
        print("-" * 80)