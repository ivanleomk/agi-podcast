#!/usr/bin/env python3
"""Generate speech audio (TTS) for AI Talk Radio co-hosts using the Gemini API.

Usage:
    uv run generate_tts.py
    uv run generate_tts.py --script script.md --out audio/ --workers 8
"""

import argparse
import io
import os
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from google import genai
from pydub import AudioSegment

load_dotenv()

# Global rate limiter to respect the 10 RPM limit of preview TTS models
rate_limit_lock = threading.Lock()
last_request_time = 0.0

def get_voice_for_speaker(speaker: str) -> str:
    name = speaker.lower().strip()
    if "paul" in name:
        return "Puck"
    elif "sarah" in name:
        return "Kore"
    elif "female" in name:
        return "Aoede"
    elif "male" in name:
        return "Charon"
    else:
        voices = ["Puck", "Kore", "Aoede", "Charon", "Fenrir"]
        return voices[sum(ord(c) for c in name) % len(voices)]

def synthesize_turn(client, index: int, speaker: str, text: str, voice: str, out_dir: str):
    global last_request_time
    segment_path = os.path.join(out_dir, f"turn_{index:04d}.wav")

    max_retries = 3
    backoff = 2

    print(f"🎙️  [Turn {index}] {speaker} ({voice}): {text[:60]}...", flush=True)

    models_to_try = [
        "gemini-3.1-flash-tts-preview",
    ]

    for attempt in range(max_retries):
        try:
            with rate_limit_lock:
                now = time.time()
                elapsed = now - last_request_time
                if elapsed < 1.2:
                    time.sleep(1.2 - elapsed)
                last_request_time = time.time()

            response = None
            last_err = None
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=text,
                        config={
                            "response_modalities": ["AUDIO"],
                            "speech_config": {
                                "voice_config": {
                                    "prebuilt_voice_config": {
                                        "voice_name": voice
                                    }
                                }
                            }
                        }
                    )
                    break
                except Exception as e:
                    err_str = str(e)
                    if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                        print(f"⚠️  [Turn {index}] {model_name} rate limited, trying next...", flush=True)
                        last_err = e
                        continue
                    raise e

            if response is None:
                raise last_err or Exception("No response from any TTS model")

            audio_data = None
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        audio_data = part.inline_data.data
                        break

            if audio_data:
                segment = AudioSegment.from_raw(
                    io.BytesIO(audio_data),
                    sample_width=2,
                    frame_rate=24000,
                    channels=1
                )
                segment.export(segment_path, format="wav")
                print(f"✅ [Turn {index}] Done ({len(audio_data) / 1024:.1f} KB)", flush=True)
                return segment_path
            else:
                print(f"⚠️  [Turn {index}] Attempt {attempt + 1}: no audio data returned.", flush=True)

        except Exception as e:
            print(f"⚠️  [Turn {index}] Attempt {attempt + 1} failed: {e}", flush=True)
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                time.sleep(10)

        if attempt < max_retries - 1:
            time.sleep(backoff)
            backoff *= 2

    print(f"❌ [Turn {index}] All attempts failed.", flush=True)
    return None

def parse_script(script_path: str) -> list[tuple[str, str]]:
    turns = []
    speaker_pattern = re.compile(r"^\*?\*?([a-zA-Z0-9_\s]+)\*?\*?:\s*(.*)$")

    with open(script_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = speaker_pattern.match(line)
            if match:
                speaker = match.group(1).strip()
                text = match.group(2).strip().replace("**", "").replace("*", "")
                if speaker and text:
                    turns.append((speaker, text))
            elif turns:
                last_speaker, last_text = turns[-1]
                turns[-1] = (last_speaker, last_text + " " + line)

    return turns

def main():
    parser = argparse.ArgumentParser(description="Convert AI Talk Radio script to WAV using Gemini TTS")
    parser.add_argument("--script", default="script.md", help="Path to the script markdown file")
    parser.add_argument("--out", default="audio", help="Output directory for audio files")
    parser.add_argument("--workers", type=int, default=4, help="Parallel worker threads")
    args = parser.parse_args()

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY must be set in .env or environment")

    client = genai.Client(api_key=api_key)

    segments_dir = os.path.join(args.out, "segments")
    os.makedirs(segments_dir, exist_ok=True)

    if not os.path.exists(args.script):
        raise FileNotFoundError(f"Script not found: {args.script}")

    print(f"📖 Parsing script from {args.script}...")
    turns = parse_script(args.script)
    print(f"📋 Found {len(turns)} dialogue turns. Synthesizing with {args.workers} workers...\n")

    synthesized_paths = [None] * len(turns)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                synthesize_turn, client, i, speaker, text, get_voice_for_speaker(speaker), segments_dir
            ): i
            for i, (speaker, text) in enumerate(turns)
        }
        for fut, i in futures.items():
            synthesized_paths[i] = fut.result()

    print("\n🔗 Concatenating segments...")
    combined = AudioSegment.empty()
    skipped = 0
    for i, path in enumerate(synthesized_paths):
        if path and os.path.exists(path):
            combined += AudioSegment.from_file(path)
        else:
            skipped += 1

    if skipped:
        print(f"⚠️  {skipped}/{len(turns)} turns were skipped.")

    out_path = os.path.join(args.out, "speech.wav")
    combined.export(out_path, format="wav")
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"\n✅ Done! Saved to {out_path} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    main()
