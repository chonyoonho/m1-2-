"""GPT function calling 및 MCP 서버가 공유하는 도구 스키마/실행 로직.

시스템 프롬프트에는 전체 집계(요약)만 주입되기 때문에, 특정 연도의 월별 수치나
프로그램별 비교처럼 더 세부적인 질문에는 GPT가 이 도구들을 스스로 호출해서
Firestore의 실제 데이터를 조회한 뒤 답한다.
"""

from app.services import analysis
from app.services.data_service import fetch_all_rows

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_monthly_breakdown",
            "description": (
                "월별 참가자 수 합계/평균/건수를 반환한다. "
                "특정 연도나 특정 월의 정확한 수치, 최근 몇 개월의 추이 등 "
                "요약 정보만으로는 답할 수 없는 질문에 사용한다."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "조회할 연도 (예: 2025). 생략하면 전체 기간의 월별 데이터를 반환한다.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_program_breakdown",
            "description": (
                "프로그램/행사명(예: 보드게임으로 만나는 민주주의, 3.8민주아카데미 등)별 "
                "참가자 수 합계/평균/건수를 총합 기준 내림차순으로 반환한다. "
                "어떤 프로그램이 인기 있는지, 프로그램별 비교가 필요할 때 사용한다."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_data_summary",
            "description": (
                "전체 데이터 기간, 총 레코드 수, 총합/평균/최대/최소, 최근 추세를 반환한다. "
                "시스템 프롬프트에 이미 포함된 정보와 동일하지만, 최신 값을 다시 확인하고 싶을 때 사용한다."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def execute_tool(name: str, arguments: dict) -> dict:
    rows = fetch_all_rows()

    if name == "get_monthly_breakdown":
        year = arguments.get("year")
        return {"monthly": analysis.monthly_breakdown(rows, year=year)}

    if name == "get_program_breakdown":
        return {"programs": analysis.program_breakdown(rows)}

    if name == "get_data_summary":
        summary = analysis.build_summary(rows)
        return summary.model_dump()

    return {"error": f"알 수 없는 도구입니다: {name}"}
