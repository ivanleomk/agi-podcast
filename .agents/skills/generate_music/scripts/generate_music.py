#!/usr/bin/env python3
"""Generate background music for AI Talk Radio using Lyria-3.

Usage:
    uv run generate_lyria.py
    uv run generate_lyria.py --script script.md --out audio/music
"""

import argparse
import base64
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

FALLBACK_PROMPT = (
    "15-second lo-fi ambient intro. "
    "Soft synthesizer pads, gentle melodic tones, slow unhurried tempo. "
    "Calm, thoughtful, understated. Instrumental only, no vocals."
)

def generate_music_prompt(client, script_content: str) -> str:
    print("Generating Lyria-3 prompt from script...")
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=f"Write a 15-second Lyria-3 music generation prompt for this tech podcast intro:\n\n{script_content}",
            config={
                "system_instruction": (
                    "You are an expert music prompt engineer for the Lyria-3 music generation model. "
                    "Rules: instrumental only (no vocals), 15 seconds, chill and relaxed tone — not upbeat or energetic. "
                    "Think lo-fi, ambient, understated. Slow tempo, soft pads, gentle melodies. "
                    "Use positive descriptive language about instruments, tempo, and atmosphere. "
                    "Avoid any negative, violent, or disruptive descriptors. "
                    "Output ONLY the prompt itself — no preamble, no markdown, no quotes."
                )
            }
        )
        prompt = response.text.strip().strip('"').strip("'")
        if prompt.startswith("```"):
            prompt = prompt.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        return prompt
    except Exception as e:
        print(f"⚠️  Prompt generation failed: {e}. Using fallback.")
        return FALLBACK_PROMPT

def generate_music(client, prompt: str, out_dir: str) -> bool:
    print(f"Prompt: \"{prompt}\"")
    print("Calling Lyria-3...")
    try:
        interaction = client.interactions.create(
            model="lyria-3-clip-preview",
            input=prompt,
            store=False,
        )

        for step in getattr(interaction, "steps", []):
            for item in getattr(step, "content", []):
                mime = getattr(item, "mime_type", "")
                item_type = getattr(item, "type", "")
                if item_type == "audio" or (isinstance(mime, str) and mime.startswith("audio/")):
                    out_path = os.path.join(out_dir, "background.mp3")
                    with open(out_path, "wb") as f:
                        f.write(base64.b64decode(item.data))
                    size_kb = os.path.getsize(out_path) / 1024
                    print(f"✅ Music saved to {out_path} ({size_kb:.0f} KB)")
                    return True
                elif item_type == "text":
                    print(f"   Lyria: {item.text[:200]}")

        print("⚠️  No audio returned from Lyria.")
        return False
    except Exception as e:
        print(f"⚠️  Music generation failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate background music with Lyria-3")
    parser.add_argument("--script", default="script.md", help="Path to the script markdown file")
    parser.add_argument("--out", default="audio/music", help="Output directory for music files")
    args = parser.parse_args()

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY must be set in .env or environment")

    client = genai.Client(api_key=api_key)
    os.makedirs(args.out, exist_ok=True)

    if not os.path.exists(args.script):
        raise FileNotFoundError(f"Script not found: {args.script}")

    with open(args.script, "r", encoding="utf-8") as f:
        script_content = f.read()
    print(f"📖 Loaded script from {args.script} ({len(script_content)} chars)")

    prompt = generate_music_prompt(client, script_content)
    success = generate_music(client, prompt, args.out)

    if not success:
        print("\n🔄 Retrying with fallback prompt...")
        success = generate_music(client, FALLBACK_PROMPT, args.out)

    if not success:
        print("\n❌ Both attempts failed.")

if __name__ == "__main__":
    main()
