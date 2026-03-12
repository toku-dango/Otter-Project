# Frontend Components — Unit 2: UI & Configuration

## コンポーネント階層

```
FloatingWidget (CTkToplevel)
  ├── HeaderBar (CTkFrame)
  │     ├── OtterDisplay (CTkLabel)        ← Otter アニメーション/プレースホルダー
  │     ├── StatusLabel (CTkLabel)         ← "画面を確認しました ✓" 等
  │     └── MinimizeButton (CTkButton)     ← ▼/▲
  │
  ├── ResponseArea (tkinterweb.HtmlFrame)  ← マークダウンレンダリング
  │
  ├── CopyButton (CTkButton)              ← "コピー" / "✓ コピーしました"
  │
  └── InputArea (CTkFrame)
        ├── InputField (CTkTextbox)        ← 複数行入力
        └── SendButton (CTkButton)         ← "送信"
```

---

## FloatingWidget（ルートコンポーネント）

**props（コンストラクタ引数）**:
- `animation_ctrl: OtterAnimationController`

**state**:
- `_is_visible: bool` — 表示中かどうか
- `_is_minimized: bool` — 最小化中かどうか
- `_last_response: str` — コピー用の最後の応答テキスト
- `_drag_start_x: int` / `_drag_start_y: int` — ドラッグ開始座標
- `_on_submit_callback: Callable[[str], None] | None`
- `_on_close_callback: Callable[[], None] | None`
- `_on_copy_callback: Callable[[], None] | None`
- `_resize_debounce_id: str | None` — リサイズデバウンス用 after ID

**data-testid 属性**（UI自動化対応）:
```
floating-widget-root
floating-widget-header
floating-widget-otter-display
floating-widget-status-label
floating-widget-minimize-button
floating-widget-response-area
floating-widget-copy-button
floating-widget-input-field
floating-widget-send-button
```

**公開メソッド（Unit 1 インターフェース契約）**:
```python
def show(self) -> None
def hide(self) -> None
def is_visible(self) -> bool
def set_state(self, state: str) -> None      # "IDLE" / "THINKING" / "DONE"
def set_status_message(self, msg: str) -> None
def display_response(self, text: str) -> None
def get_last_response(self) -> str
def on_submit(self, callback: Callable[[str], None]) -> None
def on_close(self, callback: Callable[[], None]) -> None
def on_copy(self, callback: Callable[[], None]) -> None
```

---

## HeaderBar

**役割**: ドラッグハンドル・Otter 表示・ステータス表示・最小化ボタン

**レイアウト**:
```
[🦦 状態表示] [ステータスメッセージ ............] [▼]
  OtterDisplay    StatusLabel                    MinimizeBtn
```

**ドラッグバインド**:
- `<ButtonPress-1>` → 開始座標を記録
- `<B1-Motion>` → ウィジェット位置を更新
- `<ButtonRelease-1>` → 位置を ConfigManager に保存

---

## OtterAnimationController

**props（コンストラクタ引数）**:
- `label: CTkLabel` — 描画先の CTkLabel
- `assets_dir: str` — GIF ファイルが置かれるディレクトリ（デフォルト: `"assets"`）

**state**:
- `_current_state: AnimationState`
- `_frames: dict[AnimationState, list[ImageTk.PhotoImage]]` — GIF フレームリスト
- `_frame_index: int` — 現在フレーム番号
- `_after_id: str | None` — アニメーションタイマー ID

**アニメーション再生ロジック**:
```python
def play(self, state: AnimationState) -> None:
    # GIF が存在する場合: フレームアニメーション
    # GIF が存在しない場合: プレースホルダー絵文字を表示
    if self._has_gif(state):
        self._start_animation(state)
    else:
        self._show_placeholder(state)
```

**DONE 状態の自動遷移**:
```python
# done.gif の最終フレーム到達後、または一定時間後に IDLE へ遷移
self._label.after(2000, lambda: self.play(AnimationState.IDLE))
```

---

## ResponseArea（tkinterweb.HtmlFrame）

**役割**: マークダウンを HTML に変換してレンダリングする

**更新フロー**:
```python
def display_response(self, text: str) -> None:
    html = markdown.markdown(
        text,
        extensions=["fenced_code", "tables", "nl2br"]
    )
    styled_html = f"<style>{CSS}</style><body>{html}</body>"
    self._html_frame.load_html(styled_html)
```

**フォールバック**: `tkinterweb` がインポートできない場合は `CTkTextbox`（プレーンテキスト）にフォールバックする。

---

## InputArea

**InputField（CTkTextbox）**:
- 高さ: 3行分（約60px）
- Enter: 送信（`<Return>` バインド）
- Shift+Enter: 改行（BR-U2-05）
- THINKING 状態: `state="disabled"`

**SendButton（CTkButton）**:
- ラベル: "送信"
- THINKING 状態: `state="disabled"`
- クリック時: InputField のテキストを取得 → `on_submit_callback(text)` → InputField クリア

---

## ConfigManager

**props**:
- `config_file: str` — デフォルト `~/.config/project-otter/config.json`

**内部状態**:
- `_config: AppConfig` — メモリ上の設定オブジェクト

**フォーム バリデーション**（設定値）:
- `widget_x`, `widget_y`: 0 以上の整数
- `widget_width`: 300 以上
- `widget_height`: 200 以上

---

## ClipboardService

シンプルなユーティリティ。UI コンポーネントなし。

```python
class ClipboardService:
    def copy(self, text: str) -> bool:
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            return False
```
