# Component Dependencies — Project Otter

## 依存関係マトリクス

| コンポーネント | 依存先 |
|---|---|
| AssistantOrchestrator | HotkeyManager, ScreenCaptureService, GeminiClient, SessionManager, FloatingWidget, ConfigManager, ClipboardService |
| FloatingWidget | OtterAnimationController |
| GeminiClient | ConfigManager（APIキー取得） |
| HotkeyManager | — |
| ScreenCaptureService | — |
| SessionManager | — |
| OtterAnimationController | — |
| ConfigManager | — |
| ClipboardService | — |

---

## 依存関係図

```
main.py
  |
  v
AssistantOrchestrator
  |-- HotkeyManager
  |-- ScreenCaptureService
  |-- GeminiClient
  |     +-- ConfigManager (APIキー取得)
  |-- SessionManager
  |-- FloatingWidget
  |     +-- OtterAnimationController
  |-- ConfigManager
  +-- ClipboardService
```

---

## コンポーネント間通信パターン

### パターン 1: コールバック（イベント駆動）

HotkeyManager → AssistantOrchestrator の通知に使用。

```python
# HotkeyManager はコールバックを保持するだけ
hotkey_manager.register(callback=orchestrator.on_hotkey_triggered)
```

### パターン 2: 直接呼び出し（同期）

AssistantOrchestrator が各サービスを直接呼び出す。
ScreenCaptureService・ClipboardService・ConfigManager はシンプルな同期処理。

```python
result = capture_service.capture()
clipboard.copy(text)
```

### パターン 3: 非同期呼び出し（async/await または threading）

GeminiClient の API 呼び出しは時間がかかるため、UIスレッドをブロックしないよう非同期処理。

```python
# threading または asyncio で実行
thread = threading.Thread(target=self._preload_and_update_ui, args=(image,))
thread.start()
```

---

## データフロー

### ホットキー起動時のデータフロー

```
HotkeyManager
  |
  | (イベント発火)
  v
AssistantOrchestrator
  |
  | capture()
  v
ScreenCaptureService
  |
  | CaptureResult { image_base64: str }
  v
AssistantOrchestrator
  |
  | preload_context(image_base64)
  v
GeminiClient (Gemini API)
  |
  | PreloadResult { chat_session, context_summary }
  v
AssistantOrchestrator
  |
  | start_session(chat_session)
  v
SessionManager
  |
  | Session { session_id, chat_session }
  v
AssistantOrchestrator → FloatingWidget (show + IDLE state)
```

### ユーザー入力時のデータフロー

```
FloatingWidget
  |
  | (submit callback) text: str
  v
AssistantOrchestrator
  |
  | generate_response(text, chat_session)
  v
GeminiClient (Gemini API)
  |
  | response_text: str
  v
AssistantOrchestrator
  |
  | add_exchange(user_input, response_text)
  v
SessionManager (履歴更新)
  |
AssistantOrchestrator
  |
  | display_response(response_text)
  v
FloatingWidget (DONE state)
```

---

## ファイル構成（フラット構成）

```
project-otter/
  main.py                       # エントリーポイント・AssistantOrchestrator 起動
  assistant_orchestrator.py     # C1: メインサービス
  hotkey_manager.py             # C2
  screen_capture_service.py     # C3
  gemini_client.py              # C4
  session_manager.py            # C5
  floating_widget.py            # C6
  otter_animation_controller.py # C7
  config_manager.py             # C8
  clipboard_service.py          # C9
  assets/
    idle.gif                    # Otter アイドルアニメ
    thinking.gif                # Otter 考え中アニメ
    done.gif                    # Otter 完了アニメ
  config.json                   # 設定ファイル（自動生成）
  requirements.txt
```
