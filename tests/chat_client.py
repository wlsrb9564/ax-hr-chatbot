"""
HR 챗봇 터미널 클라이언트

실행:
  1. uv run uvicorn main:app --reload
  2. uv run python tests/chat_client.py
"""

import httpx

BASE_URL = "http://localhost:8000"


def chat():
    history = []
    print("HR 챗봇입니다. 종료하려면 'exit' 또는 'quit'을 입력하세요.\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("대화를 종료합니다.")
            break

        try:
            response = httpx.post(
                f"{BASE_URL}/chat",
                json={"message": user_input, "history": history},
                timeout=30,
            )
            response.raise_for_status()
            answer = response.json()["answer"]

            print(f"\nBot: {answer}\n")

            # 대화 이력 누적
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": answer})

        except httpx.ConnectError:
            print("서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해 주세요.\n")
        except httpx.HTTPStatusError as e:
            print(f"오류: {e.response.json().get('detail', '알 수 없는 오류')}\n")


if __name__ == "__main__":
    chat()
