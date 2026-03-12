"""Project Otter — アセット生成スクリプト

assets/ フォルダに idle.gif / thinking.gif / done.gif を生成する。
実行: python3 generate_assets.py
"""

from pathlib import Path
from PIL import Image, ImageDraw

ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)

SIZE = (120, 80)


def new_frame() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    return img, draw


def draw_otter_side(draw: ImageDraw.ImageDraw, x: int, y: int,
                    leg_phase: int = 0, eye_open: bool = True) -> None:
    """横向きカワウソを描く。x,y は体の中心。leg_phase=0~3"""

    # 尻尾（後ろ）
    tail_points = [
        (x - 28, y + 2),
        (x - 42, y - 8),
        (x - 50, y + 4),
        (x - 38, y + 12),
    ]
    draw.polygon(tail_points, fill=(110, 70, 30, 255))

    # 体
    draw.ellipse([x - 28, y - 14, x + 24, y + 16], fill=(139, 90, 43, 255))

    # お腹（薄い色）
    draw.ellipse([x - 18, y - 8, x + 16, y + 14], fill=(193, 150, 90, 255))

    # 脚（走るアニメ）
    leg_configs = [
        # phase0: 前脚前・後脚後ろ
        [(-10, 16, -6, 28), (8, 16, 18, 26)],
        # phase1: 両脚中間
        [(-14, 16, -10, 28), (4, 16, 14, 26)],
        # phase2: 前脚後ろ・後脚前
        [(-16, 16, -8, 26), (0, 16, 8, 28)],
        # phase3: 両脚中間（逆）
        [(-12, 16, -4, 26), (4, 16, 16, 28)],
    ]
    for lx1, ly1, lx2, ly2 in leg_configs[leg_phase % 4]:
        draw.ellipse([x + lx1, y + ly1, x + lx2, y + ly2],
                     fill=(110, 70, 30, 255))

    # 頭
    draw.ellipse([x + 8, y - 26, x + 42, y + 4], fill=(139, 90, 43, 255))

    # 顔（薄茶）
    draw.ellipse([x + 12, y - 22, x + 40, y + 2], fill=(193, 150, 90, 255))

    # 耳
    draw.ellipse([x + 10, y - 30, x + 22, y - 18], fill=(139, 90, 43, 255))
    draw.ellipse([x + 26, y - 30, x + 38, y - 20], fill=(139, 90, 43, 255))

    # 目
    if eye_open:
        draw.ellipse([x + 26, y - 18, x + 33, y - 11], fill=(30, 20, 10, 255))
        draw.ellipse([x + 28, y - 17, x + 30, y - 15], fill=(255, 255, 255, 200))
    else:
        draw.arc([x + 26, y - 18, x + 33, y - 11], 0, 180, fill=(30, 20, 10, 255), width=2)

    # 鼻
    draw.ellipse([x + 35, y - 10, x + 41, y - 5], fill=(50, 25, 10, 255))

    # ひげ
    draw.line([x + 41, y - 9, x + 52, y - 12], fill=(200, 180, 150, 200), width=1)
    draw.line([x + 41, y - 7, x + 52, y - 7], fill=(200, 180, 150, 200), width=1)


def make_idle_gif() -> None:
    """待機: 楽しそうに走っている"""
    frames = []
    durations = []

    # 走る：4フレームループ + 体の上下ぶれ
    run_data = [
        (0, 0),   # phase, y_offset
        (1, -2),
        (2, 0),
        (3, -2),
        (0, 0),
        (1, -2),
        (2, 0),
        (3, -2),
    ]
    blink_at = 6

    for i, (phase, y_off) in enumerate(run_data):
        img, draw = new_frame()
        eye_open = (i != blink_at)
        draw_otter_side(draw, 30, 42 + y_off, leg_phase=phase, eye_open=eye_open)
        frames.append(img)
        durations.append(100)

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
    """思考中: 立ち止まって頭上に「...」"""
    frames = []
    durations = []

    dot_states = [
        [True, False, False],
        [True, True, False],
        [True, True, True],
        [False, True, True],
        [False, False, True],
        [False, False, False],
    ]

    for i, state in enumerate(dot_states):
        img, draw = new_frame()
        draw_otter_side(draw, 20, 44, leg_phase=0, eye_open=True)
        # 思考の「...」
        for j, visible in enumerate(state):
            if visible:
                x = 62 + j * 10
                draw.ellipse([x, 8, x + 7, 15], fill=(180, 180, 220, 220))
        frames.append(img)
        durations.append(280)

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
    """完了: ジャンプしてキラキラ"""
    frames = []
    durations = []

    # ジャンプ: y_offset が上がって戻る
    jump_offsets = [0, -6, -10, -10, -6, 0, 0]
    sparkle_frames = [[], [], [(80, 10), (100, 20)], [(75, 8), (105, 15), (90, 25)],
                      [(80, 12), (100, 22)], [(85, 10)], []]

    for y_off, sparkles in zip(jump_offsets, sparkle_frames):
        img, draw = new_frame()
        draw_otter_side(draw, 20, 44 + y_off, leg_phase=0, eye_open=True)
        for sx, sy in sparkles:
            draw.line([sx - 5, sy, sx + 5, sy], fill=(255, 220, 50, 230), width=2)
            draw.line([sx, sy - 5, sx, sy + 5], fill=(255, 220, 50, 230), width=2)
        frames.append(img)
        durations.append(120)

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
