# NFR Design Plan — Unit 2: UI & Configuration

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
| Fallback Chain | tkinterweb → CTkTextbox / GIF → 絵文字 / config.json 破損 → デフォルト |
| Debounce | リサイズイベントの config.json 保存 |
| Observer（コールバック） | on_submit / on_close / on_copy |
| Null Object | ClipboardService の失敗時（bool を返し例外を上げない） |
