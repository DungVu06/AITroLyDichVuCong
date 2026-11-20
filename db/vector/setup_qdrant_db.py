import json
import argparse
import os
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# This file lives in db/vector; data remains at the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

def load_dotenv(path: Path = PROJECT_ROOT / ".env") -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_dotenv()

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
if not qdrant_url or not qdrant_api_key:
    raise RuntimeError(
        "Thiếu QDRANT_URL hoặc QDRANT_API_KEY. "
        "Hãy cấu hình hai biến môi trường trước khi chạy."
    )

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=60.0)

model = SentenceTransformer('keepitreal/vietnamese-sbert')
vector_size = model.get_embedding_dimension()

def ensure_collection(collection_name: str) -> None:
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )


def reset_collection(collection_name: str) -> None:
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name=collection_name)
        print(f"Đã xóa collection cũ: {collection_name}")


def embed_and_upsert(jsonl_file: str, collection_name: str, batch_size: int = 50) -> None:
    input_file = Path(jsonl_file)
    if not input_file.exists():
        print(f"Bỏ qua {collection_name}: không tìm thấy {jsonl_file}")
        return

    ensure_collection(collection_name)

    print(f"\n--- Đang xử lý {jsonl_file} -> Collection '{collection_name}' ---")
    batch_points = []
    total_upserted = 0

    with input_file.open("r", encoding="utf-8") as file:
        for point_id, line in enumerate(file):
            chunk = json.loads(line)
            text = chunk["page_content"]
            metadata = chunk.get("metadata", {})

            vector = model.encode(text).tolist()
            batch_points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={"text": text, **metadata},
                )
            )

            if len(batch_points) >= batch_size:
                client.upsert(collection_name=collection_name, points=batch_points)
                total_upserted += len(batch_points)
                print(f"[{collection_name}] Đã đẩy {total_upserted} chunks...")
                batch_points = []

    if batch_points:
        client.upsert(collection_name=collection_name, points=batch_points)
        total_upserted += len(batch_points)
        print(f"[{collection_name}] Đã đẩy {total_upserted} chunks...")

    print(f"==> Hoàn tất: Đã đưa thành công {total_upserted} chunks vào collection '{collection_name}'!")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Embedding và import procedure/law chunks vào Qdrant."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Xóa các collection procedures và laws hiện tại trước khi import lại",
    )
    args = parser.parse_args()

    collections = [
        (PROJECT_ROOT / "data" / "chunks" / "procedure_chunks.jsonl", "procedures"),
        (PROJECT_ROOT / "data" / "chunks" / "law_chunks.jsonl", "laws"),
    ]

    if args.reset:
        for _, collection_name in collections:
            reset_collection(collection_name)

    for jsonl_file, collection_name in collections:
        embed_and_upsert(jsonl_file, collection_name)


if __name__ == "__main__":
    main()
