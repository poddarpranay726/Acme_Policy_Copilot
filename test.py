# from openai import OpenAI
# from dotenv import load_dotenv
# import os

# load_dotenv()

# client = OpenAI(
#     api_key=os.getenv("OPENROUTER_API_KEY"),
#     base_url="https://openrouter.ai/api/v1"
# )

# response = client.chat.completions.create(
#     model="nvidia/nemotron-3-ultra-550b-a55b:free",
#     messages=[
#         {
#             "role": "user",
#             "content": "Explain what RAG is in 2 sentences."
#         }
#     ],
#     temperature=0
# )

# print(response.choices[0].message.content)
# from deepeval.models import OllamaModel

# judge = OllamaModel(
#     model="qwen3.5:4b",
#     base_url="http://localhost:11434"
# )

# print(judge)


# from openai import OpenAI
# import os
# from dotenv import load_dotenv

# load_dotenv()

# client = OpenAI(
#     api_key=os.getenv("NVIDIA_API_KEY"),
#     base_url="https://integrate.api.nvidia.com/v1"
# )

# response = client.chat.completions.create(
#     model="mistralai/mistral-large-4-1t-a52b",
#     messages=[
#         {"role": "user", "content": "Say hello"}
#     ],
#     temperature=0
# )

# print(response.choices[0].message.content)


