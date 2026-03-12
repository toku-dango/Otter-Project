# Code Summary — Unit 1: Core Engine

## 生成ファイル一覧

| ファイル | 種別 | 説明 |
|---|---|---|
| `main.py` | Application | エントリーポイント・OAuth認証・ログ設定・起動フロー |
| `session_manager.py` | Application | セッション・会話履歴のメモリ管理 |
| `hotkey_manager.py` | Application | グローバルホットキー登録・解除（pynput） |
| `screen_capture_service.py` | Application | アクティブモニターのキャプチャ・Base64変換（mss） |
| `gemini_client.py` | Application | Gemini API通信・OAuth認証・リトライ処理 |
| `assistant_orchestrator.py` | Application | 全フロー制御Facade・スレッド管理 |
| `requirements.txt` | Config | 依存ライブラリ定義 |
| `tests/__init__.py` | Test | テストパッケージ初期化 |
| `tests/test_session_manager.py` | Test | SessionManager ユニットテスト（9件） |
| `tests/test_gemini_client.py` | Test | GeminiClient ユニットテスト（6件） |
| `tests/test_assistant_orchestrator.py` | Test | AssistantOrchestrator ユニットテスト（9件） |

---

## ストーリー実装状況

| US ID | タイトル | 実装ファイル | 状態 |
|---|---|---|---|
| US-01 | ホットキーで即時起動 | hotkey_manager.py, assistant_orchestrator.py | ✅ |
| US-03 | 起動時に画面自動把握 | screen_capture_service.py, gemini_client.py, assistant_orchestrator.py | ✅ |
| US-04 | 代名詞だけで対象特定 | gemini_client.py（Gemini Reasoning で自動対応） | ✅ |
| US-05 | 短い指示でメール改善 | gemini_client.py, assistant_orchestrator.py | ✅ |
| US-08 | コーディング中起動 | hotkey_manager.py（pynput はフォーカスを奪わない） | ✅ |
| US-09 | GitHub PR文脈把握 | screen_capture_service.py, gemini_client.py | ✅ |
| US-10 | PR説明文改善 | gemini_client.py, assistant_orchestrator.py | ✅ |
| US-13 | Notion議事録把握 | screen_capture_service.py, gemini_client.py | ✅ |
| US-14 | 議事録からメール生成 | gemini_client.py, assistant_orchestrator.py | ✅ |
| US-16 | PowerPointスライド把握 | screen_capture_service.py, gemini_client.py | ✅ |
| US-17 | スライド冒頭メッセージ改善 | gemini_client.py, assistant_orchestrator.py | ✅ |
| US-19 | 一言指示でトーン調整 | gemini_client.py, assistant_orchestrator.py | ✅ |

---

## Unit 2 との統合ポイント

`main.py` の以下の箇所が Unit 2 完成後に差し替えられる：

```python
# Unit 2 完成後に差し替える箇所（main.py L45-52）
from floating_widget import FloatingWidget
from config_manager import ConfigManager
from clipboard_service import ClipboardService

widget = FloatingWidget(animation_ctrl=OtterAnimationController(...))
config = ConfigManager()
clipboard = ClipboardService()
```

また `widget.mainloop()` の呼び出しで tkinter イベントループを開始する。

---

## テスト実行方法

```bash
cd project-otter
pip install -r requirements.txt
pytest tests/ -v
```
