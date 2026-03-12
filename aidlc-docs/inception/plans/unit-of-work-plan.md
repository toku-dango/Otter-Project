# Unit of Work Plan — Project Otter

## 生成チェックリスト

### PART 1: Planning
- [x] Step 1: コンポーネント分析・ユニット境界特定
- [x] Step 2: 質問生成
- [x] Step 3: ユーザー回答収集
- [x] Step 4: 回答分析

### PART 2: Generation
- [x] Step 5: unit-of-work.md 生成
- [x] Step 6: unit-of-work-dependency.md 生成
- [x] Step 7: unit-of-work-story-map.md 生成

---

## 特定したユニット構成（案）

Application Design の結果、以下の2ユニット分割を想定しています。

| Unit | 名称 | コンポーネント |
|---|---|---|
| **Unit 1** | Core Engine | AssistantOrchestrator, HotkeyManager, ScreenCaptureService, GeminiClient, SessionManager |
| **Unit 2** | UI & Configuration | FloatingWidget, OtterAnimationController, ConfigManager, ClipboardService |

---

## Questions

以下の質問に回答してください。完了したら「done」とお知らせください。

---

## Question 1
ユニットの開発順序はどうしますか？（ソロ開発のため実装順序の確認です）

A) Unit 1 → Unit 2 の順番（コア機能を先に動かし、その後UIを仕上げる）
B) Unit 1 と Unit 2 を同時並行（機能とUIを同時に作る）
C) Other (please describe after [Answer]: tag below)

[Answer]:B

---
