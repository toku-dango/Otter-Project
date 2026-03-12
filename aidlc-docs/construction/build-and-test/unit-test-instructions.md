# Unit Test Execution — Project Otter

## テスト構成

| テストファイル | 対象コンポーネント | テスト数 |
|---|---|---|
| `tests/test_session_manager.py` | SessionManager (C5) | 9 |
| `tests/test_gemini_client.py` | GeminiClient (C4) | 6 |
| `tests/test_assistant_orchestrator.py` | AssistantOrchestrator (C1) | 9 |
| `tests/test_clipboard_service.py` | ClipboardService (C9) | 3 |
| `tests/test_config_manager.py` | ConfigManager (C8) | 6 |
| **合計** | | **33** |

---

## 実行手順

### 1. 全ユニットテスト実行

```bash
cd project-otter
pytest tests/ -v
```

### 2. 特定ファイルのみ実行

```bash
# Unit 1 コアエンジンのみ
pytest tests/test_session_manager.py tests/test_gemini_client.py tests/test_assistant_orchestrator.py -v

# Unit 2 UI/設定のみ
pytest tests/test_clipboard_service.py tests/test_config_manager.py -v
```

### 3. カバレッジ計測

```bash
pip install pytest-cov
pytest tests/ --cov=. --cov-report=term-missing --cov-report=html
# レポート: htmlcov/index.html
```

---

## 期待結果

```
=================== test session starts ====================
platform win32 -- Python 3.11.x, pytest-8.x.x
collected 33 items

tests/test_session_manager.py ..........       [ 27%]
tests/test_gemini_client.py ......             [ 45%]
tests/test_assistant_orchestrator.py .........  [ 72%]
tests/test_clipboard_service.py ...            [ 81%]
tests/test_config_manager.py ......            [100%]

=================== 33 passed in X.Xs ====================
```

- **期待**: 33 passed, 0 failures, 0 errors
- **カバレッジ目標**: ビジネスロジック層 ≥ 80%（UI層は除く）

---

## テスト詳細

### test_session_manager.py（9件）
| テスト名 | 検証内容 |
|---|---|
| test_start_session | セッション開始・ID生成 |
| test_end_session | セッション終了・None 返却 |
| test_add_exchange | Exchange 追加・履歴保持 |
| test_get_session_none_when_no_active | セッションなし時の None |
| test_get_history | 履歴取得 |
| test_update_preload_summary | preload_summary 更新 |
| test_session_isolation | 複数セッション独立性 |
| test_exchange_immutability | Exchange frozen dataclass |
| test_history_limit | 履歴上限チェック |

### test_gemini_client.py（6件）
| テスト名 | 検証内容 |
|---|---|
| test_preload_context_success | preload 正常系 |
| test_preload_context_timeout | タイムアウト → PreloadResult(success=False) |
| test_generate_response_success | generate 正常系 |
| test_generate_response_retry | リトライ（最大3回） |
| test_generate_response_exhausted | 全リトライ失敗 |
| test_credentials_configure | genai.configure 呼び出し確認 |

### test_assistant_orchestrator.py（9件）
| テスト名 | 検証内容 |
|---|---|
| test_start_registers_hotkey | start() → hotkey 登録 |
| test_on_hotkey_shows_widget | ホットキー → widget.show() |
| test_on_hotkey_confirmation_when_visible | 表示中の再押下 → 確認ダイアログ |
| test_on_user_input_empty_ignored | 空入力スキップ |
| test_on_user_input_triggers_generate | 入力 → generate 呼び出し |
| test_error_handling_network | ネットワークエラー → 日本語メッセージ |
| test_stop_unregisters_hotkey | stop() → hotkey 解除 |
| test_on_copy_requested | コピー → ClipboardService 呼び出し |
| test_session_close | セッション終了フロー |

### test_clipboard_service.py（3件）
| テスト名 | 検証内容 |
|---|---|
| test_copy_success | 正常コピー → True |
| test_copy_failure_returns_false | pyperclip 例外 → False（例外非伝播）|
| test_copy_empty_string | 空文字コピー → True |

### test_config_manager.py（6件）
| テスト名 | 検証内容 |
|---|---|
| test_get_setting_default | 未設定キー → デフォルト値 |
| test_set_and_get_setting | set → get 往復 |
| test_corrupted_config_fallback | 破損 JSON → デフォルト起動 |
| test_get_widget_config_default | デフォルトウィジェット設定 |
| test_get_widget_config_saved | 保存済み位置の復元 |
| test_credentials_persistence | 認証情報保存・読み込み |

---

## 失敗時の対応

1. `pytest tests/ -v --tb=short` でエラーの短いトレースを確認
2. `pytest tests/test_XXX.py::test_YYY -v -s` で単一テストを詳細実行
3. モック失敗の場合: `pytest-mock` バージョン確認 (`pip show pytest-mock`)
4. import エラーの場合: 仮想環境の有効化を確認

```bash
# デバッグ実行例
pytest tests/test_gemini_client.py -v -s --tb=long
```
