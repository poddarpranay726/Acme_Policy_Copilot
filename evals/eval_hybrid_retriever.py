import json
from dotenv import load_dotenv
from .groq_judge import GroqJudge
from deepeval.models import OllamaModel, GeminiModel, OpenAIModel
from .openRouter_judge import OpenRouterJudge
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import ContextualRecallMetric, ContextualPrecisionMetric
from src.acme_policy_copilot.retrieval.hybrid_retriever import HybridRetriever
import os 

load_dotenv()

GOLDEN_PATH = "eval_datasets/retriever_dataset.json"
# JUDGE_MODEL = GroqJudge(
#     model="openai/gpt-oss-120b"
# )
JUDGE_MODEL = OpenRouterJudge(
    model="nvidia/nemotron-3-ultra-550b-a55b:free"
)
# JUDGE_MODEL = OllamaModel(
#     model="qwen3.5:4b",
#     base_url="http://localhost:11434"
# )
# JUDGE_MODEL = GeminiModel(
#     model="gemini-3.8-flash",
#     api_key=os.getenv("GOOGLE_API_KEY"),
#     temperature=0
# )
# JUDGE_MODEL = OpenAIModel(
#     model="mistralai/mistral-large-4-1t-a52b",
#     api_key=os.getenv("NVIDIA_API_KEY"),
#     base_url="https://integrate.api.nvidia.com/v1",
#     temperature=0
# )
THRESHOLD = 0.7

with open(GOLDEN_PATH) as f:
    goldens = json.load(f)

retriever = HybridRetriever()

test_cases = []

for g in goldens:
    retrieved_docs = retriever.retrieve(
        g["input"],
        top_k=5
    )
    retrieval_results = [doc["text"] for doc in retrieved_docs]

    test_cases.append(
        LLMTestCase(
            input=g["input"],
            actual_output="(generator not evaluated in this run)",
            expected_output=g["expected_output"],
            retrieval_context=retrieval_results 
        )
    )

metrics = [
    ContextualRecallMetric(threshold=THRESHOLD, model=JUDGE_MODEL, include_reason=True),
    ContextualPrecisionMetric(threshold=THRESHOLD, model=JUDGE_MODEL, include_reason=True)
]

evaluate(
    test_cases = test_cases,
    metrics = metrics,
    hyperparameters = {
        "retriever" : "base_k5",
        "embedding_model" : "BAAI/bge-small-en-v1.5",
        "chunk_size" : 800,
        "chunk_overlap" : 100,
        "top_k" : 5,
        "threshold" : THRESHOLD,
        "judge_model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "golden_set" : GOLDEN_PATH
    }
)