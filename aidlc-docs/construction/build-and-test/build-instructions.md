# Build Instructions — Project Otter

## Prerequisites

### Build Tool
- **Python**: 3.11 以上
- **pip**: 23.0 以上（`python -m pip install --upgrade pip` で更新）

### システム要件
| 要件 | 内容 |
|---|---|
| OS | Windows 10/11（64-bit）|
| メモリ | 4GB 以上推奨 |
| ディスク | 500MB 以上（依存ライブラリ含む）|
| ネットワーク | Google OAuth 認証に必要（初回のみ）|

### 必要ファイル（事前準備）
- `client_secrets.json` — Google Cloud Console から取得し、`project-otter/` 直下に配置
  - 取得手順: [Google Cloud Console](https://console.cloud.google.com/) → 認証情報 → OAuth クライアントID → デスクトップアプリ → JSON ダウンロード

### 依存ライブラリ一覧

| パッケージ | バージョン | 用途 |
|---|---|---|
| pynput | >=1.7 | グローバルホットキー・マウス位置取得 |
| mss | >=9.0 | マルチモニター対応スクリーンキャプチャ |
| Pillow | >=10.0 | GIF アニメーション読み込み |
| google-generativeai | >=0.8 | Gemini API クライアント |
| google-auth | >=2.0 | OAuth 認証基盤 |
| google-auth-oauthlib | >=1.2 | OAuth フロー（InstalledAppFlow）|
| customtkinter | >=5.2 | モダン UI フレームワーク |
| pyperclip | >=1.8 | クリップボードコピー |
| tkinterweb | >=3.24 | マークダウン HTML レンダリング |
| markdown | >=3.6 | マークダウン → HTML 変換 |
| pytest | >=8.0 | テストフレームワーク |
| pytest-mock | >=3.12 | モックユーティリティ |
| ruff | >=0.4 | リンター・フォーマッター |

---

## Build Steps

### 1. リポジトリ移動

```bash
cd project-otter
```

### 2. 仮想環境作成（推奨）

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

### 3. 依存ライブラリインストール

```bash
pip install -r requirements.txt
```

### 4. tkinterweb 追加依存（Windows）

tkinterweb は内部で `tkhtml3` を使用。インストールに失敗した場合:

```bash
pip install tkinterweb --extra-index-url https://pypi.org/simple
```

失敗してもアプリは動作します（CTkTextbox フォールバックあり）。

### 5. リンター確認（任意）

```bash
ruff check .
ruff format --check .
```

### 6. ビルド成功確認

Python はインタープリタ言語のためコンパイル不要。構文チェックのみ実施:

```bash
python -c "import ast; [ast.parse(open(f).read()) for f in ['main.py','assistant_orchestrator.py','hotkey_manager.py','screen_capture_service.py','gemini_client.py','session_manager.py','floating_widget.py','otter_animation_controller.py','config_manager.py','clipboard_service.py']]"
echo "Syntax check passed"
```

---

## 起動確認

```bash
# client_secrets.json を配置した上で実行
python main.py
```

初回起動時: ブラウザが開き、Google アカウントでログイン → 認証後アプリが起動。

---

## トラブルシューティング

### ImportError: No module named 'customtkinter'

```bash
pip install customtkinter
```

### tkinterweb インストール失敗

- 無視して続行可（フォールバックあり）
- または `pip install tkinterweb` を単体で再試行

### `client_secrets.json が見つかりません` エラー

- Google Cloud Console から OAuth 2.0 クライアントID（デスクトップアプリ）を作成
- ダウンロードした JSON ファイルを `project-otter/client_secrets.json` にリネーム配置

### pynput でキーボードフックエラー（Linux）

```bash
sudo apt-get install python3-xlib
```

### mss でスクリーンキャプチャエラー

- Windows: 管理者権限不要（通常ユーザーで動作）
- 失敗時は `Null Object`（空キャプチャ）でフォールバック
