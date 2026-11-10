
import json

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

COLLECTION_NAME = "acme_policy_chunks"

client = QdrantClient(url="http://localhost:6333")

# Create collection if it doesn't exist
collections = client.get_collections().collections

if not any(c.name == COLLECTION_NAME for c in collections):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        ),
    )

# Load exported data
with open("qdrant_export.json", "r", encoding="utf-8") as file:
    records = json.load(file)

points = [
    PointStruct(
        id=record["id"],
        vector=record["vector"],
        payload=record["payload"],
    )
    for record in records
]

# Import in batches
for start in range(0, len(points), 100):
    batch = points[start:start + 100]

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=batch,
        wait=True,
    )

print(f"Imported {len(points)} points successfully.")

# Verify
info = client.get_collection(COLLECTION_NAME)
print("Total points in Docker Qdrant:", info.points_count)

client.close()
