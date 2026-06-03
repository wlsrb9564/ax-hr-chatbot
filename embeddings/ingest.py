import json
import os
from pathlib import Path

import chromadb
import voyageai
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = Path(__file__).parent.parent / "data" / "qa_data.json"
CHROMA_PATH = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "hr_qa"
EMBED_MODEL = "voyage-4-lite"


def load_qa_data() -> list[dict]:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def build_embed_texts(items: list[dict]) -> list[str]:
    # question + answer 합산 텍스트로 임베딩 → 두 필드 모두 검색에 반영
    return [f"{item['question']} {item['answer']}" for item in items]


def ingest():
    print("Q&A 데이터 로드 중...")
    items = load_qa_data()
    texts = build_embed_texts(items)
    print(f"  총 {len(items)}개 항목")

    print("Voyage AI 임베딩 생성 중...")
    vc = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])
    # input_type="document": 저장용 문서 임베딩 (검색 쿼리는 "query" 사용)
    result = vc.embed(texts, model=EMBED_MODEL, input_type="document")
    embeddings = result.embeddings
    print(f"  임베딩 완료 ({len(embeddings)}개)")

    print("ChromaDB에 저장 중...")
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    # 재실행 시 중복 방지 — 기존 컬렉션 삭제 후 재생성
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(COLLECTION_NAME)
    collection.add(
        ids=[item["id"] for item in items],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {
                "id": item["id"],
                "category": item["category"],
                "question": item["question"],
                "answer": item["answer"],
                # ChromaDB metadata는 str만 허용 → keywords 리스트를 문자열로 변환
                "keywords": ", ".join(item["keywords"]),
            }
            for item in items
        ],
    )
    print(f"  저장 완료 → chroma_db/ ({len(items)}개 문서)")


if __name__ == "__main__":
    ingest()
