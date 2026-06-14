import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import run_agent

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


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="메시지를 입력해 주세요.")

    history = [{"role": m.role, "content": m.content} for m in request.history]
    try:
        result = await asyncio.to_thread(run_agent, request.message, history)
    except Exception:
        raise HTTPException(status_code=500, detail="답변 생성 중 오류가 발생했습니다.")
    if not result["answer"]:
        raise HTTPException(status_code=500, detail="답변을 생성하지 못했습니다.")
    return ChatResponse(answer=result["answer"], snippets=result["snippets"])


@app.get("/health")
async def health():
    return {"status": "ok"}


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
