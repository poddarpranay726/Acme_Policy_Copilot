import sys
import uuid
from ..logger import logger
from ..exception import RAGException
from ..conversation.conversation_manager import ConversationManager
from ..retrieval.query_rewriter import QueryRewriter
from ..retrieval.hybrid_retriever import HybridRetriever
from ..retrieval.reranker import Reranker
from ..generation.generator import ResponseGenerator

class RAGPipeline:

    def __init__(self):
        try:
            # Initialize all components
            self.conversation_manager = ConversationManager()

            self.query_rewriter = QueryRewriter()

            self.hybrid_retriever = HybridRetriever()

            self.reranker = Reranker()

            self.response_generator = ResponseGenerator()

            logger.info("RAG pipeline initialized successfully")

        except Exception as e:
            logger.exception("RAG pipeline initialization failed")
            raise RAGException(e, sys)

    def run(
        self,
        query: str,
        conversation_id: uuid.UUID,
    ):

        try:
            # 1. Retrieve previous conversation history
            chat_history = self.conversation_manager.get_history(
                conversation_id
            )

            # 2. Save the current user message
            self.conversation_manager.add_message(
                conversation_id,
                "user",
                query,
            )

            # 3. Rewrite query using conversation history
            if chat_history:
                search_query = self.query_rewriter.rewrite_with_history(
                    query,
                    chat_history,
                )
            else:
                search_query = self.query_rewriter.rewrite(query)

            # 4. Hybrid retrieval
            retrieved_documents = self.hybrid_retriever.retrieve(
                search_query,
                top_k=20,
                candidate_k=20,
            )

            # 5. Handle no retrieved documents
            if not retrieved_documents:

                answer = (
                    "I couldn't find relevant information "
                    "in the available company documents."
                )

                self.conversation_manager.add_message(
                    conversation_id,
                    "assistant",
                    answer,
                )

                return {
                    "query": query,
                    "rewritten_query": search_query,
                    "answer": answer,
                    "sources": [],
                }

            # 6. Rerank retrieved documents
            ranked_documents = self.reranker.rerank(
                search_query,
                retrieved_documents,
                top_k=5,
            )

            # 7. Generate answer
            answer = self.response_generator.generate_stream(
                query=query,
                documents=ranked_documents,
            )

            # 8. Save assistant response
            self.conversation_manager.add_message(
                conversation_id,
                "assistant",
                answer,
            )

            # 9. Prepare sources
            sources = [
                document["metadata"]
                for document in ranked_documents
            ]

            return {
                "query": query,
                "rewritten_query": search_query,
                "answer": answer,
                "sources": sources,
            }

        except Exception:
            logger.exception("Error while executing RAG pipeline")
            raise
    

    def run_stream(self, query: str, conversation_id):

        try:
            # 1. Retrieve previous conversation history
            chat_history = self.conversation_manager.get_history(
                conversation_id
            )

            # 2. Save current user question
            self.conversation_manager.add_message(
                conversation_id,
                "user",
                query,
            )

            # 3. Rewrite query
            if chat_history:
                search_query = self.query_rewriter.rewrite_with_history(
                    query,
                    chat_history,
                )
            else:
                search_query = self.query_rewriter.rewrite(query)

            # 4. Hybrid retrieval
            retrieved_documents = self.hybrid_retriever.retrieve(
                search_query,
                top_k=20,
                candidate_k=20,
            )

            # 5. Handle empty retrieval
            if not retrieved_documents:

                answer = (
                    "I couldn't find relevant information "
                    "in the available company documents."
                )

                self.conversation_manager.add_message(
                    conversation_id,
                    "assistant",
                    answer,
                )

                yield {
                    "type": "sources",
                    "data": [],
                }

                yield {
                    "type": "token",
                    "data": answer,
                }

                yield {
                    "type": "done",
                    "data": None,
                }

                return

            # 6. Rerank documents
            ranked_documents = self.reranker.rerank(
                search_query,
                retrieved_documents,
                top_k=5,
            )

            # 7. Prepare sources
            sources = [
                document["metadata"]
                for document in ranked_documents
            ]

            yield {
                "type": "sources",
                "data": sources,
            }

            # 8. Stream LLM response
            complete_answer = []

            for chunk in self.response_generator.generate_stream(
                query=query,
                documents=ranked_documents,
            ):

                complete_answer.append(chunk)

                yield {
                    "type": "token",
                    "data": chunk,
                }

            # 9. Combine all chunks into one answer
            final_answer = "".join(complete_answer)

            # 10. Save complete assistant response
            self.conversation_manager.add_message(
                conversation_id,
                "assistant",
                final_answer,
            )

            # 11. Notify completion
            yield {
                "type": "done",
                "data": None,
            }

            logger.info("Streaming RAG pipeline completed")

        except Exception:
            logger.exception("Streaming RAG pipeline failed")

            yield {
                "type": "error",
                "data": "An error occurred while generating the response.",
            }
