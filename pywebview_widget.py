"""PyWebView フローティングウィジェット

FloatingWidget（CustomTkinter）と同一インターフェースを提供する。
AssistantOrchestrator はこのクラスを FloatingWidget の代替として使用する。
"""

import json
import logging
import threading
from pathlib import Path
from typing import Callable, Any

import webview

logger = logging.getLogger(__name__)

_ASSETS_DIR = Path(__file__).parent / "assets"
_UI_DIR     = Path(__file__).parent / "ui" / "dist"


class _JsApi:
    """JavaScript から呼び出される Python API。"""

    def __init__(self, widget: "PyWebViewWidget") -> None:
        self._widget = widget

    def on_ready(self) -> None:
        """Svelte アプリ起動完了通知。"""
        logger.debug("JS: on_ready")
        self._widget._on_js_ready()

    def submit_text(self, text: str) -> None:
        """ユーザーがテキストを送信。"""
        logger.debug("JS: submit_text: %s", text[:40])
        if self._widget._on_submit_callback:
            threading.Thread(
                target=self._widget._on_submit_callback,
                args=(text,),
                daemon=True,
            ).start()

    def copy_response(self) -> None:
        """コピーボタン押下。"""
        logger.debug("JS: copy_response")
        if self._widget._on_copy_callback:
            self._widget._on_copy_callback()

    def close_session(self) -> None:
        """閉じるボタン押下 → プロセス終了。"""
        logger.debug("JS: close_session → destroy")
        import sys
        if self._widget._window:
            self._widget._window.destroy()
        sys.exit(0)

    def move_window(self, dx: int, dy: int) -> None:
        """ドラッグによるウィンドウ移動。"""
        if self._widget._window:
            w = self._widget._window
            x = w.x + dx
            y = w.y + dy
            w.move(x, y)


class PyWebViewWidget:
    """PyWebView ベースのフローティングアシスタントウィジェット。

    FloatingWidget（CustomTkinter）と同一の公開インターフェースを持つ。
    """

    def __init__(self, config: Any) -> None:
        self._config = config
        self._window: webview.Window | None = None
        self._js_ready = threading.Event()
        self._visible = False
        self._last_response = ""

        self._on_submit_callback: Callable[[str], None] | None = None
        self._on_close_callback:  Callable[[], None]   | None = None
        self._on_copy_callback:   Callable[[], None]   | None = None

        self._api = _JsApi(self)

    def start(self, orchestrator_start_fn: Callable) -> None:
        """PyWebView イベントループを開始（ここでブロック）。

        orchestrator_start_fn は WebView 起動後に別スレッドで呼ばれる。
        """
        wc = self._config.get_widget_config()
        w = wc.width  or 400
        h = wc.height or 560

        # 画面右下に配置
        import tkinter as tk
        root = tk.Tk(); root.withdraw()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.destroy()
        x = wc.x if not wc.is_default() else sw - w - 20
        y = wc.y if not wc.is_default() else sh - h - 60

        self._window = webview.create_window(
            title="Otter",
            url=str(_UI_DIR / "index.html"),
            js_api=self._api,
            width=w,
            height=h,
            x=x,
            y=y,
            resizable=True,
            frameless=False,   # WSL2 では frameless=True が不安定なため False
            on_top=True,
            background_color="#0e0e12",
            min_size=(320, 240),
        )

        # assets/ を静的サーブ（GIF 用）
        def _serve_assets(window):
            pass  # pywebview は file:// で assets にアクセス可能

        def _after_start():
            self._js_ready.wait(timeout=5)
            orchestrator_start_fn()

        threading.Thread(target=_after_start, daemon=True).start()

        webview.start(debug=False)

    def _on_js_ready(self) -> None:
        self._visible = True
        self._js_ready.set()

    # ── FloatingWidget 互換インターフェース ────────────────────────────────

    def show(self) -> None:
        if self._window:
            self._window.show()
            self._visible = True
        logger.debug("PyWebViewWidget shown")

    def hide(self) -> None:
        if self._window:
            self._window.hide()
            self._visible = False
        logger.debug("PyWebViewWidget hidden")

    def is_visible(self) -> bool:
        return self._visible

    def set_state(self, state: str) -> None:
        """状態を JS に通知（IDLE / THINKING / DONE）。"""
        self._js_eval(f"window._otterSetState && window._otterSetState({json.dumps(state)})")
        logger.debug("set_state: %s", state)

    def set_status_message(self, message: str) -> None:
        self._js_eval(f"window._otterSetStatus && window._otterSetStatus({json.dumps(message)})")

    def display_response(self, text: str) -> None:
        self._last_response = text
        self._js_eval(f"window._otterDisplayResponse && window._otterDisplayResponse({json.dumps(text)})")

    def get_last_response(self) -> str:
        return self._last_response

    def after(self, ms: int, callback: Callable) -> None:
        """tkinter.after 互換メソッド。ms 後に callback を別スレッドで実行する。"""
        def _run():
            if ms > 0:
                import time; time.sleep(ms / 1000)
            callback()
        threading.Thread(target=_run, daemon=True).start()

    def on_submit(self, callback: Callable[[str], None]) -> None:
        self._on_submit_callback = callback

    def on_close(self, callback: Callable[[], None]) -> None:
        self._on_close_callback = callback

    def on_copy(self, callback: Callable[[], None]) -> None:
        self._on_copy_callback = callback

    def destroy(self) -> None:
        if self._window:
            self._window.destroy()

    # ── 内部ヘルパー ───────────────────────────────────────────────────────

    def _js_eval(self, script: str) -> None:
        if self._window and self._js_ready.is_set():
            try:
                self._window.evaluate_js(script)
            except Exception as e:
                logger.warning("evaluate_js failed: %s", e)
