from src.acme_policy_copilot.retrieval.hybrid_retriever import HybridRetriever
from src.acme_policy_copilot.retrieval.reranker import Reranker


hybrid_retriever = HybridRetriever()
reranker = Reranker()


query = "What are the password requirements at Acme Corp?"


# Step 1: Get candidate documents from Hybrid Retrieval
candidates = hybrid_retriever.retrieve(
    query,
    top_k=20,
    candidate_k=20
)


print(f"Hybrid candidates: {len(candidates)}")


# Step 2: Rerank those candidates
results = reranker.rerank(
    query,
    candidates,
    top_k=5
)


# Step 3: Display final results
for rank, result in enumerate(results, start=1):

    print("\n" + "=" * 80)
    print(f"Rank: {rank}")
    print(f"Rerank Score: {result['rerank_score']}")
    print(f"RRF Score: {result['rrf_score']}")
    print(f"Source: {result['metadata']['source']}")
    print(f"Page: {result['metadata']['page']}")
    print(f"Chunk: {result['metadata']['chunk_id']}")
    print("-" * 80)
    print(result["text"])