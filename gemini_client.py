import base64
import logging
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Any

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from PIL import Image

logger = logging.getLogger(__name__)

# リトライ設定（BR-04）
MAX_RETRIES = 3
BACKOFF_BASE = 1.0  # 秒

# タイムアウト設定（BR-02, BR-03）
PRELOAD_TIMEOUT = 10   # 秒
GENERATE_TIMEOUT = 30  # 秒

# リトライ対象エラー（BR-04）
RETRYABLE_EXCEPTIONS = (
    google_exceptions.ServiceUnavailable,
    google_exceptions.DeadlineExceeded,
    google_exceptions.ResourceExhausted,
    ConnectionError,
    TimeoutError,
)

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
    """Gemini API と通信し、画面理解・応答生成を行う。

    API キーを受け取って初期化する。
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-thinking-exp",
    ) -> None:
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)
        logger.debug("GeminiClient initialized: model=%s", model)

    def preload_context(self, image_base64: str) -> PreloadResult:
        """スクリーンショットを送信し、AIに画面状況を事前把握させる（FL-02）。

        タイムアウト: 10秒。失敗時は最大3回リトライ（指数バックオフ）。
        """
        def _call():
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))

            chat = self._model.start_chat()
            response = chat.send_message(
                [image, PRELOAD_PROMPT],
                request_options={"timeout": PRELOAD_TIMEOUT},
            )
            return chat, response.text

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                chat, summary = _call()
                logger.debug(
                    "preload_context succeeded: summary_length=%d", len(summary)
                )
                return PreloadResult(
                    success=True,
                    context_summary=summary,
                    chat_session=chat,
                    error_message=None,
                )
            except RETRYABLE_EXCEPTIONS as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    wait = BACKOFF_BASE * (2**attempt)
                    logger.warning(
                        "preload_context failed (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1,
                        MAX_RETRIES + 1,
                        wait,
                        type(e).__name__,
                    )
                    time.sleep(wait)
            except Exception as e:
                logger.error("preload_context non-retryable error: %s", type(e).__name__)
                return PreloadResult(
                    success=False,
                    context_summary=None,
                    chat_session=None,
                    error_message=str(e),
                )

        logger.error(
            "preload_context exhausted retries: %s", type(last_error).__name__
        )
        return PreloadResult(
            success=False,
            context_summary=None,
            chat_session=None,
            error_message=str(last_error),
        )

    def generate_response(self, user_input: str, chat_session: Any) -> str:
        """ユーザー指示をセッション経由で送信し、AI応答テキストを返す（FL-04）。

        タイムアウト: 30秒。失敗時は最大3回リトライ（指数バックオフ）。
        失敗時は例外を raise する（呼び出し元で _handle_error に渡すこと）。
        """
        def _call() -> str:
            response = chat_session.send_message(
                user_input,
                request_options={"timeout": GENERATE_TIMEOUT},
            )
            return response.text

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                result = _call()
                logger.debug(
                    "generate_response succeeded: response_length=%d", len(result)
                )
                return result
            except RETRYABLE_EXCEPTIONS as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    wait = BACKOFF_BASE * (2**attempt)
                    logger.warning(
                        "generate_response failed (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1,
                        MAX_RETRIES + 1,
                        wait,
                        type(e).__name__,
                    )
                    time.sleep(wait)
            except Exception as e:
                logger.error(
                    "generate_response non-retryable error: %s", type(e).__name__
                )
                raise

        raise last_error  # type: ignore[misc]

    def create_session(self) -> Any:
        """新しい Gemini ChatSession を生成して返す。"""
        return self._model.start_chat()

    def is_available(self) -> bool:
        """APIが利用可能かどうかを確認する。"""
        try:
            self._model.generate_content(
                "test", request_options={"timeout": 5}
            )
            return True
        except Exception:
            return False
