# 사내 HR 챗봇 — RAG + Tool Use Agent

> 사내 규정 Q&A를 벡터 DB에 임베딩하고, Claude API Tool Use로 LLM이 필요할 때만 검색을 호출하는 HR 챗봇 POC

---

## 아키텍처

```
[사용자 질문]
     ↓
[Claude API — Tool Use 판단]
     ├── 검색 필요 → search_hr_docs(query) 호출
     │                    ↓
     │              [ChromaDB 유사도 검색]
     │                    ↓
     │              [검색 결과 반환 → Claude]
     │
     └── 검색 불필요 → 바로 답변 생성
             ↓
     [최종 답변 + 출처 반환]
```

### Tool Use를 선택한 이유

- 모든 질문에 무조건 검색 실행 → 불필요한 비용·지연 발생 가능
- Tool 정의만 추가하면 새 기능을 자연스럽게 확장 가능 (agent 루프 수정 불필요)
- LLM이 런타임에 판단 → LangGraph 같은 사전 분기 설계 불필요

---

## 기술 스택

| 역할 | 기술 | 비고 |
|------|------|------|
| LLM + Agent | Claude API (`claude-sonnet-4-6`) | Tool Use 내장 |
| 임베딩 | Voyage AI (`voyage-multilingual-2`) | 한국어 지원, Anthropic 공식 파트너 |
| 벡터 DB | ChromaDB | 로컬 파일 기반, 서버 불필요 |
| 백엔드 | FastAPI (Python) | async 지원 |
| 데이터 | JSON 파일 (`data/qa_data.json`) | Q&A 원본 |

---

## 디렉토리 구조

```
project/
├── main.py                  # FastAPI 엔트리포인트
├── agent.py                 # Claude Tool Use 루프
├── tools/
│   └── search_hr_docs.py    # ChromaDB 검색 Tool
├── embeddings/
│   └── ingest.py            # Q&A JSON → ChromaDB 임베딩
├── data/
│   └── qa_data.json         # Q&A 원본 데이터
├── chroma_db/               # ChromaDB 저장 디렉토리 (자동 생성)
├── pyproject.toml
└── .env                     # ANTHROPIC_API_KEY, VOYAGE_API_KEY
```

---

## 시작하기

### 1. 환경 변수 설정

`.env` 파일 생성:

```
ANTHROPIC_API_KEY=sk-ant-...
VOYAGE_API_KEY=pa-...
```

### 2. 의존성 설치

```bash
uv sync
```

### 3. Q&A 데이터 임베딩

```bash
uv run python embeddings/ingest.py
```

### 4. 서버 실행

```bash
uv run uvicorn main:app --reload
```

---

## Q&A 데이터 구조

파일: `data/qa_data.json`

```json
[
  {
    "id": "reg_001",
    "category": "근태",
    "question": "휴일근무신청서는 언제까지 신청 가능한가요?",
    "answer": "휴일근무신청서는 근무 전날까지 신청 가능합니다.",
    "keywords": ["휴일근무", "신청서", "마감"]
  },
  {
    "id": "contact_001",
    "category": "담당자",
    "question": "정보보안 담당자가 누구인가요?",
    "answer": "정보보안 관련 문의는 개발실 플랫폼개발팀 김용인 과장에게 문의하시면 됩니다.",
    "keywords": ["정보보안", "보안", "담당자"]
  }
]
```

임베딩 시 `question + " " + answer`를 합쳐 단일 청크로 저장. `category`, `id`는 ChromaDB metadata로 저장해 출처 표시에 활용.

---

## Tool 확장 구조

`agent.py`의 TOOLS 배열에 정의만 추가하면 agent 루프 수정 없이 기능 확장 가능:

```python
# 추후 확장 예시
{ "name": "submit_form", ... }
{ "name": "send_teams_notification", ... }
```

---

## 설계 원칙

1. **근거 없으면 답변 안 함** — 환각 방지, system prompt에 명시
2. **출처 표시** — 답변에 `category`, 문서 `id` 포함
3. **Tool 추가만으로 기능 확장** — agent 루프 수정 불필요
4. **ChromaDB → pgvector 마이그레이션 고려** — 추후 PostgreSQL 도입 시 검색 인터페이스 동일하게 유지
