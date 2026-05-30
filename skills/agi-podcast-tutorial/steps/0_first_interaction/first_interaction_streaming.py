#!/usr/bin/env python3
"""Your first interaction with a Gemini Managed Agent using streaming."""

import os
from google import genai
from dotenv import load_dotenv
from rich import print

# Load credentials from environment or local .env file
load_dotenv()

def main():
    # Initialize the client
    client = genai.Client()

    print("User > What is the capital of France?")
    print("\nAgent > ", end="", flush=True)

    try:
        # Make a streaming call to the Interactions API
        response = client.interactions.create(
            model="gemini-3.5-flash",
            input="What is the capital of France?",
            stream=True,
            generation_config={
                "thinking_summaries": "auto"
            }
        )

        for chunk in response:
            print(chunk)
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
