# Logical Components — Unit 1: Core Engine

## 概要

Unit 1 はデスクトップアプリケーションであり、外部インフラ（クラウド・キュー・DBなど）を持たない。
論理コンポーネントはローカルファイルシステムと外部APIのみで構成される。

---

## 論理コンポーネント図

```
[Windows OS]
  |
  +-- [pynput グローバルキーフック]
  |       |
  |       v
  +-- [Project Otter プロセス]
  |       |
  |       +-- AssistantOrchestrator（Facade）
  |       |     |
  |       |     +-- HotkeyManager（pynputスレッド）
  |       |     +-- ScreenCaptureService（mss）
  |       |     |       |
  |       |     |       v
  |       |     |   [アクティブモニター画像]
  |       |     |
  |       |     +-- GeminiClient
  |       |     |       |
  |       |     |       v（HTTPS）
  |       |     |   [Gemini API]
  |       |     |
  |       |     +-- SessionManager（メモリ）
  |       |     +-- ConfigManager
  |       |             |
  |       |             v
  |       |         [ローカルファイルシステム]
  |       |           ~/.config/project-otter/
  |       |             credentials.json  ← OAuth トークン
  |       |             config.json       ← アプリ設定
  |       |             app.log           ← ログ（RotatingFileHandler）
  |       |
  |       +-- [メインスレッド: tkinter イベントループ]
  |       +-- [バックグラウンドスレッド: API呼び出し]
  |       +-- [pynput スレッド: ホットキー監視]
```

---

## ローカルファイルシステム

| パス | 種別 | 内容 | 書き込みタイミング |
|---|---|---|---|
| `~/.config/project-otter/credentials.json` | 認証情報 | Google OAuth Credentials（トークン・リフレッシュトークン） | 初回ログイン時・トークン更新時 |
| `~/.config/project-otter/config.json` | 設定 | ウィジェット位置・ホットキー設定等 | 設定変更時 |
| `~/.config/project-otter/app.log` | ログ | アプリケーションログ（DEBUG以上） | 随時（RotatingFileHandler） |

**セキュリティ**:
- `credentials.json` はパーミッション 600（所有者のみ読み書き）で作成する
- `config.json` / `app.log` はパーミッション 644 で作成する

---

## 外部サービス

| サービス | 接続方式 | 認証 | タイムアウト |
|---|---|---|---|
| Gemini API | HTTPS / google-generativeai SDK | Google OAuth Credentials | preload: 10秒 / generate: 30秒 |
| Google OAuth エンドポイント | HTTPS / google-auth-oauthlib | OAuthフロー（初回のみ） | ライブラリデフォルト |

---

## スレッド構成

| スレッド | 管理者 | 役割 | UI操作 |
|---|---|---|---|
| メインスレッド | tkinter | UIイベントループ・widget.after()コールバック処理 | 直接可 |
| バックグラウンドスレッド | threading.Thread（daemon=True） | preload_context / generate_response の実行 | 不可・after()経由のみ |
| pynputスレッド | pynput 内部 | グローバルホットキー監視 | 不可・after()経由のみ |

---

## 起動時の初期化順序

```
1. logging 設定（RotatingFileHandler）
2. ConfigManager 初期化
3. Google OAuth 認証確認 / 実行
4. GeminiClient 初期化（Credentials を渡す）
5. HotkeyManager 初期化
6. SessionManager 初期化（永続セッション開始）
7. FloatingWidget 初期化（Unit 2）
8. AssistantOrchestrator.start()
   8a. シグナルハンドラ登録（SIGINT / SIGTERM）
   8b. HotkeyManager.register()
   8c. tkinter メインループ開始（ブロッキング）
```

---

## 終了時のクリーンアップ順序

```
1. シグナル受信 or ウィンドウ閉じる
2. AssistantOrchestrator.stop()
   2a. HotkeyManager.unregister()  ← 必須（ホットキー残留防止）
   2b. SessionManager.end_session() ← メモリ解放
   2c. FloatingWidget.destroy()
3. プロセス終了
```
