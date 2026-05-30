#!/usr/bin/env python3
"""Creating Our AI Podcast.

This script demonstrates the complete end-to-end AI Podcast production pipeline
by packing all three local skills, the agent guidelines, and the research content,
injecting GCS credentials, and triggering the remote agent to write, generate,
mix, and upload the podcast episode.
"""

import os
import warnings
import json
import re
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
            rel_path = os.path.relpath(filepath, start=dir_path)
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

class StreamParser:
    def __init__(self, on_chunk=None):
        self.steps = {}
        self.on_chunk = on_chunk or self.default_on_chunk
        self.current_type = None
        self.full_text = []

    def default_on_chunk(self, chunk: str, chunk_type: str):
        if chunk_type == "thought":
            if self.current_type != "thought":
                print("\n[thinking]")
                self.current_type = "thought"
            print(chunk, end="", flush=True)
            return

        if chunk_type == "text":
            if self.current_type != "text":
                print("\n[text]")
                self.current_type = "text"
            print(chunk, end="", flush=True)
            return

        if chunk_type == "arguments":
            if self.current_type != "arguments":
                self.current_type = "arguments"
            print(chunk, end="", flush=True)
            return

        if chunk_type == "result":
            if self.current_type != "result":
                self.current_type = "result"
            print(chunk, end="", flush=True)
            return

        if chunk_type == "code_call":
            if self.current_type != "code_call":
                print("\n[code_call]")
                self.current_type = "code_call"
            print(chunk, end="", flush=True)
            return

        if chunk_type == "code_result":
            if self.current_type != "code_result":
                print("\n[result]")
                self.current_type = "code_result"
            print(chunk, end="", flush=True)
            return

    def process_event(self, event: dict):
        if not event:
            return

        event_type = event.get("event_type")
        if not event_type:
            return

        if event_type in ("interaction.created", "interaction.completed"):
            return

        index = event.get("index")
        if index is None:
            return

        step = self.steps.get(index)

        if event_type == "step.start":
            start_step = event.get("step") or {}
            stype = start_step.get("type")
            
            step = {"type": stype}
            self.steps[index] = step

            if stype == "function_call":
                name = start_step.get("name")
                if name:
                    self.on_chunk(f"\n[tool_call] {name}\nArguments: ", "arguments")
                return

            if stype == "function_result":
                name = start_step.get("name")
                if name:
                    self.on_chunk(f"\n[tool_result] {name}\nResult: ", "result")
                return
            return

        if event_type == "step.delta":
            delta = event.get("delta") or {}
            
            if not step:
                stype = "model_output"
                delta_type = delta.get("type")
                if delta_type == "thought_summary":
                    stype = "thought"
                elif delta_type == "arguments_delta":
                    stype = "function_call"
                elif delta_type == "function_result":
                    stype = "function_result"
                elif delta_type == "code_execution_call":
                    stype = "code_execution_call"
                elif delta_type == "code_execution_result":
                    stype = "code_execution_result"
                step = {"type": stype}
                self.steps[index] = step

            stype = step["type"]

            if stype == "thought":
                if delta.get("type") == "thought_summary":
                    content = delta.get("content") or {}
                    text = content.get("text", "")
                    if text:
                        self.on_chunk(text, "thought")
                return

            if stype == "model_output":
                if delta.get("type") == "text":
                    text = delta.get("text", "")
                    if text:
                        self.full_text.append(text)
                        self.on_chunk(text, "text")
                return

            if stype == "function_call":
                if delta.get("type") == "arguments_delta":
                    args = delta.get("arguments", "")
                    chunk_text = ""
                    if isinstance(args, str):
                        chunk_text = args
                    else:
                        chunk_text = json.dumps(args)
                    if chunk_text:
                        self.on_chunk(chunk_text, "arguments")
                return

            if stype == "function_result":
                if delta.get("type") == "function_result":
                    res = delta.get("result")
                    chunk_text = ""
                    if isinstance(res, list):
                        for item in res:
                            if isinstance(item, dict) and "text" in item:
                                chunk_text += item["text"]
                            elif isinstance(item, str):
                                chunk_text += item
                    elif isinstance(res, str):
                        chunk_text = res
                    else:
                        chunk_text = json.dumps(res)
                    if chunk_text:
                        self.on_chunk(chunk_text, "result")
                return

            if stype == "code_execution_call":
                if delta.get("type") == "code_execution_call":
                    args = delta.get("arguments")
                    if isinstance(args, dict) and "code" in args:
                        self.on_chunk(args["code"], "code_call")
                    elif isinstance(args, str):
                        self.on_chunk(args, "code_call")
                return

            if stype == "code_execution_result":
                if delta.get("type") == "code_execution_result":
                    res = delta.get("result")
                    if isinstance(res, str) and res:
                        self.on_chunk(res, "code_result")
                return
            return

        if event_type == "step.stop":
            return

def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        rprint("Warning: GOOGLE_API_KEY is not set in your environment or .env file.")
        return

    client = genai.Client()

    # Step 1: Pack resources dynamically relative to Step 4 directory
    sources = []
    step_dir = os.path.dirname(os.path.abspath(__file__))
    
    rprint("[bold cyan]Scanning and packing Step 4 resources...[/bold cyan]")
    
    # Pack .agents/ and content/ directories under Step 4
    agents_dir = os.path.join(step_dir, ".agents")
    content_dir = os.path.join(step_dir, "content")
    
    # We map them into the remote container exactly as expected (.agents/ and content/)
    # So we want rel_path target to be relative to step_dir
    add_directory_sources(step_dir, sources)
    
    # Locate and pack GCS service account key from project root or step folder if it exists
    gcs_key_name = "gcs-key.json"
    root_gcs_path = os.path.abspath(os.path.join(step_dir, "..", "..", "..", "..", gcs_key_name))
    step_gcs_path = os.path.join(step_dir, gcs_key_name)
    
    gcs_found_path = None
    if os.path.exists(step_gcs_path):
        gcs_found_path = step_gcs_path
    elif os.path.exists(root_gcs_path):
        gcs_found_path = root_gcs_path
        
    if gcs_found_path:
        rprint(f"Bundling GCS service account key from: [green]{gcs_found_path}[/green]")
        with open(gcs_found_path, "r", encoding="utf-8") as f:
            sources.append({
                "type": "inline",
                "target": gcs_key_name,
                "content": f.read()
            })
    else:
        rprint("[yellow]Warning: gcs-key.json not found in root or step directory. Audio mixing upload may skip GCS upload.[/yellow]")

    # Verify packed files
    rprint(f"Packed {len(sources)} files into remote environment sources.")

    # Step 2: Set up pipeline prompt
    pipeline_prompt = (
        "Please run the full AGI podcast production pipeline end-to-end:\n\n"
        "1. Write the podcast script by running the script_writing skill:\n"
        "   - Read all research/input markdown files in content/.\n"
        "   - Perform a quick web search to gather extra background/context on the topic.\n"
        "   - Generate a highly engaging and punchy co-host podcast script (featuring Paul and Sarah) of around 500 words in choice bites, following the formatting rules in .agents/skills/script_writing/SKILL.md.\n"
        "   - Save the script directly to script.md in the working directory.\n"
        "2. Generate TTS speech audio from script.md by running the generate_tts skill (e.g., generate_tts.py) saving to audio/speech.wav.\n"
        "3. Generate background music from script.md by running the generate_music skill (e.g., generate_music.py) saving to audio/music/background.mp3.\n"
        "4. Mix the speech and music together, then upload to GCS by running the audio_mixing skill (e.g., mix_audio.py) with the --upload and --gcs-key gcs-key.json flags.\n\n"
        "Please make sure to install any required packages (like pydub, google-cloud-storage) and system dependencies (like ffmpeg if not already available) needed for these scripts. "
        "Verify the final mixed podcast MP3 is uploaded successfully and output the GCS public URL so I can listen to it.\n\n"
        "At the very end of your final response, make sure to output the public GCS URL wrapped inside <video_link> and </video_link> tags (literally like that, with no extra spaces or formatting around the tags, e.g. <video_link>URL</video_link>) so it can be programmatically parsed."
    )

    rprint("\n[bold cyan]Spawning remote agent for end-to-end podcast production...[/bold cyan]")
    try:
        interaction = client.interactions.create(
            agent="antigravity-preview-05-2026",
            input=pipeline_prompt,
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
        )

        parser = StreamParser()
        
        # Open and write raw interaction logs for troubleshooting
        log_path = os.path.join(step_dir, "result.jsonl")
        with open(log_path, "w", encoding="utf-8") as f:
            for chunk in interaction:
                if hasattr(chunk, "model_dump_json"):
                    chunk_json = chunk.model_dump_json(indent=2)
                elif hasattr(chunk, "model_dump"):
                    chunk_json = json.dumps(chunk.model_dump(), indent=2, default=str)
                else:
                    chunk_json = json.dumps(chunk, indent=2, default=str)
                    
                f.write(chunk_json + "\n")
                
                if hasattr(chunk, "model_dump"):
                    chunk_dict = chunk.model_dump()
                elif isinstance(chunk, dict):
                    chunk_dict = chunk
                else:
                    try:
                        chunk_dict = json.loads(chunk_json)
                    except Exception:
                        chunk_dict = {}
                        
                parser.process_event(chunk_dict)

        full_response = "".join(parser.full_text)
        
        # Extract GCS URL from the final response text
        gcs_url = None
        video_link_match = re.search(r"<video_link>([\s]*https://storage\.googleapis\.com/[^\s\)\*<]+?\.mp3[\s]*)</video_link>", full_response)
        if video_link_match:
            gcs_url = video_link_match.group(1).strip()
        
        if not gcs_url:
            gcs_url_match = re.search(r"https://storage\.googleapis\.com/[^\s\)\*]+?\.mp3", full_response)
            if gcs_url_match:
                gcs_url = gcs_url_match.group(0).strip()
        
        if gcs_url:
            rprint(f"\n\n[bold green]🎯 Extracted GCS Podcast URL: {gcs_url}[/bold green]")
        else:
            rprint("\n[yellow]No GCS Podcast URL found in the agent's final output.[/yellow]")

    except Exception as e:
        rprint(f"\nError running pipeline: {e}")

if __name__ == "__main__":
    main()
