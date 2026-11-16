from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VIDEO_DIR = ROOT / "video"
OUTPUT_DIR = ROOT / "output"
VIDEO_EXTENSIONS = {
    ".avi", ".flv", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg",
    ".mts", ".m2ts", ".ts", ".webm", ".wmv",
}
LEGACY_FRAME = re.compile(r"^(?:frame_)?\d+\.(?:jpg|png)$", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ekstrak frame dari semua video di folder video/ ke folder output/.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--interval", type=float, default=0.5,
        help="jarak antar gambar dalam detik; gunakan 0 untuk ekstrak semua frame",
    )
    parser.add_argument("--format", choices=("jpg", "png"), default="jpg", help="format gambar")
    parser.add_argument("--quality", type=int, default=2, help="kualitas JPG, 1 paling baik sampai 31 lebih kecil")
    parser.add_argument("--ffmpeg", default="", help="path ke ffmpeg.exe bila FFmpeg tidak ada di PATH")
    return parser.parse_args()


def find_ffmpeg(override: str) -> str | None:
    if override:
        candidate = Path(override.strip('"')).expanduser()
        if candidate.is_file():
            return str(candidate)
        return None
    return shutil.which("ffmpeg")


def clean_previous_frames(folder: Path, video_prefix: str) -> None:
    """Remove only frame files created by this converter before replacing a result."""
    current_frames = re.compile(
        rf"^{re.escape(video_prefix)}_\d+\.(?:jpg|png)$", re.IGNORECASE
    )
    for item in folder.iterdir():
        if item.is_file() and (
            LEGACY_FRAME.fullmatch(item.name) or current_frames.fullmatch(item.name)
        ):
            item.unlink()


def run_conversion(
    ffmpeg: str,
    video: Path,
    destination: Path,
    interval: float,
    image_format: str,
    quality: int,
) -> bool:
    destination.mkdir(parents=True, exist_ok=True)
    video_prefix = destination.name
    clean_previous_frames(destination, video_prefix)

    command = [ffmpeg, "-hide_banner", "-i", str(video), "-map", "0:v:0"]
    if interval > 0:
        command += ["-vf", f"fps=1/{interval:.12g}"]
    command += ["-fps_mode", "passthrough"]
    if image_format == "jpg":
        command += ["-q:v", str(quality)]
    else:
        command += ["-compression_level", "3"]
    command.append(str(destination / f"{video_prefix}_%03d.{image_format}"))

    print(f"\n[{video.name}] → {destination.relative_to(ROOT)}")
    try:
        completed = subprocess.run(command, check=False)
    except OSError as error:
        print(f"Gagal menjalankan FFmpeg: {error}", file=sys.stderr)
        return False

    if completed.returncode != 0:
        print(f"Gagal memproses {video.name} (kode {completed.returncode}).", file=sys.stderr)
        return False

    frame_count = sum(1 for _ in destination.glob(f"{video_prefix}_*.{image_format}"))
    if frame_count == 0:
        print(f"Tidak ada frame yang diekstrak dari {video.name}.", file=sys.stderr)
        return False
    print(f"Selesai: {frame_count:,} frame")
    return True


def main() -> int:
    args = parse_args()
    if args.interval < 0:
        print("Interval harus 0 atau lebih.", file=sys.stderr)
        return 2
    if not 1 <= args.quality <= 31:
        print("Kualitas JPG harus 1 sampai 31.", file=sys.stderr)
        return 2

    ffmpeg = find_ffmpeg(args.ffmpeg)
    if not ffmpeg:
        print(
            "FFmpeg tidak ditemukan. Pasang FFmpeg dan tambahkan ke PATH, "
            "atau jalankan dengan --ffmpeg \"C:\\path\\ke\\ffmpeg.exe\".",
            file=sys.stderr,
        )
        return 2

    if not VIDEO_DIR.is_dir():
        print(f"Folder input tidak ditemukan: {VIDEO_DIR}", file=sys.stderr)
        return 2
    videos = sorted(
        (path for path in VIDEO_DIR.iterdir() if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS),
        key=lambda path: path.name.casefold(),
    )
    if not videos:
        print(f"Belum ada video di folder {VIDEO_DIR}.")
        print("Masukkan file video ke folder video, lalu jalankan perintah ini lagi.")
        return 0

    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"Tidak bisa membuat folder output: {error}", file=sys.stderr)
        return 2

    print(f"Menemukan {len(videos)} video di folder video.")
    success_count = 0
    used_names: set[str] = set()
    for video in videos:
        folder_name = video.stem
        unique_name = folder_name
        suffix = 2
        while unique_name.casefold() in used_names:
            unique_name = f"{folder_name}_{suffix}"
            suffix += 1
        used_names.add(unique_name.casefold())
        destination = OUTPUT_DIR / unique_name
        if run_conversion(ffmpeg, video, destination, args.interval, args.format, args.quality):
            success_count += 1

    print(f"\nSelesai: {success_count}/{len(videos)} video berhasil.")
    print(f"Folder hasil: {OUTPUT_DIR}")
    return 0 if success_count == len(videos) else 1


if __name__ == "__main__":
    raise SystemExit(main())
