---
title: CLAUDE.md 문서 구조 재정비
date: 2026-06-03
status: approved
---

# CLAUDE.md 문서 구조 재정비 설계

## 배경

현재 `CLAUDE.md` 한 파일에 Claude 작업 지침, 외부 공개용 문서, 코드 예시, Q&A 데이터 구조가 모두 혼재되어 있다.
CLAUDE.md는 매 대화마다 context에 자동 로드되므로, 불필요한 내용이 토큰을 낭비하고 있다.

## 목표

- `CLAUDE.md`: Claude가 작업 시 꼭 알아야 할 설계 원칙 + 파일 포인터만 유지 (60줄 이하)
- `README.md`: 외부 오픈소스 공개용 완전한 문서
- `todo.md`: 현재 Sprint 태스크 + 미래 Backlog 관리

## 파일별 설계

### CLAUDE.md (~60줄)

포함:
- 프로젝트 목적 (2-3문장)
- 아키텍처 핵심 판단 및 이유 (Tool Use 선택 근거, ChromaDB → pgvector 마이그레이션 제약)
- 임베딩 방식 (question + answer 단일 청크)
- 주요 설계 원칙 3가지
- 핵심 파일 위치 포인터
- 주요 커맨드 (ingest, 서버 실행)
- 환경 변수 목록

제거:
- 기술 스택 테이블 → README.md
- 디렉토리 트리 → README.md
- Q&A 데이터 JSON 예시 → README.md (파일 위치 포인터로 대체)
- agent.py 코드 스니펫 / system prompt → README.md
- Tool Use 루프 상세 설명 → README.md

### README.md (~100줄)

대상 독자: 외부 개발자 (오픈소스 공개)

포함:
- 프로젝트 소개 및 개요
- 아키텍처 ASCII 다이어그램
- Tool Use 선택 이유
- 기술 스택 테이블
- 디렉토리 구조
- 시작하기 (uv sync 기반)
  - .env 설정
  - `uv sync`
  - `uv run python embeddings/ingest.py`
  - `uv run uvicorn main:app --reload`
- Q&A 데이터 구조 (JSON 예시 포함)
- 확장 가능한 Tool 구조 설명
- 설계 원칙

### todo.md

섹션 구조:
- **진행 중**: 현재 작업 중인 항목
- **Sprint**: 현재 사이클 완료 목표 태스크
- **Backlog**: 미래 기능 아이디어

초기 Sprint 항목:
- main.py FastAPI 엔드포인트 구현
- agent.py Tool Use 루프 구현
- tools/search_hr_docs.py ChromaDB 검색 연동
- embeddings/ingest.py Q&A JSON 임베딩 파이프라인
- pyproject.toml 의존성 정리

초기 Backlog 항목:
- submit_form Tool 추가
- Teams 알림 연동
- pgvector 마이그레이션
- 멀티턴 대화 지원
- 웹 UI

## 가상환경

`requirements.txt` 대신 `pyproject.toml` + `uv.lock` (uv 네이티브) 사용.
실행 커맨드는 `uv run` prefix 사용으로 venv 활성화 불필요.
