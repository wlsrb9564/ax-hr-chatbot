import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import run_agent


def test_exact_question_has_source():
    answer = run_agent("휴일근무신청서는 언제까지 신청 가능한가요?")
    assert "[출처:" in answer, "출처가 답변에 포함되지 않았습니다"


def test_paraphrase_question_has_source():
    answer = run_agent("보안 담당자 누구예요?")
    assert "[출처:" in answer, "출처가 답변에 포함되지 않았습니다"


def test_no_evidence_question():
    answer = run_agent("연차 몇 일이나 쓸 수 있나요?")
    assert answer  # 빈 응답이 아닌지만 확인


def test_off_topic_blocked():
    answer = run_agent("오늘 날씨 어때?")
    assert "HR" in answer or "hr" in answer.lower(), "HR 외 질문 차단 안내가 없습니다"


def test_multi_turn():
    answer1 = run_agent("정보보안 담당자가 누구인가요?")
    history = [
        {"role": "user", "content": "정보보안 담당자가 누구인가요?"},
        {"role": "assistant", "content": answer1},
    ]
    answer2 = run_agent("그 분 소속 팀이 어디예요?", history=history)
    assert "플랫폼" in answer2, "이전 대화 이력이 반영되지 않았습니다"
