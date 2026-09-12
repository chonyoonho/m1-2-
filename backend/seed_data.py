"""
3.8민주의거기념사업회 교육·행사 프로그램 참가자 수 샘플 데이터 생성 스크립트.

- 실제 방문객/참가자 통계가 공개되어 있지 않아, 기념관이 실제 운영하는 프로그램군
  (3.8민주아카데미, 보드게임 교육, 청소년 백일장·사생대회, 학교 연계 체험학습,
  시민 해설사 양성과정, 특별전 연계 교육)을 기준으로 현실적인 추정 데이터를 생성한다.
- 2019-01 ~ 2025-12, 총 100개 이상의 (date, value, memo) 레코드를 만든다.
- 2020~2021년은 코로나19 영향으로 참가자 수가 급감하도록 반영했다.

사용법:
  python seed_data.py            # Firestore에 업로드 (.env / FIREBASE_SERVICE_ACCOUNT_JSON 필요)
  python seed_data.py --dry-run  # 업로드 없이 backend/sample_data.json 파일로만 저장
"""

import argparse
import json
import random
from datetime import date
from pathlib import Path

random.seed(38)

MONTHLY_PROGRAMS = [
    "3.8민주아카데미 오늘을 묻다",
    "보드게임으로 만나는 민주주의",
]

ANNUAL_EVENTS = {
    3: ["3.8민주의거 기념식 연계 교육"],
    5: ["청소년 백일장"],
    9: ["청소년 사생대회"],
    10: ["시민 해설사 양성과정"],
}

SCHOOL_TRIP_MONTHS = [3, 4, 5, 6, 9, 10, 11]


def _covid_factor(year: int) -> float:
    if year == 2020:
        return 0.25
    if year == 2021:
        return 0.45
    if year == 2022:
        return 0.8
    return 1.0


def _growth_factor(year: int) -> float:
    # 코로나 이후 회복 및 완만한 성장 추세를 반영
    baseline_year = 2019
    return 1.0 + max(0, year - baseline_year) * 0.04


def generate_sample_data() -> list[dict]:
    rows: list[dict] = []

    for year in range(2019, 2026):
        for month in range(1, 13):
            if year == 2025 and month > 12:
                continue
            factor = _covid_factor(year) * _growth_factor(year)

            # 월별 정기 프로그램
            for program in MONTHLY_PROGRAMS:
                base = 28 if program == MONTHLY_PROGRAMS[0] else 22
                value = max(0, round(base * factor + random.uniform(-4, 6)))
                rows.append(
                    {
                        "date": date(year, month, random.randint(5, 15)),
                        "value": value,
                        "memo": program,
                    }
                )

            # 학교 연계 현장체험학습 (봄/가을 성수기)
            if month in SCHOOL_TRIP_MONTHS:
                base = 60
                value = max(0, round(base * factor + random.uniform(-10, 15)))
                rows.append(
                    {
                        "date": date(year, month, random.randint(1, 28)),
                        "value": value,
                        "memo": "학교 연계 현장체험학습",
                    }
                )

            # 연 1회 행사
            if month in ANNUAL_EVENTS:
                for event_name in ANNUAL_EVENTS[month]:
                    base = 90 if event_name == "3.8민주의거 기념식 연계 교육" else 45
                    value = max(0, round(base * factor + random.uniform(-8, 12)))
                    rows.append(
                        {
                            "date": date(year, month, random.randint(1, 20)),
                            "value": value,
                            "memo": event_name,
                        }
                    )

    rows.sort(key=lambda r: r["date"])
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Firestore에 업로드하지 않고 backend/sample_data.json 파일로만 저장",
    )
    args = parser.parse_args()

    rows = generate_sample_data()
    print(f"생성된 데이터 포인트 수: {len(rows)}개")

    if args.dry_run:
        out_path = Path(__file__).parent / "sample_data.json"
        serializable = [{**r, "date": r["date"].isoformat()} for r in rows]
        out_path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"dry-run 모드: {out_path} 파일로 저장했습니다. (Firestore 업로드 안 함)")
        return

    from app.services.firestore_service import DATA_COLLECTION, get_db

    db = get_db()
    batch = db.batch()
    collection = db.collection(DATA_COLLECTION)
    for i, row in enumerate(rows, start=1):
        doc_ref = collection.document()
        batch.set(doc_ref, {"date": row["date"].isoformat(), "value": row["value"], "memo": row["memo"]})
        if i % 400 == 0:
            batch.commit()
            batch = db.batch()
    batch.commit()
    print(f"Firestore '{DATA_COLLECTION}' 컬렉션에 {len(rows)}개 데이터를 업로드했습니다.")


if __name__ == "__main__":
    main()
