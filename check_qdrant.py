from qdrant_client import QdrantClient

client = QdrantClient(path="qdrant_data")

collection = client.get_collection("acme_policy_chunks")

print("Collection:", "acme_policy_chunks")
print("Total vectors:", collection.points_count)
print("Vector configuration:", collection.config.params.vectors)

client.close()