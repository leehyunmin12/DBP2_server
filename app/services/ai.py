from google import genai
from google.genai import types

from app.core.config import settings


class AIError(Exception):
    ''' AI 호출 실패 시 에러 '''

_client: genai.Client | None = None

def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not settings.gemini_api_key:
            raise AIError("GEMINI_API_KEY가 설정되지 않았습니다.")
        _client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=60_000), # 밀리초 단위, 30초
        )
    return _client

def generate_summary(system_instruction: str, content: str) -> str:
    try:
        response = _get_client().models.generate_content(
            model=settings.gemini_model,
            contents=content,
            config=types.GenerateContentConfig(system_instruction=system_instruction),
        )
    except AIError:
        raise
    except Exception as e:
        raise AIError("AI 요약 생성에 실패했습니다.") from e

    text = (response.text or "").strip()
    if not text:
        raise AIError("AI가 빈 응답을 돌려줬습니다.")
    return text