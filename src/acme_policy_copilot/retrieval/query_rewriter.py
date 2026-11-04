import os
from dotenv import load_dotenv
from openai import OpenAI
from ..logger import logger
from ..exception import RAGException

load_dotenv()

class QueryRewriter:
    def __init__(self):
        try:
            self.client = OpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1"
            )
            self.model = os.getenv("QUERY_REWRITE_MODEL")
            if not self.model:
                raise ValueError("QUERY_REWRITE_MODEL is not configured")

            logger.info("Query rewriter initialized successfully")

        except Exception as e:
            raise RAGException(e, __import__("sys"))

    def rewrite(self, query):

        try:
            prompt = f"""
            You are a query rewriting assistant for an enterprise
            document retrieval system.

            Rewrite the user's question into a clear and specific
            search query suitable for retrieving relevant company
            policy documents.

            Rules:
            1. Preserve the original intent.
            2. Do not invent facts or missing information.
            3. Expand abbreviations only when their meaning is clear.
            4. Do not answer the user's question.
            5. Return only the rewritten search query.

            User question:
            {query}
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )

            rewritten_query = response.choices[0].message.content.strip()

            if not rewritten_query:
                logger.warning("Empty rewritten query; using original query")
                return query

            logger.info(f"Original query: {query}")
            logger.info(f"Rewritten query: {rewritten_query}")

            return rewritten_query

        except Exception as e:
            logger.exception("Query rewriting failed")
            raise RAGException(e, __import__("sys"))