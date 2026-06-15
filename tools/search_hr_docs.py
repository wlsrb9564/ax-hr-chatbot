import logging
import os
from pathlib import Path

import chromadb
import voyageai
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

CHROMA_PATH = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "hr_qa"
EMBED_MODEL = "voyage-4-lite"
DISTANCE_THRESHOLD = 1.0  # 이 값 이하인 문서만 출처로 표시


def search_hr_docs(query: str, top_k: int = 3) -> list[dict]:
    # 쿼리는 "query" 타입으로 임베딩 — 문서 검색 의도에 최적화
    vc = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])
    query_embedding = vc.embed([query], model=EMBED_MODEL, input_type="query").embeddings[0]

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_collection(COLLECTION_NAME)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    items = []
    for meta, distance in zip(results["metadatas"][0], results["distances"][0]):
        log.info("  [검색] %s | distance=%.4f | 임계값 이하=%s",
                 meta["id"], distance, distance <= DISTANCE_THRESHOLD)
        items.append({
            "id": meta["id"],
            "category": meta["category"],
            "question": meta["question"],
            "answer": meta["answer"],
            "distance": distance,
        })

    return items
