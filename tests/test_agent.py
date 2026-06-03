"""
agent Tool Use 루프 테스트

실행: uv run python tests/test_agent.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import run_agent


def test_with_source(label: str, question: str):
    print(f"=== {label} ===")
    print(f"Q: {question}")
    answer = run_agent(question)
    print(f"A: {answer}")
    # 출처 포함 여부 확인
    assert "[출처:" in answer, "출처가 답변에 포함되지 않았습니다"
    print("  ✓ 출처 확인\n")


def test_no_source(label: str, question: str):
    """HR 규정 외 질문 — 인사팀 문의 안내 확인"""
    print(f"=== {label} ===")
    print(f"Q: {question}")
    answer = run_agent(question)
    print(f"A: {answer}\n")


def test_off_topic(label: str, question: str):
    """HR 무관 질문 — tool 호출 없이 즉시 차단 안내 확인"""
    print(f"=== {label} ===")
    print(f"Q: {question}")
    answer = run_agent(question)
    print(f"A: {answer}\n")
    assert "HR" in answer or "hr" in answer.lower(), "HR 외 질문 차단 안내가 없습니다"


def test_multi_turn():
    """멀티턴 대화 — 이전 대화 이력 반영 확인"""
    print("=== 5. 멀티턴 대화 ===")
    # 1턴: 첫 질문
    answer1 = run_agent("정보보안 담당자가 누구인가요?")
    print(f"Q1: 정보보안 담당자가 누구인가요?")
    print(f"A1: {answer1}\n")

    # 2턴: 이전 대화 이력 포함해서 후속 질문
    history = [
        {"role": "user", "content": "정보보안 담당자가 누구인가요?"},
        {"role": "assistant", "content": answer1},
    ]
    answer2 = run_agent("그 분 소속 팀이 어디예요?", history=history)
    print(f"Q2: 그 분 소속 팀이 어디예요?")
    print(f"A2: {answer2}\n")
    assert "플랫폼" in answer2, "이전 대화 이력이 반영되지 않았습니다"


if __name__ == "__main__":
    test_with_source("1. 정확한 질문", "휴일근무신청서는 언제까지 신청 가능한가요?")
    test_with_source("2. 유사 표현 질문", "보안 담당자 누구예요?")
    test_no_source("3. 근거 없는 질문", "연차 몇 일이나 쓸 수 있나요?")
    test_off_topic("4. HR 무관 질문 차단", "오늘 날씨 어때?")
    test_multi_turn()

    print("모든 테스트 완료")
