# Business Logic Model — Unit 2: UI & Configuration

## フロー概要

| フロー ID | 名称 | トリガー |
|---|---|---|
| FL-01 | ウィジェット初期化 | アプリ起動時 |
| FL-02 | ウィジェット表示 | show() 呼び出し |
| FL-03 | ドラッグ移動 | マウスドラッグ |
| FL-04 | リサイズ | ウィンドウ端をドラッグ |
| FL-05 | 状態切り替え | set_state() 呼び出し |
| FL-06 | 応答テキスト表示 | display_response() 呼び出し |
| FL-07 | コピーボタン押下 | on_copy コールバック |
| FL-08 | 最小化・復元 | 最小化ボタン押下 |
| FL-09 | 設定の読み込み・保存 | アプリ起動時 / 設定変更時 |

---

## FL-01: ウィジェット初期化

```
FloatingWidget.__init__(animation_ctrl)
  |
  +--> customtkinter.CTkToplevel 生成（フレームレス・半透明）
  +--> ウィンドウ設定:
  |      - overrideredirect(True)  # タイトルバーなし
  |      - attributes("-topmost", True)  # 常時最前面
  |      - attributes("-alpha", 0.95)   # 半透明
  |      - resizable(True, True)        # リサイズ可能（Q2:B）
  |
  +--> UIレイアウト構築（FL-06参照）
  +--> ドラッグ移動のイベントバインド（FL-03）
  +--> withdraw()  # 初期状態は非表示
  |
  +--> ConfigManager から前回ウィジェット位置を読み込む（FL-09）
       |--> 取得できた場合: その位置に設定
       +--> 取得できない場合: 画面右下にデフォルト配置（Q1:A）
```

---

## FL-02: ウィジェット表示

```
FloatingWidget.show()
  |
  +--> deiconify()  # 非表示 → 表示
  +--> lift()        # 最前面に移動
  +--> focus_force() # フォーカス設定
  +--> テキスト入力フィールドをクリア
  +--> 応答エリアをクリア
  +--> ステータスメッセージをクリア
```

---

## FL-03: ドラッグ移動

```
<ButtonPress-1> イベント（タイトルバー領域）
  |
  +--> _drag_start_x, _drag_start_y を記録

<B1-Motion> イベント
  |
  +--> マウス移動量 = 現在位置 - 開始位置
  +--> ウィジェット新位置 = 現在ウィジェット位置 + 移動量
  +--> geometry(f"+{new_x}+{new_y}")

<ButtonRelease-1> イベント
  |
  +--> ConfigManager.set_setting("widget_x", x)
  +--> ConfigManager.set_setting("widget_y", y)
```

---

## FL-05: 状態切り替え

```
FloatingWidget.set_state(state: str)  # "IDLE" / "THINKING" / "DONE"
  |
  +--> [IDLE]
  |      - テキスト入力フィールド: 有効化
  |      - 送信ボタン: 有効化
  |      - OtterAnimationController.play("idle")
  |
  +--> [THINKING]
  |      - テキスト入力フィールド: 無効化
  |      - 送信ボタン: 無効化（BR-08）
  |      - OtterAnimationController.play("thinking")
  |
  +--> [DONE]
         - テキスト入力フィールド: 有効化
         - 送信ボタン: 有効化
         - コピーボタン: 表示
         - OtterAnimationController.play("done")
           （done アニメーション完了後、自動的に idle へ）
```

---

## FL-06: 応答テキスト表示（マークダウンレンダリング）

```
FloatingWidget.display_response(text: str)
  |
  +--> markdown ライブラリで HTML に変換
  |      markdown.markdown(text, extensions=["fenced_code", "tables"])
  |
  +--> CSS スタイルを付与（フォント・色・余白）
  +--> tkinterweb.HtmlFrame に HTML を流し込む
  +--> _last_response = text  # コピー用に保持
  +--> コピーボタンを表示
```

**対応マークダウン記法**:
| 記法 | 表示 |
|---|---|
| `**太字**` | **太字** |
| `` `コード` `` | 等幅フォント |
| ` ```ブロック``` ` | コードブロック（背景色付き） |
| `- 箇条書き` | 箇条書き |
| `## 見出し` | 見出しサイズ |

---

## FL-07: コピーボタン押下

```
コピーボタン クリック
  |
  +--> on_copy コールバック呼び出し（AssistantOrchestrator.on_copy_requested）
  +--> フィードバック表示: コピーボタンのテキストを "✓ コピーしました" に変更
  +--> 1秒後: ボタンテキストを "コピー" に戻す
```

---

## FL-08: 最小化・復元

```
最小化ボタン押下
  |
  +--> _is_minimized = True
  +--> ウィジェット高さを 50px（ヘッダーバーのみ）に縮小
  +--> 最小化ボタンアイコンを ▲ に変更

▲ ボタン（復元）押下
  |
  +--> _is_minimized = False
  +--> ウィジェット高さを通常サイズに復元
  +--> ボタンアイコンを ▼ に変更
```

---

## FL-09: 設定の読み込み・保存

```
ConfigManager.__init__(config_file="~/.config/project-otter/config.json")
  |
  +--> config.json が存在すれば読み込む
  +--> 存在しなければデフォルト設定で初期化

保存対象の設定:
  - widget_x, widget_y  (int): ウィジェット位置
  - widget_width        (int): ウィジェット幅（デフォルト: 400）
  - widget_height       (int): ウィジェット高さ（デフォルト: 500）
```
