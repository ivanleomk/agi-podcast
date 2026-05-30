---
name: generate_tts
description: A skill to generate TTS audio for AI Talk Radio co-host scripts using the Gemini TTS API.
---

# TTS Generation Skill

This skill converts a podcast script (`script.md`) into a full WAV audio file by synthesizing each dialogue turn using the Gemini TTS API.

## Co-Host Voices

| Speaker | Voice |
|---------|-------|
| Paul    | Puck  |
| Sarah   | Kore  |

## Setup & Prerequisites

Install required Python dependencies:
```bash
pip install google-genai pydub --break-system-packages
```

`pydub` also requires `ffmpeg` for some audio formats. WAV output works without it.

## How to Run

```bash
export GOOGLE_API_KEY=dummy  # MITM proxy injects the real key
python3 /.agents/skills/generate_tts/scripts/generate_tts.py \
    --script /path/to/script.md \
    --out /path/to/audio/output \
    --workers 8
```

This will:
1. Parse the script into individual dialogue turns.
2. Synthesize each turn in parallel using `gemini-3.1-flash-tts-preview`.
3. Save each segment to `<out>/segments/turn_XXXX.wav`.
4. Concatenate all segments into a final `<out>/speech.wav`.
