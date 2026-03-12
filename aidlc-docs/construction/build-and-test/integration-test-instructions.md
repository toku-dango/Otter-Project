# Integration Test Instructions — Project Otter

## 概要

Project Otter はシングルプロセス・デスクトップアプリのため、サービス間通信は存在しない。
統合テストは「コンポーネント間の協調動作」を手動シナリオで検証する。

---

## テストシナリオ

### Scenario 1: ホットキー → スクリーンキャプチャ → Gemini プリロード

**検証内容**: HotkeyManager → AssistantOrchestrator → ScreenCaptureService → GeminiClient の連携

**手順**:
1. `python main.py` で起動（初回 OAuth 認証完了済みであること）
2. 任意のウィンドウを前面に表示（例: メモ帳にテキストを入力）
3. `Ctrl+Shift+Space` を押下
4. ウィジェットが表示され、ステータスラベルに「画面を解析中...」が表示されることを確認
5. 2〜10秒以内にアニメーションが IDLE に戻ることを確認

**期待結果**:
- ウィジェットが画面右下付近に表示される
- 🦦💭 → 🦦 のアニメーション遷移（GIF 非配置時は絵文字）
- ログ（`~/.config/project-otter/app.log`）に `preload_context succeeded` が記録

---

### Scenario 2: 質問入力 → Gemini 応答 → マークダウン表示

**検証内容**: FloatingWidget → AssistantOrchestrator → GeminiClient → FloatingWidget.display_response()

**手順**:
1. Scenario 1 完了後、ウィジェットのテキスト入力欄に「この画面を一言で説明して」と入力
2. Enter キーを押下（または「送信」ボタンクリック）
3. 入力欄が disabled になり、ステータスラベルが「考え中...」になることを確認
4. 応答が返ったら応答エリアに表示されることを確認

**期待結果**:
- マークダウン（`**太字**`、`\`コード\`` 等）が適切にレンダリングされる
- 「コピー」ボタンが表示される
- 🦦✨ のアニメーション後 🦦 に戻る

---

### Scenario 3: コピーボタン → クリップボード

**検証内容**: FloatingWidget → ClipboardService → pyperclip

**手順**:
1. Scenario 2 で応答が表示された状態
2. 「コピー」ボタンをクリック
3. ボタンテキストが「✓ コピーしました」に変わることを確認（1秒後に元に戻る）
4. メモ帳等に貼り付け（Ctrl+V）して応答テキストが貼り付けられることを確認

**期待結果**:
- クリップボードに応答テキスト全文がコピーされている
- 1000ms 後にボタンテキストが「コピー」に戻る

---

### Scenario 4: ウィジェット移動 → 位置永続化

**検証内容**: FloatingWidget ドラッグ → ConfigManager → config.json

**手順**:
1. ウィジェットのヘッダー部分をドラッグして移動
2. `python main.py` を終了（Ctrl+C）
3. 再起動
4. ウィジェットが前回の位置に表示されることを確認

**期待結果**:
- `~/.config/project-otter/config.json` に `widget_x`, `widget_y` が保存されている
- 再起動後も同じ位置に表示される

---

### Scenario 5: ホットキー再押下（確認ダイアログ）

**検証内容**: BR-01 — ウィジェット表示中の再押下 → 確認ダイアログ

**手順**:
1. ウィジェットを表示した状態
2. 再度 `Ctrl+Shift+Space` を押下
3. 確認ダイアログ（「新しいセッションを開始しますか？」）が表示されることを確認
4. 「はい」を選択 → 新しいキャプチャが実行される
5. 「いいえ」を選択 → ダイアログが閉じてウィジェットはそのまま

**期待結果**:
- 「はい」: セッションリセット + 新規プリロード
- 「いいえ」: 何も変化しない

---

### Scenario 6: 最小化・復元

**検証内容**: BR-U2-02 — ウィジェットの最小化

**手順**:
1. ウィジェットを表示した状態
2. 「▼」ボタンをクリック → ウィジェットが高さ 50px に縮小
3. 「▲」ボタンをクリック → 元の高さに復元

**期待結果**:
- 最小化: ヘッダーのみ表示、コンテンツ非表示
- 復元: 応答・入力エリアが再表示

---

## ログ確認

```bash
# リアルタイムログ確認（PowerShell）
Get-Content "$env:USERPROFILE\.config\project-otter\app.log" -Wait -Tail 20

# Linux/macOS
tail -f ~/.config/project-otter/app.log
```

---

## 環境クリーンアップ（テスト後）

```bash
# 設定リセット（位置情報・設定値を初期化したい場合）
Remove-Item "$env:USERPROFILE\.config\project-otter\config.json"  # Windows
rm ~/.config/project-otter/config.json  # Linux/macOS

# OAuth 認証をリセットしたい場合（再認証が必要になる）
Remove-Item "$env:USERPROFILE\.config\project-otter\credentials.json"  # Windows
rm ~/.config/project-otter/credentials.json  # Linux/macOS
```
