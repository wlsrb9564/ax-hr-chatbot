import asyncio
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import stream_agent

app = FastAPI(title="HR 챗봇 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


class Message(BaseModel):
    role: str   # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []


class Snippet(BaseModel):
    id: str
    category: str
    question: str
    answer: str


class ChatResponse(BaseModel):
    answer: str
    snippets: list[Snippet] = []


@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="메시지를 입력해 주세요.")

    history = [{"role": m.role, "content": m.content} for m in request.history]

    async def generate():
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue = asyncio.Queue()

        def run_in_thread():
            try:
                for chunk in stream_agent(request.message, history):
                    loop.call_soon_threadsafe(queue.put_nowait, chunk)
            except Exception:
                loop.call_soon_threadsafe(
                    queue.put_nowait,
                    {"type": "error", "text": "답변 생성 중 오류가 발생했습니다."},
                )
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, None)  # 종료 신호

        thread_task = asyncio.create_task(asyncio.to_thread(run_in_thread))

        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        await thread_task

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/health")
async def health():
    return {"status": "ok"}


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
