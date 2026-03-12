# Component Methods — Project Otter

> **注**: 詳細なビジネスロジック・バリデーションルールは CONSTRUCTION フェーズの Functional Design で定義します。

---

## C1: AssistantOrchestrator

```python
class AssistantOrchestrator:
    def __init__(
        self,
        hotkey: HotkeyManager,
        capture: ScreenCaptureService,
        gemini: GeminiClient,
        session_mgr: SessionManager,
        widget: FloatingWidget,
        config: ConfigManager,
    ) -> None: ...

    def start(self) -> None:
        """アプリケーション起動。全コンポーネント初期化・ホットキー登録。"""

    def stop(self) -> None:
        """アプリケーション終了。リソース解放・ホットキー解除。"""

    def on_hotkey_triggered(self) -> None:
        """ホットキー押下イベント。キャプチャ→Gemini事前把握→ウィジェット表示。"""

    def on_user_input(self, text: str) -> None:
        """ユーザーテキスト送信イベント。Gemini応答生成→UI更新。"""

    def on_session_close(self) -> None:
        """ウィジェット閉じるイベント。セッション終了・データ消去。"""

    def _handle_error(self, error: Exception, context: str) -> None:
        """エラーハンドリング。UIへのフィードバック表示。"""
```

---

## C2: HotkeyManager

```python
class HotkeyManager:
    def __init__(self, hotkey_combo: str = "<ctrl>+<shift>+<space>") -> None: ...

    def register(self, callback: Callable[[], None]) -> None:
        """グローバルホットキーをシステムに登録し、押下時にcallbackを呼び出す。"""

    def unregister(self) -> None:
        """ホットキー登録を解除する。"""

    def is_registered(self) -> bool:
        """ホットキーが登録済みかどうかを返す。"""
```

---

## C3: ScreenCaptureService

```python
@dataclass
class CaptureResult:
    success: bool
    image_pil: Image | None       # PIL Image オブジェクト
    image_base64: str | None      # Base64 エンコード文字列
    error_message: str | None

class ScreenCaptureService:
    def capture(self) -> CaptureResult:
        """現在の全画面スクリーンショットを取得しBase64エンコードして返す。"""

    def capture_window(self, hwnd: int) -> CaptureResult:
        """指定ウィンドウのスクリーンショットを取得する。（将来拡張用）"""
```

---

## C4: GeminiClient

```python
@dataclass
class PreloadResult:
    success: bool
    context_summary: str | None   # AIが把握した画面状況の要約
    chat_session: Any | None      # Gemini ChatSession オブジェクト
    error_message: str | None

class GeminiClient:
    def __init__(self, credentials: Any, model: str = "gemini-2.0-flash-thinking-exp") -> None:
        """credentials: google.oauth2.credentials.Credentials オブジェクト"""

    def preload_context(self, image_base64: str) -> PreloadResult:
        """スクリーンショットを送信し、AIに画面状況を把握させる。
        ユーザー入力前に呼び出す事前把握フェーズ。"""

    def generate_response(
        self,
        user_input: str,
        chat_session: Any,
    ) -> str:
        """ユーザー指示をセッション経由で送信し、AI応答テキストを返す。"""

    def create_session(self) -> Any:
        """新しい Gemini ChatSession を生成して返す。"""

    def is_available(self) -> bool:
        """APIキーが設定済みでAPIが利用可能かどうかを確認する。"""
```

---

## C5: SessionManager

```python
@dataclass
class Session:
    session_id: str
    chat_session: Any             # Gemini ChatSession
    history: list[dict]           # [{"role": "user/model", "text": "..."}]
    created_at: datetime

class SessionManager:
    def start_session(self) -> Session:
        """新しいセッションを開始し、IDを付与して返す。"""

    def end_session(self, session_id: str) -> None:
        """セッションを終了し、全履歴をメモリから消去する。"""

    def add_exchange(
        self,
        session_id: str,
        user_input: str,
        ai_response: str,
    ) -> None:
        """会話1往復（ユーザー入力＋AI応答）を履歴に追加する。"""

    def get_session(self, session_id: str) -> Session | None:
        """セッションIDからセッションオブジェクトを取得する。"""
```

---

## C6: FloatingWidget

```python
from enum import Enum

class WidgetState(Enum):
    IDLE = "idle"           # 通常待機中
    THINKING = "thinking"   # AI処理中
    DONE = "done"           # 応答完了

class FloatingWidget:
    def __init__(self, animation_ctrl: OtterAnimationController) -> None: ...

    def show(self) -> None:
        """ウィジェットを画面に表示する（最前面）。"""

    def hide(self) -> None:
        """ウィジェットを非表示にする。"""

    def minimize(self) -> None:
        """ウィジェットを最小化（縮小表示）する。"""

    def set_state(self, state: WidgetState) -> None:
        """ウィジェット状態を切り替える。Otterアニメーションも連動。"""

    def display_response(self, text: str) -> None:
        """AI応答テキストを応答エリアに表示する。"""

    def set_status_message(self, message: str) -> None:
        """ステータスメッセージ（「画面を確認しました」等）を表示する。"""

    def on_submit(self, callback: Callable[[str], None]) -> None:
        """テキスト送信イベントのコールバックを登録する。"""

    def on_close(self, callback: Callable[[], None]) -> None:
        """ウィジェット閉じるイベントのコールバックを登録する。"""

    def on_copy(self, callback: Callable[[], None]) -> None:
        """コピーボタンクリックイベントのコールバックを登録する。"""

    def get_last_response(self) -> str:
        """最後に表示したAI応答テキストを返す（コピー用）。"""
```

---

## C7: OtterAnimationController

```python
from enum import Enum

class AnimationState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    DONE = "done"

class OtterAnimationController:
    def __init__(self, canvas: Any, assets_dir: str = "assets") -> None: ...

    def load_animations(self) -> None:
        """assets/ から状態別GIFファイルを読み込む。"""

    def play(self, state: AnimationState) -> None:
        """指定状態のアニメーションを再生する。
        DONE は1回再生後自動的に IDLE に遷移する。"""

    def stop(self) -> None:
        """アニメーション再生を停止する。"""

    def _update_frame(self) -> None:
        """次のGIFフレームをキャンバスに描画する（内部タイマー処理）。"""
```

---

## C8: ConfigManager

```python
class ConfigManager:
    def __init__(self, config_file: str = "config.json") -> None: ...

    def get_credentials(self) -> Any | None:
        """キャッシュ済みのGoogle OAuth Credentials を返す。なければ None。"""

    def save_credentials(self, credentials: Any) -> None:
        """Google OAuth Credentials を ~/.config/project-otter/credentials.json に保存する。"""

    def has_valid_credentials(self) -> bool:
        """有効な認証情報（キャッシュ or リフレッシュ可能）が存在するかを返す。"""

    def get_setting(self, key: str, default: Any = None) -> Any:
        """config.json から設定値を取得する。"""

    def set_setting(self, key: str, value: Any) -> None:
        """config.json に設定値を保存する。"""
```

---

## C9: ClipboardService

```python
class ClipboardService:
    def copy(self, text: str) -> bool:
        """テキストをクリップボードにコピーする。成功時True、失敗時Falseを返す。"""
```
