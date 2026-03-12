"""
Otter GIF Generator
ベース画像4枚から状態別GIF（透過背景）を生成するスクリプト
"""

from pathlib import Path
from PIL import Image
import math

SOURCE_DIR = Path("!result/260313")
OUTPUT_DIR = Path("assets/otter")

# ソース画像
SOURCES = {
    "base":     SOURCE_DIR / "base.png",
    "thinking": SOURCE_DIR / "thinking.png",
    "speaking": SOURCE_DIR / "speaking.png",
    "done":     SOURCE_DIR / "done.png",
}

# GIF設定
CANVAS_SIZE = (300, 300)  # 出力サイズ（正方形）


def remove_white_background(img: Image.Image, threshold: int = 240) -> Image.Image:
    """白背景をアルファ透過に変換"""
    img = img.convert("RGBA")
    data = img.getdata()
    new_data = []
    for r, g, b, a in data:
        if r > threshold and g > threshold and b > threshold:
            new_data.append((r, g, b, 0))  # 透明
        else:
            new_data.append((r, g, b, a))
    img.putdata(new_data)
    return img


def fit_to_canvas(img: Image.Image, size: tuple) -> Image.Image:
    """透過キャンバスにセンタリングしてリサイズ"""
    img.thumbnail((size[0] - 20, size[1] - 20), Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    offset = ((size[0] - img.width) // 2, (size[1] - img.height) // 2)
    canvas.paste(img, offset, img)
    return canvas


def make_idle_gif(base_img: Image.Image, output_path: Path):
    """baseをゆらゆら回転させてidleアニメGIFを作成（8フレーム）"""
    # 回転角度（度）: 0→-10→-15→-10→0→+10→+15→+10→(loop)
    angles = [0, -6, -12, -6, 0, 6, 12, 6]
    frames = []

    for angle in angles:
        rotated = base_img.rotate(angle, resample=Image.BICUBIC, expand=False)
        frames.append(rotated)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=120,  # ms per frame
        disposal=2,
    )
    print(f"  → {output_path} ({len(frames)} frames, {len(angles)*120}ms/loop)")


def make_thinking_gif(thinking_img: Image.Image, output_path: Path):
    """thinkingは小さく上下にぼよんするアニメ（6フレーム）"""
    base_size = CANVAS_SIZE
    frames = []

    # 上下オフセット（px）: 0, -4, -7, -4, 0, +3
    offsets = [0, -4, -7, -4, 0, 3]

    for dy in offsets:
        canvas = Image.new("RGBA", base_size, (0, 0, 0, 0))
        img_copy = thinking_img.copy()
        cx = (base_size[0] - img_copy.width) // 2
        cy = (base_size[1] - img_copy.height) // 2 + dy
        canvas.paste(img_copy, (cx, cy), img_copy)
        frames.append(canvas)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=150,
        disposal=2,
    )
    print(f"  → {output_path} ({len(frames)} frames)")


def make_speaking_gif(speaking_img: Image.Image, output_path: Path):
    """speakingは手がぴょこぴょこするアニメ（base + speaking交互）"""
    # base と speaking を交互に表示（口パクっぽく）
    base_img = fit_to_canvas(
        remove_white_background(Image.open(SOURCES["base"])), CANVAS_SIZE
    )
    frames = [speaking_img, base_img, speaking_img, base_img, speaking_img, base_img]

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=200,
        disposal=2,
    )
    print(f"  → {output_path} ({len(frames)} frames)")


def make_done_gif(done_img: Image.Image, output_path: Path):
    """doneはドンっと表示してフェードっぽく（done→base）"""
    base_img = fit_to_canvas(
        remove_white_background(Image.open(SOURCES["base"])), CANVAS_SIZE
    )
    frames = [done_img, done_img, done_img, base_img]
    durations = [100, 100, 300, 500]

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        loop=1,  # 1回だけ再生
        duration=durations,
        disposal=2,
    )
    print(f"  → {output_path} ({len(frames)} frames, plays once)")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("=== Otter GIF Generator ===\n")

    # 各画像を読み込み → 背景透過 → キャンバスフィット
    print("[1/2] 画像を読み込み中...")
    prepared = {}
    for name, path in SOURCES.items():
        if not path.exists():
            print(f"  !! {path} が見つかりません")
            return
        img = Image.open(path)
        img = remove_white_background(img)
        img = fit_to_canvas(img, CANVAS_SIZE)
        prepared[name] = img
        print(f"  ✓ {name}: {path}")

    print("\n[2/2] GIF生成中...")
    make_idle_gif(prepared["base"],         OUTPUT_DIR / "idle.gif")
    make_thinking_gif(prepared["thinking"], OUTPUT_DIR / "thinking.gif")
    make_speaking_gif(prepared["speaking"], OUTPUT_DIR / "speaking.gif")
    make_done_gif(prepared["done"],         OUTPUT_DIR / "done.gif")

    print(f"\n完了！ → {OUTPUT_DIR}/")
    print("  idle.gif     — ゆらゆら待機")
    print("  thinking.gif — ぼよん思考中")
    print("  speaking.gif — 口パク返答中")
    print("  done.gif     — バンザイ完了（1回再生）")


if __name__ == "__main__":
    main()
