import base64
import logging
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Any

from google import genai
from google.genai import types
from PIL import Image

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE = 1.0
RETRYABLE_ERRORS = ("ServiceUnavailable", "DeadlineExceeded", "ResourceExhausted")

PRELOAD_PROMPT = (
    "この画面の内容を把握してください。"
    "画面に何が表示されているか、ユーザーが何をしているかを理解し、簡潔に要約してください。"
)


@dataclass(frozen=True)
class PreloadResult:
    success: bool
    context_summary: str | None
    chat_session: Any | None
    error_message: str | None


class GeminiClient:
    """Gemini API と通信し、画面理解・応答生成を行う（google.genai SDK）。"""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._history: list[types.Content] = []
        logger.debug("GeminiClient initialized: model=%s", model)

    def preload_context(self, image_base64: str) -> PreloadResult:
        """スクリーンショットを送信し、AIに画面状況を事前把握させる。"""
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))

            response = self._client.models.generate_content(
                model=self._model,
                contents=[PRELOAD_PROMPT, image],
            )
            summary = response.text
            # 画面要約をシステムコンテキストとして履歴に追加
            self._history = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(f"[画面コンテキスト] {summary}")],
                ),
                types.Content(
                    role="model",
                    parts=[types.Part.from_text("画面の内容を確認しました。何かご質問はありますか？")],
                ),
            ]
            logger.debug("preload_context succeeded")
            return PreloadResult(
                success=True,
                context_summary=summary,
                chat_session=self._history,
                error_message=None,
            )
        except Exception as e:
            logger.error("preload_context failed: %s - %s", type(e).__name__, e)
            self._history = []
            return PreloadResult(
                success=False,
                context_summary=None,
                chat_session=None,
                error_message=str(e),
            )

    def generate_response(self, user_input: str, chat_session: Any) -> str:
        """ユーザー指示を送信し、AI応答テキストを返す（会話履歴付き）。"""
        # 会話履歴にユーザー入力を追加
        history = list(self._history)
        history.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(user_input)],
            )
        )

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=history,
                )
                result = response.text
                # 応答を履歴に追加
                self._history = history + [
                    types.Content(
                        role="model",
                        parts=[types.Part.from_text(result)],
                    )
                ]
                logger.debug("generate_response succeeded: length=%d", len(result))
                return result
            except Exception as e:
                last_error = e
                if type(e).__name__ in RETRYABLE_ERRORS and attempt < MAX_RETRIES:
                    wait = BACKOFF_BASE * (2 ** attempt)
                    logger.warning("generate_response retrying in %.1fs: %s", wait, type(e).__name__)
                    time.sleep(wait)
                else:
                    logger.error("generate_response error: %s - %s", type(e).__name__, e)
                    raise

        raise last_error  # type: ignore[misc]

    def create_session(self) -> Any:
        """新しいセッション（会話履歴をリセット）。"""
        self._history = []
        return self._history

    def is_available(self) -> bool:
        try:
            self._client.models.generate_content(
                model=self._model, contents="test"
            )
            return True
        except Exception:
            return False
