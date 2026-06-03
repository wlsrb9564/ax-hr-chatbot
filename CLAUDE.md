# 사내 HR 챗봇 — RAG + Tool Use Agent

## 프로젝트 목적

사내 규정 Q&A를 ChromaDB에 임베딩하고, Claude Tool Use로 필요할 때만 검색을 호출하는 HR 챗봇. POC 단계.

---

## 아키텍처 핵심 판단

- **Tool Use 선택 이유**: 모든 질문에 무조건 검색 X → LLM이 런타임에 판단. Tool 정의만 추가하면 기능 확장 가능
- **임베딩 방식**: `question + " " + answer` 합쳐서 단일 청크로 저장. `category`, `id`는 metadata로 보존
- **ChromaDB → pgvector 마이그레이션 고려**: 검색 인터페이스(`tools/search_hr_docs.py`) 변경 금지

---

## 주요 설계 원칙

1. 근거 없으면 답변 안 함 — 환각 방지
2. 답변에 출처(`category`, 문서 `id`) 표시
3. Tool 정의 추가만으로 기능 확장 (agent 루프 수정 불필요)

---

## 핵심 파일 위치

| 파일 | 역할 |
|------|------|
| `main.py` | FastAPI 엔트리포인트 |
| `agent.py` | Claude Tool Use 루프 |
| `tools/search_hr_docs.py` | ChromaDB 검색 Tool |
| `embeddings/ingest.py` | Q&A JSON → ChromaDB 임베딩 |
| `data/qa_data.json` | Q&A 원본 데이터 |

---

## 주요 커맨드

```bash
uv run python embeddings/ingest.py   # Q&A 데이터 재임베딩
uv run uvicorn main:app --reload     # 서버 실행
```

## 환경 변수

`.env` 파일 필요: `ANTHROPIC_API_KEY`, `VOYAGE_API_KEY`
