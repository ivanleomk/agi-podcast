#!/usr/bin/env python3
"""Adding Our First Skill - TTS Generation.

This script demonstrates how to pack and inject a local skill directory
into the remote agent's container using the `sources` property, configure the
outbound network and credentials, and instruct the agent to run the skill.
"""

import os
import warnings
from google import genai
from dotenv import load_dotenv
from rich import print as rprint

warnings.filterwarnings("ignore")

load_dotenv()

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

def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        rprint("Warning: GOOGLE_API_KEY is not set in your environment or .env file.")
        return

    client = genai.Client()

    # Step 1: Pack the current step's files (including script.md and the generate_tts skill)
    sources = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    rprint("[bold cyan]Scanning and packing Step 3 directory contents...[/bold cyan]")
    add_directory_sources(current_dir, sources)
    
    # Print the packed file targets for verification
    rprint(f"Packed {len(sources)} files into inline sources:")
    for source in sources:
        rprint(f"  • {source['target']}")

    # Step 2: Define system prompt instructing the agent to act as a Producer
    system_instruction = (
        "You are an AI Podcast Producer. You automate the creation, processing, "
        "and verification of podcast assets using your code execution sandbox tools."
    )

    rprint("\n[bold cyan]Spawning agent with TTS skill mounted...[/bold cyan]")
    try:
        # Prompt the agent to run the TTS script using the mounted files
        prompt = (
            "Please run the TTS generation script in your workspace to synthesize the speech audio.\n\n"
            "Details:\n"
            "1. Find the script at: `skills/agi-podcast-tutorial/steps/3_adding_our_first_skill/generate_tts/scripts/generate_tts.py`\n"
            "2. Find the input script at: `skills/agi-podcast-tutorial/steps/3_adding_our_first_skill/script.md`\n"
            "3. Run the script using Python. Put output audio inside `skills/agi-podcast-tutorial/steps/3_adding_our_first_skill/audio/`.\n"
            "4. Verify that the output `skills/agi-podcast-tutorial/steps/3_adding_our_first_skill/audio/speech.wav` was written successfully and print its file size."
        )

        response = client.interactions.create(
            agent="antigravity-preview-05-2026",
            input=prompt,
            stream=True,
            environment={
                "type": "remote",
                "sources": sources,
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
            },
            system_instruction=system_instruction
        )

        for chunk in response:
            if hasattr(chunk, "model_dump"):
                event = chunk.model_dump()
                delta = event.get("delta", {})
                if delta.get("type") == "text":
                    print(delta.get("text", ""), end="", flush=True)
        print()

    except Exception as e:
        rprint(f"\nError running TTS skill demo: {e}")

if __name__ == "__main__":
    main()
