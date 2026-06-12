#!/usr/bin/env python3
"""Stitch video chunk files back into a single video file."""

import argparse
import sys
import tempfile
from pathlib import Path

import ffmpeg


def stitch_videos(input_dir: str, output_path: str) -> None:
    dir_path = Path(input_dir)
    if not dir_path.is_dir():
        print(f"Error: directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    video_files = sorted(dir_path.glob("*.mp4"))
    if not video_files:
        print(f"Error: no .mp4 files found in {input_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Stitching {len(video_files)} video chunk(s) -> {output_path}")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        filelist = f.name
        for v in video_files:
            f.write(f"file '{v.resolve()}'\n")

    try:
        stream = ffmpeg.input(filelist, f="concat", safe=0)
        stream = ffmpeg.output(stream, output_path, c="copy")
        ffmpeg.run(stream, quiet=True, overwrite_output=True)
        print("Done!")
    finally:
        Path(filelist).unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stitch video chunk files into a single video."
    )
    parser.add_argument(
        "input_dir",
        help="Directory containing .mp4 video chunk files",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output video path (default: <input_dir>/combined.mp4)",
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    output_path = args.output or str(Path(input_dir) / "combined.mp4")

    stitch_videos(input_dir, output_path)


if __name__ == "__main__":
    main()
