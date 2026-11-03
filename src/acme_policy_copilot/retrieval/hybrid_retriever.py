from acme_policy_copilot.retrieval.retriever import Retriever
from acme_policy_copilot.retrieval.bm25_retriever import BM25Retriever

class HybridRetriever:
    def __init__(self):
        self.dense_retriever = Retriever()
        self.bm25_retriever = BM25Retriever()

    def retrieve(self, query, top_k=5, candidate_k=20):
        dense_results = self.dense_retriever.retrieve(
            query,
            top_k=candidate_k
        )
        bm25_results = self.bm25_retriever.retrieve(
            query,
            top_k=candidate_k
        )
        rrf_scores = {}
        documents = {}
        k = 60
        for rank, result in enumerate(dense_results, start=1):
            chunk_id = result["metadata"]["chunk_id"]
            rrf_scores[chunk_id] = (
                rrf_scores.get(chunk_id, 0)
                + 1 / (k + rank)
            )
            documents[chunk_id] = result

        for rank, result in enumerate(bm25_results, start=1):
            chunk_id = result["metadata"]["chunk_id"]
            rrf_scores[chunk_id] = (
                rrf_scores.get(chunk_id, 0)
                + 1 / (k + rank)
            )
            documents[chunk_id] = result

        ranked_chunks = sorted(
            rrf_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        results = []

        for chunk_id, score in ranked_chunks[:top_k]:
            result = documents[chunk_id].copy()
            result["rrf_score"] = score
            results.append(result)

        return results