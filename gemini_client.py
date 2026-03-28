import base64
import logging
import threading
import time
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any

from google import genai
from google.genai import types
from PIL import Image

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE = 1.0
RETRYABLE_ERRORS = ("ServiceUnavailable", "DeadlineExceeded", "ResourceExhausted", "ServerError")

DEEP_THINKING_MODEL = "gemini-2.5-flash"
DEEP_THINKING_BUDGET = 1024

DEEP_THINKING_PROMPT = """\
以下の初期分析を踏まえ、画面をより深く分析してください：
---
{stage1_detail}
---
以下の形式のみで回答：

---DEEP_DETAIL---
（画面内テキストの正確な抽出・UI要素の状態（入力済み/エラー/無効等）・\
ユーザーが詰まっている可能性があること・次に取りそうなアクション）

---DEEP_DISPLAY---
（2〜3文。より詳しく把握した状況。「〜してるね。〜しようとしてるのかな。」口調で。）
"""

PRELOAD_PROMPT_IMAGE_ONLY = """\
画面を確認し、以下の形式のみで回答：

---DETAIL---
（アプリ名・ファイル名・表示中のテキスト内容・ユーザーの作業を具体的に。テキストは正確に抽出すること。）

---DISPLAY---
（1文。「今は〜してるね。」口調で。）
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


def _parse_deep_response(text: str) -> tuple[str, str]:
    """DEEP_DETAIL / DEEP_DISPLAY セクションを抽出して返す。"""
    detail = text
    display = text
    if "---DEEP_DETAIL---" in text and "---DEEP_DISPLAY---" in text:
        parts = text.split("---DEEP_DISPLAY---", 1)
        display = parts[1].strip()
        detail_part = parts[0].split("---DEEP_DETAIL---", 1)
        detail = detail_part[1].strip() if len(detail_part) > 1 else text
    return detail, display


@dataclass(frozen=True)
class PreloadResult:
    success: bool
    context_summary: str | None    # 詳細分析（LLMコンテキスト用）
    display_message: str | None    # 短いフレンドリーメッセージ（GUI表示用）
    chat_session: Any | None
    error_message: str | None


@dataclass(frozen=True)
class DeepThinkingResult:
    success: bool
    enriched_context: str | None   # _history 差し替え用（詳細分析）
    display_message: str | None    # context パネル更新用（2〜3文）
    error_message: str | None


class GeminiClient:
    """Gemini API と通信し、画面理解・応答生成を行う（google.genai SDK）。"""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        # 会話履歴: [{"role": "user"/"model", "parts": [{"text": "..."}]}]
        self._history: list[dict] = []
        self._history_lock = threading.Lock()
        logger.debug("GeminiClient initialized: model=%s", model)

    def preload_context(self, image_base64: str) -> PreloadResult:
        """スクリーンショットを送信し、AIに画面状況を事前把握させる。"""
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))
        prompt = PRELOAD_PROMPT_IMAGE_ONLY

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=[prompt, image],
                )
                detail, display = _parse_preload_response(response.text)
                context_text = f"[画面コンテキスト]\n{detail}"
                with self._history_lock:
                    self._history = [
                        {"role": "user", "parts": [{"text": context_text}]},
                        {"role": "model", "parts": [{"text": "画面の内容を確認しました。何かご質問はありますか？"}]},
                    ]
                logger.debug("preload_context succeeded")
                return PreloadResult(success=True, context_summary=detail,
                                     display_message=display,
                                     chat_session=self._history, error_message=None)
            except Exception as e:
                last_error = e
                if type(e).__name__ in RETRYABLE_ERRORS and attempt < MAX_RETRIES:
                    wait = BACKOFF_BASE * (2 ** attempt)
                    logger.warning("preload_context retrying in %.1fs: %s", wait, type(e).__name__)
                    time.sleep(wait)
                else:
                    logger.error("preload_context failed: %s - %s", type(e).__name__, e)
                    with self._history_lock:
                        self._history = []
                    return PreloadResult(success=False, context_summary=None,
                                         display_message=None,
                                         chat_session=None, error_message=str(e))

        with self._history_lock:
            self._history = []
        return PreloadResult(success=False, context_summary=None,
                             display_message=None,
                             chat_session=None, error_message=str(last_error))

    def generate_response(self, user_input: str, chat_session: Any,
                          on_chunk: Any = None) -> str:
        """ユーザー指示を送信し、AI応答テキストを返す（会話履歴付き）。

        on_chunk が指定された場合はストリーミングで返す（リトライなし）。
        """
        with self._history_lock:
            history_snapshot = list(self._history)
        contents = history_snapshot + [
            {"role": "user", "parts": [{"text": user_input}]}
        ]

        if on_chunk is not None:
            # ストリーミングモード
            try:
                full_text = ""
                for chunk in self._client.models.generate_content_stream(
                    model=self._model,
                    contents=contents,
                ):
                    if chunk.text:
                        full_text += chunk.text
                        on_chunk(chunk.text)
                with self._history_lock:
                    self._history = contents + [
                        {"role": "model", "parts": [{"text": full_text}]}
                    ]
                logger.debug("generate_response(stream) succeeded: length=%d", len(full_text))
                return full_text
            except Exception as e:
                logger.error("generate_response(stream) error: %s - %s", type(e).__name__, e)
                raise

        # 通常モード（リトライあり）
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=contents,
                )
                result = response.text
                with self._history_lock:
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

    def deepen_context(self, image_base64: str, stage1_detail: str) -> DeepThinkingResult:
        """Stage 2: thinkingモデルで画面をより深く分析する。

        Stage 1 の結果と同じスクリーンショットを使い、詳細なコンテキストを生成する。
        """
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))
        prompt = DEEP_THINKING_PROMPT.format(stage1_detail=stage1_detail)

        try:
            response = self._client.models.generate_content(
                model=DEEP_THINKING_MODEL,
                contents=[prompt, image],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=DEEP_THINKING_BUDGET)
                ),
            )
            detail, display = _parse_deep_response(response.text)
            enriched = f"[画面コンテキスト（詳細分析）]\n{detail}"
            logger.debug("deepen_context succeeded")
            return DeepThinkingResult(success=True, enriched_context=enriched,
                                      display_message=display, error_message=None)
        except Exception as e:
            logger.error("deepen_context failed: %s - %s", type(e).__name__, e)
            return DeepThinkingResult(success=False, enriched_context=None,
                                      display_message=None, error_message=str(e))

    def update_initial_context(self, enriched_context: str) -> bool:
        """_history[0] のコンテキスト注入部分を差し替える。会話履歴は保持する。"""
        with self._history_lock:
            if not self._history:
                return False
            self._history[0] = {"role": "user", "parts": [{"text": enriched_context}]}
            logger.debug("update_initial_context: context replaced")
            return True

    def create_session(self) -> Any:
        """会話履歴をリセットして新しいセッションを開始。"""
        with self._history_lock:
            self._history = []
        return self._history

    def is_available(self) -> bool:
        try:
            self._client.models.generate_content(model=self._model, contents="test")
            return True
        except Exception:
            return False
