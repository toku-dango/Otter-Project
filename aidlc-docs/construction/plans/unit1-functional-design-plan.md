# Functional Design Plan — Unit 1: Core Engine

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
- [ ] Step 7: 完了メッセージ提示
- [ ] Step 8: 承認待ち

---

## ユニット概要（再掲）

| 項目 | 内容 |
|---|---|
| Unit ID | Unit 1 |
| 名称 | Core Engine |
| コンポーネント | AssistantOrchestrator, HotkeyManager, ScreenCaptureService, GeminiClient, SessionManager |
| 担当ストーリー | US-01, 03, 04, 05, 08, 09, 10, 13, 14, 16, 17, 19（MVP 12件） |

---

## 質問

以下の質問に回答してください。完了したら「done」とお知らせください。

---

## Question 1
ホットキーが**既にウィジェット表示中に再度押された**場合の動作は？

A) 何もしない（無視する）
B) ウィジェットを閉じる（トグル動作）
C) 画面を再キャプチャして事前把握をやり直す（再起動）
D) Other (please describe after [Answer]: tag below)

[Answer]:D 例えば1度押されたら、終了しました画面が出てきてOKを押すと閉じるという感じが良い

---

## Question 2
`preload_context`（Gemini事前把握）のタイムアウト値と、タイムアウト時の動作は？

A) 5秒タイムアウト → 「画面取得に失敗しました」表示、ユーザー入力は引き続き受け付ける（文脈なしで応答）
B) 10秒タイムアウト → 「画面取得に失敗しました」表示、ユーザー入力は引き続き受け付ける
C) タイムアウトなし（APIが返るまで待つ）→ UIは「確認中...」のまま
D) Other (please describe after [Answer]: tag below)

[Answer]:B


---

## Question 3
Gemini API呼び出し失敗時（ネットワークエラー・レート制限等）の**リトライ戦略**は？

A) リトライなし → 即座にエラーをUIに表示する
B) 1回リトライ（即時）→ それでも失敗したらエラー表示
C) 最大3回リトライ（指数バックオフ）→ 失敗したらエラー表示
D) Other (please describe after [Answer]: tag below)

[Answer]:C


---

## Question 4
**セッションのライフサイクル**はどう定義しますか？

A) ホットキー1回押下 = 1セッション（ウィジェットを閉じるとセッション終了・履歴消去）
B) アプリ起動中は1セッション継続（ウィジェットの開閉に関わらず履歴保持）
C) ホットキー押下のたびに新セッション開始。ただしウィジェット閉じずに再押下した場合は継続
D) Other (please describe after [Answer]: tag below)

[Answer]:B

---

## Question 5
**複数モニター環境**でのスクリーンキャプチャ対象は？

A) プライマリモニターのみ
B) マウスカーソルがあるモニター（アクティブモニター）
C) 全モニターを結合した1枚の画像
D) Other (please describe after [Answer]: tag below)

[Answer]:B

---

## Question 6
`AssistantOrchestrator` の**非同期処理モデル**は？（UIスレッドとバックグラウンド処理の分離方法）

A) `threading.Thread` で preload/generate をバックグラウンド実行。完了後 `widget.after()` でUIスレッドに通知
B) `asyncio` + `async/await` でイベントループ管理
C) シングルスレッド（同期処理）。UIは応答中フリーズしても許容
D) Other (please describe after [Answer]: tag below)

[Answer]:どうしたらよいかわからないので、最適な方法を提案して

---
