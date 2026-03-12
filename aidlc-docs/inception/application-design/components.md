# Components — Project Otter

## コンポーネント一覧

| ID | コンポーネント | 分類 | Unit |
|---|---|---|---|
| C1 | AssistantOrchestrator | Service / Core | Unit 1 |
| C2 | HotkeyManager | Core | Unit 1 |
| C3 | ScreenCaptureService | Core | Unit 1 |
| C4 | GeminiClient | Core | Unit 1 |
| C5 | SessionManager | Core | Unit 1 |
| C6 | FloatingWidget | UI | Unit 2 |
| C7 | OtterAnimationController | UI | Unit 2 |
| C8 | ConfigManager | Config | Unit 2 |
| C9 | ClipboardService | Utility | Unit 2 |

---

## C1: AssistantOrchestrator

**目的**: 全コンポーネントを束ね、ホットキー起動からAI応答表示までのイベントフローを制御するメインサービス。

**責務:**
- アプリケーション起動時に全コンポーネントを初期化・接続する
- HotkeyManager からのイベントを受け取り、キャプチャ→Gemini事前把握→UI表示の流れを制御する
- ユーザー入力イベントを受け取り、Gemini応答生成→UI更新の流れを制御する
- 各コンポーネントのエラーをハンドリングし、UIにフィードバックする

**インターフェース:**
- `on_hotkey_triggered()` — ホットキーイベントハンドラ
- `on_user_input(text: str)` — ユーザーテキスト入力ハンドラ
- `on_session_close()` — セッション終了ハンドラ

---

## C2: HotkeyManager

**目的**: グローバルホットキー（Ctrl+Shift+Space）をOSレベルで常時監視し、押下イベントを発火する。

**責務:**
- アプリ起動時にグローバルホットキーをシステムに登録する
- 他のアプリが前面にある状態でもホットキーを検出する（`pynput` 使用）
- ホットキー押下時にコールバック関数を呼び出す
- アプリ終了時にホットキー登録を解除する

**インターフェース:**
- `register(callback: Callable)` — ホットキー登録
- `unregister()` — ホットキー解除

---

## C3: ScreenCaptureService

**目的**: ホットキー押下時点の画面スクリーンショットを取得し、Gemini API が処理できる形式に変換する。

**責務:**
- `mss` ライブラリを使って現在の全画面またはアクティブウィンドウをキャプチャする
- キャプチャ画像を PIL Image オブジェクトに変換する
- 画像を Base64 エンコードして GeminiClient に渡せる形にする
- キャプチャ失敗時にエラーを返す

**インターフェース:**
- `capture() -> CaptureResult` — スクリーンショット取得

---

## C4: GeminiClient

**目的**: Gemini Reasoning API（`gemini-2.0-flash-thinking-exp`）と通信し、画面理解・応答生成を行う。

**責務:**
- `google-generativeai` SDK を使って Gemini API を呼び出す
- **事前把握フェーズ**: スクリーンショット画像をAPIに送り、画面状況の把握（Reasoning）を行う
- **応答生成フェーズ**: セッション履歴 + ユーザー指示 + 事前把握結果をもとに応答を生成する
- APIキー認証・エラーハンドリング・タイムアウト処理を担う
- セッション継続のためのチャット履歴を保持する（`ChatSession`）

**インターフェース:**
- `preload_context(image_base64: str) -> PreloadResult` — 画面事前把握
- `generate_response(user_input: str, session: ChatSession) -> str` — 応答生成
- `create_session() -> ChatSession` — セッション作成

---

## C5: SessionManager

**目的**: 1回の起動セッション内での会話履歴を管理し、セッション終了時にデータを消去する。

**責務:**
- 会話履歴（ユーザー入力・AI応答のペア）をメモリ上に保持する
- GeminiClient の ChatSession オブジェクトを管理する
- セッション終了（ウィジェットを閉じる）時にすべての履歴を消去する
- ローカルディスクには保存しない（デフォルト非保存ポリシー）

**インターフェース:**
- `start_session() -> Session` — セッション開始
- `end_session(session_id: str)` — セッション終了・消去
- `get_history(session_id: str) -> list` — 履歴取得

---

## C6: FloatingWidget

**目的**: 常時最前面に表示されるフローティングUIウィジェット。ユーザーとの対話の主窓口。

**責務:**
- CustomTkinter でフレームレス・半透明のウィンドウを生成する
- ドラッグ操作による任意位置への移動を実装する
- テキスト入力フィールド・送信ボタン・応答表示エリア・コピーボタンを配置する
- Otter アニメーション表示エリアを確保する
- AI処理中・アイドル・完了の各状態に応じてUIを切り替える
- 最小化ボタンによるウィジェット縮小表示を実装する

**インターフェース:**
- `show()` — ウィジェット表示
- `hide()` — ウィジェット非表示
- `set_state(state: WidgetState)` — 状態切り替え（IDLE / THINKING / DONE）
- `display_response(text: str)` — 応答テキスト表示
- `on_submit(callback: Callable)` — 送信イベントコールバック登録

---

## C7: OtterAnimationController

**目的**: Otter キャラクターの GIF アニメーションを状態に応じて再生・切り替えする。

**責務:**
- `assets/` ディレクトリから状態別 GIF ファイルを読み込む（idle / thinking / done）
- Pillow を使って GIF フレームを逐次再生する
- FloatingWidget の Otter 表示エリアにフレームを描画する
- 状態切り替え時にアニメーションをシームレスに遷移させる

**GIF 状態定義:**
- `idle.gif` — ゆっくり浮いているような呼吸アニメ（常時ループ）
- `thinking.gif` — 考え中ポーズ（AI処理中ループ）
- `done.gif` — 嬉しそうな動き（完了時1回再生→idle に戻る）

**インターフェース:**
- `play(state: AnimationState)` — アニメーション再生
- `stop()` — アニメーション停止

---

## C8: ConfigManager

**目的**: API キーおよびアプリ設定の永続化・読み込みを担う。

**責務:**
- Gemini API キーを OS のキーチェーン（`keyring`）に安全に保存・読み込みする
- ウィジェット位置・ホットキー設定等をローカルの JSON ファイルに保存する
- 初回起動時に API キー未設定を検出し、設定UIを起動する

**インターフェース:**
- `get_api_key() -> str | None` — API キー取得
- `set_api_key(key: str)` — API キー保存
- `get_setting(key: str) -> Any` — 設定値取得
- `set_setting(key: str, value: Any)` — 設定値保存

---

## C9: ClipboardService

**目的**: AI 応答テキストをクリップボードにコピーする。

**責務:**
- `pyperclip` または `tkinter.clipboard` を使ってテキストをコピーする
- コピー成功・失敗を呼び出し元に返す

**インターフェース:**
- `copy(text: str) -> bool` — テキストをクリップボードにコピー
