# Application Design Plan — Project Otter

## 生成チェックリスト

- [x] Step 1: コンテキスト分析（要件・ストーリー）
- [x] Step 2: コンポーネント特定
- [x] Step 3: 質問生成
- [x] Step 4: ユーザー回答収集
- [x] Step 5: 回答分析（矛盾なし。GIF推奨を確認）
- [x] Step 6: components.md 生成
- [x] Step 7: component-methods.md 生成
- [x] Step 8: services.md 生成
- [x] Step 9: component-dependency.md 生成

---

## 特定したコンポーネント（案）

以下のコンポーネント構成を想定しています。

| コンポーネント | 役割 |
|---|---|
| `HotkeyManager` | グローバルホットキーの登録・監視・イベント発火 |
| `ScreenCaptureService` | `mss` を使った画面キャプチャ（PNG/バイト列） |
| `GeminiClient` | Gemini Reasoning API との通信（画像+テキスト送信・応答受信） |
| `SessionManager` | セッション内会話履歴の管理・セッション終了時消去 |
| `FloatingWidget` | フローティングUIウィジェット（メインUI） |
| `OtterAnimationController` | Otterキャラクターのアニメーション制御 |
| `ConfigManager` | APIキー・設定の保存・読み込み（`keyring` 活用） |
| `ClipboardService` | クリップボードへのコピー操作 |
| `AssistantOrchestrator` | 全コンポーネントを束ねるメインサービス（イベントフロー制御） |

---

## Questions — 設計上の確認事項

以下の質問に回答してください。完了したら「done」とお知らせください。

---

## Question 1
GUIフレームワークはどちらを使いますか？これによりウィジェットのアーキテクチャが変わります。

**CustomTkinter**:
- Pythonのみで完結、導入が簡単
- モダンな見た目（角丸・ダークモード対応）
- アニメーション: Pillow + GIF、またはキャンバス描画で実現
- ウィンドウ常時最前面・フレームレスウィンドウに対応

**PyQt6**:
- より高度なウィジェット制御とアニメーションAPI（QPropertyAnimation）
- Otterのなめらかな動きを実現しやすい
- 学習コスト高め、ライセンス（LGPL）に注意

A) CustomTkinter（シンプル・Pythonネイティブ）
B) PyQt6（高機能・滑らかアニメーション）
C) Other (please describe after [Answer]: tag below)

[Answer]:いったんAかな？

---

## Question 2
Otterアニメーションの実装方式はどうしますか？

A) GIFアニメーション（既成のアニメーションGIFを用意し、Pillowで再生）
B) 静止画 + 状態アイコン（AI処理中はスピナー表示など、シンプルな実装）
C) Other (please describe after [Answer]: tag below)

[Answer]:Aですかね？望ましい方法を教えてほしい

---

## Question 3
Pythonプロジェクトの構成はどうしますか？

A) Pythonパッケージ構成（`src/otter/` 以下にモジュール分割）— 保守性高い
B) シングルディレクトリ構成（フラットなファイル配置）— シンプル
C) Other (please describe after [Answer]: tag below)

[Answer]:Bにしてください。

---
