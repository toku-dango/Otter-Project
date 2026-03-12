# Services — Project Otter

## サービス概要

Project Otter のサービス層は **AssistantOrchestrator** 1つで構成されます。
MVP はシングルプロセスのデスクトップアプリのため、マイクロサービス分割は不要です。

---

## AssistantOrchestrator — メインサービス

### 役割
全コンポーネントの初期化・接続・イベントフロー制御を担うアプリケーションの司令塔。

### 2つのメインフロー

---

### フロー 1: ホットキー起動 → AI事前把握（Pre-load）

```
[ユーザー] Ctrl+Shift+Space 押下
    |
    v
HotkeyManager.callback()
    |
    v
AssistantOrchestrator.on_hotkey_triggered()
    |
    +---> FloatingWidget.show()
    |     FloatingWidget.set_state(THINKING)
    |     OtterAnimationController.play(THINKING)
    |
    +---> ScreenCaptureService.capture()
    |         |
    |         v
    |     [成功] image_base64 取得
    |         |
    |         v
    +---> GeminiClient.preload_context(image_base64)
    |         |
    |         v
    |     [Reasoning完了] context_summary + chat_session 取得
    |         |
    |         v
    +---> SessionManager.start_session(chat_session)
    |
    +---> FloatingWidget.set_state(IDLE)
          FloatingWidget.set_status_message("画面を確認しました")
          OtterAnimationController.play(IDLE)
          → ユーザー入力待ち
```

---

### フロー 2: ユーザー入力 → 応答生成

```
[ユーザー] テキスト入力 → 送信
    |
    v
FloatingWidget.on_submit(text)
    |
    v
AssistantOrchestrator.on_user_input(text)
    |
    +---> FloatingWidget.set_state(THINKING)
    |     OtterAnimationController.play(THINKING)
    |
    +---> GeminiClient.generate_response(text, chat_session)
    |         |
    |         v
    |     [応答生成完了] response_text 取得
    |
    +---> SessionManager.add_exchange(user_input, response_text)
    |
    +---> FloatingWidget.display_response(response_text)
          FloatingWidget.set_state(DONE)
          OtterAnimationController.play(DONE)
          → DONE アニメ完了後 IDLE に自動遷移
```

---

### フロー 3: コピー

```
[ユーザー] コピーボタン クリック
    |
    v
FloatingWidget.on_copy()
    |
    v
AssistantOrchestrator → ClipboardService.copy(last_response)
    |
    v
FloatingWidget.set_status_message("コピーしました")
```

---

### フロー 4: セッション終了

```
[ユーザー] ウィジェット閉じる
    |
    v
FloatingWidget.on_close()
    |
    v
AssistantOrchestrator.on_session_close()
    |
    +---> SessionManager.end_session()  ← 履歴消去
    +---> FloatingWidget.hide()
    +---> OtterAnimationController.stop()
```

---

### フロー 5: エラーハンドリング

```
エラー発生（APIエラー・キャプチャ失敗等）
    |
    v
AssistantOrchestrator._handle_error(error, context)
    |
    +---> FloatingWidget.set_state(IDLE)
    +---> FloatingWidget.set_status_message("[わかりやすいエラーメッセージ]")
    +---> OtterAnimationController.play(IDLE)
```

---

## 初回起動フロー（APIキー未設定時）

```
main.py 起動
    |
    v
AssistantOrchestrator.start()
    |
    v
ConfigManager.has_api_key()
    |
    +--[No]--> APIキー設定ダイアログ表示
    |               ユーザーがAPIキーを入力
    |               ConfigManager.set_api_key(key)
    |               GeminiClient.is_available() で確認
    |
    +--[Yes]--> HotkeyManager.register()
               通常起動完了（システムトレイ常駐）
```
