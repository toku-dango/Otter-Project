import logging

import pyperclip

logger = logging.getLogger(__name__)


class ClipboardService:
    """クリップボードの読み書きを担当する。

    PAT-U2-06: 失敗時は False/None を返し、例外を外部に伝播しない（Null Object）。
    """

    def __init__(self) -> None:
        self._last_used: str | None = None  # 前回ホットキーで使用したクリップボード内容

    def copy(self, text: str) -> bool:
        """テキストをクリップボードにコピーする。成功時 True、失敗時 False を返す。"""
        try:
            pyperclip.copy(text)
            logger.debug("Clipboard copy succeeded: length=%d", len(text))
            return True
        except Exception as e:
            logger.error("Clipboard copy failed: %s", type(e).__name__)
            return False

    def read_fresh(self) -> str | None:
        """前回使用済みと同じ内容は無視し、新しい選択テキストのみ返す。

        ホットキー発火時に呼ぶことで「今コピーしたもの」だけを使える。
        返した内容は次回以降のために記憶する。
        """
        try:
            text = pyperclip.paste()
            if not text or not text.strip():
                return None
            text = text.strip()
            if text == self._last_used:
                logger.debug("Clipboard unchanged since last use, skipping")
                return None
            self._last_used = text
            logger.debug("Clipboard fresh text: length=%d", len(text))
            return text
        except Exception as e:
            logger.error("Clipboard read failed: %s", type(e).__name__)
            return None
