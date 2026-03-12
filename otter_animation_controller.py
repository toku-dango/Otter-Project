import logging
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# 状態別プレースホルダー絵文字（GIF 不在時）
_PLACEHOLDER = {
    "idle":     "🦦",
    "thinking": "🦦💭",
    "done":     "🦦✨",
}

_DONE_AUTO_IDLE_MS = 2000  # DONE アニメーション後に IDLE へ戻るまでの時間


class AnimationState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    DONE = "done"


class OtterAnimationController:
    """Otter キャラクターのアニメーションを状態に応じて再生・切り替えする。

    PAT-U2-02: GIF ファイルが存在しない・破損している場合は
    絵文字プレースホルダーに自動フォールバックする。
    """

    def __init__(self, label: Any, assets_dir: str = "assets") -> None:
        self._label = label
        self._assets_dir = Path(assets_dir)
        self._frames: dict[str, list] = {}
        self._current_state: AnimationState | None = None
        self._frame_index: int = 0
        self._after_id: str | None = None
        self._load_animations()

    def _load_animations(self) -> None:
        """assets/ から状態別 GIF を読み込む。失敗はログのみ（フォールバックあり）。"""
        try:
            from PIL import Image, ImageTk
        except ImportError:
            logger.warning("Pillow not available, using placeholders only")
            return

        for state in AnimationState:
            gif_path = self._assets_dir / f"{state.value}.gif"
            if not gif_path.exists():
                logger.debug("GIF not found, will use placeholder: %s", gif_path)
                continue
            try:
                img = Image.open(gif_path)
                frames = []
                while True:
                    frames.append(ImageTk.PhotoImage(img.copy().convert("RGBA")))
                    try:
                        img.seek(img.tell() + 1)
                    except EOFError:
                        break
                self._frames[state.value] = frames
                logger.debug("GIF loaded: state=%s, frames=%d", state.value, len(frames))
            except Exception as e:
                logger.warning("GIF load failed: state=%s, %s", state.value, type(e).__name__)

    def play(self, state: AnimationState) -> None:
        """指定状態のアニメーションを再生する。"""
        self._stop_timer()
        self._current_state = state

        if state.value in self._frames and self._frames[state.value]:
            self._frame_index = 0
            self._animate()
        else:
            # プレースホルダーにフォールバック
            self._label.configure(text=_PLACEHOLDER[state.value], image="")
            if state == AnimationState.DONE:
                self._after_id = self._label.after(
                    _DONE_AUTO_IDLE_MS, lambda: self.play(AnimationState.IDLE)
                )

    def stop(self) -> None:
        """アニメーション再生を停止し、タイマーをキャンセルする。"""
        self._stop_timer()
        self._current_state = None

    def _animate(self) -> None:
        """次のフレームをラベルに描画し、タイマーで自身を再帰呼び出しする。"""
        if self._current_state is None:
            return
        frames = self._frames.get(self._current_state.value, [])
        if not frames:
            return

        frame = frames[self._frame_index]
        self._label.configure(image=frame, text="")
        self._label.image = frame  # GC 防止

        self._frame_index = (self._frame_index + 1) % len(frames)
        is_last_frame = self._frame_index == 0

        if self._current_state == AnimationState.DONE and is_last_frame:
            # DONE は1回再生後に IDLE へ自動遷移
            self._after_id = self._label.after(
                _DONE_AUTO_IDLE_MS, lambda: self.play(AnimationState.IDLE)
            )
        else:
            self._after_id = self._label.after(80, self._animate)  # ~12fps

    def _stop_timer(self) -> None:
        if self._after_id is not None:
            try:
                self._label.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
