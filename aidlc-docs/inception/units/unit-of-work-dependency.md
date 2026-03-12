# Unit of Work Dependency — Project Otter

## ユニット間依存関係

### 依存マトリクス

| 依存元 | 依存先 | 種別 | 詳細 |
|---|---|---|---|
| Unit 1 (AssistantOrchestrator) | Unit 2 (FloatingWidget) | インターフェース呼び出し | show/hide/set_state/display_response |
| Unit 1 (AssistantOrchestrator) | Unit 2 (ConfigManager) | インターフェース呼び出し | get_setting（ホットキー設定等） |
| Unit 1 (GeminiClient) | Unit 2 (ConfigManager) | インターフェース呼び出し | get_api_key() |
| Unit 2 (FloatingWidget) | Unit 1 (AssistantOrchestrator) | コールバック | on_submit → orchestrator.on_user_input |

### 依存関係図

```
main.py
  |
  v
AssistantOrchestrator [Unit 1]
  |
  |-- HotkeyManager [Unit 1]
  |-- ScreenCaptureService [Unit 1]
  |-- GeminiClient [Unit 1]
  |     |
  |     +-- ConfigManager [Unit 2]  ← APIキー取得
  |-- SessionManager [Unit 1]
  |
  |-- FloatingWidget [Unit 2]  ← UI制御
  |     |
  |     +-- OtterAnimationController [Unit 2]
  |
  |-- ConfigManager [Unit 2]  ← 設定取得
  +-- ClipboardService [Unit 2]  ← コピー操作
```

---

## 並行開発戦略

### フェーズ 1: インターフェース確定（Day 1）

両ユニットの開発開始前に以下を確定する。

**FloatingWidget インターフェース（Unit 2 → Unit 1 へ提供）:**
```python
class WidgetState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    DONE = "done"

class FloatingWidget:
    def show(self) -> None: ...
    def hide(self) -> None: ...
    def set_state(self, state: WidgetState) -> None: ...
    def display_response(self, text: str) -> None: ...
    def on_submit(self, callback: Callable[[str], None]) -> None: ...
```

**ConfigManager インターフェース（Unit 2 → Unit 1 へ提供）:**
```python
class ConfigManager:
    def get_api_key(self) -> str | None: ...
    def set_api_key(self, key: str) -> None: ...
    def get_setting(self, key: str, default: Any = None) -> Any: ...
    def set_setting(self, key: str, value: Any) -> None: ...
```

### フェーズ 2: 並行開発（各ユニット独立）

| Unit 1 開発タスク | Unit 2 開発タスク |
|---|---|
| HotkeyManager 実装・テスト | FloatingWidget 骨格実装 |
| ScreenCaptureService 実装・テスト | OtterAnimationController 実装 |
| GeminiClient 実装・テスト | ConfigManager 実装（keyring統合） |
| SessionManager 実装・テスト | ClipboardService 実装 |
| AssistantOrchestrator 実装（モック使用） | FloatingWidget 完全実装 |

### フェーズ 3: 統合

`main.py` で両ユニットを接続し、エンドツーエンドテストを実施。

---

## 開発時のモック戦略

Unit 1 開発中は Unit 2 コンポーネントをモックに置き換えてテスト:

```python
# Unit 1 テスト用 FloatingWidget モック
class MockFloatingWidget:
    def show(self): print("[MOCK] Widget shown")
    def hide(self): print("[MOCK] Widget hidden")
    def set_state(self, state): print(f"[MOCK] State: {state}")
    def display_response(self, text): print(f"[MOCK] Response: {text}")
    def on_submit(self, cb): self._callback = cb

# Unit 1 テスト用 ConfigManager モック
class MockConfigManager:
    def get_api_key(self): return "test-api-key"
    def get_setting(self, key, default=None): return default
```

Unit 2 開発中は Unit 1 コンポーネントを直接呼び出さず、UIのみ単体動作させる。
