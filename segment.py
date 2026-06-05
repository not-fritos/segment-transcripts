#!/usr/bin/env python3
"""Segment a video into chunks, extract audio, and generate subtitles."""

import argparse
import sys
from pathlib import Path

import ffmpeg
import whisper


def _format_timestamp(seconds: float) -> str:
    """Convert seconds (float) to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _write_srt(segments: list[dict], srt_path: str) -> None:
    """Write Whisper transcription segments to an SRT subtitle file."""
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start = _format_timestamp(seg["start"])
            end = _format_timestamp(seg["end"])
            text = seg["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")


def _validate_input(video_path: str) -> Path:
    """Check that the input video file exists. Exit with error if not."""
    path = Path(video_path)
    if not path.exists():
        print(f"Error: video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)
    return path


def _create_output_dirs(base_dir: str) -> dict[str, Path]:
    """Create the three output subdirectories under base_dir."""
    dirs = {
        "video": Path(base_dir) / "video-chunks",
        "audio": Path(base_dir) / "audio",
        "subtitle": Path(base_dir) / "subtitle",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def _chunk_video(
    video_path: Path, chunk_duration: int, output_dir: Path
) -> list[Path]:
    """Split video into chunks of given duration using ffmpeg segment muxer.

    Returns a sorted list of created chunk file paths.
    """
    print(f"Chunking video into {chunk_duration}s segments...")

    output_pattern = str(output_dir / "%04d.mp4")

    stream = ffmpeg.input(str(video_path))
    stream = ffmpeg.output(
        stream,
        output_pattern,
        f="segment",
        segment_time=chunk_duration,
        reset_timestamps=1,
        segment_start_number=1,
        c="copy",
    )
    ffmpeg.run(stream, quiet=True, overwrite_output=True)

    chunks = sorted(output_dir.glob("*.mp4"))
    print(f"  Created {len(chunks)} video chunk(s)")
    return chunks


def _extract_audio(video_chunk: Path, output_dir: Path) -> Path:
    """Extract audio from a video chunk as a FLAC file."""
    audio_path = output_dir / f"{video_chunk.stem}.flac"

    stream = ffmpeg.input(str(video_chunk))
    stream = ffmpeg.output(stream, str(audio_path), acodec="flac")
    ffmpeg.run(stream, quiet=True, overwrite_output=True)

    return audio_path


def _transcribe_audio(
    audio_path: Path, model: whisper.Whisper, output_dir: Path
) -> Path:
    """Transcribe audio with Whisper and write an SRT subtitle file."""
    srt_path = output_dir / f"{audio_path.stem}.srt"

    print(f"  Transcribing {audio_path.name}...")
    result = model.transcribe(str(audio_path))
    _write_srt(result["segments"], str(srt_path))

    return srt_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Segment a video into chunks with audio and subtitles."
    )
    parser.add_argument(
        "--video",
        required=True,
        help="Path to the input video file",
    )
    parser.add_argument(
        "--chunk-duration",
        type=int,
        default=60,
        help="Duration of each chunk in seconds (default: 60)",
    )
    args = parser.parse_args()

    video_path = _validate_input(args.video)
    output_base = Path.cwd() / "output"
    dirs = _create_output_dirs(str(output_base))

    print(f"Output directory: {output_base}")
    print("Loading Whisper model (large)...")
    model = whisper.load_model("large")

    chunks = _chunk_video(video_path, args.chunk_duration, dirs["video"])

    for i, chunk in enumerate(chunks, start=1):
        print(f"[{i}/{len(chunks)}] Processing {chunk.name}...")

        audio_path = _extract_audio(chunk, dirs["audio"])
        print(f"  Audio -> {audio_path.name}")

        srt_path = _transcribe_audio(audio_path, model, dirs["subtitle"])
        print(f"  Subtitle -> {srt_path.name}")

    print("Done!")


if __name__ == "__main__":
    main()
