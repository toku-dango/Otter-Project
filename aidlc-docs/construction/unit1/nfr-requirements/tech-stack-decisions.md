# Tech Stack Decisions — Unit 1: Core Engine

## 言語・ランタイム

| 項目 | 決定 | 理由 |
|---|---|---|
| 言語 | Python 3.11+ | 型ヒント強化・`tomllib`標準化・パフォーマンス改善 |
| OS | Windows 10/11（64bit） | MVP スコープ |

---

## Unit 1 依存ライブラリ

| ライブラリ | バージョン | 用途 | 選定理由 |
|---|---|---|---|
| `pynput` | `>=1.7` | グローバルホットキー検出 | Windows でのグローバルキー監視に最も実績のある軽量ライブラリ |
| `mss` | `>=9.0` | スクリーンキャプチャ | PIL/pyautogui より高速。Windows マルチモニター対応が容易 |
| `Pillow` | `>=10.0` | 画像処理・Base64変換 | Python 画像処理のデファクトスタンダード |
| `google-generativeai` | `>=0.8` | Gemini API 通信 | Google 公式 SDK。Credentials オブジェクトを直接渡せる |
| `google-auth` | `>=2.0` | OAuth2 Credentials 管理・トークンリフレッシュ | google-generativeai が内部で依存。Credentials キャッシュ管理 |
| `google-auth-oauthlib` | `>=1.2` | OAuth2 ブラウザフロー | ローカルサーバー経由の OAuth 認証フローを簡潔に実装できる |

---

## テスト・品質ツール

| ツール | バージョン | 用途 |
|---|---|---|
| `pytest` | `>=8.0` | テストランナー |
| `pytest-mock` | `>=3.12` | `unittest.mock` を pytest スタイルで使用 |
| `ruff` | `>=0.4` | リント・フォーマット（`black` + `flake8` の代替） |

---

## ログ設定

```python
# logging 設定（main.py または config_logging.py）
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path.home() / ".config" / "project-otter"
LOG_DIR.mkdir(parents=True, exist_ok=True)

handler = RotatingFileHandler(
    LOG_DIR / "app.log",
    maxBytes=5 * 1024 * 1024,  # 5MB
    backupCount=3,
    encoding="utf-8",
)
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))

logging.basicConfig(level=logging.DEBUG, handlers=[handler])
```

**注意**: スクリーンキャプチャの Base64 データ・会話テキスト全文はログに出力しない（SEC-04）。

---

## requirements.txt（Unit 1 分）

```
# Core Engine (Unit 1)
pynput>=1.7
mss>=9.0
Pillow>=10.0
google-generativeai>=0.8
google-auth>=2.0
google-auth-oauthlib>=1.2

# Testing & Quality
pytest>=8.0
pytest-mock>=3.12
ruff>=0.4
```

---

## テスト対象・方針

### テスト対象（B: コアロジックのみ）

| コンポーネント | テスト内容 |
|---|---|
| `GeminiClient` | `preload_context` / `generate_response` のモックテスト（API呼び出しをモック） |
| `SessionManager` | `start_session` / `end_session` / `add_exchange` / `get_session` の状態管理テスト |
| `AssistantOrchestrator` | `on_hotkey_triggered` / `on_user_input` のフロー（FloatingWidget・GeminiClient をモック） |

### テスト対象外（MVP では省略）

| コンポーネント | 理由 |
|---|---|
| `HotkeyManager` | OS依存・手動確認で十分 |
| `ScreenCaptureService` | 実画面依存・手動確認で十分 |
| `ConfigManager` | ファイルI/O・手動確認で十分 |

### テストファイル配置

```
project-otter/
  tests/
    test_gemini_client.py
    test_session_manager.py
    test_assistant_orchestrator.py
```
