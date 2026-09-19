from datetime import date as date_type

from app.services.firestore_service import DATA_COLLECTION, get_db


def fetch_all_rows() -> list[dict]:
    """Firestore data 컬렉션의 모든 레코드를 조회한다."""
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
