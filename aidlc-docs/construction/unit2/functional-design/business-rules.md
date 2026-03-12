# Business Rules — Unit 2: UI & Configuration

| Rule ID | カテゴリ | 名称 |
|---|---|---|
| BR-U2-01 | 表示位置 | デフォルト位置・ドラッグ移動 |
| BR-U2-02 | サイズ | リサイズ可能・最小サイズ制限 |
| BR-U2-03 | アニメーション | プレースホルダー実装 |
| BR-U2-04 | 応答表示 | マークダウンレンダリング |
| BR-U2-05 | テキスト入力 | Enter/Shift+Enter の動作 |
| BR-U2-06 | コピーフィードバック | 1秒間フィードバック表示 |
| BR-U2-07 | 最前面表示 | 常時最前面 |
| BR-U2-08 | 設定永続化 | ウィジェット位置・サイズの保存 |

---

## BR-U2-01: デフォルト位置・ドラッグ移動

**ルール**: 初回起動時は画面右下に表示する。ドラッグで任意の位置に移動できる。

**デフォルト位置の計算**:
```python
screen_width = widget.winfo_screenwidth()
screen_height = widget.winfo_screenheight()
default_x = screen_width - widget_width - 20   # 右端から20px
default_y = screen_height - widget_height - 60  # 下端から60px（タスクバー考慮）
```

**ドラッグ対象領域**: ヘッダーバー（上部 40px）のみドラッグ可能。応答エリアのテキスト選択と競合しないようにする。

---

## BR-U2-02: リサイズ可能・最小サイズ制限

**ルール**: ユーザーはウィジェットをリサイズできる。ただし最小サイズを下回らない。

**サイズ制限**:
- 最小幅: 300px
- 最小高さ: 200px
- デフォルト幅: 400px
- デフォルト高さ: 500px

**実装**: `minsize(300, 200)` をウィンドウに設定。リサイズ完了時（`<Configure>` イベント）に新しいサイズを ConfigManager に保存する。

---

## BR-U2-03: Otter アニメーション（プレースホルダー）

**ルール**: MVP では GIF の代わりに静止画プレースホルダーを使用する。GIF 追加時は `assets/` にファイルを置くだけで差し替えられる設計にする。

**プレースホルダー仕様**:
- `assets/` ディレクトリが存在しない、または GIF ファイルが存在しない場合: CTkLabel に絵文字 🦦 を表示
- 状態による視覚的区別:

| 状態 | プレースホルダー表示 |
|---|---|
| IDLE | 🦦（通常サイズ） |
| THINKING | 🦦💭（考え中テキスト付き） |
| DONE | 🦦✨（完了テキスト付き） |

**GIF 差し替え方法**: `assets/idle.gif` / `assets/thinking.gif` / `assets/done.gif` を配置すれば自動的に GIF アニメーションが有効になる。

---

## BR-U2-04: マークダウンレンダリング

**ルール**: AI 応答テキストをマークダウンとして解析し、HTML に変換して `tkinterweb.HtmlFrame` でレンダリングする。

**使用ライブラリ**: `markdown`（Python）+ `tkinterweb`

**CSS スタイル（ウィジェット配色に合わせる）**:
```css
body {
    font-family: "Yu Gothic", "Meiryo", sans-serif;
    font-size: 14px;
    color: #EBEBEB;
    background-color: #2B2B2B;
    padding: 8px;
    margin: 0;
}
code {
    background-color: #3C3C3C;
    border-radius: 3px;
    padding: 2px 4px;
    font-family: "Consolas", monospace;
}
pre {
    background-color: #3C3C3C;
    padding: 8px;
    border-radius: 4px;
    overflow-x: auto;
}
```

---

## BR-U2-05: テキスト入力の送信操作

**ルール**: Enter キーで送信、Shift+Enter で改行。

**実装**:
```python
input_field.bind("<Return>", lambda e: self._on_submit() or "break")
input_field.bind("<Shift-Return>", lambda e: None)  # デフォルト動作（改行）
```

**送信条件**: 入力が空白のみの場合は送信しない（BR-08 準拠）。THINKING 状態では送信ボタンを無効化（同 BR-08）。

---

## BR-U2-06: コピーフィードバック

**ルール**: コピーボタン押下後、1秒間「✓ コピーしました」と表示して元のラベルに戻す。

```python
def _on_copy_clicked(self):
    self._copy_button.configure(text="✓ コピーしました")
    self.after(1000, lambda: self._copy_button.configure(text="コピー"))
    if self._on_copy_callback:
        self._on_copy_callback()
```

---

## BR-U2-07: 常時最前面表示

**ルール**: ウィジェットは他のアプリが前面にある場合でも常に最前面に表示される。

**実装**: `wm_attributes("-topmost", True)` を設定。ドラッグ移動後も `lift()` を呼び出して最前面を維持する。

---

## BR-U2-08: 設定の永続化

**ルール**: ウィジェットの位置・サイズをアプリ終了時または変更時に `config.json` へ保存する。

**保存タイミング**:
- ドラッグ移動完了時（`<ButtonRelease-1>`）
- リサイズ完了時（`<Configure>` イベント、デバウンス 500ms）

**保存内容**:
```json
{
  "widget_x": 1480,
  "widget_y": 320,
  "widget_width": 400,
  "widget_height": 500
}
```
