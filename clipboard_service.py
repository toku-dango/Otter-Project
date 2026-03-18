import logging

import pyperclip

logger = logging.getLogger(__name__)


class ClipboardService:
    """AI応答テキストをクリップボードにコピーする。

    PAT-U2-06: 失敗時は False を返し、例外を外部に伝播しない（Null Object）。
    """

    def copy(self, text: str) -> bool:
        """テキストをクリップボードにコピーする。成功時 True、失敗時 False を返す。"""
        try:
            pyperclip.copy(text)
            logger.debug("Clipboard copy succeeded: length=%d", len(text))
            return True
        except Exception as e:
            logger.error("Clipboard copy failed: %s", type(e).__name__)
            return False

    def read(self) -> str | None:
        """クリップボードのテキストを読み取る。空・失敗時は None を返す。"""
        try:
            text = pyperclip.paste()
            if text and text.strip():
                logger.debug("Clipboard read succeeded: length=%d", len(text))
                return text.strip()
            return None
        except Exception as e:
            logger.error("Clipboard read failed: %s", type(e).__name__)
            return None
