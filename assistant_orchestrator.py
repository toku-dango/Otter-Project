import logging
import threading
from typing import Any

from gemini_client import GeminiClient
from hotkey_manager import HotkeyManager
from screen_capture_service import ScreenCaptureService
from session_manager import SessionManager

logger = logging.getLogger(__name__)

# ユーザー向けエラーメッセージ（BR-09）
ERROR_MESSAGES = {
    "auth": "Googleアカウントへのログインが必要です。アプリを再起動してログインしてください。",
    "timeout": "応答がタイムアウトしました。ネットワークをご確認ください。",
    "rate_limit": "利用制限に達しました。しばらく待ってからお試しください。",
    "capture": "画面取得に失敗しました。テキスト入力で相談できます。",
    "network": "ネットワークエラーが発生しました。接続をご確認ください。",
    "response": "応答の生成に失敗しました。もう一度お試しください。",
    "unknown": "エラーが発生しました。アプリを再起動してください。",
}


class AssistantOrchestrator:
    """全コンポーネントを束ねるFacade（PAT-04）。

    ホットキー起動からAI応答表示までのイベントフローを制御する。
    バックグラウンドスレッドとUIスレッドの橋渡しを担う（PAT-02）。
    """

    def __init__(
        self,
        hotkey: HotkeyManager,
        capture: ScreenCaptureService,
        gemini: GeminiClient,
        session_mgr: SessionManager,
        widget: Any,       # FloatingWidget（Unit 2）
        config: Any,       # ConfigManager（Unit 2）
        clipboard: Any,    # ClipboardService（Unit 2）
    ) -> None:
        self._hotkey = hotkey
        self._capture = capture
        self._gemini = gemini
        self._session_mgr = session_mgr
        self._widget = widget
        self._config = config
        self._clipboard = clipboard
        self._session = None
        self._is_processing = False

    def start(self) -> None:
        """アプリケーション起動。永続セッション開始・ホットキー登録。"""
        self._session = self._session_mgr.start_session()
        self._hotkey.register(callback=self._on_hotkey_triggered_from_pynput)
        logger.debug("AssistantOrchestrator started: session_id=%s", self._session.session_id)

    def stop(self) -> None:
        """アプリケーション終了。ホットキー解除・セッション終了（PAT-06）。"""
        self._hotkey.unregister()
        if self._session:
            self._session_mgr.end_session(self._session.session_id)
        logger.debug("AssistantOrchestrator stopped")

    def _on_hotkey_triggered_from_pynput(self) -> None:
        """pynput スレッドから呼ばれるホットキーコールバック。UIスレッドに委譲（PAT-02）。"""
        self._widget.after(0, self.on_hotkey_triggered)

    def on_hotkey_triggered(self) -> None:
        """ホットキー押下イベント処理（UIスレッドで実行）。

        常に画面キャプチャ → Gemini状況把握 → 上パネルに表示。
        ウィジェットが非表示なら表示する。
        """
        if not self._widget.is_visible():
            self._widget.show()

        self._widget.set_state("THINKING")
        self._widget.set_status_message("画面を確認中...")

        threading.Thread(target=self._preload_worker, daemon=True).start()

    def _preload_worker(self) -> None:
        """バックグラウンドスレッド: キャプチャ → Gemini事前把握（PAT-02）。"""
        capture_result = self._capture.capture()

        if not capture_result.success:
            logger.warning("Capture failed: %s", capture_result.error_message)
            self._widget.after(
                0,
                lambda: self._on_preload_done(success=False, chat=None, summary=None),
            )
            return

        preload_result = self._gemini.preload_context(capture_result.image_base64)
        self._widget.after(
            0,
            lambda: self._on_preload_done(
                success=preload_result.success,
                chat=preload_result.chat_session,
                summary=preload_result.context_summary,
                display_message=preload_result.display_message,
            ),
        )

    def _on_preload_done(self, success: bool, chat: Any, summary: str | None,
                         display_message: str | None = None) -> None:
        """UIスレッド: 事前把握完了後の状態更新（PAT-02）。"""
        if success and chat is not None:
            self._session.chat_session = chat
            if summary:
                self._session_mgr.update_preload_summary(self._session.session_id, summary)
            if display_message:
                self._widget.set_context_summary(display_message)
            self._widget.set_state("IDLE")
            self._widget.set_status_message("画面を確認しました ✓")
        else:
            self._widget.set_state("IDLE")
            self._widget.set_status_message(ERROR_MESSAGES["capture"])

    def on_user_input(self, text: str) -> None:
        """ユーザーテキスト送信イベント（FL-04）。

        空文字・処理中の場合はガードして早期リターン（BR-08）。
        """
        if not text.strip():
            logger.debug("on_user_input: empty input, ignored")
            return
        if self._is_processing:
            logger.debug("on_user_input: already processing, ignored")
            return

        self._is_processing = True
        self._widget.set_state("THINKING")
        self._widget.set_status_message("考え中...")

        threading.Thread(
            target=self._generate_worker, args=(text,), daemon=True
        ).start()

    def _generate_worker(self, text: str) -> None:
        """バックグラウンドスレッド: Gemini応答生成（PAT-02）。"""
        chat = self._session.chat_session if self._session else None
        if chat is None:
            chat = self._gemini.create_session()
            if self._session:
                self._session.chat_session = chat

        try:
            response_text = self._gemini.generate_response(text, chat)
            if self._session:
                self._session_mgr.add_exchange(
                    self._session.session_id, text, response_text
                )
            self._widget.after(
                0, lambda: self._on_response_done(success=True, response=response_text)
            )
        except Exception as e:
            logger.error("generate_response error: %s", type(e).__name__)
            self._widget.after(
                0, lambda: self._on_response_done(success=False, response=None)
            )

    def _on_response_done(self, success: bool, response: str | None) -> None:
        """UIスレッド: 応答生成完了後の状態更新（PAT-02）。"""
        self._is_processing = False
        if success and response:
            self._widget.set_state("DONE")
            self._widget.display_response(response)
        else:
            self._widget.set_state("IDLE")
            self._widget.set_status_message(ERROR_MESSAGES["response"])

    def on_copy_requested(self) -> None:
        """コピーボタン押下イベント。最後の応答テキストをクリップボードにコピー。"""
        text = self._widget.get_last_response()
        if text:
            self._clipboard.copy(text)

    def on_session_close(self) -> None:
        """ウィジェット閉じるイベント。セッション履歴は保持（BR-05）。"""
        self._widget.hide()
        logger.debug("Widget hidden, session continues: session_id=%s", self._session.session_id if self._session else "none")

    def _handle_error(self, error: Exception, context: str) -> None:
        """エラー種別を判定し、UIへ日本語メッセージを表示する（BR-09）。"""
        from google.api_core import exceptions as gex
        error_type = type(error)

        if issubclass(error_type, gex.Unauthenticated):
            msg = ERROR_MESSAGES["auth"]
        elif issubclass(error_type, (TimeoutError, gex.DeadlineExceeded)):
            msg = ERROR_MESSAGES["timeout"]
        elif issubclass(error_type, gex.ResourceExhausted):
            msg = ERROR_MESSAGES["rate_limit"]
        elif issubclass(error_type, ConnectionError):
            msg = ERROR_MESSAGES["network"]
        else:
            msg = ERROR_MESSAGES["unknown"]

        logger.error("Error in %s: %s - %s", context, error_type.__name__, str(error))
        self._widget.set_status_message(msg)
        self._widget.set_state("IDLE")
