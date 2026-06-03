import json

from anthropic import Anthropic
from dotenv import load_dotenv

from tools.search_hr_docs import search_hr_docs

load_dotenv()

client = Anthropic()

TOOLS = [
    {
        "name": "search_hr_docs",
        "description": (
            "사내 HR 규정, 근태, 휴가, 담당자 안내 등을 검색합니다. "
            "회사 규정이나 담당자에 대한 질문이 들어오면 반드시 이 tool을 사용하세요."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색할 키워드 또는 질문"
                }
            },
            "required": ["query"]
        }
    }
]

SYSTEM_PROMPT = """당신은 사내 HR 규정 안내 챗봇입니다. HR 규정, 근태, 휴가, 담당자 관련 질문만 답변합니다.

규칙:
- HR과 무관한 질문(날씨, 코딩, 일반 상식 등)은 search_hr_docs를 호출하지 말고 즉시 "저는 HR 규정 안내만 가능합니다. HR 관련 질문을 입력해 주세요."라고 안내하세요.
- HR 관련 질문은 반드시 search_hr_docs tool을 사용해 근거를 찾으세요.
- tool 검색 결과에 근거가 있을 때만 답변하세요.
- 근거가 없으면 "해당 내용은 인사팀에 직접 문의해 주세요."라고 안내하세요.
- 답변 마지막에 반드시 출처를 표시하세요: [출처: {category} / {id}]
- 출처 없이 답변하는 것은 금지입니다."""


def run_agent(user_message: str, history: list[dict] | None = None) -> str:
    messages = (history or []) + [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    results = search_hr_docs(block.input["query"])
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(results, ensure_ascii=False),
                    })

            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
