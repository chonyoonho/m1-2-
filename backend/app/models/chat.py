from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = Field(
        default=None, description="이어서 대화할 기존 conversation id (없으면 새로 생성)"
    )


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
