from datetime import date as date_type

from pydantic import BaseModel, Field


class DataPointCreate(BaseModel):
    """교육·행사 프로그램 참가자 수 데이터 등록/수정 요청."""

    date: date_type = Field(..., description="행사/프로그램 진행 날짜")
    value: float = Field(..., ge=0, description="참가자 수")
    memo: str = Field(..., min_length=1, max_length=200, description="프로그램/행사명 등 메모")


class DataPointResponse(DataPointCreate):
    id: str


class DataMetrics(BaseModel):
    total: float
    average: float
    max: float
    min: float


class DataSummary(BaseModel):
    period: str
    count: int
    metrics: DataMetrics
    trend: str


class MonthlyStat(BaseModel):
    month: str
    total: float
    average: float
    count: int


class ProgramStat(BaseModel):
    program: str
    total: float
    average: float
    count: int


class DataStatistics(BaseModel):
    """보너스: summary를 월별/프로그램별 세부 지표로 확장한 응답."""

    summary: DataSummary
    monthly: list[MonthlyStat]
    by_program: list[ProgramStat]
