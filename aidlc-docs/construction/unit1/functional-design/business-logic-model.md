# Business Logic Model — Unit 1: Core Engine

## フロー概要

Unit 1 は以下の5つの主要フローで構成される。

| フロー ID | 名称 | トリガー |
|---|---|---|
| FL-01 | アプリケーション起動 | main.py 実行 |
| FL-02 | ホットキー起動（ウィジェット非表示時） | Ctrl+Shift+Space |
| FL-03 | ホットキー再押下（ウィジェット表示中） | Ctrl+Shift+Space |
| FL-04 | ユーザー入力処理 | テキスト送信 |
| FL-05 | エラーハンドリング | 各フロー内例外発生時 |

---

## FL-01: アプリケーション起動フロー

```
main.py
  |
  +--> ConfigManager 初期化
  |      |
  |      +--> Google認証トークン確認（has_valid_credentials()）
  |             |
  |      [未認証] +--> ブラウザを開いてGoogle OAuthログイン実行
  |             |         google-auth-oauthlib でフロー実行
  |             |         認証完了 → トークンをローカルにキャッシュ保存
  |             |         （~/.config/project-otter/credentials.json）
  |      [認証済] |         トークンが期限切れの場合は自動リフレッシュ
  |             v
  +--> GeminiClient 初期化（Credentials オブジェクトを渡す）
  +--> HotkeyManager 初期化
  +--> SessionManager 初期化（永続セッション開始）
  +--> FloatingWidget 初期化（非表示状態）
  +--> AssistantOrchestrator.start()
         |
         +--> HotkeyManager.register(callback=on_hotkey_triggered)
         +--> tkinter メインループ開始
```

**永続セッション**: アプリ起動時に `SessionManager.start_session()` を1回呼び出す。このセッションはアプリ終了まで継続する。

**認証キャッシュ**: `google-auth` ライブラリがトークンをローカルファイルに保存する。2回目以降の起動ではブラウザを開かずにキャッシュを利用。トークン期限切れ時はリフレッシュトークンで自動更新する。

---

## FL-02: ホットキー起動フロー（ウィジェット非表示時）

```
[Ctrl+Shift+Space 押下]
  |
  v
HotkeyManager（pynput バックグラウンドスレッド）
  |
  +--> AssistantOrchestrator.on_hotkey_triggered() 呼び出し
         |
         +--> widget.is_visible() == False を確認
         |
         +--> widget.set_state(THINKING)
         +--> widget.set_status_message("画面を確認中...")
         +--> widget.show()
         |
         +--> [バックグラウンドスレッド起動]
                |
                +--> ScreenCaptureService.capture()
                |      |--> マウスカーソルのあるモニターを取得
                |      |--> mss でキャプチャ
                |      |--> PIL Image → Base64 変換
                |      +--> CaptureResult 返却
                |
                +--> [キャプチャ成功時]
                |      |
                |      +--> GeminiClient.preload_context(image_base64)
                |             |--> タイムアウト: 10秒
                |             |--> 失敗時: 最大3回リトライ（指数バックオフ: 1s, 2s, 4s）
                |             +--> PreloadResult 返却
                |
                +--> [widget.after(0, _on_preload_complete)] でUIスレッドに通知
                       |
                  [成功時] +--> widget.set_state(IDLE)
                  |         +--> widget.set_status_message("画面を確認しました ✓")
                  |
                  [失敗時] +--> widget.set_state(IDLE)
                            +--> widget.set_status_message("画面取得に失敗しました。テキスト入力で相談できます")
```

**制約**: ホットキーコールバックは pynput のバックグラウンドスレッドで実行される。tkinter UI 操作は `widget.after(0, fn)` 経由でメインスレッドに渡す。

---

## FL-03: ホットキー再押下フロー（ウィジェット表示中）

```
[Ctrl+Shift+Space 押下]
  |
  v
AssistantOrchestrator.on_hotkey_triggered()
  |
  +--> widget.is_visible() == True を確認
  |
  +--> [UIスレッドで] 終了確認ダイアログ表示
         |
         メッセージ: "セッションを終了しますか？\n会話履歴は消去されません。"
         ボタン: [はい（閉じる）] / [キャンセル]
         |
    [はい] +--> widget.hide()
    |
    [キャンセル] +--> 何もしない（ウィジェット継続表示）
```

**注意**: セッション（会話履歴）は「アプリ起動中は継続」のため、ウィジェットを閉じても履歴は保持される。次回ホットキー押下時に画面再キャプチャ・事前把握は再実行されるが、会話履歴は引き継がれる。

---

## FL-04: ユーザー入力処理フロー

```
[ユーザーがテキスト入力して送信]
  |
  v
FloatingWidget.on_submit コールバック
  |
  +--> AssistantOrchestrator.on_user_input(text)
         |
         +--> 入力バリデーション（空文字チェック）
         +--> widget.set_state(THINKING)
         +--> widget.set_status_message("考え中...")
         |
         +--> [バックグラウンドスレッド起動]
                |
                +--> GeminiClient.generate_response(text, chat_session)
                |      |--> タイムアウト: 30秒（応答生成はpreloadより長い）
                |      |--> 失敗時: 最大3回リトライ（指数バックオフ: 1s, 2s, 4s）
                |      +--> response_text: str 返却
                |
                +--> SessionManager.add_exchange(session_id, text, response_text)
                |
                +--> [widget.after(0, _on_response_complete)] でUIスレッドに通知
                       |
                  [成功時] +--> widget.set_state(DONE)
                  |         +--> widget.display_response(response_text)
                  |
                  [失敗時] +--> widget.set_state(IDLE)
                            +--> widget.display_response("応答の生成に失敗しました。もう一度お試しください。")
```

---

## FL-05: エラーハンドリングフロー

```
AssistantOrchestrator._handle_error(error, context)
  |
  +--> エラー種別判定
         |
    [APIKeyError]    → "APIキーが無効です。設定を確認してください。"
    [TimeoutError]   → "応答がタイムアウトしました。ネットワークをご確認ください。"
    [RateLimitError] → "API制限に達しました。しばらく待ってからお試しください。"
    [CaptureError]   → "画面取得に失敗しました。テキスト入力で相談できます。"
    [NetworkError]   → "ネットワークエラーが発生しました。接続をご確認ください。"
    [その他]         → "エラーが発生しました。アプリを再起動してください。"
  |
  +--> widget.set_state(IDLE)
  +--> widget.set_status_message(error_message)  ← 専門用語を使わない日本語
```

---

## スレッドモデル

```
メインスレッド（tkinter イベントループ）
  ├── FloatingWidget UI 操作
  ├── HotkeyManager コールバック受信（after() 経由）
  └── widget.after(0, fn) で受け取ったコールバック実行

バックグラウンドスレッド（threading.Thread）
  ├── preload_context 実行（FL-02）
  └── generate_response 実行（FL-04）

pynput スレッド（内部）
  └── ホットキー検出 → orchestrator.on_hotkey_triggered() 呼び出し
      （tkinter 操作は必ず widget.after() 経由でメインスレッドに渡す）
```
