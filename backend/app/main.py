from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, conversations, data

app = FastAPI(
    title="3.8민주의거기념사업회 데이터 비서 API",
    description="교육·행사 프로그램 참가자 수 데이터를 분석하고, AI가 이를 기반으로 답변하는 백엔드",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "3.8민주의거기념사업회 데이터 비서 API"}
