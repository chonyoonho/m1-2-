from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.routers.data import fetch_all_rows
from app.services import analysis, openai_service
from app.services.firestore_service import CONVERSATIONS_COLLECTION, get_db

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest):
    db = get_db()
    now = datetime.utcnow()

    # 1) 기존 대화 불러오기 또는 신규 생성 준비
    if payload.conversation_id:
        doc_ref = db.collection(CONVERSATIONS_COLLECTION).document(payload.conversation_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
        conv = doc.to_dict()
        messages = conv.get("messages", [])
        title = conv.get("title", payload.message[:30])
        created_at = conv.get("created_at", now.isoformat())
    else:
        doc_ref = db.collection(CONVERSATIONS_COLLECTION).document()
        messages = []
        title = payload.message[:30]
        created_at = now.isoformat()

    # 2) 데이터 요약 조회 후 시스템 프롬프트에 주입
    rows = fetch_all_rows()
    summary = analysis.build_summary(rows)
    system_prompt = openai_service.build_system_prompt(summary)

    # 3) 사용자 메시지 추가 후 GPT 호출
    messages.append({"role": "user", "content": payload.message, "created_at": now.isoformat()})
    history = [{"role": m["role"], "content": m["content"]} for m in messages]

    try:
        reply = openai_service.get_chat_reply(system_prompt, history)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    reply_at = datetime.utcnow()
    messages.append({"role": "assistant", "content": reply, "created_at": reply_at.isoformat()})

    # 4) 대화 자동 저장
    doc_ref.set(
        {
            "title": title,
            "messages": messages,
            "created_at": created_at,
            "updated_at": reply_at.isoformat(),
        }
    )

    return ChatResponse(conversation_id=doc_ref.id, reply=reply)
