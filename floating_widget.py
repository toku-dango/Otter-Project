import logging
from typing import Callable

import customtkinter as ctk

from config_manager import ConfigManager
from otter_animation_controller import AnimationState, OtterAnimationController

logger = logging.getLogger(__name__)

_RESIZE_DEBOUNCE_MS = 500
_COPY_FEEDBACK_MS = 1000
_MIN_WIDTH = 300
_MIN_HEIGHT = 200
_DEFAULT_WIDTH = 400
_DEFAULT_HEIGHT = 500

# マークダウンレンダリング用 CSS（テーマ別）
_DARK_CSS = """
body { font-family: "Yu Gothic","Meiryo",sans-serif; font-size:14px;
       color:#EBEBEB; background:#2B2B2B; padding:8px; margin:0; }
code { background:#3C3C3C; border-radius:3px; padding:2px 4px;
       font-family:Consolas,monospace; }
pre  { background:#3C3C3C; padding:8px; border-radius:4px; overflow-x:auto; }
a    { color:#6AB0F5; }
"""
_LIGHT_CSS = """
body { font-family: "Yu Gothic","Meiryo",sans-serif; font-size:14px;
       color:#1A1A1A; background:#F0F0F0; padding:8px; margin:0; }
code { background:#E0E0E0; border-radius:3px; padding:2px 4px;
       font-family:Consolas,monospace; }
pre  { background:#E0E0E0; padding:8px; border-radius:4px; overflow-x:auto; }
a    { color:#1A6AAF; }
"""


class FloatingWidget(ctk.CTkToplevel):
    """常時最前面に表示されるフローティングUIウィジェット（Unit 2 中核コンポーネント）。

    PAT-U2-01: tkinterweb → CTkTextbox フォールバック
    PAT-U2-04: リサイズ debounce
    PAT-U2-05: Observer コールバック
    PAT-U2-07: System Theme Bridge
    BR-U2-01〜08 全ルール準拠
    """

    def __init__(self, animation_ctrl: OtterAnimationController, config: ConfigManager) -> None:
        super().__init__()
        self._animation_ctrl = animation_ctrl
        self._config = config
        self._is_minimized = False
        self._last_response = ""
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._resize_debounce_id: str | None = None
        self._on_submit_callback: Callable[[str], None] | None = None
        self._on_close_callback: Callable[[], None] | None = None
        self._on_copy_callback: Callable[[], None] | None = None
        self._use_html = False

        self._setup_window()
        self._build_ui()
        self._restore_geometry()

    # ── ウィンドウ設定 ──────────────────────────────────────────────────

    def _setup_window(self) -> None:
        # self.overrideredirect(True)         # タイトルバーなし（WSLg互換性のため一時無効）
        self.wm_attributes("-topmost", True)  # 常時最前面（BR-U2-07）
        self.wm_attributes("-alpha", 0.95)    # 半透明
        self.resizable(True, True)            # リサイズ可能（BR-U2-02）
        self.minsize(_MIN_WIDTH, _MIN_HEIGHT)
        self.bind("<Configure>", self._on_configure)

    def _restore_geometry(self) -> None:
        wc = self._config.get_widget_config()
        w = wc.width or _DEFAULT_WIDTH
        h = wc.height or _DEFAULT_HEIGHT
        if wc.is_default():
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x = sw - w - 20
            y = sh - h - 60
        else:
            x, y = wc.x, wc.y
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── UI 構築 ─────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_response_area()
        self._build_copy_button()
        self._build_input_area()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, height=44, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)

        # Otter 表示（アニメーション or プレースホルダー）
        self._otter_label = ctk.CTkLabel(header, text="🦦", width=40, font=("", 22))
        self._otter_label.grid(row=0, column=0, padx=(8, 0), pady=4)
        self._animation_ctrl._label = self._otter_label  # ラベルを渡す

        # ステータスラベル
        self._status_label = ctk.CTkLabel(
            header, text="", anchor="w", font=("Yu Gothic", 12)
        )
        self._status_label.grid(row=0, column=1, padx=8, sticky="ew")

        # 最小化ボタン
        self._minimize_btn = ctk.CTkButton(
            header, text="▼", width=32, height=32,
            command=self._toggle_minimize,
        )
        self._minimize_btn.grid(row=0, column=2, padx=(0, 8), pady=4)

        # ドラッグバインド（ヘッダー領域のみ）（BR-U2-01）
        for widget in (header, self._otter_label, self._status_label):
            widget.bind("<ButtonPress-1>", self._on_drag_start)
            widget.bind("<B1-Motion>", self._on_drag_motion)
            widget.bind("<ButtonRelease-1>", self._on_drag_release)

    def _build_response_area(self) -> None:
        """PAT-U2-01: tkinterweb → CTkTextbox フォールバック。"""
        try:
            from tkinterweb import HtmlFrame
            self._response_area = HtmlFrame(self, messages_enabled=False)
            self._use_html = True
            logger.debug("Using tkinterweb for markdown rendering")
        except Exception:
            self._response_area = ctk.CTkTextbox(self, state="disabled", wrap="word")
            self._use_html = False
            logger.debug("Using CTkTextbox as fallback renderer")

        self._response_area.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 0))

    def _build_copy_button(self) -> None:
        self._copy_btn = ctk.CTkButton(
            self, text="コピー", height=28, command=self._on_copy_clicked,
        )
        self._copy_btn.grid(row=2, column=0, padx=8, pady=4, sticky="e")
        self._copy_btn.grid_remove()  # 初期非表示

    def _build_input_area(self) -> None:
        frame = ctk.CTkFrame(self, corner_radius=0)
        frame.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))
        frame.grid_columnconfigure(0, weight=1)

        self._input_field = ctk.CTkTextbox(frame, height=60, wrap="word")
        self._input_field.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        # Enter → 送信 / Shift+Enter → 改行（BR-U2-05）
        self._input_field.bind("<Return>", self._on_enter_key)

        self._send_btn = ctk.CTkButton(frame, text="送信", width=60, command=self._on_send)
        self._send_btn.grid(row=0, column=1)

    # ── 公開メソッド（Unit 1 インターフェース契約）──────────────────────

    def show(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()
        self._input_field.delete("0.0", "end")
        logger.debug("FloatingWidget shown")

    def hide(self) -> None:
        self.withdraw()
        logger.debug("FloatingWidget hidden")

    def is_visible(self) -> bool:
        return self.winfo_viewable() == 1

    def set_state(self, state: str) -> None:
        """状態切替: "IDLE" / "THINKING" / "DONE"（FL-05）。"""
        anim_map = {
            "IDLE": AnimationState.IDLE,
            "THINKING": AnimationState.THINKING,
            "DONE": AnimationState.DONE,
        }
        if state in anim_map:
            self._animation_ctrl.play(anim_map[state])

        is_thinking = state == "THINKING"
        input_state = "disabled" if is_thinking else "normal"
        self._input_field.configure(state=input_state)
        self._send_btn.configure(state=input_state)

        if state == "DONE":
            self._copy_btn.grid()
        elif state == "IDLE":
            self._copy_btn.grid_remove()

    def set_status_message(self, message: str) -> None:
        self._status_label.configure(text=message)

    def display_response(self, text: str) -> None:
        """マークダウンをレンダリングして表示する（FL-06）。"""
        self._last_response = text
        if self._use_html:
            try:
                import markdown
                css = _DARK_CSS if ctk.get_appearance_mode() == "Dark" else _LIGHT_CSS
                html = markdown.markdown(
                    text, extensions=["fenced_code", "tables", "nl2br"]
                )
                self._response_area.load_html(f"<style>{css}</style><body>{html}</body>")
                return
            except Exception as e:
                logger.warning("Markdown render failed, fallback to plain: %s", type(e).__name__)

        # プレーンテキストフォールバック
        self._response_area.configure(state="normal")
        self._response_area.delete("0.0", "end")
        self._response_area.insert("0.0", text)
        self._response_area.configure(state="disabled")

    def get_last_response(self) -> str:
        return self._last_response

    def on_submit(self, callback: Callable[[str], None]) -> None:
        self._on_submit_callback = callback

    def on_close(self, callback: Callable[[], None]) -> None:
        self._on_close_callback = callback

    def on_copy(self, callback: Callable[[], None]) -> None:
        self._on_copy_callback = callback

    # ── 内部イベントハンドラ ─────────────────────────────────────────────

    def _on_enter_key(self, event) -> str:
        if event.state & 0x1:  # Shift が押されている → 改行（BR-U2-05）
            return ""
        self._on_send()
        return "break"  # デフォルトの改行を抑制

    def _on_send(self) -> None:
        text = self._input_field.get("0.0", "end").strip()
        if not text:
            return
        self._input_field.delete("0.0", "end")
        if self._on_submit_callback:
            self._on_submit_callback(text)

    def _on_copy_clicked(self) -> None:
        """コピーフィードバック（BR-U2-06）。"""
        self._copy_btn.configure(text="✓ コピーしました")
        self.after(_COPY_FEEDBACK_MS, lambda: self._copy_btn.configure(text="コピー"))
        if self._on_copy_callback:
            self._on_copy_callback()

    def _toggle_minimize(self) -> None:
        """最小化・復元トグル（FL-08）。"""
        if self._is_minimized:
            self.geometry(f"{self.winfo_width()}x{_DEFAULT_HEIGHT}")
            self._minimize_btn.configure(text="▼")
            self._is_minimized = False
        else:
            self.geometry(f"{self.winfo_width()}x50")
            self._minimize_btn.configure(text="▲")
            self._is_minimized = True

    # ── ドラッグ（BR-U2-01）────────────────────────────────────────────

    def _on_drag_start(self, event) -> None:
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_drag_motion(self, event) -> None:
        x = self.winfo_x() + event.x - self._drag_start_x
        y = self.winfo_y() + event.y - self._drag_start_y
        self.geometry(f"+{x}+{y}")

    def _on_drag_release(self, event) -> None:
        self._config.set_setting("widget_x", self.winfo_x())
        self._config.set_setting("widget_y", self.winfo_y())

    # ── リサイズ debounce（PAT-U2-04）───────────────────────────────────

    def _on_configure(self, event) -> None:
        if self._resize_debounce_id:
            self.after_cancel(self._resize_debounce_id)
        self._resize_debounce_id = self.after(_RESIZE_DEBOUNCE_MS, self._save_geometry)

    def _save_geometry(self) -> None:
        self._config.set_setting("widget_width", self.winfo_width())
        self._config.set_setting("widget_height", self.winfo_height())
        self._resize_debounce_id = None
