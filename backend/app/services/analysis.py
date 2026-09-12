from datetime import date as date_type

from app.models.data import DataMetrics, DataSummary


def build_summary(rows: list[dict]) -> DataSummary:
    """참가자 수 시계열 데이터로부터 기간/통계/추세 요약을 만든다.

    rows: [{"date": date, "value": float, "memo": str}, ...]
    """
    if not rows:
        return DataSummary(
            period="데이터 없음",
            count=0,
            metrics=DataMetrics(total=0, average=0, max=0, min=0),
            trend="데이터가 없어 추세를 계산할 수 없음",
        )

    sorted_rows = sorted(rows, key=lambda r: r["date"])
    values = [r["value"] for r in sorted_rows]

    start = sorted_rows[0]["date"]
    end = sorted_rows[-1]["date"]
    period = f"{_fmt(start)} ~ {_fmt(end)}"

    total = sum(values)
    average = total / len(values)
    trend = _calc_trend(sorted_rows)

    return DataSummary(
        period=period,
        count=len(values),
        metrics=DataMetrics(
            total=round(total, 1),
            average=round(average, 1),
            max=max(values),
            min=min(values),
        ),
        trend=trend,
    )


def _fmt(d) -> str:
    if isinstance(d, date_type):
        return d.strftime("%Y-%m")
    return str(d)[:7]


def _calc_trend(sorted_rows: list[dict]) -> str:
    """최근 3개월 평균과 그 이전 3개월 평균을 비교해 상승/하락/유지를 판단한다."""
    monthly: dict[str, list[float]] = {}
    for row in sorted_rows:
        key = _fmt(row["date"])
        monthly.setdefault(key, []).append(row["value"])

    months = sorted(monthly.keys())
    if len(months) < 2:
        return "데이터 기간이 짧아 추세 판단 불가"

    def month_avg(keys: list[str]) -> float:
        vals = [v for k in keys for v in monthly[k]]
        return sum(vals) / len(vals) if vals else 0

    window = min(3, len(months) // 2) or 1
    recent = month_avg(months[-window:])
    previous = month_avg(months[-2 * window : -window]) if len(months) >= 2 * window else month_avg(months[:-window])

    if previous == 0:
        return "유지"

    change_pct = round((recent - previous) / previous * 100, 1)
    if change_pct > 5:
        return f"상승 (최근 {window}개월 평균 대비 +{change_pct}%)"
    if change_pct < -5:
        return f"하락 (최근 {window}개월 평균 대비 {change_pct}%)"
    return f"유지 (변동 {change_pct}%)"
