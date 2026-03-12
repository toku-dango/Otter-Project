# Domain Entities — Unit 1: Core Engine

## エンティティ一覧

| Entity | 種別 | 説明 |
|---|---|---|
| Session | Aggregate Root | アプリ起動中の会話セッション全体 |
| Exchange | Value Object | ユーザー入力とAI応答の1往復 |
| CaptureResult | Value Object | スクリーンキャプチャの結果 |
| PreloadResult | Value Object | Gemini事前把握の結果 |
| AppError | Value Object | エラー情報 |
| WidgetState | Enum | ウィジェットの表示状態 |
| AnimationState | Enum | Otterアニメーションの状態 |

---

## Session（Aggregate Root）

アプリケーション起動中に存在する唯一のセッション。会話履歴を保持する。

```python
@dataclass
class Session:
    session_id: str          # UUID4 形式
    chat_session: Any        # Gemini SDK ChatSession オブジェクト
    history: list[Exchange]  # 会話履歴（時系列順）
    created_at: datetime     # セッション開始日時
    preload_summary: str | None  # 最新の画面把握サマリー
```

**制約**:
- `session_id` は UUID4 で自動生成
- `history` はメモリ上のみに保持。ディスクには書き込まない
- `chat_session` は Gemini SDK が内部で会話履歴を管理するオブジェクト
- `preload_summary` は `preload_context()` 呼び出しのたびに上書きされる

---

## Exchange（Value Object）

ユーザーとAIの1往復の会話ペア。

```python
@dataclass(frozen=True)
class Exchange:
    user_input: str      # ユーザーが入力したテキスト
    ai_response: str     # AIが生成した応答テキスト
    timestamp: datetime  # 入力日時
```

**制約**:
- Immutable（`frozen=True`）
- `user_input` は1文字以上
- `ai_response` は空文字不可（エラー時は BR-09 のメッセージ文字列）

---

## CaptureResult（Value Object）

スクリーンキャプチャの成否と結果データ。

```python
@dataclass(frozen=True)
class CaptureResult:
    success: bool
    image_base64: str | None    # Base64エンコードされた画像データ
    monitor_index: int | None   # キャプチャしたモニター番号
    error_message: str | None   # 失敗時のエラー詳細（内部用）
```

**制約**:
- `success=True` のとき `image_base64` は必ず非 None
- `success=False` のとき `image_base64` は None
- `error_message` はユーザー向けではなくログ用（ユーザーへは BR-09 のメッセージを使用）

---

## PreloadResult（Value Object）

Gemini事前把握の成否と結果データ。

```python
@dataclass(frozen=True)
class PreloadResult:
    success: bool
    context_summary: str | None  # AIが把握した画面状況の要約テキスト
    chat_session: Any | None     # 事前把握済みのGemini ChatSession
    error_message: str | None    # 失敗時のエラー詳細（内部用）
```

**制約**:
- `success=True` のとき `chat_session` は必ず非 None
- `context_summary` は画面内容の日本語要約（Geminiが生成）
- 失敗時でも FL-04 のユーザー入力処理は継続可能（文脈なし応答）

---

## AppError（Value Object）

エラー種別と内部詳細を保持する。

```python
class ErrorType(Enum):
    AUTH_FAILED = "auth_failed"        # OAuth認証失敗
    AUTH_CANCELLED = "auth_cancelled"  # ユーザーがログインをキャンセル
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    CAPTURE_FAILED = "capture_failed"
    NETWORK_ERROR = "network_error"
    RESPONSE_FAILED = "response_failed"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class AppError:
    error_type: ErrorType
    internal_message: str   # ログ用（技術的詳細）
    user_message: str       # UIに表示する日本語メッセージ（BR-09準拠）
    context: str            # エラー発生箇所（例: "preload_context"）
```

---

## WidgetState（Enum）

FloatingWidget の表示状態。Unit 2 の OtterAnimationController と連動する。

```python
class WidgetState(Enum):
    IDLE = "idle"           # 待機中・入力受付可能
    THINKING = "thinking"   # AI処理中・入力無効
    DONE = "done"           # 応答表示完了
```

**状態遷移**:
```
起動時: → THINKING（画面取得中）
preload完了 or 失敗: → IDLE
ユーザー送信: → THINKING
generate完了 or 失敗: → IDLE（失敗） / DONE（成功）
DONE → （自動）→ IDLE（3秒後またはユーザー操作後）
```

---

## AnimationState（Enum）

OtterAnimationController の再生状態。WidgetState と対応する。

```python
class AnimationState(Enum):
    IDLE = "idle"           # idle.gif ループ再生
    THINKING = "thinking"   # thinking.gif ループ再生
    DONE = "done"           # done.gif 1回再生 → IDLE に自動遷移
```

**WidgetState との対応**:

| WidgetState | AnimationState |
|---|---|
| IDLE | IDLE |
| THINKING | THINKING |
| DONE | DONE（1回再生後 IDLE へ） |

---

## エンティティ関係図

```
AssistantOrchestrator
  |
  +-[1]-- SessionManager
  |         |
  |         +-[1]-- Session --------+-[*]-- Exchange
  |                   |
  |                   +-[0..1]-- PreloadResult
  |
  +-[1]-- ScreenCaptureService
  |         |
  |         +-[produces]--> CaptureResult
  |
  +-[1]-- GeminiClient
            |
            +-[produces]--> PreloadResult
            +-[produces]--> str (response_text)
```
