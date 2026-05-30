#!/usr/bin/env python3
"""Configuring Our Agent - Network & Key Transform Demo.

This script demonstrates how to configure outbound network access for the
agent's sandboxed environment, and how to securely forward credentials 
using domain transforms.

By configuring `network.allowlist` with a domain transform for 
`generativelanguage.googleapis.com` and injecting the `x-goog-api-key`,
the code executing inside the agent's sandbox can call Gemini APIs (such as
gemini-3.1-flash-tts-preview) natively using the `google-genai` library 
without ever hardcoding or leaking real API keys.
"""

import os
from google import genai
from dotenv import load_dotenv
from rich import print as rprint

load_dotenv()

def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        rprint("⚠️  Warning: GOOGLE_API_KEY is not set in your environment or .env file.")
        return

    client = genai.Client()

    rprint("[bold cyan]🔧 Configuring Secure API Key Forwarding...[/bold cyan]")
    rprint("  • Network Allowlist: Permitted [green]generativelanguage.googleapis.com[/green]")
    rprint("  • Headers Transform: Injecting [green]x-goog-api-key[/green] automatically")

    rprint("\n🚀 Spawning agent to run TTS code in sandbox...")
    try:
        # We ask the agent to run code that calls Gemini TTS.
        # Inside the sandbox, GOOGLE_API_KEY can be set to 'dummy' (or left blank if the SDK handles it,
        # but the standard client library can be initialized).
        prompt = (
            "Write and execute a Python script to synthesize a greeting using Gemini TTS.\n"
            "Inside your script, you should:\n"
            "  1. Install google-genai and pydub if they are missing.\n"
            "  2. Initialize the GenAI client with client = genai.Client(api_key='dummy') (the network proxy "
            "     will automatically inject the real key via the transformed headers!)\n"
            "  3. Use model='gemini-3.1-flash-tts-preview' to synthesize the text 'Hello from inside the sandbox!'\n"
            "     using voice 'Kore'.\n"
            "  4. Write the audio bytes to 'test_greeting.wav' and print its file size to verify success."
        )

        response = client.interactions.create(
            agent="antigravity-preview-05-2026",
            input=prompt,
            stream=True,
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
        )

        for chunk in response:
            if hasattr(chunk, "model_dump"):
                event = chunk.model_dump()
                delta = event.get("delta", {})
                if delta.get("type") == "text":
                    print(delta.get("text", ""), end="", flush=True)
        print()

    except Exception as e:
        rprint(f"\n❌ Error running network demo: {e}")

if __name__ == "__main__":
    main()
