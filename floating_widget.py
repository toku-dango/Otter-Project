import logging
from typing import Callable

import customtkinter as ctk

from config_manager import ConfigManager
from otter_animation_controller import AnimationState, OtterAnimationController

logger = logging.getLogger(__name__)

_RESIZE_DEBOUNCE_MS = 500
_COPY_FEEDBACK_MS = 1200
_MIN_WIDTH = 320
_MIN_HEIGHT = 240
_DEFAULT_WIDTH = 400
_DEFAULT_HEIGHT = 560

# ── カラーパレット（ダークモード固定） ─────────────────────────────────────
_BG          = "#0e0e12"   # 背景
_SURFACE     = "#16161d"   # カード面
_SURFACE2    = "#1e1e28"   # 入力欄背景
_BORDER      = "#2a2a38"   # 境界線
_ACCENT      = "#6c63ff"   # アクセント（パープル）
_ACCENT_HOVER= "#857cff"
_TEXT        = "#e8e8f0"   # 本文
_TEXT_SUB    = "#7878a0"   # サブテキスト
_BUBBLE_BG   = "#1e1e2e"   # AI バブル背景
_SEND_BTN    = "#6c63ff"

# マークダウン用CSS
_CSS = f"""
body {{
  font-family: "Segoe UI", "Helvetica Neue", sans-serif;
  font-size: 14px;
  color: {_TEXT};
  background: {_BUBBLE_BG};
  padding: 12px 14px;
  margin: 0;
  line-height: 1.6;
}}
code {{
  background: #2a2a3e;
  border-radius: 4px;
  padding: 2px 6px;
  font-family: "Cascadia Code", "Fira Code", Consolas, monospace;
  font-size: 13px;
  color: #a9b7ff;
}}
pre {{
  background: #13131a;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  border-left: 3px solid {_ACCENT};
}}
a {{ color: #a9b7ff; text-decoration: none; }}
h1, h2, h3 {{ color: #c8c8f0; margin-top: 8px; }}
"""


class FloatingWidget(ctk.CTkToplevel):
    """モダンダークUIのフローティングアシスタントウィジェット。"""

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

    # ── ウィンドウ設定 ──────────────────────────────────────────────────────

    def _setup_window(self) -> None:
        self.configure(fg_color=_BG)
        self.wm_attributes("-topmost", True)
        self.wm_attributes("-alpha", 0.97)
        self.resizable(True, True)
        self.minsize(_MIN_WIDTH, _MIN_HEIGHT)
        self.title("Otter")
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

    # ── UI 構築 ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_response_area()
        self._build_input_area()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, height=72, fg_color=_SURFACE, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)

        # Otter アニメーション
        self._otter_label = ctk.CTkLabel(
            header, text="", width=120, height=64, fg_color="transparent"
        )
        self._otter_label.grid(row=0, column=0, padx=(6, 0), pady=4)
        self._animation_ctrl._label = self._otter_label
        self._animation_ctrl.play(AnimationState.IDLE)

        # タイトル＋ステータス（縦積み）
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="w", padx=4)

        ctk.CTkLabel(
            title_frame, text="Otter", font=ctk.CTkFont(size=15, weight="bold"),
            text_color=_TEXT, fg_color="transparent"
        ).pack(anchor="w")

        self._status_label = ctk.CTkLabel(
            title_frame, text="Ready", font=ctk.CTkFont(size=11),
            text_color=_TEXT_SUB, fg_color="transparent"
        )
        self._status_label.pack(anchor="w")

        # 最小化ボタン
        self._minimize_btn = ctk.CTkButton(
            header, text="▼", width=32, height=32,
            fg_color="transparent", hover_color=_BORDER,
            text_color=_TEXT_SUB, font=ctk.CTkFont(size=11),
            command=self._toggle_minimize,
        )
        self._minimize_btn.grid(row=0, column=2, padx=(0, 8), pady=4)

        # ドラッグ
        for widget in (header, self._otter_label, title_frame):
            widget.bind("<ButtonPress-1>", self._on_drag_start)
            widget.bind("<B1-Motion>", self._on_drag_motion)
            widget.bind("<ButtonRelease-1>", self._on_drag_release)

    def _build_response_area(self) -> None:
        """応答表示エリア（マークダウン対応）。"""
        outer = ctk.CTkFrame(self, fg_color=_BUBBLE_BG, corner_radius=0)
        outer.grid(row=1, column=0, sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        try:
            from tkinterweb import HtmlFrame
            self._response_area = HtmlFrame(outer, messages_enabled=False, background=_BUBBLE_BG)
            self._use_html = True
            logger.debug("Using tkinterweb for markdown rendering")
        except Exception:
            self._response_area = ctk.CTkTextbox(
                outer, state="disabled", wrap="word",
                fg_color=_BUBBLE_BG, text_color=_TEXT,
                font=ctk.CTkFont(size=14), border_width=0,
                scrollbar_button_color=_BORDER,
            )
            self._use_html = False
            logger.debug("Using CTkTextbox as fallback renderer")

        self._response_area.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

    def _build_input_area(self) -> None:
        """入力エリア（区切り線あり）。"""
        # 区切り線
        sep = ctk.CTkFrame(self, height=1, fg_color=_BORDER, corner_radius=0)
        sep.grid(row=2, column=0, sticky="ew")

        # 入力パネル
        panel = ctk.CTkFrame(self, fg_color=_SURFACE, corner_radius=0)
        panel.grid(row=3, column=0, sticky="ew")
        panel.grid_columnconfigure(0, weight=1)

        # コピーボタン（初期非表示）
        self._copy_btn = ctk.CTkButton(
            panel, text="Copy response", height=24,
            fg_color="transparent", hover_color=_BORDER,
            text_color=_TEXT_SUB, font=ctk.CTkFont(size=11),
            border_width=1, border_color=_BORDER,
            command=self._on_copy_clicked,
        )
        self._copy_btn.grid(row=0, column=0, padx=12, pady=(8, 0), sticky="w")
        self._copy_btn.grid_remove()

        # テキスト入力
        self._input_field = ctk.CTkTextbox(
            panel, height=80, wrap="word",
            fg_color=_SURFACE2, text_color=_TEXT,
            font=ctk.CTkFont(size=14), border_width=1,
            border_color=_BORDER, corner_radius=10,
            scrollbar_button_color=_BORDER,
        )
        self._input_field.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        self._input_field.bind("<Return>", self._on_enter_key)

        # 送信ボタン
        self._send_btn = ctk.CTkButton(
            panel, text="Send  ↵", width=90, height=36,
            fg_color=_ACCENT, hover_color=_ACCENT_HOVER,
            text_color="#ffffff", font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=18,
            command=self._on_send,
        )
        self._send_btn.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="e")

    # ── 公開メソッド ───────────────────────────────────────────────────────

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
        anim_map = {
            "IDLE": AnimationState.IDLE,
            "THINKING": AnimationState.THINKING,
            "DONE": AnimationState.DONE,
        }
        if state in anim_map:
            self._animation_ctrl.play(anim_map[state])

        is_thinking = state == "THINKING"
        ui_state = "disabled" if is_thinking else "normal"
        self._input_field.configure(state=ui_state)
        self._send_btn.configure(state=ui_state)

        if state == "DONE":
            self._copy_btn.grid()
        elif state == "IDLE":
            self._copy_btn.grid_remove()

    def set_status_message(self, message: str) -> None:
        self._status_label.configure(text=message)

    def display_response(self, text: str) -> None:
        self._last_response = text
        if self._use_html:
            try:
                import markdown
                html = markdown.markdown(
                    text, extensions=["fenced_code", "tables", "nl2br"]
                )
                self._response_area.load_html(
                    f"<style>{_CSS}</style><body>{html}</body>"
                )
                return
            except Exception as e:
                logger.warning("Markdown render failed: %s", type(e).__name__)

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

    # ── 内部イベント ───────────────────────────────────────────────────────

    def _on_enter_key(self, event) -> str:
        if event.state & 0x1:
            return ""
        self._on_send()
        return "break"

    def _on_send(self) -> None:
        text = self._input_field.get("0.0", "end").strip()
        if not text:
            return
        self._input_field.delete("0.0", "end")
        if self._on_submit_callback:
            self._on_submit_callback(text)

    def _on_copy_clicked(self) -> None:
        self._copy_btn.configure(text="Copied!")
        self.after(_COPY_FEEDBACK_MS, lambda: self._copy_btn.configure(text="Copy response"))
        if self._on_copy_callback:
            self._on_copy_callback()

    def _toggle_minimize(self) -> None:
        if self._is_minimized:
            self.geometry(f"{self.winfo_width()}x{_DEFAULT_HEIGHT}")
            self._minimize_btn.configure(text="▼")
            self._is_minimized = False
        else:
            self.geometry(f"{self.winfo_width()}x74")
            self._minimize_btn.configure(text="▲")
            self._is_minimized = True

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

    def _on_configure(self, event) -> None:
        if self._resize_debounce_id:
            self.after_cancel(self._resize_debounce_id)
        self._resize_debounce_id = self.after(_RESIZE_DEBOUNCE_MS, self._save_geometry)

    def _save_geometry(self) -> None:
        self._config.set_setting("widget_width", self.winfo_width())
        self._config.set_setting("widget_height", self.winfo_height())
        self._resize_debounce_id = None
