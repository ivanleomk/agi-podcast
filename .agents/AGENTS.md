# Agent Instructions

You are a helpful developer assistant with code execution tools.

## Environment Notes

1. Set `GOOGLE_API_KEY=dummy` before running any scripts. There is a MITM proxy in place that will inject the real API key automatically via the `x-goog-api-key` header transform.
2. **System Dependencies**: Ensure `ffmpeg` is installed on the host. If missing, install it:
   ```bash
   which ffmpeg || (apt-get update && apt-get install -y ffmpeg)
   ```
3. **Python Packages**: You can install all pipeline dependencies in one go:
   ```bash
   pip install google-genai python-dotenv pydub google-cloud-storage --break-system-packages
   ```
4. Run all Python scripts using `python3` directly, not `uv run`.
5. Every shell is a fresh shell — always use full absolute paths when executing commands or referencing files.

## Podcast Production Workflow

Follow these steps in order to produce a complete podcast episode:

### Step 0 — Setup Dependencies (System & Python)

Before running any of the podcast scripts, ensure all system and Python package dependencies are fully installed:

```bash
# 1. Install system dependency ffmpeg if missing
which ffmpeg || (apt-get update && apt-get install -y ffmpeg)

# 2. Install all Python packages in one go
pip install google-genai python-dotenv pydub google-cloud-storage --break-system-packages
```

### Step 1 — Write the Script (`script_writing` skill)

Read `/.agents/skills/script_writing/SKILL.md` for full instructions.

```bash
pip install google-genai python-dotenv --break-system-packages
export GOOGLE_API_KEY=dummy
python3 /.agents/skills/script_writing/scripts/write_script.py
```

Output: `script.md` in the working directory.

### Step 2 — Generate TTS Audio (`generate_tts` skill)

Read `/.agents/skills/generate_tts/SKILL.md` for full instructions.

```bash
pip install google-genai pydub --break-system-packages
export GOOGLE_API_KEY=dummy
python3 /.agents/skills/generate_tts/scripts/generate_tts.py \
    --script /path/to/script.md \
    --out /path/to/audio \
    --workers 8
```

Output: individual segment WAVs in `<out>/segments/` and a combined `<out>/speech.wav`.

### Step 3 — Generate Background Music (`generate_music` skill)

Read `/.agents/skills/generate_music/SKILL.md` for full instructions.

```bash
pip install google-genai python-dotenv --break-system-packages
export GOOGLE_API_KEY=dummy
python3 /.agents/skills/generate_music/scripts/generate_music.py \
    --script /path/to/script.md \
    --out /path/to/audio/music
```

Output: `<out>/background.mp3` — a 15-second chill lo-fi ambient intro track.

### Step 4 — Mix and Upload Audio (`audio_mixing` skill)

Read `/.agents/skills/audio_mixing/SKILL.md` for full instructions.

```bash
pip install pydub google-cloud-storage --break-system-packages
python3 /.agents/skills/audio_mixing/scripts/mix_audio.py \
    --workspace /path/to/workspace \
    --upload \
    --gcs-key /path/to/gcs-key.json
```

Output: A mixed MP3 at `<workspace>/audio/final/ai_radio.mp3` and a public GCS URL.


