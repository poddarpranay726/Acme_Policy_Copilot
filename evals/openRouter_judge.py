import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from deepeval.models import DeepEvalBaseLLM

load_dotenv()


class OpenRouterJudge(DeepEvalBaseLLM):

    def __init__(
        self,
        model="nvidia/nemotron-3-ultra-550b-a55b:free"
    ):
        self.model = model

        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )

    def load_model(self):
        return self.client

    def get_model_name(self):
        return self.model

    def generate(
        self,
        prompt: str,
        schema: BaseModel | None = None
    ):
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

        return response.choices[0].message.content

    async def a_generate(
        self,
        prompt: str,
        schema: BaseModel | None = None
    ):
        return self.generate(prompt, schema)