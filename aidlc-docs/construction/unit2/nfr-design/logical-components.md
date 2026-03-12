# Logical Components — Unit 2: UI & Configuration

## 論理コンポーネント図

```
[Windows OS テーマ設定]
  |（ダーク/ライト検出）
  v
[Project Otter プロセス - メインスレッド]
  |
  +-- FloatingWidget（CTkToplevel）
  |     |
  |     +-- HeaderBar
  |     |     +-- OtterAnimationController
  |     |           |
  |     |           +-[GIF存在時]--> assets/*.gif（ローカルFS）
  |     |           +-[GIF不在時]--> 絵文字プレースホルダー
  |     |
  |     +-- ResponseArea
  |     |     +-[tkinterweb利用可能時]--> HtmlFrame（markdown → HTML）
  |     |     +-[フォールバック時]------> CTkTextbox（プレーンテキスト）
  |     |
  |     +-- InputArea
  |           +-- CTkTextbox（複数行入力）
  |           +-- CTkButton（送信）
  |
  +-- ConfigManager
  |     |
  |     v
  |   ~/.config/project-otter/config.json（ウィジェット位置・サイズ）
  |
  +-- ClipboardService
        |
        v
      [Windows クリップボード]
```

---

## ローカルファイルシステム（Unit 2 担当）

| パス | 内容 | 書き込みタイミング |
|---|---|---|
| `~/.config/project-otter/config.json` | ウィジェット位置・サイズ | ドラッグ完了時・リサイズ時（debounce 500ms） |
| `assets/idle.gif` | Otter アイドルアニメ | ユーザーが手動配置（アプリは読み取りのみ） |
| `assets/thinking.gif` | Otter 考え中アニメ | 同上 |
| `assets/done.gif` | Otter 完了アニメ | 同上 |

---

## スレッド制約

Unit 2 の全コンポーネントはメインスレッド（tkinter イベントループ）上で動作する。

| コンポーネント | スレッド | 備考 |
|---|---|---|
| FloatingWidget | メインスレッド | tkinter UI 操作はすべてここ |
| OtterAnimationController | メインスレッド | `widget.after()` でフレーム更新 |
| ConfigManager | メインスレッド | ファイル I/O は軽量なので同期で OK |
| ClipboardService | メインスレッド | `pyperclip.copy()` は高速 |

---

## 初期化順序

```
1. ctk.set_appearance_mode("system")  ← テーマ設定（main.py）
2. ConfigManager 初期化 → config.json 読み込み（破損時はデフォルト）
3. OtterAnimationController 初期化 → GIF 読み込み試行（失敗時はプレースホルダー）
4. FloatingWidget 初期化
   4a. レンダラー選択（tkinterweb or CTkTextbox）
   4b. ウィジェット位置・サイズを ConfigManager から復元
   4c. コールバック登録（on_submit / on_close / on_copy）
5. AssistantOrchestrator にウィジェットを渡す
```

---

## 終了時のクリーンアップ

```
FloatingWidget.destroy() 呼び出し前に:
  - OtterAnimationController.stop()  ← after() タイマーをキャンセル
  - 最後のウィジェット位置を ConfigManager に保存
```
