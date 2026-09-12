from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.models.conversation import (
    ConversationCreate,
    ConversationDetail,
    ConversationListItem,
    Message,
)
from app.services.firestore_service import CONVERSATIONS_COLLECTION, get_db

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


def _messages_to_dicts(messages: list[Message]) -> list[dict]:
    return [
        {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
        for m in messages
    ]


@router.post("", response_model=ConversationDetail, status_code=201)
def create_conversation(payload: ConversationCreate):
    db = get_db()
    now = datetime.utcnow()
    doc_ref = db.collection(CONVERSATIONS_COLLECTION).document()
    doc_ref.set(
        {
            "title": payload.title,
            "messages": _messages_to_dicts(payload.messages),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
    )
    return ConversationDetail(
        id=doc_ref.id,
        title=payload.title,
        messages=payload.messages,
        created_at=now,
        updated_at=now,
    )


@router.get("", response_model=list[ConversationListItem])
def list_conversations():
    db = get_db()
    docs = db.collection(CONVERSATIONS_COLLECTION).stream()
    items = []
    for doc in docs:
        payload = doc.to_dict()
        items.append(
            ConversationListItem(
                id=doc.id,
                title=payload.get("title", "(제목 없음)"),
                message_count=len(payload.get("messages", [])),
                created_at=datetime.fromisoformat(payload["created_at"]),
                updated_at=datetime.fromisoformat(payload["updated_at"]),
            )
        )
    items.sort(key=lambda x: x.updated_at, reverse=True)
    return items


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation_detail(conversation_id: str):
    db = get_db()
    doc = db.collection(CONVERSATIONS_COLLECTION).document(conversation_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    payload = doc.to_dict()
    return ConversationDetail(
        id=doc.id,
        title=payload.get("title", "(제목 없음)"),
        messages=[Message(**m) for m in payload.get("messages", [])],
        created_at=datetime.fromisoformat(payload["created_at"]),
        updated_at=datetime.fromisoformat(payload["updated_at"]),
    )


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str):
    db = get_db()
    doc_ref = db.collection(CONVERSATIONS_COLLECTION).document(conversation_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    doc_ref.delete()
