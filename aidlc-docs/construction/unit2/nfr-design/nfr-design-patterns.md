# NFR Design Patterns — Unit 2: UI & Configuration

## パターン一覧

| パターン ID | パターン名 | 対応 NFR | 適用コンポーネント |
|---|---|---|---|
| PAT-U2-01 | Fallback Chain（レンダラー） | REL-U2-01 | FloatingWidget |
| PAT-U2-02 | Fallback Chain（アニメーション） | REL-U2-02 | OtterAnimationController |
| PAT-U2-03 | Fallback Chain（設定ファイル） | REL-U2-03 | ConfigManager |
| PAT-U2-04 | Debounce（リサイズ保存） | MAINT-U2-01, PERF-U2-01 | FloatingWidget |
| PAT-U2-05 | Observer（コールバック） | — | FloatingWidget |
| PAT-U2-06 | Null Object（クリップボード） | REL-U2-04 | ClipboardService |
| PAT-U2-07 | System Theme Bridge | UX-U2-01 | main.py / FloatingWidget |

---

## PAT-U2-01: Fallback Chain（マークダウンレンダラー）

**対応 NFR**: REL-U2-01（tkinterweb 失敗時のフォールバック）

```python
def _create_response_area(self, parent):
    """tkinterweb が利用可能なら HtmlFrame、なければ CTkTextbox にフォールバック。"""
    try:
        from tkinterweb import HtmlFrame
        self._response_area = HtmlFrame(parent, messages_enabled=False)
        self._use_html = True
    except ImportError:
        self._response_area = ctk.CTkTextbox(parent, state="disabled", wrap="word")
        self._use_html = False

def display_response(self, text: str) -> None:
    if self._use_html:
        import markdown
        html = markdown.markdown(text, extensions=["fenced_code", "tables", "nl2br"])
        self._response_area.load_html(f"<style>{self._get_css()}</style>{html}")
    else:
        # プレーンテキストフォールバック
        self._response_area.configure(state="normal")
        self._response_area.delete("0.0", "end")
        self._response_area.insert("0.0", text)
        self._response_area.configure(state="disabled")
```

---

## PAT-U2-02: Fallback Chain（Otter アニメーション）

**対応 NFR**: REL-U2-02（GIF ファイル不在・破損時のフォールバック）

```python
PLACEHOLDER = {
    AnimationState.IDLE:     "🦦",
    AnimationState.THINKING: "🦦💭",
    AnimationState.DONE:     "🦦✨",
}

def play(self, state: AnimationState) -> None:
    self._stop_current()
    if self._try_load_gif(state):
        self._start_gif_animation(state)
    else:
        # プレースホルダーにフォールバック
        self._label.configure(text=PLACEHOLDER[state], image=None)
        if state == AnimationState.DONE:
            self._label.after(2000, lambda: self.play(AnimationState.IDLE))

def _try_load_gif(self, state: AnimationState) -> bool:
    """GIF の読み込みを試みる。失敗したら False を返す。"""
    gif_path = Path(self._assets_dir) / f"{state.value}.gif"
    if not gif_path.exists():
        return False
    try:
        self._load_frames(state, gif_path)
        return True
    except Exception:
        return False
```

---

## PAT-U2-03: Fallback Chain（設定ファイル）

**対応 NFR**: REL-U2-03（config.json 破損時のデフォルト起動）

```python
def _load_config(self) -> AppConfig:
    """設定ファイルを読み込む。失敗時はデフォルト設定を返す。"""
    try:
        if self._config_path.exists():
            data = json.loads(self._config_path.read_text(encoding="utf-8"))
            return AppConfig(**data)
    except Exception as e:
        logger.warning("config.json load failed, using defaults: %s", type(e).__name__)
    return AppConfig()  # デフォルト設定
```

---

## PAT-U2-04: Debounce（リサイズ保存）

**対応 NFR**: PERF-U2-01（リサイズ中の過剰なファイル書き込みを防ぐ）

```python
_RESIZE_DEBOUNCE_MS = 500

def _on_configure(self, event) -> None:
    """<Configure> イベントは連続して発火するため、debounce で書き込みを間引く。"""
    if self._resize_debounce_id:
        self.after_cancel(self._resize_debounce_id)
    self._resize_debounce_id = self.after(
        _RESIZE_DEBOUNCE_MS, self._save_geometry
    )

def _save_geometry(self) -> None:
    self._config.set_setting("widget_width", self.winfo_width())
    self._config.set_setting("widget_height", self.winfo_height())
    self._resize_debounce_id = None
```

---

## PAT-U2-05: Observer（コールバック）

**対応 NFR**: — （Unit 1 との疎結合を維持）

```python
class FloatingWidget:
    def on_submit(self, callback: Callable[[str], None]) -> None:
        self._on_submit_callback = callback

    def on_close(self, callback: Callable[[], None]) -> None:
        self._on_close_callback = callback

    def on_copy(self, callback: Callable[[], None]) -> None:
        self._on_copy_callback = callback

    def _on_send_clicked(self) -> None:
        text = self._input_field.get("0.0", "end").strip()
        if text and self._on_submit_callback:
            self._input_field.delete("0.0", "end")
            self._on_submit_callback(text)
```

---

## PAT-U2-06: Null Object（ClipboardService）

**対応 NFR**: REL-U2-04（クリップボード失敗時にアプリをクラッシュさせない）

```python
class ClipboardService:
    def copy(self, text: str) -> bool:
        """成功時 True、失敗時 False を返す。例外は外部に伝播しない。"""
        try:
            pyperclip.copy(text)
            logger.debug("Clipboard copy succeeded: length=%d", len(text))
            return True
        except Exception as e:
            logger.error("Clipboard copy failed: %s", type(e).__name__)
            return False
```

---

## PAT-U2-07: System Theme Bridge

**対応 NFR**: UX-U2-01（Windows ダーク/ライトテーマへの自動追従）

```python
# main.py での設定（起動時に1回のみ呼び出す）
import customtkinter as ctk
ctk.set_appearance_mode("system")   # Windows のテーマを検出
ctk.set_default_color_theme("blue")

# tkinterweb の CSS もテーマに合わせて動的に切替
def _get_css(self) -> str:
    mode = ctk.get_appearance_mode()  # "Dark" or "Light"
    if mode == "Dark":
        return DARK_CSS
    return LIGHT_CSS
```
