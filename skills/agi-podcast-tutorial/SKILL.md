---
name: agi-podcast-tutorial
description: A step-by-step interactive tutorial skill to guide developers and agents in building an AGI Podcast Production Pipeline.
---

# AGI Podcast Tutorial Skill

Welcome! This skill is designed to guide developers and coding agents step-by-step through understanding and building with the Gemini Interactions API, starting from the simplest agent invocation to a full-fledged streaming client and ending with a completely automated podcast production pipeline.

---

## Learning Roadmap

1. **Step 0: First Interaction** — Verify authentication and make conversational requests to the Interactions API.
2. **Step 1: Spawning a Simple Agent** — Spin up a managed agent that writes and executes code, and parse its live stream events.
3. **Step 2: Configuring Our Agent** — Control files (sources), configure secure API key forwarding (network transforms), and style the agent's persona (system instructions).
4. **Step 3: Adding Our First Skill** — Pack and inject a local skill directory (TTS) dynamically using a directory sources scanner, and execute it.
5. **Step 4: Creating Our AI Podcast** — Bundle all skills, guidelines, and input research content to execute the complete end-to-end automated pipeline remotely.


---

## Setup & API Key Configuration

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

## Step 0: First Interaction

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

## Step 1: Spawning a Simple Agent (Code Execution)

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

## Step 2: Configuring Our Agent

To build complex pipelines like the automated podcast generator, we must configure three major parts of the Gemini Managed Agent. We break this down into four specific demo files located in `steps/2_configuring_our_agent/`:

1. **[sources_demo.py](./steps/2_configuring_our_agent/sources_demo.py)** — Showcases **Sources**: Injecting local files and directories dynamically into the agent's remote workspace.
2. **[network_demo.py](./steps/2_configuring_our_agent/network_demo.py)** — Showcases **Network Allowlist & Transforms**: Specifying permitted outbound domains (`network.allowlist`) and forwarding credentials securely via header transforms.
3. **[persona_demo.py](./steps/2_configuring_our_agent/persona_demo.py)** — Showcases **Agent Persona (`system_instruction`)**: Formatting the system prompt and mounting the system instruction string dynamically as an inline source (`.agents/AGENTS.md`).
4. **[configured_agent.py](./steps/2_configuring_our_agent/configured_agent.py)** — Showcases **All Properties Combined**: Putting sources, network transforms, and custom persona instructions together.

---

### A. Sources (Inlined Files)
*Showcased in:* **[sources_demo.py](./steps/2_configuring_our_agent/sources_demo.py)**

To allow the remote agent to read local style guides, configurations, or intermediate files, we bundle them into the `sources` parameter. The agent sees these files as if they were present locally in its sandbox workspace.

```python
# Mapped local style guide to remote workspace target
sources = [
    {
        "type": "inline",
        "target": "podcast_style.txt",
        "content": style_content
    }
]
```

#### Run It:
```bash
uv run steps/2_configuring_our_agent/sources_demo.py
```

---

### B. Network & Secure Credential Transforms
*Showcased in:* **[network_demo.py](./steps/2_configuring_our_agent/network_demo.py)**

By default, the agent's sandbox container has strict network restrictions. Under the `network` block, we can:
- Allow list external/internal domains (e.g. `domain: "*"` or specific APIs).
- Securely inject API keys (like `x-goog-api-key`) into outbound headers automatically using **header transforms**. This allows code running inside the sandbox to call the Gemini TTS API without ever exposing or saving the raw API key in workspace files or logs!

```python
# Forwarding the Gemini API key securely to the remote sandbox container
environment={
    "type": "remote",
    "network": {
        "allowlist": [
            {
                "domain": "generativelanguage.googleapis.com",
                "transform": {
                    "x-goog-api-key": api_key
                }
            },
            {
                "domain": "*"
            }
        ]
    }
}
```

#### Run It:
```bash
uv run steps/2_configuring_our_agent/network_demo.py
```

---

### C. System Prompt & Persona
*Showcased in:* **[persona_demo.py](./steps/2_configuring_our_agent/persona_demo.py)**

You can sculpt the agent's tone, expertise, and operational boundaries using the `system_instruction` parameter in `interactions.create`. 

This demo showcases:
1. Setting the `system_instruction` string for a high-energy 90s tech radio host.
2. Dynamically mounting that instruction string as an inline source targeting `.agents/AGENTS.md` in the remote sandbox workspace, demonstrating how the agent can inspect the system instructions it is actively following.

```python
# Define system instruction for a witty 90s radio host
system_instruction = (
    "You are 'DJ Byte', a super energetic, rad 1990s tech radio host. "
    "Use 90s slang (like 'gnarly', 'tubular', 'rad') and retro metaphors."
)

# Dynamically mount the instruction string to the remote sandbox
sources = [
    {
        "type": "inline",
        "target": ".agents/AGENTS.md",
        "content": system_instruction
    }
]
```

#### Run It:
```bash
uv run steps/2_configuring_our_agent/persona_demo.py
```

---

### D. All Properties Combined (Configured Agent)
*Showcased in:* **[configured_agent.py](./steps/2_configuring_our_agent/configured_agent.py)**

This combines all three concepts (inlined sources, outbound network access with transforms, and system instructions) to spawn a fully functional, remote-sandboxed tech podcast producer.

#### Run It:
```bash
uv run steps/2_configuring_our_agent/configured_agent.py
```

---

## Step 3: Adding Our First Skill

Once you know how to configure sources, network transforms, and personas, you can start modularizing your tasks into **Skills**. In this step, we bundle a local Text-to-Speech (TTS) skill folder and inject it dynamically into the agent's container.

To automatically collect and bundle all local files within a directory hierarchy, we use a utility function: `add_directory_sources`.

### Directory Sources Scanner

This function recursively scans a local directory, filters out common ignored folders/files, reads each text file, and appends it to the `sources` array with its relative path.

```python
def add_directory_sources(dir_path: str, sources_list: list):
    if not os.path.exists(dir_path):
        return
    for root, dirs, files in os.walk(dir_path):
        # Exclude common generated/ignored directories
        dirs[:] = [d for d in dirs if d not in [".git", ".venv", "__pycache__"]]
        for file in files:
            # Exclude environment secrets and OS-generated files
            if file in [".env", ".DS_Store", "uv.lock"]:
                continue
            filepath = os.path.join(root, file)
            if not os.path.isfile(filepath):
                continue
            # Use relative path as the remote environment target
            rel_path = os.path.relpath(filepath, start=".")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                sources_list.append({
                    "type": "inline",
                    "target": rel_path,
                    "content": content
                })
            except Exception:
                # Silently skip binary files or unreadable files
                pass
```

### Reference Code
You can find the complete implementation in [tts_skill_demo.py](./steps/3_adding_our_first_skill/tts_skill_demo.py). It:
1. Scans and bundles the `generate_tts` skill (located inside the step 3 folder) alongside `script.md`.
2. Configures a remote sandbox environment with secure network transforms to allow the TTS script to contact `generativelanguage.googleapis.com` using your API key securely.
3. Spawns the agent to execute the Python script, generating `speech.wav` and verifying its creation.

#### Run It:
```bash
uv run steps/3_adding_our_first_skill/tts_skill_demo.py
```

---

## Step 4: Creating Our AI Podcast

Now we bring everything together into a fully automated, end-to-end podcast production system!

In this final step, we package all the skills (`script_writing`, `generate_tts`, `generate_music`, and `audio_mixing`) together with the master `AGENTS.md` instructions and input research `content/`. 

We use a complete streaming orchestrator that scans all files, securely forwards network credentials, captures and processes interaction events (thinking, tool calls, results, and text outputs) in real-time, and extracts the final podcast public GCS URL.

### Reference Code
You can find the complete implementation in [ai_podcast.py](./steps/4_creating_our_ai_podcast/ai_podcast.py). It:
1. Dynamically scans and bundles the `.agents` master instructions and skills folders along with research content in `content/`.
2. Automatically checks and bundles the local `gcs-key.json` if available.
3. Sets up secure network transforms to allow the remote agent to hit the Gemini API and synthesize audio.
4. Streams raw step events in real-time and logs them locally to `result.jsonl` for full transparency and debuggability.
5. Extracts and prints the final podcast MP3 public URL!

#### Run It:
```bash
uv run steps/4_creating_our_ai_podcast/ai_podcast.py
```

