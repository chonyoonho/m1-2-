from openai import OpenAI

from app.config import settings
from app.models.data import DataSummary

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        _client = OpenAI(api_key=settings.openai_api_key)
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
        "데이터에 없는 내용은 추측하지 말고 모른다고 답하세요."
    )


def get_chat_reply(system_prompt: str, history: list[dict]) -> str:
    """history: [{"role": "user"|"assistant", "content": str}, ...] (system 제외 이전 대화)"""
    client = get_client()
    messages = [{"role": "system", "content": system_prompt}] + history

    response = client.chat.completions.create(
        model=settings.chat_model,
        messages=messages,
        max_tokens=settings.chat_max_tokens,
    )
    return response.choices[0].message.content or ""
