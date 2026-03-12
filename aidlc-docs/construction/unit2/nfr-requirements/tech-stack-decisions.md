# Tech Stack Decisions — Unit 2: UI & Configuration

## Unit 2 依存ライブラリ

| ライブラリ | バージョン | 用途 | 選定理由 |
|---|---|---|---|
| `customtkinter` | `>=5.2` | フローティングUI フレームワーク | フレームレス・半透明ウィンドウ、ダーク/ライトテーマ自動追従をサポート |
| `tkinterweb` | `>=3.24` | マークダウン → HTML レンダリング | tkinter 上で動く WebKit ベースのHTMLレンダラー。Pillow 不要 |
| `markdown` | `>=3.6` | Markdown → HTML 変換 | Python 標準的な markdown パーサー。拡張機能（fenced_code・tables）対応 |
| `pyperclip` | `>=1.8` | クリップボードコピー | Windows でのクリップボード操作に安定した実績 |
| `Pillow` | `>=10.0` | GIF フレーム読み込み | Unit 1 と共有。OtterAnimationController の GIF アニメーション処理 |

## テーマ設定

```python
import customtkinter as ctk

# システムテーマに追従（Q1:C）
ctk.set_appearance_mode("system")   # "dark" / "light" / "system"
ctk.set_default_color_theme("blue") # アクセントカラー
```

**ダークテーマ時の配色**:
| 要素 | 色 |
|---|---|
| 背景 | `#2B2B2B` |
| テキスト | `#EBEBEB` |
| アクセント | `#1F6AA5`（customtkinter blue） |
| コードブロック背景 | `#3C3C3C` |

**ライトテーマ時の配色**:
| 要素 | 色 |
|---|---|
| 背景 | `#F0F0F0` |
| テキスト | `#1A1A1A` |
| アクセント | `#1F6AA5` |
| コードブロック背景 | `#E0E0E0` |

## requirements.txt への追加分

```
# Unit 2 追加ライブラリ
tkinterweb>=3.24
markdown>=3.6
```

（`customtkinter`・`pyperclip`・`Pillow` は既存の requirements.txt に記載済み）

## テスト方針

| コンポーネント | テスト内容 |
|---|---|
| `ConfigManager` | `get_setting` / `set_setting` / 破損ファイル読み込み時のフォールバック |
| `ClipboardService` | `copy()` 成功・失敗時の戻り値 |
| `FloatingWidget` / `OtterAnimationController` | UI コンポーネントのため手動確認（自動テストは省略） |
