---
name: agi-podcast-tutorial
description: A step-by-step interactive tutorial skill to guide developers and agents in building an AGI Podcast Production Pipeline.
---

# AGI Podcast Tutorial Skill

Welcome! This skill is designed to guide developers and coding agents step-by-step through understanding and building with the Gemini Interactions API, starting from the simplest agent invocation to a full-fledged streaming client and ending with a completely automated podcast production pipeline.

---

## 🗺️ Learning Roadmap

1. **Step 0: First Interaction** — Verify authentication and make a basic conversational call to the Interactions API.
2. **Step 1: Spawning a Simple Agent** — Spin up a managed agent that writes and executes code locally.
3. **Step 2: Building Streaming Interactions** — Capture real-time events and build a custom live output parser.
4. **Step 3: The End-to-End Podcast Pipeline** — Wire local tasks as reusable agent skills, bundle local source codes, inject environment key transforms, and run the complete pipeline remotely.

---

## 🔑 Setup & API Key Configuration

Before running any code, you need a Google Gemini API key. 

1. Go to **[ai.dev](https://ai.dev)** (or Google AI Studio).
2. Generate an API key.
3. Configure it in your terminal environment:
   ```bash
   export GOOGLE_API_KEY="your-gemini-api-key-here"
   ```
   Or place it in a `.env` file at the root of your workspace:
   `GOOGLE_API_KEY=your-gemini-api-key-here`

---

## 👋 Step 0: First Interaction

Let's verify that your environment is fully working by making a basic conversational request to the managed agent.

### Reference Code
You can find this complete pre-bundled example in [first_interaction.py](./steps/0_first_interaction/first_interaction.py). You can run it directly:

```python
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize the GenAI Client
client = genai.Client()

print("User > What is the capital of France?")

# Create a simple conversational interaction
response = client.interactions.create(
    agent="antigravity-preview-05-2026",
    input="What is the capital of France?"
)

# Output the final text response
print(f"\nAgent > {response.text}")
```

### Reference Code (Streaming)
You can also run the streaming equivalent in [first_interaction_streaming.py](./steps/0_first_interaction/first_interaction_streaming.py) to see text deltas printed in real-time:

```python
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

print("User > What is the capital of France?")
print("\nAgent > ", end="", flush=True)

response = client.interactions.create(
    agent="antigravity-preview-05-2026",
    input="What is the capital of France?",
    stream=True
)

for chunk in response:
    if hasattr(chunk, "model_dump"):
        event = chunk.model_dump()
        delta = event.get("delta", {})
        if delta.get("type") == "text":
            print(delta.get("text", ""), end="", flush=True)
print()
```

### Run Them:
```bash
# Non-streaming version:
uv run steps/0_first_interaction/first_interaction.py

# Streaming version:
uv run steps/0_first_interaction/first_interaction_streaming.py
```
*If you see the correct answer from the agent in both cases, your setup is correct and you are ready for Step 1!*

---

## 🐣 Step 1: Spawning a Simple Agent (Code Execution)

Now let's look at how the managed agent can naturally write and execute code in its remote sandbox container to solve tasks for you.

### The Simplest Code Example
You can find this complete pre-bundled example in [simple_agent.py](./steps/1_creating_our_agent/simple_agent.py). You can run it directly:

```python
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize the GenAI Client
client = genai.Client()

# Create a simple agent interaction
print("🚀 Spawning agent...")
interaction = client.interactions.create(
    agent="antigravity-preview-05-2026",
    input="Show me that you can execute code. Write a Python script to compute the 10th Fibonacci number."
)

# Output the final text response
print("\n🤖 Agent Response:")
print(interaction.text)
```

### Run It:
```bash
uv run steps/1_creating_our_agent/simple_agent.py
```
*Observe how the agent automatically writes, runs, and captures the output of the Python script in its remote sandbox to answer your question!*

---

## 🌊 Phase 2: Building Streaming Interactions

When running longer tasks or multi-stage operations, waiting for the entire interaction to complete before seeing output can feel unresponsive. By setting `stream=True`, we can listen to the event stream in real-time.

Let's look at the streaming agent script [streaming_agent.py](./steps/2_building_streaming_interactions/streaming_agent.py) that listens to live text chunks and thinking summaries:

```python
import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

print("🌊 Spawning streaming agent...")
interaction = client.interactions.create(
    agent="antigravity-preview-05-2026",
    input="Write a python code block to count to 5 with 1 second delay between numbers, execute it, and print the numbers.",
    stream=True
)

# Stream and print events
for chunk in interaction:
    # Under the hood, chunks are JSON events.
    # We can extract text delta and print it immediately:
    if hasattr(chunk, "model_dump"):
        event = chunk.model_dump()
        delta = event.get("delta", {})
        if delta.get("type") == "text":
            print(delta.get("text", ""), end="", flush=True)
```

### Run It:
```bash
uv run steps/2_building_streaming_interactions/streaming_agent.py
```

---

## 🎙️ Phase 3: The End-to-End Podcast Pipeline

Now that you understand the Interactions API and streaming, let's build the full automated podcast production pipeline. 

### 1. The Pipeline Flow
We break down the production pipeline into modular, reusable steps (packaged as local agent skills):

```
[Research Content] 
       │ (Step 2 - script_writing skill)
       ▼
  [script.md]
    ├───► (Step 1 - generate_tts skill) ────► [speech.wav] ────┐
    └───► (Step 3 - generate_music skill) ──► [background.mp3]─┴─► (Step 4 - audio_mixing skill) ──► [ai_radio.mp3] ──► ☁️ Public URL
```

### 2. The Project Structure
Set up the workspace as follows:
```
agi-podcast/
├── skills/
│   └── agi-podcast-tutorial/              # This downloadable skill
│       ├── SKILL.md
│       └── resources/
│           ├── generate_tts.py            # Local TTS script
│           ├── generate_music.py          # Local music generation script
│           ├── mix_audio.py               # Local audio mixer
│           ├── main.py                    # Complete streaming orchestrator
│           └── AGENTS.md                  # Master agent instructions
├── content/
│   └── research_paper.md                  # Source materials
└── .env
```

---

## 🛠️ Step-by-Step Implementation

### Step 0: Setup and Environment Configuration
```bash
mkdir agi-podcast && cd agi-podcast
uv init
uv add google-genai python-dotenv pydub google-cloud-storage
echo "GOOGLE_API_KEY=your-api-key-here" > .env
mkdir -p content .agents/skills
```

### Step 1: Dialogue Text-to-Speech (TTS)
- **Reference Code:** See [generate_tts.py](./resources/generate_tts.py).
- Parses `script.md` into dialogue turns and synthesizes them using `gemini-3.1-flash-tts-preview` in parallel, merging them into `speech.wav`.

### Step 2: Script Writing Instruction
- **Reference Instruction:** Define structural rules in `.agents/skills/script_writing/SKILL.md` (see [script_writing/SKILL.md](./resources/script_writing_SKILL.md)) for Paul and Sarah co-host dialogue.

### Step 3: Background Music Generation
- **Reference Code:** See [generate_music.py](./resources/generate_music.py).
- Crafts prompt based on script analysis and generates a lo-fi track using `lyria-3-clip-preview`.

### Step 4: Master Audio Mixing
- **Reference Code:** See [mix_audio.py](./resources/mix_audio.py).
- Pads end of dialogue, overlays background track at `-18dB` with transitions, and exports high-quality MP3 (and uploads to GCS).

### Step 5: Wire Skills with `AGENTS.md`
- Put master instructions in `.agents/AGENTS.md` (see [AGENTS.md](./resources/AGENTS.md)).

### Step 6: Complete Orchestrator (`main.py`)
- **Reference Code:** See [main.py](./resources/main.py).
- Bundles local source codes, injects GCS keys, handles remote Interactions stream parsing, and posts comments back on GitHub.

### Step 7: CI/CD Automation
- Set up `.github/workflows/generate.yaml` in your project root to run on workflow dispatch or new research paper commits.
