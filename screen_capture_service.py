import base64
import logging
from dataclasses import dataclass
from io import BytesIO

import mss
from PIL import Image
from pynput.mouse import Controller as MouseController

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CaptureResult:
    success: bool
    image_base64: str | None
    monitor_index: int | None
    error_message: str | None


class ScreenCaptureService:
    """マウスカーソルがあるモニターのスクリーンショットを取得する（BR-06）。

    画像はメモリ上のみで処理し、ディスクには書き込まない（SEC-02）。
    """

    def capture(self) -> CaptureResult:
        """現在のアクティブモニターをキャプチャし Base64 エンコードして返す。"""
        try:
            mouse_x, mouse_y = MouseController().position

            with mss.mss() as sct:
                target_monitor = sct.monitors[1]  # プライマリモニターをデフォルトに
                target_index = 1

                # マウスカーソルのあるモニターを特定（monitors[0] は全体なのでスキップ）
                for i, monitor in enumerate(sct.monitors[1:], start=1):
                    if (
                        monitor["left"] <= mouse_x < monitor["left"] + monitor["width"]
                        and monitor["top"] <= mouse_y < monitor["top"] + monitor["height"]
                    ):
                        target_monitor = monitor
                        target_index = i
                        break

                screenshot = sct.grab(target_monitor)
                img = Image.frombytes(
                    "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"
                )

                # 短辺を1280px以下にリサイズ（アップロード・推論時間削減）
                max_short_side = 1280
                w, h = img.size
                short_side = min(w, h)
                if short_side > max_short_side:
                    scale = max_short_side / short_side
                    img = img.resize(
                        (int(w * scale), int(h * scale)), Image.LANCZOS
                    )

                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            logger.debug(
                "Screen captured: monitor_index=%d, size=%s",
                target_index,
                screenshot.size,
            )
            return CaptureResult(
                success=True,
                image_base64=image_base64,
                monitor_index=target_index,
                error_message=None,
            )

        except Exception as e:
            logger.error("Screen capture failed: %s", type(e).__name__)
            return CaptureResult(
                success=False,
                image_base64=None,
                monitor_index=None,
                error_message=str(e),
            )
