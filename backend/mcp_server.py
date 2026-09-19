"""3.8민주의거기념사업회 데이터 비서 - MCP 서버

보너스 과제: GPT function calling과 동일한 내부 기능(요약/월별/프로그램별 통계 조회)을
MCP(Model Context Protocol) 도구로도 노출한다. Claude Desktop 등 MCP 클라이언트에서
이 서버를 연결하면, FastAPI를 거치지 않고도 동일한 Firestore 데이터를 조회할 수 있다.

실행 방법:
    python mcp_server.py            # stdio transport (Claude Desktop 등에서 사용)

Claude Desktop 설정 예시 (claude_desktop_config.json):
    {
      "mcpServers": {
        "38demo-data": {
          "command": "python",
          "args": ["<repo>/backend/mcp_server.py"],
          "env": {
            "FIREBASE_SERVICE_ACCOUNT_JSON": "...",
          }
        }
      }
    }
"""

from mcp.server.mcpserver import MCPServer

from app.services import analysis
from app.services.data_service import fetch_all_rows

mcp = MCPServer(
    name="38demo-data",
    instructions=(
        "대전광역시 3.8민주의거기념사업회의 교육·행사 프로그램 참가자 수 데이터를 조회하는 도구 모음입니다. "
        "전체 요약, 연도별 월별 통계, 프로그램별 통계를 제공합니다."
    ),
)


@mcp.tool()
def get_data_summary() -> dict:
    """전체 데이터 기간, 총 레코드 수, 참가자 수 총합/평균/최대/최소, 최근 추세를 반환한다."""
    rows = fetch_all_rows()
    return analysis.build_summary(rows).model_dump()


@mcp.tool()
def get_monthly_breakdown(year: int | None = None) -> dict:
    """월별 참가자 수 합계/평균/건수를 반환한다.

    Args:
        year: 조회할 연도 (예: 2025). 생략하면 전체 기간의 월별 데이터를 반환한다.
    """
    rows = fetch_all_rows()
    return {"monthly": analysis.monthly_breakdown(rows, year=year)}


@mcp.tool()
def get_program_breakdown() -> dict:
    """프로그램/행사명별 참가자 수 합계/평균/건수를 총합 기준 내림차순으로 반환한다."""
    rows = fetch_all_rows()
    return {"programs": analysis.program_breakdown(rows)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
