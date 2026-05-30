#!/usr/bin/env python3
"""A simple script showcasing the Gemini Interactions API.

This script demonstrates how to spin up a managed agent using the
Interactions API. The agent can write code, run commands, and solve tasks
using execution tools in its sandboxed environment, while streaming, logging
the raw interactions, and saving them to a JSONL file.
"""

import os
import warnings
from google import genai
from dotenv import load_dotenv
from rich import print as rprint

warnings.filterwarnings("ignore")


# Load environment variables (such as GOOGLE_API_KEY) from .env file
load_dotenv()

def main():
    # Verify that the API key is present
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        rprint("⚠️  Warning: GOOGLE_API_KEY is not set in your environment or .env file.")
        return

    # Initialize the Gemini client
    client = genai.Client()

    rprint("🚀 Spawning managed agent in streaming mode...")
    try:
        # Define log file path in the current working directory
        log_file_path = "stream_events.jsonl"
        
        # Create a streaming interaction with the agent
        response = client.interactions.create(
            agent="antigravity-preview-05-2026",
            input="Show me that you can execute code. Write a Python script to compute the 10th Fibonacci number.",
            stream=True,
            environment="remote",
        )

        # Open the log file and stream response
        with open(log_file_path, "w", encoding="utf-8") as f:
            for chunk in response:
                rprint(chunk)
                f.write(chunk.model_dump_json() + "\n")
                f.flush()
                
        rprint(f"\n📝 Raw stream events successfully logged to: [bold cyan]{os.path.abspath(log_file_path)}[/bold cyan]")
            
    except Exception as e:
        rprint(f"\n❌ Error spawning agent: {e}")

if __name__ == "__main__":
    main()
