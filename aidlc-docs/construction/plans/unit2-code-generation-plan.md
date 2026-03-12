# Code Generation Plan — Unit 2: UI & Configuration

## ユニット概要

| 項目 | 内容 |
|---|---|
| Unit | Unit 2: UI & Configuration |
| Workspace Root | `/workspaces/claude-code-book-template/project-otter` |
| プロジェクト種別 | Greenfield |
| 担当ストーリー | US-01（UI側）, US-02, US-06, US-08（UI側）, US-18 |

## ファイル構成（生成・更新対象）

```
project-otter/                               ← Application Code
  requirements.txt                           # 更新（tkinterweb, markdown 追加）
  clipboard_service.py                       # C9 新規
  config_manager.py                          # C8 新規
  otter_animation_controller.py              # C7 新規
  floating_widget.py                         # C6 新規
  main.py                                    # 更新（モック → 実コンポーネントに差し替え）
  tests/
    test_clipboard_service.py                # 新規
    test_config_manager.py                   # 新規
aidlc-docs/construction/unit2/code/          ← Documentation
  code-summary.md                            # 新規
```

---

## チェックリスト

### PART 1: Planning
- [x] Step 1: ユニットコンテキスト分析
- [x] Step 2: コード生成計画作成
- [x] Step 3: ユニット生成コンテキスト整理
- [x] Step 4: 計画ドキュメント保存
- [ ] Step 5: 計画サマリー提示・承認待ち

### PART 2: Generation
- [x] Step 1: `requirements.txt` 更新（tkinterweb, markdown 追加）
- [x] Step 2: `clipboard_service.py` 生成
- [x] Step 3: `tests/test_clipboard_service.py` 生成
- [x] Step 4: `config_manager.py` 生成
- [x] Step 5: `tests/test_config_manager.py` 生成
- [x] Step 6: `otter_animation_controller.py` 生成
- [x] Step 7: `floating_widget.py` 生成
- [x] Step 8: `main.py` 更新（Unit 2 実コンポーネントに差し替え）
- [x] Step 9: `aidlc-docs/construction/unit2/code/code-summary.md` 生成

---

## 各ステップ詳細

### Step 1: `requirements.txt` 更新
**内容**: `tkinterweb>=3.24` と `markdown>=3.6` を追加

---

### Step 2: `clipboard_service.py` 生成
**対応ストーリー**: US-06（応答をワンクリックコピー）
**実装内容**:
- `ClipboardService` クラス（`copy(text) -> bool`）
- PAT-U2-06: 失敗時 False を返し例外を外部に伝播しない

---

### Step 3: `tests/test_clipboard_service.py` 生成
**テスト内容**:
- `copy()` 成功時に True を返すこと
- `copy()` が pyperclip 失敗時に False を返すこと（例外を上げないこと）

---

### Step 4: `config_manager.py` 生成
**対応ストーリー**: US-01（位置記憶）, US-18（設定永続化）
**実装内容**:
- `WidgetConfig` / `AppConfig` dataclass
- `ConfigManager` クラス（get_credentials / save_credentials / has_valid_credentials / get_setting / set_setting）
- PAT-U2-03: config.json 破損時デフォルト設定フォールバック
- OAuth credentials 管理（`~/.config/project-otter/credentials.json`）

---

### Step 5: `tests/test_config_manager.py` 生成
**テスト内容**:
- `get_setting()` がデフォルト値を返すこと
- `set_setting()` → `get_setting()` で値が取得できること
- config.json が破損していても起動できること

---

### Step 6: `otter_animation_controller.py` 生成
**実装内容**:
- `AnimationState` Enum
- `OtterAnimationController` クラス（load_animations / play / stop）
- PAT-U2-02: GIF 不在時の絵文字プレースホルダーフォールバック
- DONE 状態: 2秒後に IDLE へ自動遷移

---

### Step 7: `floating_widget.py` 生成
**対応ストーリー**: US-01, US-02, US-06, US-08, US-18
**実装内容**:
- `WidgetState` Enum
- `FloatingWidget` クラス（全公開メソッド）
- PAT-U2-01: tkinterweb → CTkTextbox フォールバック
- PAT-U2-04: リサイズ debounce（500ms）
- PAT-U2-05: Observer コールバック
- PAT-U2-07: System Theme Bridge
- BR-U2-01〜08 全ルール準拠
- 全インタラクティブ要素に `data-testid` 付与

---

### Step 8: `main.py` 更新
**内容**: Unit 2 モック（MagicMock）を実コンポーネントに差し替え
**変更箇所**: `main()` 内の Unit 2 初期化ブロック + `widget.mainloop()` 呼び出し追加

---

### Step 9: `code-summary.md` 生成
**内容**: 生成ファイル一覧・ストーリー実装状況・テスト実行方法

---

## ストーリートレーサビリティ

| US ID | 実装ステップ |
|---|---|
| US-01（UI側） | Step 7（FloatingWidget.show / 位置設定） |
| US-02 | Step 7（FloatingWidget ドラッグ移動・最小化） |
| US-06 | Step 2, 7（ClipboardService + コピーボタン） |
| US-08（UI側） | Step 7（FloatingWidget 表示位置・フォーカス非奪取） |
| US-18 | Step 4, 7（ConfigManager + 初回起動フロー） |
