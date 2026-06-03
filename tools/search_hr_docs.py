import os
from pathlib import Path

import chromadb
import voyageai
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "hr_qa"
EMBED_MODEL = "voyage-4-lite"


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

    return [
        {
            "id": meta["id"],
            "category": meta["category"],
            "question": meta["question"],
            "answer": meta["answer"],
        }
        for meta in results["metadatas"][0]
    ]
