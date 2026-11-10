
import json
from qdrant_client import QdrantClient

COLLECTION_NAME = "acme_policy_chunks"

client = QdrantClient(path="qdrant_data")

points = []
offset = None

while True:
    records, offset = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,
        offset=offset,
        with_payload=True,
        with_vectors=True,
    )

    points.extend(records)

    if offset is None:
        break

export_data = []

for point in points:
    export_data.append({
        "id": str(point.id),
        "vector": point.vector,
        "payload": point.payload,
    })

with open("qdrant_export.json", "w", encoding="utf-8") as file:
    json.dump(export_data, file)

print(f"Exported {len(export_data)} points successfully.")

client.close()
