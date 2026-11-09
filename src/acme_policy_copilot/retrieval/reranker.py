from sentence_transformers import CrossEncoder
from ..exception import RAGException
from .query_rewriter import QueryRewriter
import sys
import json

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

class Reranker:
    def __init__(self):
        self.model = CrossEncoder(MODEL_NAME)
        self.query_rewriter = QueryRewriter()

    def rerank(self, query,documents, top_k=5):
        try :
            rewrited_query = self.query_rewriter.rewrite(query)
            # print(f"Candidates: {json.dumps(candidates, indent=4)}")
            pairs = [
                (rewrited_query, document["text"])
                for document in documents
            ]
            scores = self.model.predict(pairs)
            # print(f"Data Type of scores: {type(scores)}")
            # print(f"Scores: {scores}")
            reranked = []
            for document, score in zip(documents, scores):
                result = document.copy()
                result["rerank_score"] = float(score)
                reranked.append(result)

            reranked.sort(
                key=lambda x: x["rerank_score"],
                reverse=True
            )

            return reranked[:top_k]
        
        except Exception as e:
            raise RAGException(e, sys)
    
if __name__ == "__main__":
    reranker = Reranker()
    query = "What are the password requirements at Acme Corp?"
    results = reranker.rerank(
        query,
        top_k=5
    )

    for rank, result in enumerate(results, start=1):
        print("\n" + "=" * 80)
        print(f"Rank: {rank}")
        print(f"Rerank Score: {result['rerank_score']}")
        print(f"RRF Score: {result['rrf_score']}")
        print(f"Chunk: {result['metadata']['chunk_id']}")
        print(result["text"])
        print("-" * 80)
        