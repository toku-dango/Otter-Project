# Build and Test Summary — Project Otter

## Build 情報

| 項目 | 内容 |
|---|---|
| ビルドツール | pip + Python インタープリタ（コンパイル不要） |
| 対象 Python | 3.11 以上 |
| 依存解決コマンド | `pip install -r requirements.txt` |
| 構文チェックコマンド | `python -c "import ast; ..."` |
| リンターコマンド | `ruff check . && ruff format --check .` |
| ビルドアーティファクト | なし（スクリプト実行型）|

---

## テスト実行サマリー

### ユニットテスト

| テストスイート | テスト数 | 期待ステータス |
|---|---|---|
| test_session_manager.py | 9 | ✅ PASS |
| test_gemini_client.py | 6 | ✅ PASS |
| test_assistant_orchestrator.py | 9 | ✅ PASS |
| test_clipboard_service.py | 3 | ✅ PASS |
| test_config_manager.py | 6 | ✅ PASS |
| **合計** | **33** | **全件 PASS 期待** |

```bash
# 実行コマンド
pytest tests/ -v
```

### 統合テスト

| シナリオ | 検証対象 | テスト種別 |
|---|---|---|
| Scenario 1 | ホットキー → キャプチャ → プリロード | 手動 |
| Scenario 2 | 質問入力 → 応答 → MD 表示 | 手動 |
| Scenario 3 | コピーボタン → クリップボード | 手動 |
| Scenario 4 | ドラッグ移動 → 位置永続化 | 手動 |
| Scenario 5 | ホットキー再押下 → 確認ダイアログ | 手動 |
| Scenario 6 | 最小化・復元 | 手動 |

### 性能テスト

| 指標 | 目標値 | テスト方法 |
|---|---|---|
| ホットキー → 表示 | < 500ms | 目視計測 |
| スクリーンキャプチャ | < 2s | `perf_capture.py` |
| アプリ起動時間 | < 3s | PowerShell Stopwatch |
| メモリ使用量 | < 200MB | タスクマネージャー |

---

## 生成ファイル一覧

| ファイル | 内容 |
|---|---|
| `build-instructions.md` | 依存インストール・構文チェック・トラブルシューティング |
| `unit-test-instructions.md` | pytest 実行手順・33件テスト詳細 |
| `integration-test-instructions.md` | 6シナリオ手動統合テスト手順 |
| `performance-test-instructions.md` | レスポンスタイム・メモリ計測手順 |
| `build-and-test-summary.md` | 本ファイル |

---

## 全体ステータス

| カテゴリ | ステータス |
|---|---|
| ビルド（依存解決・構文）| ✅ Ready |
| ユニットテスト | ✅ 33件 定義済み・実行可能 |
| 統合テスト | ✅ 6シナリオ 手順定義済み |
| 性能テスト | ✅ 計測手順定義済み |
| **Operations 移行可否** | **✅ Yes** |

---

## クイックスタート（全テスト実行）

```bash
# 1. 環境構築
cd project-otter
python -m venv .venv && .venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. ユニットテスト（自動）
pytest tests/ -v

# 3. 統合テスト（手動）
# → integration-test-instructions.md の Scenario 1〜6 を順番に実施
python main.py

# 4. 性能テスト（手動）
python tests/perf_capture.py
```

---

## 次のステップ

CONSTRUCTION フェーズ完了。Operations フェーズ（デプロイ計画）に移行可能。

**MVP 動作に必要な手動作業**:
1. `client_secrets.json` を `project-otter/` に配置（Google Cloud Console から取得）
2. `assets/` に GIF ファイルを配置（任意 — 省略時は絵文字プレースホルダー）
3. `python main.py` で起動 → 初回 OAuth ブラウザ認証を完了
