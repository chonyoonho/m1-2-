from datetime import date as date_type

from fastapi import APIRouter, HTTPException

from app.models.data import DataPointCreate, DataPointResponse, DataSummary
from app.services import analysis
from app.services.firestore_service import DATA_COLLECTION, get_db

router = APIRouter(prefix="/api/data", tags=["data"])


def _doc_to_response(doc) -> DataPointResponse:
    payload = doc.to_dict()
    return DataPointResponse(
        id=doc.id,
        date=date_type.fromisoformat(payload["date"]),
        value=payload["value"],
        memo=payload["memo"],
    )


def fetch_all_rows() -> list[dict]:
    db = get_db()
    docs = db.collection(DATA_COLLECTION).stream()
    rows = []
    for doc in docs:
        payload = doc.to_dict()
        rows.append(
            {
                "date": date_type.fromisoformat(payload["date"]),
                "value": payload["value"],
                "memo": payload["memo"],
            }
        )
    return rows


@router.post("", response_model=DataPointResponse, status_code=201)
def create_data(item: DataPointCreate):
    db = get_db()
    doc_ref = db.collection(DATA_COLLECTION).document()
    doc_ref.set(
        {
            "date": item.date.isoformat(),
            "value": item.value,
            "memo": item.memo,
        }
    )
    return DataPointResponse(id=doc_ref.id, **item.model_dump())


@router.get("", response_model=list[DataPointResponse])
def list_data():
    db = get_db()
    docs = db.collection(DATA_COLLECTION).stream()
    items = [_doc_to_response(doc) for doc in docs]
    items.sort(key=lambda x: x.date)
    return items


@router.get("/summary", response_model=DataSummary)
def get_summary():
    rows = fetch_all_rows()
    return analysis.build_summary(rows)


@router.put("/{item_id}", response_model=DataPointResponse)
def update_data(item_id: str, item: DataPointCreate):
    db = get_db()
    doc_ref = db.collection(DATA_COLLECTION).document(item_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    doc_ref.set(
        {
            "date": item.date.isoformat(),
            "value": item.value,
            "memo": item.memo,
        }
    )
    return DataPointResponse(id=item_id, **item.model_dump())


@router.delete("/{item_id}", status_code=204)
def delete_data(item_id: str):
    db = get_db()
    doc_ref = db.collection(DATA_COLLECTION).document(item_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    doc_ref.delete()
