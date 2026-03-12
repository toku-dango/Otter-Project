# Functional Design Plan — Unit 2: UI & Configuration

## チェックリスト

### PART 1: Planning
- [x] Step 1: ユニットコンテキスト分析
- [x] Step 2: 計画作成
- [x] Step 3: 質問生成
- [x] Step 4: 計画保存
- [x] Step 5: 回答収集・分析

### PART 2: Generation
- [x] Step 6: Functional Design アーティファクト生成
  - [x] business-logic-model.md
  - [x] business-rules.md
  - [x] domain-entities.md
  - [x] frontend-components.md
- [ ] Step 7: 完了メッセージ提示
- [ ] Step 8: 承認待ち

---

## ユニット概要（再掲）

| 項目 | 内容 |
|---|---|
| Unit ID | Unit 2 |
| 名称 | UI & Configuration |
| コンポーネント | FloatingWidget, OtterAnimationController, ConfigManager, ClipboardService |
| 担当ストーリー | US-01（UI側）, US-02, US-06, US-08（UI側）, US-18（MVP 5件） |

---

## 質問

以下の質問に回答してください。完了したら「done」とお知らせください。

---

## Question 1
**FloatingWidget のデフォルト表示位置**はどこにしますか？

A) 画面右下（タスクバー付近）
B) 画面中央
C) 前回終了時の位置を記憶して復元（初回は右下）
D) Other (please describe after [Answer]: tag below)

[Answer]:A ドラッグして動かせるように

---

## Question 2
**ウィジェットのサイズ**はどうしますか？

A) 固定サイズ（例：幅400px × 高さ500px）
B) ユーザーがリサイズ可能
C) 状態によって自動的に縦方向に伸縮（応答テキストに合わせる）
D) Other (please describe after [Answer]: tag below)

[Answer]:B

---

## Question 3
**Otter アニメーション用 GIF** はどうしますか？（現時点でアセットは存在しません）

A) プレースホルダー（静止画アイコン）で実装し、GIF は後から差し替え
B) シンプルな色変化アニメーション（Pillow で生成）でダミー実装
C) GIF ファイルを先に用意してから実装する（開発を一時停止）
D) Other (please describe after [Answer]: tag below)

[Answer]:Aだけど、見栄えとか雰囲気悪い？

---

## Question 4
**応答テキストエリア**の表示仕様は？

A) スクロール可能なテキストボックス（読み取り専用）
B) マークダウンをレンダリングして表示（太字・コードブロック等）
C) プレーンテキストのみ（シンプル優先）
D) Other (please describe after [Answer]: tag below)

[Answer]:Bこれってどういうこと？markdownをちゃんと表示できるようにしてほしい

---

## Question 5
**テキスト入力エリア**の仕様は？

A) 1行入力（Enter キーで送信）
B) 複数行入力（Shift+Enter で改行、Enter で送信）
C) 複数行入力（送信ボタンのみで送信、Enter は改行）
D) Other (please describe after [Answer]: tag below)

[Answer]:B

---
