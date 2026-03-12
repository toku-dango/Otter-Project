import base64
import logging
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Any

from google import genai
from PIL import Image

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE = 1.0
PRELOAD_TIMEOUT = 10
GENERATE_TIMEOUT = 30

RETRYABLE_ERRORS = ("ServiceUnavailable", "DeadlineExceeded", "ResourceExhausted")

PRELOAD_PROMPT = (
    "この画面の内容を把握してください。これはユーザーが短い指示を送る前の事前把握フェーズです。"
    "画面に何が表示されているか、ユーザーが何をしているかを理解してください。"
    "把握した内容を簡潔に要約してください。"
)


@dataclass(frozen=True)
class PreloadResult:
    success: bool
    context_summary: str | None
    chat_session: Any | None
    error_message: str | None


class GeminiClient:
    """Gemini API と通信し、画面理解・応答生成を行う（google.genai SDK）。"""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        logger.debug("GeminiClient initialized: model=%s", model)

    def preload_context(self, image_base64: str) -> PreloadResult:
        """スクリーンショットを送信し、AIに画面状況を事前把握させる。"""
        def _call():
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            chat = self._client.chats.create(model=self._model)
            response = chat.send_message([PRELOAD_PROMPT, image])
            return chat, response.text

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                chat, summary = _call()
                logger.debug("preload_context succeeded: summary_length=%d", len(summary))
                return PreloadResult(
                    success=True,
                    context_summary=summary,
                    chat_session=chat,
                    error_message=None,
                )
            except Exception as e:
                last_error = e
                if type(e).__name__ in RETRYABLE_ERRORS and attempt < MAX_RETRIES:
                    wait = BACKOFF_BASE * (2 ** attempt)
                    logger.warning("preload_context retrying in %.1fs: %s", wait, type(e).__name__)
                    time.sleep(wait)
                else:
                    logger.error("preload_context failed: %s", type(e).__name__)
                    return PreloadResult(
                        success=False,
                        context_summary=None,
                        chat_session=None,
                        error_message=str(e),
                    )

        return PreloadResult(
            success=False, context_summary=None, chat_session=None,
            error_message=str(last_error),
        )

    def generate_response(self, user_input: str, chat_session: Any) -> str:
        """ユーザー指示をセッション経由で送信し、AI応答テキストを返す。"""
        def _call() -> str:
            response = chat_session.send_message(user_input)
            return response.text

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                result = _call()
                logger.debug("generate_response succeeded: length=%d", len(result))
                return result
            except Exception as e:
                last_error = e
                if type(e).__name__ in RETRYABLE_ERRORS and attempt < MAX_RETRIES:
                    wait = BACKOFF_BASE * (2 ** attempt)
                    logger.warning("generate_response retrying in %.1fs: %s", wait, type(e).__name__)
                    time.sleep(wait)
                else:
                    logger.error("generate_response non-retryable error: %s", type(e).__name__)
                    raise

        raise last_error  # type: ignore[misc]

    def create_session(self) -> Any:
        """新しい Chat セッションを生成して返す。"""
        return self._client.chats.create(model=self._model)

    def is_available(self) -> bool:
        try:
            self._client.models.generate_content(
                model=self._model, contents="test"
            )
            return True
        except Exception:
            return False
