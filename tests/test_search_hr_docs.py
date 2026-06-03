"""
search_hr_docs 검색 품질 테스트

실행: uv run python tests/test_search_hr_docs.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.search_hr_docs import search_hr_docs


def print_results(query: str, results: list[dict]):
    print(f"검색어: {query}")
    for i, doc in enumerate(results, 1):
        print(f"  {i}. [{doc['category']}] {doc['id']}")
        print(f"     Q: {doc['question']}")
        print(f"     A: {doc['answer']}")
    print()


def test_exact_match():
    """데이터에 있는 질문과 동일한 표현으로 검색"""
    print("=== 1. 정확한 질문 검색 ===")
    results = search_hr_docs("정보보안 담당자가 누구인가요?")
    print_results("정보보안 담당자가 누구인가요?", results)
    assert results[0]["id"] == "contact_001"


def test_paraphrase():
    """다른 표현으로 같은 의도를 검색"""
    print("=== 2. 유사 표현 검색 ===")
    results = search_hr_docs("보안 관련해서 누구한테 물어봐야 해요?")
    print_results("보안 관련해서 누구한테 물어봐야 해요?", results)
    assert results[0]["category"] == "담당자"


def test_category_attendance():
    """근태 카테고리 검색"""
    print("=== 3. 근태 카테고리 검색 ===")
    results = search_hr_docs("휴일에 일하면 신청서 언제까지 내야 해요?")
    print_results("휴일에 일하면 신청서 언제까지 내야 해요?", results)
    assert results[0]["category"] == "근태"


def test_contact_recruit():
    """채용 담당자 검색"""
    print("=== 4. 채용 담당자 검색 ===")
    results = search_hr_docs("채용 관련 문의는 누구에게 하나요?")
    print_results("채용 관련 문의는 누구에게 하나요?", results)
    assert results[0]["category"] == "담당자"


def test_top_k():
    """top_k 파라미터 동작 확인"""
    print("=== 5. top_k=1 결과 개수 확인 ===")
    results = search_hr_docs("담당자 문의", top_k=1)
    print_results("담당자 문의 (top_k=1)", results)
    assert len(results) == 1


if __name__ == "__main__":
    # Voyage AI 무료 플랜 Rate Limit: 3 RPM → 테스트 사이 20초 대기
    tests = [
        test_exact_match,
        test_paraphrase,
        test_category_attendance,
        test_contact_recruit,
        test_top_k,
    ]
    for i, test in enumerate(tests):
        test()
        if i < len(tests) - 1:
            print("  (Rate Limit 대기 중... 20초)\n")
            time.sleep(1)

    print("모든 테스트 통과")
