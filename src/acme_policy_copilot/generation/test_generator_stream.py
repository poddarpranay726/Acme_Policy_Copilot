from acme_policy_copilot.generation.generator import (
    ResponseGenerator,
)

generator = ResponseGenerator()

query = "What is the leave policy?"

documents = [
    {
        "text": "Employees receive 20 annual leave days.",
        "metadata": {
            "source": "leave_policy.pdf",
            "page": 5,
        },
    }
]

for chunk in generator.generate_response(query, documents):
    print(chunk, end="", flush=True)

print()