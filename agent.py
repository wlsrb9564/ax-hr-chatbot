import json
import logging
from typing import TypedDict

from anthropic import Anthropic
from dotenv import load_dotenv

from tools.search_hr_docs import DISTANCE_THRESHOLD, search_hr_docs

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

client = Anthropic()


class AgentResponse(TypedDict):
    answer: str
    snippets: list[dict]  # search_hr_docs 원본 결과; UI가 직접 렌더링


TOOLS = [
    {
        "name": "search_hr_docs",
        "description": (
            "사내 규정, 근태, 담당자 연락처, 회사 정보 등을 검색합니다. "
            "회사 내부 관련 질문이 들어오면 반드시 이 tool을 사용하세요."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "검색할 키워드 또는 질문"}
            },
            "required": ["query"],
        },
    }
]

# 출처 표시는 시스템 프롬프트가 아닌 코드(AgentResponse.snippets)가 담당하므로
# 프롬프트에 인용 지시를 넣지 않는다 — LLM이 id/category를 hallucinate하는 것을 방지
SYSTEM_PROMPT = """당신은 시원스쿨 회사의 사내 문의 안내 챗봇입니다. 사내 규정, 근태, 담당자 연락처, 회사 정보 등 회사 내부 관련 질문에 답변합니다.

규칙:
- 표, 이모지로 답변 생성하지말고, 간결한 문장으로 답변하세요.
- 회사 내부와 무관한 질문(날씨, 코딩, 일반 상식 등)은 search_hr_docs를 호출하지 말고 즉시 "저는 사내 문의 안내만 가능합니다. 회사 관련 질문을 입력해 주세요."라고 안내하세요.
- 회사 내부 관련 질문은 반드시 search_hr_docs tool을 사용해 근거를 찾으세요.
- tool 검색 결과에 근거가 있을 때만 답변하세요.
- 근거가 없으면 "해당 내용은 담당 부서에 직접 문의해 주세요."라고 안내하세요."""


def stream_agent(user_message: str, history: list[dict] | None = None):
    """tool_use 판단은 messages.create()로 처리하고, 최종 답변만 토큰 단위로 yield한다."""
    log.info("▶ [stream] 질문: %s", user_message)
    messages = (history or []) + [{"role": "user", "content": user_message}]
    all_snippets: list[dict] = []

    while True:
        # tool_use 판단 단계 — 화면에 보여줄 텍스트 없으므로 스트리밍 불필요
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        log.info("stop_reason: %s", response.stop_reason)

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    log.info("🔍 RAG 검색 쿼리: %s", block.input["query"])
                    results = search_hr_docs(block.input["query"])
                    log.info("검색 결과 %d건: %s", len(results), [r["id"] for r in results])
                    all_snippets.extend(r for r in results if r["distance"] <= DISTANCE_THRESHOLD)

                    claude_content = [
                        {"question": r["question"], "answer": r["answer"]}
                        for r in results
                    ]
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(claude_content, ensure_ascii=False),
                        }
                    )

            messages.append({"role": "user", "content": tool_results})

        else:
            # 최종 답변 단계 — 토큰 단위로 스트리밍
            log.info("✅ [stream] 최종 답변 스트리밍 시작 (RAG 사용: %s)", bool(all_snippets))
            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield {"type": "token", "text": text}

            yield {"type": "done", "snippets": all_snippets}
            return
