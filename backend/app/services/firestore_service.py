import json

import firebase_admin
from firebase_admin import credentials, firestore

from app.config import settings

_app = None


def get_db():
    """Firestore 클라이언트를 지연 초기화해서 반환한다."""
    global _app
    if _app is None:
        if not settings.firebase_service_account_json:
            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_JSON 환경 변수가 설정되지 않았습니다."
            )
        cred_dict = json.loads(settings.firebase_service_account_json)
        cred = credentials.Certificate(cred_dict)
        _app = firebase_admin.initialize_app(cred)
    return firestore.client()


DATA_COLLECTION = "data"
CONVERSATIONS_COLLECTION = "conversations"
