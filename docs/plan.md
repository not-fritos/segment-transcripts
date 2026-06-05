# Video Segmentation Tool — Plan

## Requirements

- **Inputs:**
  1. Path to a video file
  2. Chunk duration (default: 60 seconds / 1 minute)
- **Output directories (created alongside the input video or in a specified location):**
  1. `video-chunks/` — segmented video chunks in `.mp4` format
  2. `audio/` — audio chunks in `.flac` format
  3. `subtitle/` — subtitle chunks in `.srt` format
- **Naming convention:** `[xxxx].[extension]` where `xxxx` is a zero-padded chunk number (e.g., `0001.mp4`, `0002.flac`, `0003.srt`)
- **Pipeline flow:**
  1. Validate that the input video exists
  2. Segment video into chunks of the specified duration → `video-chunks/`
  3. For each video chunk, extract audio → `audio/`
  4. For each audio chunk, transcribe via Whisper → `subtitle/`
- **Tools/libraries:**
  - `ffmpeg` (via `ffmpeg-python` or subprocess) for video/audio processing
  - `openai-whisper` for speech-to-text transcription
- **Style:** Clean coding, self-descriptive names, function comments where relevant, readability and conciseness prioritized
- **Python CLI script**

## Proposed Architecture

```
project/
├── docs/
│   └── plan.md            ← this file
├── segment.py             ← main CLI entrypoint
├── requirements.txt       ← Python dependencies
└── (output dirs created at runtime)
```

## Decisions Required

> Each item below is an open question. You will present them to the user one at a time and wait for approval before proceeding.

- [x] **Decision 1:** Output dirs go under `./output/` in the current working directory
- [x] **Decision 2:** Use `argparse` with `--video` and `--chunk-duration` flags
- [x] **Decision 3:** Use `ffmpeg-python` library
- [x] **Decision 4:** Use Whisper `large` model

## Execution Steps

- [x] **Step 1:** Create `requirements.txt` with dependencies
- [x] **Step 2:** Create `segment.py` — argument parsing and scaffolding
- [x] **Step 3:** Implement input validation
- [x] **Step 4:** Implement video chunking logic
- [x] **Step 5:** Implement audio extraction for each chunk
- [x] **Step 6:** Implement subtitle transcription for each audio chunk
- [x] **Step 7:** Wire up the pipeline flow
- [x] **Step 8:** Test with `zoom0006.mp4`

---

*Plan will be updated as decisions are made.*
