import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() / ".config" / "project-otter"
CREDENTIALS_PATH = CONFIG_DIR / "credentials.json"
CONFIG_PATH = CONFIG_DIR / "config.json"


@dataclass
class WidgetConfig:
    x: int = -1       # -1 はデフォルト位置（画面右下）を意味する
    y: int = -1
    width: int = 420
    height: int = 740

    def is_default(self) -> bool:
        return self.x == -1 or self.y == -1


@dataclass
class AppConfig:
    widget: WidgetConfig = field(default_factory=WidgetConfig)


class ConfigManager:
    """APIキー不要。Google OAuth Credentials とアプリ設定を管理する。

    PAT-U2-03: config.json 破損時はデフォルト設定にフォールバックする。
    """

    def __init__(self, config_file: Path = CONFIG_PATH) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._config_path = config_file
        self._app_config = self._load_config()

    # ── OAuth Credentials ────────────────────────────────────────────────

    def get_credentials(self) -> Any | None:
        """キャッシュ済みの Google OAuth Credentials を返す。なければ None。"""
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        if not CREDENTIALS_PATH.exists():
            return None
        try:
            creds = Credentials.from_authorized_user_file(str(CREDENTIALS_PATH))
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self.save_credentials(creds)
                logger.debug("Credentials refreshed")
            return creds if creds.valid else None
        except Exception as e:
            logger.warning("Failed to load credentials: %s", type(e).__name__)
            return None

    def save_credentials(self, credentials: Any) -> None:
        """Google OAuth Credentials を保存する（パーミッション 600）。"""
        CREDENTIALS_PATH.write_text(credentials.to_json(), encoding="utf-8")
        CREDENTIALS_PATH.chmod(0o600)
        logger.debug("Credentials saved: path=%s", CREDENTIALS_PATH)

    def has_valid_credentials(self) -> bool:
        """有効な認証情報が存在するかを返す。"""
        return self.get_credentials() is not None

    # ── アプリ設定 ─────────────────────────────────────────────────────

    def get_setting(self, key: str, default: Any = None) -> Any:
        """フラットキーで設定値を取得する（例: "widget_x"）。"""
        widget_keys = {"widget_x", "widget_y", "widget_width", "widget_height"}
        if key in widget_keys:
            attr = key.replace("widget_", "")
            return getattr(self._app_config.widget, attr, default)
        return default

    def set_setting(self, key: str, value: Any) -> None:
        """フラットキーで設定値を保存する。"""
        widget_keys = {"widget_x", "widget_y", "widget_width", "widget_height"}
        if key in widget_keys:
            attr = key.replace("widget_", "")
            setattr(self._app_config.widget, attr, value)
        self._save_config()

    def get_widget_config(self) -> WidgetConfig:
        return self._app_config.widget

    # ── 内部メソッド ────────────────────────────────────────────────────

    def _load_config(self) -> AppConfig:
        """PAT-U2-03: 読み込み失敗時はデフォルト設定を返す。"""
        try:
            if self._config_path.exists():
                data = json.loads(self._config_path.read_text(encoding="utf-8"))
                widget_data = data.get("widget", {})
                return AppConfig(widget=WidgetConfig(**widget_data))
        except Exception as e:
            logger.warning("config.json load failed, using defaults: %s", type(e).__name__)
        return AppConfig()

    def _save_config(self) -> None:
        """設定を config.json に書き込む。"""
        try:
            data = {"widget": asdict(self._app_config.widget)}
            self._config_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception as e:
            logger.error("config.json save failed: %s", type(e).__name__)
