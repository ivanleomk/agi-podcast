# AGI Podcast — Build an AI Podcast Agent with Gemini Managed Agents

> **Workshop: AIE Singapore 2026**
>
> Build a fully automated podcast production pipeline powered by Gemini Managed Agents. You'll develop each piece locally first, test it, package it as a skill, and then hand it off to an agent that runs the whole thing end-to-end in a remote sandbox.

## What You'll Build

An AI agent that reads research articles, writes a co-host podcast script, generates speech, creates background music, mixes everything, and uploads the final episode — all orchestrated by a single `main.py`.

```
content/*.md → script.md → speech.wav → + music → final.mp3 → ☁️ GCS URL
```

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- A [Google AI API key](https://aistudio.google.com/apikey)
- `ffmpeg` installed (`brew install ffmpeg` / `apt install ffmpeg`)
- (Optional) A GCS service account key for upload

---

## Step 0 — Project Setup

```bash
mkdir agi-podcast && cd agi-podcast
uv init
uv add google-genai python-dotenv pydub google-cloud-storage
echo "GOOGLE_API_KEY=your-api-key-here" > .env
mkdir -p content .agents/skills
```

Set up `.gitignore`:

```gitignore
__pycache__/
*.py[oc]
.venv
.env
gcs-key.json
script.md
audio/
result.jsonl
```

Drop a research article into `content/` — this is what the podcast will be about.

---

## Step 1 — TTS: Develop Locally, Then Package as a Skill

The pattern for every skill is the same:
1. **Write the script locally** and test it
2. **Package it** into `.agents/skills/` with a `SKILL.md`
3. **Reference it** from `AGENTS.md` so the agent knows about it

### 1a. Write the TTS script locally

Create `generate_tts.py` at the project root and iterate on it until it works:

```python
#!/usr/bin/env python3
"""Generate speech audio from a podcast script using Gemini TTS."""

import argparse, io, os, re, time, threading
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from google import genai
from pydub import AudioSegment

load_dotenv()

# Rate limiter for TTS preview model limits
rate_limit_lock = threading.Lock()
last_request_time = 0.0

VOICES = {"paul": "Puck", "sarah": "Kore"}

def get_voice(speaker: str) -> str:
    return VOICES.get(speaker.lower().strip(), "Puck")

def parse_script(path: str) -> list[tuple[str, str]]:
    """Parse script.md into (speaker, text) turns."""
    turns = []
    pattern = re.compile(r"^\*?\*?([a-zA-Z0-9_\s]+)\*?\*?:\s*(.*)$")
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = pattern.match(line)
            if match:
                speaker = match.group(1).strip()
                text = match.group(2).strip().replace("**", "").replace("*", "")
                if speaker and text:
                    turns.append((speaker, text))
            elif turns:
                # Continuation line — append to previous turn
                turns[-1] = (turns[-1][0], turns[-1][1] + " " + line)
    return turns

def synthesize_turn(client, index, speaker, text, voice, out_dir):
    """Synthesize a single dialogue turn to WAV."""
    global last_request_time
    segment_path = os.path.join(out_dir, f"turn_{index:04d}.wav")
    print(f"🎙️  [Turn {index}] {speaker} ({voice}): {text[:60]}...")

    # Rate limit: ~1 request per 1.2s
    with rate_limit_lock:
        elapsed = time.time() - last_request_time
        if elapsed < 1.2:
            time.sleep(1.2 - elapsed)
        last_request_time = time.time()

    # The core TTS call
    response = client.models.generate_content(
        model="gemini-3.1-flash-tts-preview",
        contents=text,
        config={
            "response_modalities": ["AUDIO"],
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {"voice_name": voice}
                }
            }
        }
    )

    # Extract raw audio bytes
    audio_data = response.candidates[0].content.parts[0].inline_data.data

    # Convert raw PCM to WAV (24kHz, 16-bit, mono)
    segment = AudioSegment.from_raw(
        io.BytesIO(audio_data),
        sample_width=2, frame_rate=24000, channels=1
    )
    segment.export(segment_path, format="wav")
    print(f"✅ [Turn {index}] Done ({len(audio_data) / 1024:.1f} KB)")
    return segment_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", default="script.md")
    parser.add_argument("--out", default="audio")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    client = genai.Client()
    segments_dir = os.path.join(args.out, "segments")
    os.makedirs(segments_dir, exist_ok=True)

    turns = parse_script(args.script)
    print(f"📋 {len(turns)} turns, synthesizing with {args.workers} workers...\n")

    paths = [None] * len(turns)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(synthesize_turn, client, i, s, t, get_voice(s), segments_dir): i
            for i, (s, t) in enumerate(turns)
        }
        for fut, i in futures.items():
            paths[i] = fut.result()

    # Concatenate all segments
    combined = AudioSegment.empty()
    for p in paths:
        if p and os.path.exists(p):
            combined += AudioSegment.from_file(p)

    out_path = os.path.join(args.out, "speech.wav")
    combined.export(out_path, format="wav")
    print(f"\n✅ Saved to {out_path} ({os.path.getsize(out_path) / 1024 / 1024:.1f} MB)")

if __name__ == "__main__":
    main()
```

Test it locally (you'll need a `script.md` first — write one by hand or skip to Step 2):

```bash
uv run generate_tts.py --script script.md --out audio/ --workers 4
```

### 1b. Package it as a skill

Once it works, move it into the skills directory:

```bash
mkdir -p .agents/skills/generate_tts/scripts
mv generate_tts.py .agents/skills/generate_tts/scripts/
```

Create `.agents/skills/generate_tts/SKILL.md`:

```markdown
---
name: generate_tts
description: Generate TTS audio using the Gemini TTS API.
---

# TTS Generation Skill

Converts a podcast script into a WAV by synthesizing each dialogue turn.

## Co-Host Voices

| Speaker | Voice |
|---------|-------|
| Paul    | Puck  |
| Sarah   | Kore  |

## How to Run

\```bash
export GOOGLE_API_KEY=dummy
python3 /.agents/skills/generate_tts/scripts/generate_tts.py \
    --script /path/to/script.md \
    --out /path/to/audio \
    --workers 8
\```
```

Now the agent can read `SKILL.md` to understand what the skill does, and run the script.

---

## Step 2 — Script Writing: An LLM-Only Skill

Not every skill needs a Python script. The script-writing skill is just **instructions** — the agent writes the podcast script itself.

### 2a. Understand what a good script looks like

Write a sample `script.md` by hand first to understand the format:

```
Paul: Hey everyone, welcome back to AI Talk Radio. I'm Paul.
Sarah: And I'm Sarah. So Paul, [excitedly] have you seen what DeepMind just dropped?
Paul: Oh, you mean Genie 3? Yeah, 24 frames per second, 720p, real-time interactive worlds.
Sarah: [laughter] It's basically a game engine that dreams.
```

Key rules you want the agent to follow:
- No markdown formatting (no `**bold**`, no headers)
- Each line starts with `Paul: ` or `Sarah: `
- Emotion tags like `[laughter]`, `[sighs]` woven naturally
- ~1000 words, grounded in the research

### 2b. Package it as a skill

```bash
mkdir -p .agents/skills/script_writing
```

Create `.agents/skills/script_writing/SKILL.md`:

```markdown
---
name: script_writing
description: Write co-host podcast scripts from research materials.
---

# Script Writing Skill

You (the agent) write the script yourself — no Python script to run.

## Steps
1. Read the research files in `content/`.
2. Web search for extra context on the topics.
3. Write the script following the rules below.
4. Save to `script.md`.

## Script Guidelines

Co-Hosts:
- **Paul**: Thoughtful, tech-savvy.
- **Sarah**: Inquisitive, curious.

Goals:
1. Catchy title, introduced naturally in the banter.
2. Explain the tech in short, fun, conversational bites.
3. Highlight surprising facts from the research.
4. ~1000 words. No filler.

## Formatting Rules

- NO MARKDOWN. No bold, italics, headers, or lists. Pure text.
- Each line: `Paul: ` or `Sarah: ` (not bolded).
- Emotion tags in brackets: `[laughter]`, `[excitedly]`, `[sighs]`.
- Short sentences, natural speech, active banter.
- Ground everything in the research — don't fabricate.
```

---

## Step 3 — Music Generation: Develop Locally, Then Package

### 3a. Write the music generation script locally

```python
#!/usr/bin/env python3
"""Generate background music using Lyria-3."""

import argparse, base64, os
from dotenv import load_dotenv
from google import genai

load_dotenv()

FALLBACK_PROMPT = (
    "15-second lo-fi ambient intro. Soft synthesizer pads, gentle melodic tones, "
    "slow tempo. Calm, thoughtful, instrumental only."
)

def generate_music_prompt(client, script_content: str) -> str:
    """Use Gemini to craft a Lyria-3 prompt from the script."""
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=f"Write a 15-second Lyria-3 music prompt for this podcast:\n\n{script_content}",
        config={
            "system_instruction": (
                "You are a music prompt engineer for Lyria-3. "
                "Rules: instrumental only, 15 seconds, chill lo-fi ambient. "
                "Slow tempo, soft pads, gentle melodies. "
                "Output ONLY the prompt — no preamble, no markdown."
            )
        }
    )
    return response.text.strip().strip('"').strip("'")

def generate_music(client, prompt: str, out_dir: str) -> bool:
    """Call Lyria-3 and save the audio."""
    print(f'Prompt: "{prompt}"')
    interaction = client.interactions.create(
        model="lyria-3-clip-preview",
        input=prompt,
        store=False,
    )
    for step in getattr(interaction, "steps", []):
        for item in getattr(step, "content", []):
            if getattr(item, "type", "") == "audio":
                out_path = os.path.join(out_dir, "background.mp3")
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(item.data))
                print(f"✅ Saved to {out_path}")
                return True
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", default="script.md")
    parser.add_argument("--out", default="audio/music")
    args = parser.parse_args()

    client = genai.Client()
    os.makedirs(args.out, exist_ok=True)

    with open(args.script) as f:
        script = f.read()

    prompt = generate_music_prompt(client, script)
    if not generate_music(client, prompt, args.out):
        print("Retrying with fallback...")
        generate_music(client, FALLBACK_PROMPT, args.out)

if __name__ == "__main__":
    main()
```

Test locally:

```bash
uv run generate_music.py --script script.md --out audio/music
```

### 3b. Package it

```bash
mkdir -p .agents/skills/generate_music/scripts
mv generate_music.py .agents/skills/generate_music/scripts/
```

Create `.agents/skills/generate_music/SKILL.md` with usage instructions.

---

## Step 4 — Audio Mixing: Develop Locally, Then Package

### 4a. Write the mixer locally

The mixer combines `speech.wav` + `background.mp3` into a polished final MP3:

- Pad 3s silence at the end (so fade-out doesn't clip speech)
- Loop music to match speech duration, lower to -18dB
- Overlay speech on music with 1s music intro
- Fade-in/fade-out transitions
- Export as 192kbps MP3
- Optionally upload to GCS

```bash
uv run mix_audio.py --workspace . --upload --gcs-key gcs-key.json
```

### 4b. Package it

```bash
mkdir -p .agents/skills/audio_mixing/scripts
mv mix_audio.py .agents/skills/audio_mixing/scripts/
```

Create `.agents/skills/audio_mixing/SKILL.md` with arguments and mixing specs.

---

## Step 5 — Wire It All Together: `AGENTS.md`

Now that all 4 skills are packaged, create `.agents/AGENTS.md` — the master instruction file the managed agent reads:

```markdown
# Agent Instructions

You are a helpful developer assistant with code execution tools.

## Environment Notes

1. Set `GOOGLE_API_KEY=dummy` before running scripts (MITM proxy injects the real key).
2. Install ffmpeg: `which ffmpeg || (apt-get update && apt-get install -y ffmpeg)`
3. Install packages: `pip install google-genai python-dotenv pydub google-cloud-storage --break-system-packages`
4. Use `python3` directly, not `uv run`.
5. Every shell is fresh — use absolute paths.

## Podcast Production Workflow

### Step 0 — Setup dependencies
### Step 1 — Write script (script_writing skill)
### Step 2 — Generate TTS (generate_tts skill)
### Step 3 — Generate music (generate_music skill)
### Step 4 — Mix + upload (audio_mixing skill)
```

The agent reads this file, discovers the skills via SKILL.md references, and follows the workflow.

---

## Step 6 — The Orchestrator: `main.py`

This is where it all comes together. `main.py` bundles your local files into a remote sandbox and kicks off the agent.

### 6.1 Bundle files as inline sources

The agent runs in a **remote container** — it doesn't have your files. You inject them:

```python
def add_directory_sources(dir_path, sources):
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in [".git", ".venv", "__pycache__"]]
        for file in files:
            if file in [".env", ".DS_Store", "uv.lock"]:
                continue
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, start=".")
            try:
                with open(filepath, "r") as f:
                    sources.append({"type": "inline", "target": rel_path, "content": f.read()})
            except Exception:
                pass

sources = []
add_directory_sources(".agents", sources)
add_directory_sources("content", sources)
```

### 6.2 Create the interaction

```python
client = genai.Client()

interaction = client.interactions.create(
    agent="antigravity-preview-05-2026",
    input="Run the full podcast pipeline end-to-end...",
    stream=True,
    environment={
        "type": "remote",
        "sources": sources,
        "network": {
            "allowlist": [
                {
                    "domain": "generativelanguage.googleapis.com",
                    "transform": {"x-goog-api-key": os.environ["GOOGLE_API_KEY"]}
                },
                {"domain": "*"}
            ]
        }
    },
)
```

**Key concepts**:
- `environment.type: "remote"` — sandboxed container
- `sources` — your files injected into the container
- `network.allowlist[0].transform` — injects your API key into the agent's outbound Gemini API calls without exposing it in source files
- `stream=True` — real-time streaming events

### 6.3 Stream and parse

```python
for chunk in interaction:
    chunk_dict = chunk.model_dump()
    # Process step.start, step.delta, step.stop events
    # Collect full_text for URL extraction at the end
```

### 6.4 Run it

```bash
uv run main.py
```

---

## Step 7 — Automate with GitHub Actions (Optional)

Create `.github/workflows/generate.yaml`:

```yaml
name: Generate Podcast
on:
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
          python-version: "3.12"
      - name: Create GCS Key
        if: env.GCS_KEY_JSON != ''
        run: python3 -c "import os; open('gcs-key.json','w').write(os.environ['GCS_KEY_JSON'])"
        env:
          GCS_KEY_JSON: ${{ secrets.GCS_KEY_JSON }}
      - run: uv run main.py
        env:
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│  main.py (your machine / GitHub Actions)         │
│                                                  │
│  1. Bundle .agents/ + content/ as inline sources │
│  2. Create interaction → remote sandbox          │
│  3. Stream events back                           │
│  4. Parse GCS URL from response                  │
└──────────────┬───────────────────────────────────┘
               │ Gemini Interactions API
               ▼
┌──────────────────────────────────────────────────┐
│  Remote Sandbox                                  │
│                                                  │
│  Agent reads AGENTS.md                           │
│  ┌────────────┐  ┌────────────┐                  │
│  │ 1. Script  │→ │ 2. TTS     │                  │
│  │ (LLM)      │  │ (Flash)    │                  │
│  └────────────┘  └─────┬──────┘                  │
│  ┌────────────┐  ┌─────▼──────┐                  │
│  │ 3. Music   │→ │ 4. Mix +   │                  │
│  │ (Lyria-3)  │  │ Upload     │                  │
│  └────────────┘  └────────────┘                  │
└──────────────────────────────────────────────────┘
```

## Gemini APIs Used

| API | Model | Purpose |
|-----|-------|---------|
| Interactions | `antigravity-preview-05-2026` | Managed agent with code execution |
| Generate Content | `gemini-3.1-flash-tts-preview` | Text-to-speech |
| Generate Content | `gemini-3.5-flash` | Generate music prompt |
| Interactions | `lyria-3-clip-preview` | Music generation (Lyria-3) |

## Project Structure

```
agi-podcast/
├── .agents/
│   ├── AGENTS.md                          # Agent master instructions
│   └── skills/
│       ├── script_writing/SKILL.md        # Script writing guidelines
│       ├── generate_tts/
│       │   ├── SKILL.md
│       │   └── scripts/generate_tts.py
│       ├── generate_music/
│       │   ├── SKILL.md
│       │   └── scripts/generate_music.py
│       └── audio_mixing/
│           ├── SKILL.md
│           └── scripts/mix_audio.py
├── content/*.md                           # Research articles (input)
├── .github/workflows/generate.yaml        # CI automation
├── main.py                                # Orchestrator
├── pyproject.toml
└── .env                                   # API keys (not committed)
```
