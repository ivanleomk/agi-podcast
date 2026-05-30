#!/usr/bin/env python3
"""Configuring Our Agent - Sources Demo.

This script demonstrates how to inject local files/directories into the remote
agent's container using the `sources` property. This lets the agent access 
custom configs, documentation, or input content in its sandboxed environment.
"""

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

    # Step 1: Read the local podcast style guide
    style_file_path = os.path.join(os.path.dirname(__file__), "podcast_style.txt")
    if not os.path.exists(style_file_path):
        rprint(f"❌ Error: style guide not found at {style_file_path}")
        return

    with open(style_file_path, "r", encoding="utf-8") as f:
        style_content = f.read()

    # Step 2: Bundle style guide as an inline source mapping to "podcast_style.txt"
    sources = [
        {
            "type": "inline",
            "target": "podcast_style.txt",
            "content": style_content
        }
    ]

    rprint("[bold cyan]🔧 Bundling Inline Sources...[/bold cyan]")
    rprint(f"  • Mapped local style guide to remote path: [green]podcast_style.txt[/green]")

    rprint("\n🚀 Spawning agent to read injected sources...")
    try:
        response = client.interactions.create(
            agent="antigravity-preview-05-2026",
            input="Read 'podcast_style.txt' and list the rules mentioned in it, then confirm you can access the file successfully.",
            stream=True,
            environment={
                "type": "remote",
                "sources": sources
            }
        )

        for chunk in response:
            if hasattr(chunk, "model_dump"):
                event = chunk.model_dump()
                delta = event.get("delta", {})
                if delta.get("type") == "text":
                    print(delta.get("text", ""), end="", flush=True)
        print()

    except Exception as e:
        rprint(f"\n❌ Error running sources demo: {e}")

if __name__ == "__main__":
    main()
