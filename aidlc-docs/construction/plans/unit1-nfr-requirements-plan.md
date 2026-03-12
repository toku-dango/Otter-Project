# NFR Requirements Plan — Unit 1: Core Engine

## チェックリスト

### PART 1: Planning
- [x] Step 1: Functional Design 分析
- [x] Step 2: NFR Requirements 計画作成
- [x] Step 3: 質問生成
- [x] Step 4: 計画保存
- [x] Step 5: 回答収集・分析

### PART 2: Generation
- [x] Step 6: NFR Requirements アーティファクト生成
  - [x] nfr-requirements.md
  - [x] tech-stack-decisions.md
- [ ] Step 7: 完了メッセージ提示
- [ ] Step 8: 承認待ち

---

## 既知のパフォーマンス要件（ストーリーから確定済み）

| 項目 | 要件値 | 出典 |
|---|---|---|
| ホットキー起動 → ウィジェット表示 | 500ms 以内 | US-01 |
| アイドル時 CPU 使用率 | 1% 以下 | execution-plan.md |
| AI応答表示（APIレイテンシ除く） | 500ms 以内 | US-05 |
| preload_context タイムアウト | 10秒 | BR-02 |
| generate_response タイムアウト | 30秒 | BR-03 |

---

## 質問

以下の質問に回答してください。完了したら「done」とお知らせください。

---

## Question 1
**ターゲットOS**はどこまでサポートしますか？

A) Windows のみ（MVP スコープ）
B) Windows + macOS（両方対応）
C) Windows + macOS + Linux（クロスプラットフォーム）
D) Other (please describe after [Answer]: tag below)

[Answer]:A

---

## Question 2
**Pythonバージョン**の要件は？

A) Python 3.11 以上
B) Python 3.12 以上
C) 特に指定なし（最新安定版に追従）
D) Other (please describe after [Answer]: tag below)

[Answer]:A

---

## Question 3
**アプリのログ出力**はどうしますか？

A) ログなし（シンプルさ優先）
B) コンソール出力のみ（開発中のデバッグ用）
C) ファイルにログ保存（`~/.config/project-otter/app.log`）、ERROR レベル以上のみ
D) ファイルにログ保存、DEBUG レベルも含む詳細ログ
E) Other (please describe after [Answer]: tag below)

[Answer]:D

---

## Question 4
**スクリーンキャプチャ画像の機密情報対策**はどこまで行いますか？（画像はGemini APIに送信されます）

A) 対策なし（ユーザーの責任）
B) 特定アプリを除外リストに追加できる設定を用意する（例：パスワードマネージャーは除外）
C) Other (please describe after [Answer]: tag below)

[Answer]:A

---

## Question 5
**単体テスト**の方針は？

A) テストなし（MVP優先・後で追加）
B) コアロジックのみテスト（GeminiClient・SessionManager のモックテスト）
C) 全コンポーネントのユニットテスト（カバレッジ 80% 以上目標）
D) Other (please describe after [Answer]: tag below)

[Answer]:B

---
