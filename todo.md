# TODO

## 진행 중

- [ ] Railway 배포 세팅

---

## 완료

- [x] `main.py` — FastAPI 엔드포인트 구현
- [x] `agent.py` — Claude Tool Use 루프 구현
- [x] `tools/search_hr_docs.py` — ChromaDB 검색 연동
- [x] `embeddings/ingest.py` — Q&A JSON 임베딩 파이프라인
- [x] `pyproject.toml` — 의존성 정리 (uv)
- [x] `.python-version` — Python 3.11 명시 (Railway 배포 대응)
- [x] 멀티턴 대화 지원 — history 백엔드 전달 구현
- [x] 웹 UI — `frontend/` (HTML/CSS/JS 분리)
- [x] 프론트엔드 백엔드 연동 — `callChatbot()` API 연결
- [x] CORS 설정 — CORSMiddleware 추가
- [x] FastAPI StaticFiles — 프론트엔드 통합 서빙 (`/` 마운트)
- [x] System prompt 범위 확장 — HR 한정 → 사내 문의 전반
- [x] ngrok 외부 공개 — 단일 터널로 프론트+백엔드 통합 서빙
- [x] 출처 칩 표시 — AgentResponse.snippets → 프론트엔드 칩 렌더링
- [x] Distance threshold 필터 — 임계값(1.0) 이하 문서만 출처로 표시
- [x] Debug 로깅 — RAG 호출 여부·검색 쿼리·distance 콘솔 출력
- [x] chroma_db git 추적 — .gitignore 제외 해제 후 push

---

## Backlog

- [ ] `submit_form` Tool 추가 — 신청서 제출 연동
- [ ] `send_teams_notification` Tool — Teams 알림
- [ ] pgvector 마이그레이션 — PostgreSQL 전환
- [ ] 인증 추가 — 사내 전용 접근 제어
- [ ] qa_data.json 데이터 확충 — 카테고리 추가
