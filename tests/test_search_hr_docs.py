import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.search_hr_docs import search_hr_docs


def test_exact_match():
    results = search_hr_docs("정보보안 담당자가 누구인가요?")
    assert results[0]["id"] == "contact_001"


def test_paraphrase():
    results = search_hr_docs("보안 관련해서 누구한테 물어봐야 해요?")
    assert results[0]["category"] == "담당자"


def test_category_attendance():
    results = search_hr_docs("휴일에 일하면 신청서 언제까지 내야 해요?")
    assert results[0]["category"] == "근태"


def test_contact_recruit():
    results = search_hr_docs("채용 관련 문의는 누구에게 하나요?")
    assert results[0]["category"] == "담당자"


def test_top_k():
    results = search_hr_docs("담당자 문의", top_k=1)
    assert len(results) == 1
