# NFR Requirements — Unit 1: Core Engine

## パフォーマンス要件

| NFR-ID | 要件 | 目標値 | 計測方法 |
|---|---|---|---|
| PERF-01 | ホットキー押下 → ウィジェット表示 | 500ms 以内 | 手動計測（Ctrl+Shift+Space → UI表示） |
| PERF-02 | アイドル時 CPU 使用率 | 1% 以下 | タスクマネージャーで確認 |
| PERF-03 | ユーザー入力 → 応答表示（APIレイテンシ除く） | 500ms 以内 | ログのタイムスタンプ差分 |
| PERF-04 | アプリ起動時間 | 3秒 以内 | main.py 実行 → ホットキー登録完了まで |
| PERF-05 | メモリ使用量（アイドル時） | 200MB 以下 | タスクマネージャーで確認 |

---

## 信頼性要件

| NFR-ID | 要件 | 詳細 |
|---|---|---|
| REL-01 | API リトライ | 最大3回・指数バックオフ（1s, 2s, 4s）|
| REL-02 | タイムアウト（preload） | 10秒 |
| REL-03 | タイムアウト（generate） | 30秒 |
| REL-04 | ホットキー登録解除 | アプリ終了時（正常・異常問わず）に必ず `unregister()` を実行 |
| REL-05 | スレッド安全性 | バックグラウンドスレッドからの UI 操作は `widget.after(0, fn)` 経由のみ |
| REL-06 | 認証トークン自動更新 | リフレッシュトークンで期限切れを自動対応 |

---

## セキュリティ要件

| NFR-ID | 要件 | 詳細 |
|---|---|---|
| SEC-01 | 認証情報保存 | Google OAuth Credentials を `~/.config/project-otter/credentials.json` に保存。ファイルパーミッション 600（所有者のみ読み書き）|
| SEC-02 | スクリーンキャプチャ | 画像はメモリ上のみで処理。Base64 文字列として Gemini API に送信後、参照を破棄する。ディスクへの書き込みなし |
| SEC-03 | セッションデータ | 会話履歴はメモリ上のみ。アプリ終了時に GC に委ねる。ディスクへの書き込みなし |
| SEC-04 | ログの機密情報 | スクリーンキャプチャの Base64 データ・会話テキストはログに出力しない。APIレスポンスの先頭50文字のみ DEBUG ログに出力可 |
| SEC-05 | キャプチャ免除 | MVP スコープでは除外リストなし（ユーザー責任）。将来の拡張ポイントとして設計に余地を残す |

---

## 可用性要件

| NFR-ID | 要件 | 詳細 |
|---|---|---|
| AVAIL-01 | デスクトップアプリ | サーバー不要。インターネット接続があれば動作 |
| AVAIL-02 | オフライン時 | ホットキーは受け付けるが「ネットワークエラー」を表示。アプリはクラッシュしない |
| AVAIL-03 | 異常終了対応 | `signal.signal(SIGINT/SIGTERM)` でシグナルキャッチ → `orchestrator.stop()` を呼び出してホットキーを解除してから終了 |

---

## 保守性要件

| NFR-ID | 要件 | 詳細 |
|---|---|---|
| MAINT-01 | ログ出力 | Python 標準 `logging` モジュール使用。DEBUG レベル以上をファイル保存 |
| MAINT-02 | ログ保存先 | `~/.config/project-otter/app.log` |
| MAINT-03 | ログローテーション | `RotatingFileHandler`（最大 5MB × 3ファイル） |
| MAINT-04 | ログフォーマット | `%(asctime)s [%(levelname)s] %(name)s: %(message)s` |
| MAINT-05 | テスト対象 | `GeminiClient`・`SessionManager` のコアロジック（モックを使用） |
| MAINT-06 | テストフレームワーク | `pytest` + `unittest.mock` |
| MAINT-07 | コードスタイル | `ruff` でリント・フォーマット |

---

## 環境要件

| NFR-ID | 要件 | 詳細 |
|---|---|---|
| ENV-01 | ターゲットOS | Windows 10 / 11（64bit）|
| ENV-02 | Python バージョン | 3.11 以上 |
| ENV-03 | 配布形式 | MVP は Python 実行環境（`python main.py`）。将来的に PyInstaller で `.exe` 化 |
