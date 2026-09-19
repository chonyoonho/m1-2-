import json

from openai import OpenAI

from app.config import settings
from app.models.data import DataSummary
from app.services.tools import TOOLS_SCHEMA, execute_tool

_client: OpenAI | None = None
MAX_TOOL_ITERATIONS = 4


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        _client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
    return _client


def build_system_prompt(summary: DataSummary) -> str:
    return (
        "당신은 대전광역시 3.8민주의거기념사업회의 데이터 분석 비서입니다. "
        "3.8민주의거의 정신(자유·민주·정의)을 계승하는 기념관의 교육·행사 프로그램 운영을 돕습니다.\n\n"
        "[교육·행사 참가자 수 데이터 요약]\n"
        f"- 데이터 기간: {summary.period}\n"
        f"- 총 레코드: {summary.count}개\n"
        f"- 참가자 수 지표(총합/평균/최대/최소): "
        f"{summary.metrics.total} / {summary.metrics.average} / {summary.metrics.max} / {summary.metrics.min}\n"
        f"- 최근 추세: {summary.trend}\n\n"
        "위 데이터를 근거로 담당자의 질문에 구체적인 수치를 인용하며 답변하세요. "
        "특정 연도의 월별 수치나 프로그램별 비교처럼 위 요약만으로 답할 수 없는 질문을 받으면, "
        "추측하지 말고 제공된 도구(get_monthly_breakdown, get_program_breakdown, get_data_summary)를 "
        "호출해 실제 데이터를 조회한 뒤 답변하세요. 도구로도 확인할 수 없는 내용은 모른다고 답하세요."
    )


def get_chat_reply(system_prompt: str, history: list[dict]) -> str:
    """history: [{"role": "user"|"assistant", "content": str}, ...] (system 제외 이전 대화)

    GPT가 필요하다고 판단하면 TOOLS_SCHEMA에 정의된 도구(월별/프로그램별 통계 등)를
    스스로 호출하도록 하고(Function Calling), 도구 실행 결과를 다시 모델에 전달해
    최종 답변을 받는다. 프록시가 SDK의 전체 message dump를 그대로 되돌려 보내면
    거부하는 것을 확인했기 때문에, role/content/tool_calls만 담은 최소 형태로 재구성해 보낸다.
    """
    client = get_client()
    messages = [{"role": "system", "content": system_prompt}] + history

    for _ in range(MAX_TOOL_ITERATIONS):
        response = client.chat.completions.create(
            model=settings.chat_model,
            messages=messages,
            max_tokens=settings.chat_max_tokens,
            tools=TOOLS_SCHEMA,
        )
        choice = response.choices[0]
        msg = choice.message

        if choice.finish_reason != "tool_calls" or not msg.tool_calls:
            return msg.content or ""

        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in msg.tool_calls
                ],
            }
        )

        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = execute_tool(tc.function.name, args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    return "요청하신 내용을 확인하는 데 필요한 조회가 너무 많아 답변을 완료하지 못했습니다. 질문을 조금 더 구체적으로 나눠서 다시 시도해주세요."
