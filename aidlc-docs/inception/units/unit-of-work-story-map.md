# Unit of Work Story Map — Project Otter

## ストーリーマップ（MVP）

### Unit 1: Core Engine — 担当ストーリー

| US ID | タイトル | 関連コンポーネント | 優先度 |
|---|---|---|---|
| US-01 | ホットキーで即時起動 | HotkeyManager, AssistantOrchestrator | 最高 |
| US-03 | 起動時に画面自動把握 | ScreenCaptureService, GeminiClient, AssistantOrchestrator | 最高 |
| US-04 | 代名詞だけで対象特定 | GeminiClient（Reasoning活用） | 高 |
| US-05 | 短い指示でメール改善 | GeminiClient, AssistantOrchestrator | 最高 |
| US-08 | コーディング中起動 | HotkeyManager（フォーカス維持） | 高 |
| US-09 | GitHub PR文脈把握 | ScreenCaptureService, GeminiClient | 高 |
| US-10 | PR説明文改善 | GeminiClient | 高 |
| US-13 | Notion議事録把握 | ScreenCaptureService, GeminiClient | 中 |
| US-14 | 議事録からメール生成 | GeminiClient | 中 |
| US-16 | PowerPointスライド把握 | ScreenCaptureService, GeminiClient | 中 |
| US-17 | スライド冒頭メッセージ改善 | GeminiClient | 中 |
| US-19 | 一言指示でトーン調整 | GeminiClient, AssistantOrchestrator | 高 |

**MVPストーリー数: 12件**

---

### Unit 2: UI & Configuration — 担当ストーリー

| US ID | タイトル | 関連コンポーネント | 優先度 |
|---|---|---|---|
| US-01 | ホットキーで即時起動（UI側） | FloatingWidget（表示） | 最高 |
| US-02 | ウィジェットを任意位置に移動 | FloatingWidget（ドラッグ・最小化） | 高 |
| US-06 | 応答をワンクリックコピー | ClipboardService, FloatingWidget（コピーボタン） | 高 |
| US-08 | コーディング中起動（UI側） | FloatingWidget（配置制御） | 高 |
| US-18 | 追加設定なし即時利用 | ConfigManager（初回設定UI）, FloatingWidget | 高 |

**MVPストーリー数: 5件（US-01・US-08はUnit 1と共同）**

---

### Step 2 ストーリー（将来対応）

| US ID | タイトル | 担当Unit | 関連コンポーネント |
|---|---|---|---|
| US-07 | 画面移動後も文脈継続 | Unit 1 | SessionManager（履歴保持強化） |
| US-11 | コードレビュー文脈継続 | Unit 1 | SessionManager |
| US-12 | 音声で指示入力 | Unit 2 + Unit 1 新規 | FloatingWidget（マイクボタン）+ 新規VoiceInputService |
| US-15 | ツール横断で文脈継続 | Unit 1 | SessionManager |

---

## MVP完成基準

すべてのMVPストーリーの受け入れ条件を満たし、以下のエンドツーエンドフローが動作すること：

```
Ctrl+Shift+Space
  → 500ms以内にFloatingWidget表示
  → 画面自動取得・Gemini事前把握（「画面を確認しました」表示）
  → ユーザーが短い指示入力（例：「丁寧に」）
  → AI応答表示（3秒以内、APIレイテンシ除く）
  → コピーボタンでクリップボードに保存
  → 元のアプリに貼り付け完了
```

## ユニット別ビルド順序（同時並行）

```
Week 1-2:  [Unit 1] HotkeyManager + ScreenCaptureService
           [Unit 2] FloatingWidget骨格 + ConfigManager

Week 3-4:  [Unit 1] GeminiClient + SessionManager
           [Unit 2] OtterAnimationController + ClipboardService

Week 5-6:  [Unit 1] AssistantOrchestrator（モック統合）
           [Unit 2] FloatingWidget完成（全状態対応）

Week 7:    統合テスト（main.py）+ Build and Test
```
