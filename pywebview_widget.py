"""PyWebView フローティングウィジェット

FloatingWidget（CustomTkinter）と同一インターフェースを提供する。
AssistantOrchestrator はこのクラスを FloatingWidget の代替として使用する。

【通信方式】
  Python→JS: evaluate_js はバックグラウンドスレッドから呼ぶと
             Windows/EdgeWebView2 でデッドロックするため使用しない。
             代わりに JS 側が get_pending_update() を定期 polling する。
  JS→Python: pywebview.api.* 経由（通常通り）
"""

import logging
import queue
import threading
from pathlib import Path
from typing import Callable, Any

import webview

logger = logging.getLogger(__name__)

_UI_DIR = Path(__file__).parent / "ui" / "dist"


class _JsApi:
    """JavaScript から呼び出される Python API。"""

    def __init__(self, widget: "PyWebViewWidget") -> None:
        self._widget = widget

    def on_ready(self) -> None:
        """Svelte アプリ起動完了通知。"""
        logger.debug("JS: on_ready")
        self._widget._on_js_ready()

    def get_pending_update(self) -> dict | None:
        """JS が polling で呼び出す：保留中の状態更新を1件返す。"""
        try:
            return self._widget._pending_queue.get_nowait()
        except queue.Empty:
            return None

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

    def minimize_window(self) -> None:
        """最小化ボタン押下 → ウィジェットを最小化モードへ。"""
        logger.debug("JS: minimize_window")
        self._widget.minimize()

    def restore_window(self) -> None:
        """最小化モードのクリック → フルサイズに復帰。"""
        logger.debug("JS: restore_window")
        self._widget.show()

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
        self._pending_queue: queue.SimpleQueue = queue.SimpleQueue()

        self._minimized: bool = False
        self._screen_w: int = 1920
        self._screen_h: int = 1080
        # 復元用にウィンドウ初期ジオメトリをキャッシュ
        self._restore_x: int = 0
        self._restore_y: int = 0
        self._restore_w: int = 420
        self._restore_h: int = 740

        self._on_submit_callback: Callable[[str], None] | None = None
        self._on_close_callback:  Callable[[], None]   | None = None
        self._on_copy_callback:   Callable[[], None]   | None = None

        self._api = _JsApi(self)

    def start(self, orchestrator_start_fn: Callable) -> None:
        """PyWebView イベントループを開始（ここでブロック）。"""
        wc = self._config.get_widget_config()
        w = wc.width  or 420
        h = wc.height or 740

        import tkinter as tk
        root = tk.Tk(); root.withdraw()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.destroy()
        self._screen_w, self._screen_h = sw, sh
        x = wc.x if not wc.is_default() else sw - w - 20
        y = wc.y if not wc.is_default() else sh - h - 60
        self._restore_x, self._restore_y, self._restore_w, self._restore_h = x, y, w, h

        self._window = webview.create_window(
            title="Otter",
            url=str(_UI_DIR / "index.html"),
            js_api=self._api,
            width=w,
            height=h,
            x=x,
            y=y,
            resizable=True,
            frameless=False,
            on_top=True,
            background_color="#0e0e12",
            min_size=(280, 60),
        )

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
        """フルサイズに戻す。最小化モードからの復帰時はウィンドウを元のサイズに戻す。"""
        if self._window and self._minimized:
            # move→resize の順：小さいウィンドウをまず目標位置に動かしてから拡大
            self._window.move(self._restore_x, self._restore_y)
            self._window.resize(self._restore_w, self._restore_h)
        self._visible = True
        self._minimized = False
        self._pending_queue.put({"type": "minimize_mode", "value": False})
        logger.debug("PyWebViewWidget shown (full)")

    def hide(self) -> None:
        if self._window:
            self._window.hide()
            self._visible = False
        logger.debug("PyWebViewWidget hidden")

    def minimize(self) -> None:
        """ウィンドウを左下の小さいサイズに縮小し、最小化モードへ。
        hide() ではなく resize() を使うことで JS コンテンツが生き続ける。
        move→resize の順：大きいウィンドウをまず目標位置に動かしてから縮小。
        """
        if self._window:
            _, sh = self._screen_size()
            mini_y = sh - 140  # タスクバー考慮（40px）+ 余裕（28px）
            self._window.move(20, mini_y)
            self._window.resize(360, 72)
        self._visible = False
        self._minimized = True
        self._pending_queue.put({"type": "minimize_mode", "value": True})
        logger.debug("PyWebViewWidget minimized (toast mode)")

    def _screen_size(self) -> tuple[int, int]:
        """start() でキャッシュした画面サイズを返す。"""
        return self._screen_w, self._screen_h

    def is_visible(self) -> bool:
        return self._visible

    def is_minimized(self) -> bool:
        return self._minimized

    def set_state(self, state: str) -> None:
        """状態更新をキューに積む（IDLE / THINKING / DONE）。"""
        self._pending_queue.put({"type": "state", "value": state})
        logger.debug("set_state: %s (queued)", state)

    def set_status_message(self, message: str) -> None:
        """ステータスメッセージ更新をキューに積む。"""
        self._pending_queue.put({"type": "status", "value": message})

    def show_context_loading(self) -> None:
        """画面分析中アニメーションをキューに積む。"""
        self._pending_queue.put({"type": "context_loading"})

    def show_ai_thinking(self) -> None:
        """AI思考中バブルをキューに積む。"""
        self._pending_queue.put({"type": "ai_thinking"})

    def display_user_message(self, text: str) -> None:
        """ユーザーメッセージをキューに積む（チャット表示用）。"""
        self._pending_queue.put({"type": "user_message", "value": text})

    def display_response(self, text: str) -> None:
        """AI応答テキストをキューに積む（非ストリーミング用）。"""
        self._last_response = text
        self._pending_queue.put({"type": "ai_message", "value": text})
        logger.debug("display_response: length=%d (queued)", len(text))

    def start_response_stream(self) -> None:
        """ストリーミング開始を通知（表示をリセット）。"""
        self._last_response = ""
        self._pending_queue.put({"type": "ai_stream_start"})

    def append_response_chunk(self, chunk: str) -> None:
        """ストリーミングチャンクをキューに積む。"""
        self._last_response += chunk
        self._pending_queue.put({"type": "ai_chunk", "value": chunk})

    def show_toast(self, text: str) -> None:
        """トースト通知をキューに積む（最小化モード用）。"""
        self._pending_queue.put({"type": "toast", "value": text})
        logger.debug("show_toast: length=%d (queued)", len(text))

    def set_context_summary(self, text: str) -> None:
        """画面分析結果をキューに積む（上パネル表示用）。"""
        self._pending_queue.put({"type": "context", "value": text})
        logger.debug("set_context_summary: length=%d (queued)", len(text))

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
