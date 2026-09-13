import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

client = QdrantClient(
    url="https://e455e45e-f953-4bad-b8e5-9cbc8230cb85.australia-southeast1-0.gcp.cloud.qdrant.io", # URL bạn lấy trên web
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NDRjYTYxNTEtMWIwNi00OTYyLWI5NDUtNWI3ZmE1OWM3NmM3In0.JEqEijIGgIkSAN6LOpvRwFYqpbbRFL153mWmtcaqkhs"                                         # API Key bạn lấy trên web
)

print("Đang tải mô hình Embedding...")
model = SentenceTransformer('keepitreal/vietnamese-sbert')
vector_size = model.get_embedding_dimension()

# 3. Tạo Collection (Bảng dữ liệu) trong Qdrant
collection_name = "procedures"
if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

points = []
jsonl_file = "data/procedure_chunks.jsonl"

print("Đang đọc file và nhúng (embedding) văn bản...")
with open(jsonl_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        chunk = json.loads(line)
        text = chunk["page_content"]
        metadata = chunk["metadata"]
        
        vector = model.encode(text).tolist()

        points.append(
            PointStruct(
                id=i, 
                vector=vector, 
                payload={   
                    "text": text,
                    **metadata
                } 
            )
        )

client.upsert(
    collection_name=collection_name,
    points=points
)

print(f"Đã đưa thành công {len(points)} chunks vào Qdrant!")