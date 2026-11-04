from acme_policy_copilot.retrieval.retriever import Retriever
from acme_policy_copilot.retrieval.bm25_retriever import BM25Retriever
import json 

class HybridRetriever:

    def __init__(self):
        self.dense_retriever = Retriever()
        self.bm25_retriever = BM25Retriever()

    def retrieve(self, query, top_k=5, candidate_k=20):
        dense_results = self.dense_retriever.retrieve(
            query,
            top_k=candidate_k
        )
        # print(f"Dense Results: {json.dumps(dense_results[0], indent=4)}")
        bm25_results = self.bm25_retriever.retrieve(
            query,
            top_k=candidate_k
        )
        # print(f"BM25 Results: {json.dumps(bm25_results[0], indent=4)}")
        rrf_scores = {}
        documents = {}
        k = 60
        for rank, result in enumerate(dense_results, start=1):
            chunk_id = result["metadata"]["chunk_id"]
            print()
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

        # print(f"Final Results: {json.dumps(results, indent=4)}")
        return results

if __name__ == "__main__":

    retriever = HybridRetriever()
    query = "What are the password requirements at Acme Corp?"
    results = retriever.retrieve(
        query,
        top_k=5,
        candidate_k=20
    )
    for rank, result in enumerate(results, start=1):
        print("\n" + "=" * 80)
        print(f"Rank: {rank}")
        print(f"RRF Score: {result['rrf_score']}")
        print(f"Source: {result['metadata']['source']}")
        print(f"Page: {result['metadata']['page']}")
        print(f"Chunk: {result['metadata']['chunk_id']}")
        print("-" * 80)
        print(result["text"]) 