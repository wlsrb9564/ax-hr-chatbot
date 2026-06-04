# 사내 HR 챗봇 — RAG + Tool Use Agent

## Project Overview

사내 HR 규정 Q&A를 ChromaDB에 임베딩하고, Claude Tool Use로 필요할 때만 검색을 호출하는 HR 챗봇. POC 단계.  
FastAPI 서버(`/chat`)를 통해 멀티턴 대화를 지원하며, 검색 근거가 없으면 답변하지 않는다.

---

## Commands

```bash
uv sync                                      # 의존성 설치
uv run python embeddings/ingest.py           # Q&A 데이터 재임베딩
uv run uvicorn main:app --reload             # 서버 실행 (http://localhost:8000)
uv run python tests/test_agent.py            # agent Tool Use 루프 테스트
uv run python tests/test_search_hr_docs.py  # 검색 품질 테스트
```

---

## Tech Stack

- Python 3.11+ (uv로 관리)
- FastAPI + Uvicorn — REST API 서버
- Anthropic SDK (`claude-sonnet-4-6`) — Tool Use 에이전트
- Voyage AI (`voyage-4-lite`) — 텍스트 임베딩
- ChromaDB (PersistentClient) — 로컬 벡터 DB
- python-dotenv — 환경 변수 관리

---

## Structure

```
ax-hr-chatbot/
├── main.py                   # FastAPI 엔트리포인트 (/chat, /health)
├── agent.py                  # Claude Tool Use 루프
├── tools/
│   └── search_hr_docs.py     # ChromaDB 검색 Tool (인터페이스 변경 금지)
├── embeddings/
│   └── ingest.py             # Q&A JSON → ChromaDB 임베딩
├── data/
│   └── qa_data.json          # Q&A 원본 데이터
├── chroma_db/                # ChromaDB 영속 저장소 (ingest 후 생성)
└── tests/
    ├── test_agent.py         # 멀티턴·출처·차단 시나리오 테스트
    └── test_search_hr_docs.py # 검색 정확도·top_k 테스트
```

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

## Code Style

- 포맷팅/린트/import 정렬은 Ruff가 처리 (수동 정렬 금지)
- 타입 힌트 필수 (함수 인자·반환값)
- docstring은 Google 스타일
- 네이밍: 함수·변수 snake_case, 클래스 PascalCase, 상수 UPPER_SNAKE_CASE
- f-string 사용 (% 포매팅, `.format()` 금지)

---

## Rules

- 계획·설계 논의 중에는 명시적 구현 요청 전까지 코드를 작성하지 않는다
- 요청 범위 밖의 신규 파일 생성·패키지 설치는 먼저 확인하고 진행한다
- 현재 대화에서 유저가 명시한 금지사항·완료 작업은 이후에도 유지한다
- 요청 외 리팩토링·스타일 정리·추가 기능은 하지 않는다
- 모든 Python 명령은 `uv run`으로 실행 (전역 python 직접 호출 금지)

---

## 환경 변수

`.env` 파일 필요: `ANTHROPIC_API_KEY`, `VOYAGE_API_KEY`
