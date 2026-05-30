#!/usr/bin/env python3
"""Configuring Our Agent - Persona & System Prompt Demo.

This script demonstrates how to configure the agent's persona and rules
using the `system_instruction` parameter. 

By setting a custom system instruction, you can transform the agent's tone, 
expertise, and behavioral rules. Here, we configure the agent to act as a 
highly energetic, witty 1990s tech radio host.
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

    # Define the original high-energy 90s tech radio persona
    system_instruction = (
        "You are 'DJ Byte', a super energetic, rad 1990s tech radio host. "
        "Use 90s slang (like 'gnarly', 'tubular', 'rad', 'all that and a bag of chips', 'booyah'). "
        "Every sentence should be filled with high-voltage enthusiasm. "
        "Explain tech concepts using retro metaphors (like floppy disks, dial-up sounds, VHS tapes)."
    )

    # Mount the system instruction dynamically to the remote workspace as .agents/AGENTS.md
    sources = [
        {
            "type": "inline",
            "target": ".agents/AGENTS.md",
            "content": system_instruction
        }
    ]

    rprint("[bold cyan]🔧 Configuring Agent Persona...[/bold cyan]")
    rprint("  • System Instruction: [green]DJ Byte (1990s Tech Radio Persona)[/green]")
    rprint("  • Inline Sources: Mounted system instruction string to [green].agents/AGENTS.md[/green]\n")

    rprint("🚀 Spawning agent in streaming mode...")
    try:
        prompt = (
            "1. Read the mounted source file '.agents/AGENTS.md' in your workspace and print its content.\n"
            "2. Explain, in your rad DJ Byte persona, how this file acts as your system instruction and shapes your character!"
        )

        response = client.interactions.create(
            agent="antigravity-preview-05-2026",
            input=prompt,
            stream=True,
            environment={
                "type": "remote",
                "sources": sources
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
        rprint(f"\n❌ Error running persona demo: {e}")

if __name__ == "__main__":
    main()
