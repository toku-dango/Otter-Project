# Code Generation Plan — Unit 1: Core Engine

## ユニット概要

| 項目 | 内容 |
|---|---|
| Unit | Unit 1: Core Engine |
| Workspace Root | `/workspaces/claude-code-book-template/project-otter` |
| プロジェクト種別 | Greenfield |
| 担当ストーリー | US-01, 03, 04, 05, 08, 09, 10, 13, 14, 16, 17, 19（MVP 12件） |

## ファイル構成（生成対象）

```
project-otter/                          ← Application Code（Workspace Root）
  main.py                               # エントリーポイント
  session_manager.py                    # C5
  hotkey_manager.py                     # C2
  screen_capture_service.py             # C3
  gemini_client.py                      # C4
  assistant_orchestrator.py             # C1
  requirements.txt
  tests/
    __init__.py
    test_session_manager.py
    test_gemini_client.py
    test_assistant_orchestrator.py
aidlc-docs/construction/unit1/code/    ← Documentation Only
  code-summary.md
```

---

## チェックリスト

### PART 1: Planning
- [x] Step 1: ユニットコンテキスト分析
- [x] Step 2: コード生成計画作成
- [x] Step 3: ユニット生成コンテキスト整理
- [x] Step 4: 計画ドキュメント保存
- [ ] Step 5: 計画サマリー提示
- [ ] Step 6: 承認プロンプトログ記録
- [ ] Step 7: 承認待ち
- [ ] Step 8: 承認記録

### PART 2: Generation
- [x] Step 1: プロジェクト構造セットアップ（requirements.txt / tests/__init__.py）
- [x] Step 2: `session_manager.py` 生成
- [x] Step 3: `tests/test_session_manager.py` 生成
- [x] Step 4: `hotkey_manager.py` 生成
- [x] Step 5: `screen_capture_service.py` 生成
- [x] Step 6: `gemini_client.py` 生成
- [x] Step 7: `tests/test_gemini_client.py` 生成
- [x] Step 8: `assistant_orchestrator.py` 生成
- [x] Step 9: `tests/test_assistant_orchestrator.py` 生成
- [x] Step 10: `main.py` 生成
- [x] Step 11: `aidlc-docs/construction/unit1/code/code-summary.md` 生成

---

## 各ステップ詳細

### Step 1: プロジェクト構造セットアップ
**生成ファイル**:
- `requirements.txt` — Unit 1 + Unit 2 合算の依存ライブラリ（tech-stack-decisions.md 準拠）
- `tests/__init__.py` — テストパッケージ初期化（空ファイル）

---

### Step 2: `session_manager.py` 生成
**対応ストーリー**: US-07（Step2）の基盤、US-04, 05の会話継続
**実装内容**:
- `Session` dataclass（session_id, chat_session, history, created_at, preload_summary）
- `Exchange` dataclass（user_input, ai_response, timestamp）
- `SessionManager` クラス（start_session / end_session / add_exchange / get_session）
- セッションはメモリのみ保持（ディスク書き込みなし）

---

### Step 3: `tests/test_session_manager.py` 生成
**テスト内容**:
- `start_session()` で Session が生成されること
- `add_exchange()` で履歴が追加されること
- `end_session()` でセッションが消去されること
- `get_session()` で存在しない ID は None を返すこと

---

### Step 4: `hotkey_manager.py` 生成
**対応ストーリー**: US-01, US-08
**実装内容**:
- `HotkeyManager` クラス（register / unregister / is_registered）
- `pynput.keyboard.GlobalHotKeys` を使用
- デフォルトホットキー: `<ctrl>+<shift>+<space>`
- コールバックは pynput スレッドで実行（UI操作はしない）

---

### Step 5: `screen_capture_service.py` 生成
**対応ストーリー**: US-03, US-09, US-13, US-16
**実装内容**:
- `CaptureResult` dataclass（success, image_base64, monitor_index, error_message）
- `ScreenCaptureService` クラス（capture メソッド）
- `mss` でマウスカーソルのあるモニターをキャプチャ（BR-06）
- PIL Image → Base64 変換
- エラー時は `success=False` の CaptureResult を返す（PAT-05）

---

### Step 6: `gemini_client.py` 生成
**対応ストーリー**: US-03, 04, 05, 09, 10, 13, 14, 16, 17, 19
**実装内容**:
- `PreloadResult` dataclass（success, context_summary, chat_session, error_message）
- `GeminiClient` クラス（preload_context / generate_response / create_session / is_available）
- Google OAuth Credentials を受け取って初期化（BR-10）
- `preload_context`: 10秒タイムアウト + PAT-01 リトライ（BR-02, REL-01）
- `generate_response`: 30秒タイムアウト + PAT-01 リトライ（BR-03, REL-01）
- PAT-07 Structured Logging（機密情報をログに含めない）

---

### Step 7: `tests/test_gemini_client.py` 生成
**テスト内容**:
- `preload_context()` 成功時に `PreloadResult(success=True)` を返すこと（APIモック）
- `preload_context()` 失敗時に `PreloadResult(success=False)` を返すこと
- `generate_response()` 成功時に応答テキストを返すこと（APIモック）
- `generate_response()` がリトライを実行すること（mock side_effect で一時失敗をシミュレート）

---

### Step 8: `assistant_orchestrator.py` 生成
**対応ストーリー**: US-01, 03, 04, 05, 08（全 Core Engine ストーリー）
**実装内容**:
- `AssistantOrchestrator` クラス（start / stop / on_hotkey_triggered / on_user_input / on_session_close / _handle_error）
- PAT-02: バックグラウンドスレッド + `widget.after()` コールバック
- PAT-04: Facade（全コンポーネントの統合）
- PAT-06: シグナルハンドラ登録（SIGINT/SIGTERM）
- FL-02 / FL-03 / FL-04 / FL-05 のフロー実装
- BR-01: ホットキー再押下時の終了確認ダイアログ
- BR-08: 空文字入力のガード
- BR-09: 日本語エラーメッセージ

---

### Step 9: `tests/test_assistant_orchestrator.py` 生成
**テスト内容**:
- `on_hotkey_triggered()` がウィジェット非表示時に `set_state(THINKING)` → `show()` を呼ぶこと
- `on_hotkey_triggered()` がウィジェット表示中に終了確認ダイアログを表示すること
- `on_user_input("")` が空文字で早期リターンすること
- `on_user_input("丁寧に")` が `generate_response()` を呼び出すこと
- API失敗時に `_handle_error()` が日本語メッセージを Widget に渡すこと

---

### Step 10: `main.py` 生成
**実装内容**:
- ログ設定（RotatingFileHandler、DEBUG レベル、PAT-07準拠）
- Google OAuth 認証フロー（`ConfigManager.has_valid_credentials()` → 未認証時はブラウザフロー）
- 全コンポーネント初期化・`AssistantOrchestrator` 起動
- PAT-06: シグナルハンドラ登録

---

### Step 11: `code-summary.md` 生成（aidlc-docs）
**内容**:
- 生成ファイル一覧と説明
- 各ストーリーの実装状況
- Unit 2 との統合ポイント

---

## ストーリートレーサビリティ

| US ID | 実装ステップ |
|---|---|
| US-01 | Step 4, 8（HotkeyManager + Orchestrator） |
| US-03 | Step 5, 6, 8（Capture + Gemini + Orchestrator） |
| US-04 | Step 6, 8（GeminiClient Reasoning） |
| US-05 | Step 6, 8（generate_response） |
| US-08 | Step 4, 8（フォーカス維持はpynputの特性で自動対応） |
| US-09 | Step 5, 6（mss + GeminiClient） |
| US-10 | Step 6, 8（generate_response） |
| US-13 | Step 5, 6（mss + GeminiClient） |
| US-14 | Step 6, 8（generate_response） |
| US-16 | Step 5, 6（mss + GeminiClient） |
| US-17 | Step 6, 8（generate_response） |
| US-19 | Step 6, 8（generate_response） |

---

## Unit 2 との統合ポイント（インターフェース契約）

Unit 2 が提供する以下のインターフェースに依存する。Unit 2 未完了時はモックで代替する。

| Unit 2 コンポーネント | 使用箇所 | インターフェース |
|---|---|---|
| `FloatingWidget` | AssistantOrchestrator | `show()`, `hide()`, `set_state()`, `display_response()`, `set_status_message()`, `on_submit()`, `on_close()`, `is_visible()` |
| `ConfigManager` | main.py, GeminiClient | `has_valid_credentials()`, `get_credentials()`, `save_credentials()` |
| `ClipboardService` | AssistantOrchestrator | `copy(text)` |
