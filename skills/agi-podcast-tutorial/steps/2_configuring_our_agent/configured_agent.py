#!/usr/bin/env python3
"""Configuring Our Agent.

This script demonstrates how to configure the Gemini Interactions API with:
1. Sources: Injecting local files into the remote agent's container.
2. Network: Setting up the outbound network allowlist and using header
   transforms to forward the Google Gemini API key securely.
3. System Prompt: Setting a custom system instruction/persona for the agent.

The agent uses these to read a style guide, run a python script inside the
sandbox, call the Gemini TTS API, and verify the generated output.
"""

import json
import os
import warnings
from google import genai
from dotenv import load_dotenv
from rich import print as rprint

warnings.filterwarnings("ignore")


load_dotenv()

def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        rprint("⚠️  Warning: GOOGLE_API_KEY is not set in your environment or .env file.")
        return

    client = genai.Client()

    # Step 1: Prepare the local file as an inline source
    style_file_path = os.path.join(
        os.path.dirname(__file__), "podcast_style.txt"
    )
    if not os.path.exists(style_file_path):
        rprint(f"❌ Error: style guide not found at {style_file_path}")
        return

    with open(style_file_path, "r", encoding="utf-8") as f:
        style_content = f.read()

    # We map the local podcast_style.txt file to the remote workspace
    sources = [
        {
            "type": "inline",
            "target": "podcast_style.txt",
            "content": style_content
        }
    ]

    rprint("[bold cyan]🔧 Configuration Parameters Built:[/bold cyan]")
    rprint(f"  • Inline Sources: Added [green]podcast_style.txt[/green] ({len(style_content)} bytes)")
    rprint("  • Network: Forwarding [green]generativelanguage.googleapis.com[/green] with x-goog-api-key transform")
    rprint("  • System Prompt: Tech Podcast Producer Persona\n")

    rprint("🚀 Spawning agent with custom configuration...")
    try:
        # We prompt the agent to use the style guide, make an outbound Gemini TTS call,
        # and verify it has access to both the files and the network.
        prompt = (
            "1. Read the style guide from 'podcast_style.txt' and show me a quick summary of it.\n"
            "2. Write and execute a Python script to call the Gemini TTS API using the `google-genai` library.\n"
            "   The script should generate a short 5-word audio clip (e.g. 'Hey, welcome to AI Talk!') using the voice 'Puck' "
            "   and save it to `greeting.wav` in the workspace.\n"
            "3. Verify that `greeting.wav` was written successfully and print its file size."
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
            system_instruction=(
                "You are a professional AI Podcast Producer. You are highly energetic, "
                "knowledgeable, and use your coding sandbox tools to automate, check, and generate podcast resources."
            )
        )

        # Print the stream in real-time
        for chunk in response:
            if hasattr(chunk, "model_dump"):
                event = chunk.model_dump()
                delta = event.get("delta", {})
                if delta.get("type") == "text":
                    print(delta.get("text", ""), end="", flush=True)
        print()

    except Exception as e:
        rprint(f"\n❌ Error running configured agent: {e}")

if __name__ == "__main__":
    main()
