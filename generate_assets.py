"""Project Otter — アセット生成スクリプト

assets/ フォルダに idle.gif / thinking.gif / done.gif を生成する。
実行: python3 generate_assets.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)

SIZE = (80, 80)
BG = (45, 45, 48, 0)  # 透明背景


def new_frame() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    return img, draw


def draw_otter(draw: ImageDraw.ImageDraw, cx: int, cy: int, eye_open: bool = True) -> None:
    """カワウソの顔を描く"""
    # 体（茶色の丸）
    draw.ellipse([cx - 26, cy - 24, cx + 26, cy + 28], fill=(139, 90, 43, 255))
    # 顔（薄茶）
    draw.ellipse([cx - 22, cy - 20, cx + 22, cy + 22], fill=(193, 140, 80, 255))
    # 耳（左右）
    draw.ellipse([cx - 28, cy - 28, cx - 14, cy - 14], fill=(139, 90, 43, 255))
    draw.ellipse([cx + 14, cy - 28, cx + 28, cy - 14], fill=(139, 90, 43, 255))
    # 鼻
    draw.ellipse([cx - 5, cy - 2, cx + 5, cy + 5], fill=(60, 30, 10, 255))
    # 目
    if eye_open:
        draw.ellipse([cx - 12, cy - 12, cx - 5, cy - 5], fill=(30, 20, 10, 255))
        draw.ellipse([cx + 5, cy - 12, cx + 12, cy - 5], fill=(30, 20, 10, 255))
        # 目のハイライト
        draw.ellipse([cx - 10, cy - 11, cx - 8, cy - 9], fill=(255, 255, 255, 200))
        draw.ellipse([cx + 7, cy - 11, cx + 9, cy - 9], fill=(255, 255, 255, 200))
    else:
        # 閉じた目（まばたき）
        draw.arc([cx - 12, cy - 12, cx - 5, cy - 5], 0, 180, fill=(30, 20, 10, 255), width=2)
        draw.arc([cx + 5, cy - 12, cx + 12, cy - 5], 0, 180, fill=(30, 20, 10, 255), width=2)
    # 口（笑顔）
    draw.arc([cx - 8, cy + 4, cx + 8, cy + 14], 0, 180, fill=(60, 30, 10, 255), width=2)


def make_idle_gif() -> None:
    """待機: ゆらゆら上下に揺れる"""
    frames = []
    durations = []

    # 揺れパターン: オフセット
    offsets = [0, -2, -3, -2, 0, 2, 3, 2]
    blink_at = 6  # このフレームでまばたき

    for i, offset in enumerate(offsets):
        img, draw = new_frame()
        eye_open = (i != blink_at)
        draw_otter(draw, 40, 38 + offset, eye_open=eye_open)
        frames.append(img)
        durations.append(120)

    frames[0].save(
        ASSETS_DIR / "idle.gif",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
    )
    print("✓ idle.gif")


def make_thinking_gif() -> None:
    """思考中: 頭上に「...」が順番に出る"""
    frames = []
    durations = []

    dot_states = [
        [True, False, False],
        [True, True, False],
        [True, True, True],
        [False, False, False],
    ]

    for state in dot_states:
        img, draw = new_frame()
        draw_otter(draw, 40, 44, eye_open=True)
        # 思考の「...」
        for j, visible in enumerate(state):
            if visible:
                x = 44 + j * 9
                draw.ellipse([x, 12, x + 6, 18], fill=(200, 200, 220, 220))
        frames.append(img)
        durations.append(300)

    frames[0].save(
        ASSETS_DIR / "thinking.gif",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
    )
    print("✓ thinking.gif")


def make_done_gif() -> None:
    """完了: キラキラが出る"""
    frames = []
    durations = []

    sparkle_positions = [
        [(15, 15), (60, 20)],
        [(20, 10), (55, 25), (65, 55)],
        [(10, 20), (60, 10), (70, 50), (15, 60)],
        [(12, 15), (65, 15), (68, 52)],
        [(15, 20), (60, 20)],
        [],
    ]

    for sparkles in sparkle_positions:
        img, draw = new_frame()
        draw_otter(draw, 40, 42, eye_open=True)
        for sx, sy in sparkles:
            # 星形（十字で近似）
            draw.line([sx - 5, sy, sx + 5, sy], fill=(255, 220, 50, 230), width=2)
            draw.line([sx, sy - 5, sx, sy + 5], fill=(255, 220, 50, 230), width=2)
            draw.line([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 220, 50, 180), width=1)
            draw.line([sx + 3, sy - 3, sx - 3, sy + 3], fill=(255, 220, 50, 180), width=1)
        frames.append(img)
        durations.append(150)

    frames[0].save(
        ASSETS_DIR / "done.gif",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
    )
    print("✓ done.gif")


if __name__ == "__main__":
    make_idle_gif()
    make_thinking_gif()
    make_done_gif()
    print("完了: assets/ にGIFを生成しました")
