# Code Summary — Unit 2: UI & Configuration

## 生成・更新ファイル一覧

| ファイル | 種別 | 説明 |
|---|---|---|
| `requirements.txt` | Config | tkinterweb・markdown 追加（更新） |
| `clipboard_service.py` | Application | クリップボードコピー（Null Object パターン） |
| `config_manager.py` | Application | OAuth credentials 管理・設定永続化・破損フォールバック |
| `otter_animation_controller.py` | Application | GIF アニメーション再生・プレースホルダー切替 |
| `floating_widget.py` | Application | FloatingWidget 本体（マークダウン・ドラッグ・リサイズ・テーマ追従） |
| `main.py` | Application | Unit 2 実コンポーネントに差し替え・コールバック登録・mainloop（更新） |
| `tests/test_clipboard_service.py` | Test | ClipboardService テスト（3件） |
| `tests/test_config_manager.py` | Test | ConfigManager テスト（6件） |

---

## ストーリー実装状況

| US ID | タイトル | 実装ファイル | 状態 |
|---|---|---|---|
| US-01（UI側） | ホットキーで即時起動（ウィジェット表示） | floating_widget.py | ✅ |
| US-02 | ウィジェットを任意位置に移動 | floating_widget.py（ドラッグ・最小化） | ✅ |
| US-06 | 応答をワンクリックコピー | clipboard_service.py, floating_widget.py | ✅ |
| US-08（UI側） | コーディング中起動（フォーカス非奪取） | floating_widget.py（focus_force 制御） | ✅ |
| US-18 | 追加設定なし即時利用 | config_manager.py（OAuth キャッシュ）, main.py | ✅ |

---

## 全ユニット統合後のファイル構成

```
project-otter/
  main.py                       ← エントリーポイント（Unit 1 + Unit 2 統合済み）
  assistant_orchestrator.py     ← C1
  hotkey_manager.py             ← C2
  screen_capture_service.py     ← C3
  gemini_client.py              ← C4
  session_manager.py            ← C5
  floating_widget.py            ← C6
  otter_animation_controller.py ← C7
  config_manager.py             ← C8
  clipboard_service.py          ← C9
  requirements.txt
  assets/                       ← GIF ファイル配置先（手動）
  tests/
    test_session_manager.py
    test_gemini_client.py
    test_assistant_orchestrator.py
    test_clipboard_service.py
    test_config_manager.py
```

---

## テスト実行方法

```bash
cd project-otter
pip install -r requirements.txt
pytest tests/ -v
```

## 起動方法

```bash
# client_secrets.json を同ディレクトリに配置してから実行
python main.py
```
