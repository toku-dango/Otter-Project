"""Project Otter — エントリーポイント

起動手順:
1. ログ設定（RotatingFileHandler）
2. Google OAuth 認証（初回のみブラウザ起動）
3. 全コンポーネント初期化
4. AssistantOrchestrator 起動
"""

import logging
import os
import signal
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ─── ログ設定（PAT-07）─────────────────────────────────────────────────────
CONFIG_DIR = Path.home() / ".config" / "project-otter"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

_handler = RotatingFileHandler(
    CONFIG_DIR / "app.log",
    maxBytes=5 * 1024 * 1024,  # 5MB
    backupCount=3,
    encoding="utf-8",
)
_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)
logging.basicConfig(level=logging.DEBUG, handlers=[_handler])
logger = logging.getLogger(__name__)


def _load_api_key() -> str:
    """Gemini API キーを環境変数または .env ファイルから読み込む。

    優先順位:
    1. 環境変数 GEMINI_API_KEY
    2. プロジェクトルートの .env ファイル（GEMINI_API_KEY=xxx 形式）
    """
    # 1. 環境変数
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        logger.debug("API key loaded from environment variable")
        return api_key

    # 2. .env ファイル
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.split("=", 1)[1].strip()
                if api_key:
                    logger.debug("API key loaded from .env file")
                    return api_key

    print(
        "エラー: Gemini API キーが見つかりません。\n"
        "以下のいずれかで設定してください:\n"
        "  1. 環境変数: export GEMINI_API_KEY=your_key\n"
        "  2. .env ファイル: GEMINI_API_KEY=your_key"
    )
    sys.exit(1)


def main() -> None:
    logger.info("Project Otter starting")

    # ─── Gemini API キー読み込み ────────────────────────────────────────────
    api_key = _load_api_key()

    # ─── Unit 2 コンポーネント初期化────────────────────────────────────────
    import customtkinter as ctk
    from config_manager import ConfigManager
    from clipboard_service import ClipboardService
    from otter_animation_controller import OtterAnimationController
    from floating_widget import FloatingWidget

    # PAT-U2-07: システムテーマに追従
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    config = ConfigManager()
    clipboard = ClipboardService()

    # OtterAnimationController はラベルが FloatingWidget 初期化後に確定するため
    # FloatingWidget 内部で接続する（otter_label を渡す設計）
    anim_ctrl = OtterAnimationController(label=None)  # label は FloatingWidget 内で設定
    widget = FloatingWidget(animation_ctrl=anim_ctrl, config=config)

    # コールバック登録はオーケストレーター初期化後に行う

    # ─── Unit 1 コンポーネント初期化────────────────────────────────────────
    from gemini_client import GeminiClient
    from hotkey_manager import HotkeyManager
    from screen_capture_service import ScreenCaptureService
    from session_manager import SessionManager
    from assistant_orchestrator import AssistantOrchestrator

    gemini = GeminiClient(api_key=api_key)
    hotkey = HotkeyManager()
    capture = ScreenCaptureService()
    session_mgr = SessionManager()

    orchestrator = AssistantOrchestrator(
        hotkey=hotkey,
        capture=capture,
        gemini=gemini,
        session_mgr=session_mgr,
        widget=widget,
        config=config,
        clipboard=clipboard,
    )

    # ─── コールバック登録（PAT-U2-05）────────────────────────────────────
    widget.on_submit(orchestrator.on_user_input)
    widget.on_close(orchestrator.on_session_close)
    widget.on_copy(orchestrator.on_copy_requested)

    # ─── シグナルハンドラ（PAT-06）────────────────────────────────────────
    def _graceful_shutdown(signum, frame):
        logger.info("Shutdown signal received (%s), stopping...", signum)
        orchestrator.stop()
        widget.destroy()
        sys.exit(0)

    signal.signal(signal.SIGINT, _graceful_shutdown)
    signal.signal(signal.SIGTERM, _graceful_shutdown)

    # ─── アプリケーション起動──────────────────────────────────────────────
    orchestrator.start()
    logger.info("Project Otter started. Press Ctrl+Shift+Space to activate.")

    # tkinter メインループ（ここでブロック）
    widget.mainloop()


if __name__ == "__main__":
    main()
