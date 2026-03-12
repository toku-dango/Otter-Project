import logging
from typing import Callable

from pynput import keyboard

logger = logging.getLogger(__name__)


class HotkeyManager:
    """グローバルホットキー（Ctrl+Shift+Space）をOSレベルで常時監視する。

    コールバックは pynput の内部スレッドで実行される。
    UI操作が必要な場合はコールバック内で widget.after(0, fn) を使うこと。
    """

    def __init__(self, hotkey_combo: str = "<ctrl>+<shift>+<space>") -> None:
        self._hotkey_combo = hotkey_combo
        self._listener: keyboard.GlobalHotKeys | None = None

    def register(self, callback: Callable[[], None]) -> None:
        """グローバルホットキーをシステムに登録し、押下時に callback を呼び出す。"""
        if self._listener is not None:
            logger.warning("Hotkey already registered, unregistering first.")
            self.unregister()

        self._listener = keyboard.GlobalHotKeys({self._hotkey_combo: callback})
        self._listener.start()
        logger.debug("Hotkey registered: %s", self._hotkey_combo)

    def unregister(self) -> None:
        """ホットキー登録を解除する。アプリ終了時に必ず呼び出すこと。"""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
            logger.debug("Hotkey unregistered: %s", self._hotkey_combo)

    def is_registered(self) -> bool:
        """ホットキーが登録済みかどうかを返す。"""
        return self._listener is not None
