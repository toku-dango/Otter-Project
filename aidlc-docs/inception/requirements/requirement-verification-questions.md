# Requirements Verification Questions — Project Otter

企画書PDFの内容を読み込みました。以下の点について確認させてください。
すべての質問に [Answer]: タグの後に回答を記入してください。完了したら「done」とお知らせください。

---

## Question 1
MVPのターゲットプラットフォームはどれですか？

A) macOS のみ
B) Windows のみ
C) macOS と Windows の両方（同時リリース）
D) まず macOS、後から Windows 対応
E) Other (please describe after [Answer]: tag below)

[Answer]:B

---

## Question 2
デスクトップアプリの実装方式はどれを想定していますか？

A) Electron（Web技術ベース、クロスプラットフォーム）
B) Tauri（Rust + Web技術、軽量）
C) macOS ネイティブ（Swift/SwiftUI）
D) Python ベースのアプリ（tkinter / PyQtなど）
E) Other (please describe after [Answer]: tag below)

[Answer]:Dだと私も書けると思うけど、ほかが適切ならそれでもよい。

---

## Question 3
AI（LLM）バックエンドはどれを使いますか？

A) Claude API（Anthropic）— マルチモーダル対応
B) OpenAI API（GPT-4o など）
C) 複数のプロバイダーを切り替え可能にする
D) まだ決めていない（MVP段階では柔軟に）
E) Other (please describe after [Answer]: tag below)

[Answer]:GCPサービスを使用したい。 Gemini API/Vertex AI/Agent Engine等

---

## Question 4
画面キャプチャの方式はどれを想定していますか？

A) OS標準API（macOS: ScreenCaptureKit / Windows: Graphics Capture API）
B) スクリーンショットツール連携（サードパーティ）
C) ブラウザ拡張機能も並行開発する
D) まだ検討中
E) Other (please describe after [Answer]: tag below)

[Answer]:E 負荷が軽く適切な方法を提案してほしい

---

## Question 5
音声入力（STT: Speech-to-Text）の方式はどれですか？

A) クラウドSTT（OpenAI Whisper API / Google Speech-to-Text など）
B) ローカルSTT（Whisper.cpp などデバイス上で処理）
C) OS標準の音声認識（macOS Dictation / Windows Speech Recognition）
D) MVP段階では音声は含めず、テキスト入力のみ
E) Other (please describe after [Answer]: tag below)

[Answer]:D Step2での実装を想定するため、いったんはテキスト入力のみ

---

## Question 6
3月のMVP（基礎プロトタイプ）のスコープはどれですか？

A) 画面キャプチャ → テキスト指示 → AI応答のみ（最小限）
B) 上記に加えて、簡易UIパネル表示（コピーボタン付き）
C) 上記に加えて、音声入力も含む
D) 企画書のスライド通り：画面取得→指示→生成（テキストのみ、UIパネル含む）
E) Other (please describe after [Answer]: tag below)

[Answer]:Aではあるが、ユーザーがテキスト指示をする前に、画面キャプチャなどを自動でAIに送って、状況を把握しておくステップを回すなどの対応をしたい。ユーザーが効く前に状況を把握させ、状況が分かった状態からセッション開始できるようにすることが望ましい。

---

## Question 7
アシスタントUIの表示方式はどれですか？

A) オーバーレイウィンドウ（常に最前面に表示）
B) サイドパネル（画面端に固定）
C) フローティングウィジェット（ドラッグ可能）
D) システムトレイ常駐 + ポップアップ
E) Other (please describe after [Answer]: tag below)

[Answer]:C 邪魔かもなのでずらせたら良い

---

## Question 8
会話履歴・セッションデータの保存ポリシーはどれですか？

A) デフォルト非保存（セッション終了で消去）、ユーザーが明示的に保存を選択
B) ローカルのみ保存（クラウドに送信しない）
C) 暗号化してローカル保存、オプションでクラウド同期
D) 企画書の「保存しないデフォルト」通りに実装
E) Other (please describe after [Answer]: tag below)

[Answer]:B

---

## Question 9
機密情報マスキング（安全設計）の実装レベルはどれですか？

A) MVP段階ではマスキングなし、後フェーズで実装
B) 基本的なマスキング（パスワードフィールド等のOSヒントを利用）
C) カスタムルールでアプリ単位・ドメイン単位で除外設定
D) 完全なマスキング機能をMVPから実装
E) Other (please describe after [Answer]: tag below)

[Answer]:A


---

## Question 10
バックエンドサーバーの構成はどれですか？

A) フルクライアントサイド（LLM API 直呼び出し、サーバーなし）
B) 軽量バックエンドサーバー（認証・使用量管理のため）
C) クラウドバックエンド（ユーザー管理・Free/Pro制限・課金管理）
D) MVPはサーバーレス、後からバックエンドを追加
E) Other (please describe after [Answer]: tag below)

[Answer]:現状(MVP)はA、そのうちCで対応する

---

## Question 11
開発に使用するプログラミング言語・技術スタックの希望はありますか？

A) TypeScript / JavaScript メイン（Electron/Tauri + Node.js）
B) Python メイン（バックエンドロジック + GUI）
C) Swift メイン（macOS ネイティブ優先）
D) 特にこだわりなし（最適な技術を選んでほしい）
E) Other (please describe after [Answer]: tag below)

[Answer]:BのPythonは私も書ける。ただ、ほかが望ましい場合は、それを適用してほしい。
多少ビジュアルにもこだわる必要があり、例えば、Otter画像が動くとかできれば望ましいけどね

---

## Question 12 — Security Extension（セキュリティ拡張ルール）
このプロジェクトにセキュリティ拡張ルール（SECURITY-01〜SECURITY-15）を適用しますか？
これらは本番品質アプリ向けの厳格なセキュリティ制約です。

A) Yes — すべてのSECURITYルールをブロッキング制約として適用する（本番品質アプリ向け）
B) No — SECURITYルールをスキップする（PoC・プロトタイプ・実験的プロジェクト向け）
C) Other (please describe after [Answer]: tag below)

[Answer]:B

---
