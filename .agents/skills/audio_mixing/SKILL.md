---
name: audio_mixing
description: Mix speech audio and background music into a polished radio show file.
---

# Audio Mixing Skill

Combines TTS speech audio and Lyria background music into a single, polished radio show MP3.

## Output

A final MP3 at `<workspace>/audio/final/ai_radio.mp3` (192kbps).

## Setup & Prerequisites

```bash
pip install pydub google-cloud-storage --break-system-packages
```

Requires `ffmpeg` installed on the system.

## How to Run

```bash
python3 /.agents/skills/audio_mixing/scripts/mix_audio.py \
    --workspace /path/to/workspace \
    --upload \
    --gcs-key /path/to/gcs-key.json
```

## Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--workspace` | `.` | Root workspace directory |
| `--upload` | `false` | Upload final MP3 to GCS after mixing |
| `--gcs-key` | `$GOOGLE_GCS_KEY_PATH` | Path to GCS service account JSON key |

## What it does

1. Loads speech from `<workspace>/audio/speech.wav`.
2. Adds 3 seconds of silence padding to prevent fade-out from cutting into speech.
3. Loads background music from `<workspace>/audio/music/background.mp3` (if it exists).
4. Loops music to match speech duration, lowers volume to -18 dB.
5. Overlays speech on music with a 1-second music intro.
6. Applies fade-in/fade-out transitions.
7. Exports as MP3 (192kbps).
8. If `--upload` is set, uploads to GCS bucket `agi-podcast-audio` and prints the public URL.

## Mixing Levels

| Element | Level | Notes |
|---------|-------|-------|
| Speech | 0 dB | Untouched, full volume |
| Background music | -18 dB | Barely audible bed under speech |

## Transitions

| Transition | Duration |
|------------|----------|
| Music fade-in | 3 seconds |
| Music fade-out | 5 seconds |
| Overall fade-in | 500ms |
| Overall fade-out | 2 seconds |

## Fallback

If no background music exists, produces speech-only output with just fade-in/fade-out applied.
