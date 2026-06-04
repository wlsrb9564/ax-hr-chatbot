from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent import run_agent

app = FastAPI(title="HR 챗봇 API")


class Message(BaseModel):
    role: str   # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []


class ChatResponse(BaseModel):
    answer: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="메시지를 입력해 주세요.")

    history = [{"role": m.role, "content": m.content} for m in request.history]
    try:
        answer = run_agent(request.message, history=history)
    except Exception:
        raise HTTPException(status_code=500, detail="답변 생성 중 오류가 발생했습니다.")
    if not answer:
        raise HTTPException(status_code=500, detail="답변을 생성하지 못했습니다.")
    return ChatResponse(answer=answer)


@app.get("/health")
async def health():
    return {"status": "ok"}
