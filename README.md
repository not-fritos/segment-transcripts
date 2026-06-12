# contracked-segmentation

Segment a video into chunks, extract audio, and generate SRT subtitle files using Whisper.

## Requirements

- **Python 3.8+**
- **ffmpeg** — install via [Homebrew](https://brew.sh): `brew install ffmpeg`

## Setup

```bash
# Clone the repo
git clone <repo-url>
cd contracked-segmentation

# Create a virtualenv (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (includes ffmpeg-python and openai-whisper)
pip install -r requirements.txt

**Note:** The first run downloads the Whisper `large` model (~3 GB) automatically.
```

## Usage

```bash
python segment.py --video /path/to/video.mp4
```

Optional: set chunk duration in seconds (default: 60).

```bash
python segment.py --video zoom0006.mp4 --chunk-duration 120
```

Optional: set the output directory (defaut: output)

Output is written to `./output/`:
```
output/
├── video-chunks/  # .mp4 segments
├── audio/         # .flac audio files
└── subtitle/      # .srt subtitle files
```

Example:
```
python3 segment.py --video zoom0007.mp4 --chunk-duration 60 --output session-03-output
```

## Notes

- Each video chunk is processed sequentially — long videos may take significant time.

---

Built with [opencode/big-pickle](https://opencode.ai).
