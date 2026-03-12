# NFR Design Plan — Unit 1: Core Engine

## チェックリスト

### PART 1: Planning
- [x] Step 1: NFR Requirements 分析
- [x] Step 2: NFR Design 計画作成
- [x] Step 3: 質問生成（追加質問なし — NFR要件が十分明確）
- [x] Step 4: 計画保存

### PART 2: Generation
- [x] Step 6: NFR Design アーティファクト生成
  - [x] nfr-design-patterns.md
  - [x] logical-components.md
- [ ] Step 7: 完了メッセージ提示
- [ ] Step 8: 承認待ち

## 適用するデザインパターン

| パターン | 適用箇所 |
|---|---|
| Retry with Exponential Backoff | GeminiClient API 呼び出し |
| Background Thread + Callback | AssistantOrchestrator 非同期処理 |
| Observer（コールバック） | HotkeyManager → AssistantOrchestrator |
| Facade | AssistantOrchestrator（全コンポーネントの統合窓口） |
| Null Object | CaptureResult / PreloadResult（失敗時の安全な返却値） |
