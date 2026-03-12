# Unit of Work — Project Otter

## 開発方式

**同時並行開発**（B選択）

Unit 1 と Unit 2 は独立して並行開発する。ただし `AssistantOrchestrator`（Unit 1）が両ユニットのインターフェースに依存するため、**開発開始前にインターフェース契約を確定**させること。

---

## Unit 1: Core Engine

### 概要

| 項目 | 内容 |
|---|---|
| **Unit ID** | Unit 1 |
| **名称** | Core Engine |
| **目的** | ホットキー検出→画面取得→Gemini API連携→セッション管理の一連フローを実現する |
| **フェーズ** | MVP |

### 含まれるコンポーネント

| ID | コンポーネント | ファイル | 役割 |
|---|---|---|---|
| C1 | AssistantOrchestrator | `assistant_orchestrator.py` | 全体フロー制御（両ユニット統合点） |
| C2 | HotkeyManager | `hotkey_manager.py` | グローバルホットキー監視 |
| C3 | ScreenCaptureService | `screen_capture_service.py` | スクリーンショット取得・Base64変換 |
| C4 | GeminiClient | `gemini_client.py` | Gemini API通信・Reasoning処理 |
| C5 | SessionManager | `session_manager.py` | 会話履歴のインメモリ管理 |

### 受け入れ基準

- Ctrl+Shift+Space 押下から画面取得・Gemini事前把握完了まで 500ms 以内（APIレイテンシ除く）
- アイドル時の CPU 使用率 1% 以下
- APIエラー時にエラーコードと日本語メッセージを返すこと
- セッション終了時に全履歴がメモリから消去されること

### 主要依存ライブラリ

| ライブラリ | 用途 |
|---|---|
| `pynput` | グローバルホットキー検出 |
| `mss` | 高速スクリーンキャプチャ |
| `Pillow` | 画像処理・Base64変換 |
| `google-generativeai` | Gemini API SDK |

---

## Unit 2: UI & Configuration

### 概要

| 項目 | 内容 |
|---|---|
| **Unit ID** | Unit 2 |
| **名称** | UI & Configuration |
| **目的** | フローティングUI表示・Otterアニメーション・APIキー設定・クリップボード操作を実現する |
| **フェーズ** | MVP |

### 含まれるコンポーネント

| ID | コンポーネント | ファイル | 役割 |
|---|---|---|---|
| C6 | FloatingWidget | `floating_widget.py` | 常時最前面フローティングUI |
| C7 | OtterAnimationController | `otter_animation_controller.py` | 状態別GIFアニメ再生 |
| C8 | ConfigManager | `config_manager.py` | APIキー・設定の永続化 |
| C9 | ClipboardService | `clipboard_service.py` | 応答テキストのクリップボードコピー |

### 受け入れ基準

- ウィジェット表示・非表示が 100ms 以内で切り替わること
- ドラッグ移動後も常時最前面表示が維持されること
- 初回起動時のAPIキー設定が 3ステップ以内で完了できること
- コピーボタン押下後 1秒以内に「コピーしました」フィードバックが表示されること
- Otter アニメーションが idle / thinking / done の各状態でシームレスに切り替わること

### 主要依存ライブラリ

| ライブラリ | 用途 |
|---|---|
| `customtkinter` | フレームレス・半透明ウィンドウ |
| `Pillow` | GIFフレーム逐次再生 |
| `keyring` | OSキーチェーンへのAPIキー保存 |
| `pyperclip` | クリップボード操作 |

---

## 並行開発の注意点

### インターフェース契約（開発開始前に確定）

Unit 1 の AssistantOrchestrator は Unit 2 の FloatingWidget・ConfigManager を呼び出す。
Unit 2 の GeminiClient は ConfigManager（Unit 2）からAPIキーを取得する。

**先行確定が必要なインターフェース:**

```python
# FloatingWidget（Unit 2）が提供するインターフェース
widget.show()
widget.hide()
widget.set_state(state: WidgetState)   # IDLE / THINKING / DONE
widget.display_response(text: str)
widget.on_submit(callback: Callable)

# ConfigManager（Unit 2）が提供するインターフェース
config.get_api_key() -> str | None
config.set_api_key(key: str)
config.get_setting(key: str) -> Any
config.set_setting(key: str, value: Any)
```

### 統合ポイント

Unit 1 と Unit 2 の統合は `main.py` および `AssistantOrchestrator` で行う。
各ユニットの単体開発中はモック（スタブ）を用いてテストする。
