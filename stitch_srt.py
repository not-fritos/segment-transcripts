#!/usr/bin/env python3
"""Stitch together SRT subtitle files from a directory into one combined SRT."""

import argparse
import re
import sys
from pathlib import Path


def _ts_to_seconds(ts: str) -> float:
    """Convert SRT timestamp (HH:MM:SS,mmm) to seconds."""
    m = re.match(r"(\d{2}):(\d{2}):(\d{2})[.,](\d{3})", ts)
    if not m:
        return 0.0
    h, mn, s, ms = int(m[1]), int(m[2]), int(m[3]), int(m[4])
    return h * 3600 + mn * 60 + s + ms / 1000


def _format_timestamp(seconds: float) -> str:
    """Convert seconds (float) to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _parse_srt_entries(path: Path) -> list[tuple[str, str, str]]:
    """Parse an SRT file into a list of (start_ts, end_ts, text) tuples."""
    entries: list[tuple[str, str, str]] = []
    text = path.read_text(encoding="utf-8")

    block_pattern = re.compile(
        r"\d+\s*\n(\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[.,]\d{3})\s*\n(.+?)(?=\n\n|\Z)",
        re.DOTALL,
    )
    for match in block_pattern.finditer(text):
        start_ts = match.group(1).replace(",", ",")
        end_ts = match.group(2).replace(",", ",")
        text_content = match.group(3).strip()
        entries.append((start_ts, end_ts, text_content))

    return entries


def _apply_offset(
    entries: list[tuple[str, str, str]], offset_secs: float
) -> list[tuple[str, str, str]]:
    """Add offset_secs to all timestamps in a list of SRT entries."""
    result = []
    for start_ts, end_ts, text in entries:
        new_start = _format_timestamp(_ts_to_seconds(start_ts) + offset_secs)
        new_end = _format_timestamp(_ts_to_seconds(end_ts) + offset_secs)
        result.append((new_start, new_end, text))
    return result


def _chunk_index(path: Path) -> int:
    """Extract a 1-based chunk index from the filename stem (e.g. 0001 -> 1)."""
    stem = path.stem
    m = re.search(r"(\d+)", stem)
    return int(m[1]) if m else 0


def stitch_srt_files(input_dir: str, output_path: str, chunk_duration: int) -> None:
    """Combine all .srt files from input_dir into a single SRT file."""
    dir_path = Path(input_dir)
    if not dir_path.is_dir():
        print(f"Error: directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    srt_files = sorted(dir_path.glob("*.srt"))
    if not srt_files:
        print(f"Error: no .srt files found in {input_dir}", file=sys.stderr)
        sys.exit(1)

    all_entries: list[tuple[str, str, str]] = []
    for srt_path in srt_files:
        idx = _chunk_index(srt_path)
        offset = (idx - 1) * chunk_duration if idx > 0 else 0.0
        entries = _parse_srt_entries(srt_path)
        entries = _apply_offset(entries, offset)
        all_entries.extend(entries)

    with open(output_path, "w", encoding="utf-8") as f:
        for i, (start, end, text) in enumerate(all_entries, start=1):
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    print(f"Stitched {len(srt_files)} SRT file(s) -> {output_path}")
    print(f"  Total subtitle entries: {len(all_entries)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stitch multiple SRT subtitle files into one combined SRT."
    )
    parser.add_argument(
        "input_dir",
        help="Directory containing .srt subtitle files (sorted by filename)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output SRT file path (default: <input_dir>/combined.srt)",
    )
    parser.add_argument(
        "--chunk-duration",
        type=int,
        default=60,
        help="Duration of each video chunk in seconds (default: 60)",
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    output_path = args.output or str(Path(input_dir) / "combined.srt")

    stitch_srt_files(input_dir, output_path, args.chunk_duration)


if __name__ == "__main__":
    main()
