# NFR Design Patterns — Unit 1: Core Engine

## パターン一覧

| パターン ID | パターン名 | 対応 NFR | 適用コンポーネント |
|---|---|---|---|
| PAT-01 | Retry with Exponential Backoff | REL-01 | GeminiClient |
| PAT-02 | Background Thread + widget.after() Callback | PERF-01, REL-05 | AssistantOrchestrator |
| PAT-03 | Observer（コールバック登録） | PERF-01 | HotkeyManager |
| PAT-04 | Facade | MAINT-01 | AssistantOrchestrator |
| PAT-05 | Null Object（安全な失敗表現） | REL-01, AVAIL-02 | CaptureResult, PreloadResult |
| PAT-06 | Shutdown Hook（シグナルハンドリング） | AVAIL-03, REL-04 | main.py |
| PAT-07 | Structured Logging | MAINT-01〜04, SEC-04 | 全コンポーネント |

---

## PAT-01: Retry with Exponential Backoff

**対応 NFR**: REL-01（最大3回・指数バックオフ）

**適用箇所**: `GeminiClient.preload_context()` / `GeminiClient.generate_response()`

```python
import time
import logging

logger = logging.getLogger(__name__)

RETRYABLE_ERRORS = (NetworkError, TimeoutError, RateLimitError)
MAX_RETRIES = 3
BACKOFF_BASE = 1.0  # 秒

def _call_with_retry(fn, *args, **kwargs):
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            return fn(*args, **kwargs)
        except RETRYABLE_ERRORS as e:
            last_error = e
            if attempt < MAX_RETRIES:
                wait = BACKOFF_BASE * (2 ** attempt)  # 1s, 2s, 4s
                logger.warning(
                    "API call failed (attempt %d/%d), retrying in %.1fs: %s",
                    attempt + 1, MAX_RETRIES + 1, wait, type(e).__name__
                )
                time.sleep(wait)
        except Exception as e:
            # 非リトライ対象エラー（401/403等）は即座に再raiseする
            raise
    raise last_error
```

**非リトライ対象**: `AuthError`（401/403）、`InvalidRequestError`（400）→ 即座にエラーとして扱う

---

## PAT-02: Background Thread + widget.after() Callback

**対応 NFR**: PERF-01（500ms以内のUI表示）、REL-05（スレッド安全性）

**適用箇所**: `AssistantOrchestrator._run_preload()` / `AssistantOrchestrator._run_generate()`

```python
import threading

class AssistantOrchestrator:

    def _run_in_background(self, task_fn, callback_fn):
        """task_fn をバックグラウンドで実行し、完了後 callback_fn をUIスレッドで呼び出す。"""
        def _worker():
            result = task_fn()
            # UIスレッドへの通知は必ず widget.after() 経由
            self._widget.after(0, lambda: callback_fn(result))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
```

**`daemon=True`の理由**: メインスレッド（tkinter）終了時にバックグラウンドスレッドも自動終了させる。

---

## PAT-03: Observer（コールバック登録）

**対応 NFR**: PERF-01（ホットキー→UI表示の最短経路）

**適用箇所**: `HotkeyManager` → `AssistantOrchestrator`

```python
class HotkeyManager:
    def register(self, callback: Callable[[], None]) -> None:
        """pynput の GlobalHotKeys に callback を登録する。
        コールバックは pynput の内部スレッドで実行されるため、
        UI操作は callback 内で widget.after() を使うこと。"""
        from pynput import keyboard
        self._listener = keyboard.GlobalHotKeys({
            "<ctrl>+<shift>+<space>": callback
        })
        self._listener.start()
```

---

## PAT-04: Facade

**対応 NFR**: MAINT（コンポーネント間の結合を AssistantOrchestrator に集約）

`AssistantOrchestrator` は Unit 1 の全コンポーネント（HotkeyManager, ScreenCaptureService, GeminiClient, SessionManager）と Unit 2 の FloatingWidget・ConfigManager の Facade として機能する。外部（main.py）は `orchestrator.start()` / `orchestrator.stop()` のみ呼び出せばよい。

---

## PAT-05: Null Object（安全な失敗表現）

**対応 NFR**: REL-01, AVAIL-02（失敗時もクラッシュしない）

`CaptureResult` と `PreloadResult` は `success=False` のときも有効なオブジェクトを返す。呼び出し元は `None` チェックではなく `result.success` で分岐する。

```python
# 安全なパターン
result = capture_service.capture()
if not result.success:
    widget.set_status_message("画面取得に失敗しました。テキスト入力で相談できます。")
    return
# success=True のとき image_base64 は必ず非 None
gemini.preload_context(result.image_base64)
```

---

## PAT-06: Shutdown Hook（シグナルハンドリング）

**対応 NFR**: AVAIL-03, REL-04（異常終了時のホットキー解除保証）

```python
import signal
import sys

def _setup_shutdown_hooks(orchestrator):
    def _graceful_shutdown(signum, frame):
        logger.info("Shutdown signal received (%s), stopping...", signum)
        orchestrator.stop()  # HotkeyManager.unregister() を内部で呼ぶ
        sys.exit(0)

    signal.signal(signal.SIGINT, _graceful_shutdown)
    signal.signal(signal.SIGTERM, _graceful_shutdown)
```

---

## PAT-07: Structured Logging

**対応 NFR**: MAINT-01〜04, SEC-04（機密情報をログに含めない）

```python
# 各コンポーネントでのロガー取得
logger = logging.getLogger(__name__)

# 良い例（機密情報を含まない）
logger.debug("preload_context started, monitor_index=%d", monitor_index)
logger.debug("generate_response completed, response_length=%d", len(response))
logger.error("API call failed: %s", type(e).__name__)

# 悪い例（NG）
logger.debug("image_base64=%s", image_base64)      # NG: 画像データ
logger.debug("response=%s", response_text)          # NG: 会話内容全文
logger.debug("user_input=%s", user_input)           # NG: ユーザー入力
```
