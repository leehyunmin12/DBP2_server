from google import genai
from google.genai import types

from app.core.config import settings
from pydantic import BaseModel



class AIError(Exception):
    ''' AI 호출 실패 시 에러 '''

# 클라이언트를 담아 둘 빈 칸
_client: genai.Client | None = None

def _get_client() -> genai.Client:
    global _client # 위에서 선언한 _client를 바꾸겠다.
    if _client is None:
        if not settings.gemini_api_key: # 키 없을 때 에러
            raise AIError("GEMINI_API_KEY가 설정되지 않았습니다.")
        _client = genai.Client( # 키를 넣어서 Gemini와 통신할 클라이언트 만든다.
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=60_000), # 밀리초 단위, 30초
        )
    return _client

# 규칙, 데이터
def generate_summary(system_instruction: str, content: str) -> str:
    try:
        response = _get_client().models.generate_content(
            model=settings.gemini_model, # 모델
            contents=content, # 질문 내용
            config=types.GenerateContentConfig(system_instruction=system_instruction), # AI의 역할과 규칙
        )
    except AIError:
        raise
    except Exception as e: # 기타 에러
        raise AIError("AI 요약 생성에 실패했습니다.") from e

    text = (response.text or "").strip() # 없으면 빈 문자열
    if not text:
        raise AIError("AI가 빈 응답을 돌려줬습니다.")
    return text

def generate_from_image(
    system_instruction: str,
    prompt: str,
    image: bytes,
    mime_type: str,
    schema: type[BaseModel],
) -> BaseModel:
    try:
        response = _get_client().models.generate_content(
            model=settings.gemini_model,
            contents=[
                types.Part.from_bytes(data=image, mime_type=mime_type),
                prompt,
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
    except AIError:
        raise
    except Exception as e:
        raise AIError("AI 이미지 인식에 실패했습니다.") from e

    result = response.parsed
    if result is None:
        raise AIError("AI가 형식에 맞는 응답을 돌려주지 않았습니다.")
    return result