import base64
import logging
import time
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any

from google import genai
from PIL import Image

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE = 1.0
RETRYABLE_ERRORS = ("ServiceUnavailable", "DeadlineExceeded", "ResourceExhausted")

PRELOAD_PROMPT = """\
この画面の内容を把握してください。
以下の形式で必ず回答してください（他の文は不要）：

---DETAIL---
（詳細な分析：画面に何が表示されているか、ユーザーが何をしようとしているか、使用中のアプリやファイル名なども含めて詳しく）

---DISPLAY---
（ユーザーへの表示用：2〜3文のフレンドリーなメッセージ。「今は〜しているかな。困ったら聞いてね。」のような親しみやすい口調で。）
"""


def _parse_preload_response(text: str) -> tuple[str, str]:
    """DETAIL / DISPLAY セクションを抽出して返す。"""
    detail = text
    display = text
    if "---DETAIL---" in text and "---DISPLAY---" in text:
        parts = text.split("---DISPLAY---", 1)
        display = parts[1].strip()
        detail_part = parts[0].split("---DETAIL---", 1)
        detail = detail_part[1].strip() if len(detail_part) > 1 else text
    return detail, display


@dataclass(frozen=True)
class PreloadResult:
    success: bool
    context_summary: str | None    # 詳細分析（LLMコンテキスト用）
    display_message: str | None    # 短いフレンドリーメッセージ（GUI表示用）
    chat_session: Any | None
    error_message: str | None


class GeminiClient:
    """Gemini API と通信し、画面理解・応答生成を行う（google.genai SDK）。"""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        # 会話履歴: [{"role": "user"/"model", "parts": [{"text": "..."}]}]
        self._history: list[dict] = []
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
            detail, display = _parse_preload_response(response.text)
            self._history = [
                {"role": "user", "parts": [{"text": f"[画面コンテキスト] {detail}"}]},
                {"role": "model", "parts": [{"text": "画面の内容を確認しました。何かご質問はありますか？"}]},
            ]
            logger.debug("preload_context succeeded")
            return PreloadResult(success=True, context_summary=detail,
                                 display_message=display,
                                 chat_session=self._history, error_message=None)
        except Exception as e:
            logger.error("preload_context failed: %s - %s", type(e).__name__, e)
            self._history = []
            return PreloadResult(success=False, context_summary=None,
                                 display_message=None,
                                 chat_session=None, error_message=str(e))

    def generate_response(self, user_input: str, chat_session: Any) -> str:
        """ユーザー指示を送信し、AI応答テキストを返す（会話履歴付き）。"""
        contents = self._history + [
            {"role": "user", "parts": [{"text": user_input}]}
        ]

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=contents,
                )
                result = response.text
                self._history = contents + [
                    {"role": "model", "parts": [{"text": result}]}
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
        """会話履歴をリセットして新しいセッションを開始。"""
        self._history = []
        return self._history

    def is_available(self) -> bool:
        try:
            self._client.models.generate_content(model=self._model, contents="test")
            return True
        except Exception:
            return False
