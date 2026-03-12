# Story Generation Plan — Project Otter

## ストーリー生成チェックリスト

### PART 1: Planning
- [x] Step 1: User Stories アセスメント実施（user-stories-assessment.md）
- [x] Step 2: ストーリープラン作成（本ファイル）
- [x] Step 3: 質問生成（下記 Questions セクション）
- [x] Step 4: ユーザー回答収集
- [x] Step 5: 回答の矛盾・曖昧さ分析（矛盾なし）

### PART 2: Generation
- [x] Step 6: personas.md 生成
- [x] Step 7: stories.md 生成（INVEST基準・受け入れ条件付き）
- [x] Step 8: ペルソナとストーリーのマッピング確認
- [x] Step 9: aidlc-state.md 更新

---

## Questions — ストーリー生成プランの確認事項

以下の質問に回答してください。完了したら「done」とお知らせください。

---

## Question 1
ユーザーストーリーのスコープはどこまでにしますか？

A) MVP（Step 1）のみ — 3月プロトタイプで動くものだけ
B) MVP + Step 2（音声・セッション継続）まで
C) 全フェーズ（Step 1〜3）を網羅する
D) Other (please describe after [Answer]: tag below)

[Answer]:Bまでにする

---

## Question 2
ストーリーの粒度はどうしますか？

A) エピック → ストーリーの2階層（大きな機能まとまりの下に詳細ストーリー）
B) フラットなストーリー一覧（階層なし、シンプル）
C) エピック → ストーリー → タスクの3階層
D) Other (please describe after [Answer]: tag below)

[Answer]:Aにする

---

## Question 3
受け入れ条件（Acceptance Criteria）の記述形式はどうしますか？

A) BDD形式（Given / When / Then）— テスト自動化に向く
B) 箇条書き形式（「〜できること」「〜が表示されること」）— シンプルで読みやすい
C) チェックリスト形式（[ ] 項目を列挙）
D) Other (please describe after [Answer]: tag below)

[Answer]:Bにする

---

## Question 4
5ペルソナ（エンジニア・PM/PL・営業企画・コンサル・管理職）のうち、MVPで最優先すべきペルソナはどれですか？

A) エンジニア（自分自身が使うため、まず自分向けに作る）
B) 営業・企画（メール・資料修正のニーズが最も高い）
C) すべてのペルソナを均等に扱う
D) Other (please describe after [Answer]: tag below)

[Answer]:Bにする

---

## Question 5
ストーリーの整理方式はどうしますか？

A) ユーザージャーニー順（呼び出し→キャプチャ→指示→応答→コピーの流れで整理）
B) ペルソナ別（エンジニア用ストーリー群、PM用ストーリー群…と整理）
C) 機能別（ホットキー機能・画面キャプチャ機能・AI応答機能…と整理）
D) Other (please describe after [Answer]: tag below)

[Answer]:Bにする

---
