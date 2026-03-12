# Unit 2 フロントエンド刷新計画
## CustomTkinter → PyWebView + Svelte + Tailwind

作成日: 2026-03-13

---

## 概要

既存の CustomTkinter UI（`floating_widget.py`, `otter_animation_controller.py`）を
PyWebView + Svelte によるモダン Web フロントエンドに置き換える。

Unit 1 コアエンジン（`gemini_client.py`, `assistant_orchestrator.py` 等）は変更しない。

---

## 実装チェックリスト

### フェーズ A: 環境セットアップ
- [x] 1. `pip install pywebview` — PyWebView をインストール
- [x] 2. `npm create vite@latest ui -- --template svelte` — Svelte プロジェクト生成（`ui/` ディレクトリ）
- [x] 3. `npm install -D tailwindcss @tailwindcss/postcss` — Tailwind CSS インストール
- [x] 4. `npm install marked` — Markdown レンダリングライブラリ

### フェーズ B: Svelte UI 実装
- [x] 5. `ui/src/App.svelte` — メインコンポーネント（状態管理・レイアウト）
- [x] 6. `ui/src/lib/OtterChar.svelte` — Otter GIF 表示コンポーネント（状態別GIF切替）
- [x] 7. `ui/src/lib/ResponseArea.svelte` — AI応答エリア（Markdown描画）
- [x] 8. `ui/src/lib/InputArea.svelte` — テキスト入力・送信ボタン
- [x] 9. `ui/src/app.css` — Tailwind + グローバルスタイル（glassmorphism変数等）
- [x] 10. Svelte ビルド実行 (`npm run build`) → `ui/dist/` 生成

### フェーズ C: Python PyWebView ブリッジ実装
- [x] 11. `pywebview_widget.py` 新規作成 — FloatingWidget と同一インターフェース
    - `show()` / `hide()` / `is_visible()`
    - `set_state(state)` — JS の `window._otterSetState()` 呼び出し
    - `set_status_message(msg)` — JS の `window._otterSetStatus()` 呼び出し
    - `display_response(text)` — JS の `window._otterDisplayResponse()` 呼び出し
    - `get_last_response()` / `on_submit()` / `on_close()` / `on_copy()`
    - `after(ms, callback)` — tkinter 互換（スレッド安全な callback 実行）
    - JS API: `submit_text()`, `close_session()`, `copy_response()`

### フェーズ D: main.py 更新
- [x] 12. `main.py` を更新
    - `customtkinter` 依存を削除
    - `pywebview_widget.PyWebViewWidget` を使用
    - pywebview のイベントループで起動

### フェーズ E: クリーンアップ・動作確認
- [x] 13. `floating_widget.py` 削除
- [x] 14. `otter_animation_controller.py` 削除
- [ ] 15. `python3 main.py` で起動確認（要 Windows 環境）

---

## 設計詳細

### Python ↔ JS 通信

```
JS → Python:   window.pywebview.api.submit_text(text)  → Promise
Python → JS:   window.evaluate_js('window._otterSetState("THINKING")')
```

### 状態遷移

```
IDLE      → idle.gif     + 入力欄 enabled
THINKING  → thinking.gif + 入力欄 disabled  + ローディング表示
DONE      → done.gif(1回) → idle.gif + 応答表示 + Copyボタン表示
```

### UI ビジュアル設計

```
┌─────────────────────────────────────────┐  ← frameless, 角丸16px
│  backdrop-filter: blur(20px)            │    半透明ダーク背景
│  ┌──────────────────────────────────┐   │
│  │  [Otter GIF 80px]  Otter         │   │  ← ヘッダー (drag可能)
│  │                    Ready         │   │
│  └──────────────────────────────────┘   │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  AI応答（Markdown）              │   │  ← スクロール可能
│  │  スムーズフェードイン            │   │
│  └──────────────────────────────────┘   │
│                                         │
│  [Copy response]                        │
│  ┌──────────────────────────────────┐   │
│  │  入力テキスト...                 │   │  ← glassmorphism input
│  └──────────────────────────────────┘   │
│  [Paste]                    [Send ↵]   │
└─────────────────────────────────────────┘
```

### カラーパレット（継続）

| 変数 | 値 | 用途 |
|---|---|---|
| `--bg` | `#0e0e12` | 背景 |
| `--surface` | `#16161d` | カード |
| `--accent` | `#6c63ff` | 送信ボタン・ハイライト |
| `--text` | `#e8e8f0` | 本文 |
| `--text-sub` | `#7878a0` | サブテキスト |

---

## 影響範囲

| ファイル | 変更種別 |
|---|---|
| `floating_widget.py` | **削除** |
| `otter_animation_controller.py` | **削除** |
| `main.py` | **更新**（customtkinter → pywebview） |
| `pywebview_widget.py` | **新規作成** |
| `ui/` | **新規作成**（Svelte プロジェクト） |
| `gemini_client.py` | 変更なし |
| `assistant_orchestrator.py` | 変更なし |
| `session_manager.py` | 変更なし |
| `hotkey_manager.py` | 変更なし |
| その他 Unit 1 | 変更なし |
