import os
import instructor

from groq import Groq
from pydantic import BaseModel
from deepeval.models import DeepEvalBaseLLM


class GroqJudge(DeepEvalBaseLLM):

    def __init__(self, model="openai/gpt-oss-120b"):
        self.model = model
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
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
        client = instructor.from_groq(
            self.load_model(),
            mode=instructor.Mode.JSON
        )

        if schema:
            return client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_model=schema,
            )

        response = self.load_model().chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
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