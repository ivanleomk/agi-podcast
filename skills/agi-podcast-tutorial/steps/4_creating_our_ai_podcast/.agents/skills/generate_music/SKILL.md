---
name: generate_music
description: A skill to generate a chill lo-fi background music intro for AI Talk Radio using the Lyria-3 model.
---

# Music Generation Skill

This skill generates a short ambient intro track for the podcast by using Gemini to craft a tailored music prompt and then calling Lyria-3 to produce the audio.

## Output

A 15-second lo-fi ambient MP3 saved to `<out>/background.mp3`.

## Setup & Prerequisites

```bash
pip install google-genai python-dotenv --break-system-packages
```

## How to Run

```bash
export GOOGLE_API_KEY=dummy  # MITM proxy injects the real key
python3 /.agents/skills/generate_music/scripts/generate_music.py \
    --script /path/to/script.md \
    --out /path/to/audio/music
```

This will:
1. Read the podcast script to understand the episode's topic and mood.
2. Use `gemini-3.5-flash` to generate a tailored Lyria-3 music prompt (chill, lo-fi, 15 seconds).
3. Call `lyria-3-clip-preview` to produce the audio.
4. Save the result to `<out>/background.mp3`.
