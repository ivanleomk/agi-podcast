import os
from dotenv import load_dotenv
from google import genai
import json

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

# Prepare remote environment sources
sources = []
add_directory_sources(".agents", sources)
add_directory_sources("content", sources)

# Add GCS service account key to the remote environment if it exists
if os.path.exists("gcs-key.json"):
    with open("gcs-key.json", "r", encoding="utf-8") as f:
        sources.append({
            "type": "inline",
            "target": "gcs-key.json",
            "content": f.read()
        })

google_api_key = os.environ.get("GOOGLE_API_KEY")

client = genai.Client()

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
                        "x-goog-api-key": google_api_key
                    }
                },
                {
                    "domain": "*"
                }
            ]
        }
    },
)

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

parser = StreamParser()

# Stream response events
with open("./result.jsonl", "w") as f:
    for chunk in interaction:
        if hasattr(chunk, "model_dump_json"):
            chunk_json = chunk.model_dump_json(indent=2)
        elif hasattr(chunk, "model_dump"):
            chunk_json = json.dumps(chunk.model_dump(), indent=2, default=str)
        else:
            chunk_json = json.dumps(chunk, indent=2, default=str)
            
        f.write(chunk_json + "\n")
        
        # Convert chunk to dict for live parsing
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

# Parse GCS URL from the final response text
full_response = "".join(parser.full_text)

import re
gcs_url = None

# Attempt to find within <video_link> tags first
video_link_match = re.search(r"<video_link>([\s]*https://storage\.googleapis\.com/[^\s\)\*<]+?\.mp3[\s]*)</video_link>", full_response)
if video_link_match:
    gcs_url = video_link_match.group(1).strip()

if not gcs_url:
    # Fallback to any storage.googleapis.com URL ending in .mp3
    gcs_url_match = re.search(r"https://storage\.googleapis\.com/[^\s\)\*]+?\.mp3", full_response)
    if gcs_url_match:
        gcs_url = gcs_url_match.group(0).strip()

if gcs_url:
    print(f"\n\n🎯 Extracted GCS Podcast URL: {gcs_url}")
    
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    
    if token and repo:
        import urllib.request
        
        issue_number = None
        commit_sha = None
        
        if event_path and os.path.exists(event_path):
            try:
                with open(event_path, "r", encoding="utf-8") as f:
                    event_data = json.load(f)
                
                if "pull_request" in event_data:
                    issue_number = event_data["pull_request"]["number"]
                elif "issue" in event_data:
                    issue_number = event_data["issue"]["number"]
                
                if not issue_number:
                    if "head_commit" in event_data:
                        commit_sha = event_data["head_commit"]["id"]
                    elif "after" in event_data:
                        commit_sha = event_data["after"]
            except Exception as e:
                print(f"Error parsing GITHUB_EVENT_PATH: {e}")
                
        if not issue_number and not commit_sha:
            commit_sha = os.environ.get("GITHUB_SHA")
            
        comment_body = (
            f"### 🎉 Podcast Episode Generated!\n\n"
            f"The latest podcast episode has been successfully produced and uploaded to Google Cloud Storage.\n\n"
            f"👉 **[Listen to the Episode]({gcs_url})**"
        )
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "antigravity-podcast-agent"
        }
        
        if issue_number:
            url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
            data = json.dumps({"body": comment_body}).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req) as response:
                    print(f"✅ Successfully posted comment to PR/Issue #{issue_number}!")
            except Exception as e:
                print(f"❌ Failed to comment on PR/Issue #{issue_number}: {e}")
                
        elif commit_sha:
            url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}/comments"
            data = json.dumps({"body": comment_body}).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req) as response:
                    print(f"✅ Successfully posted comment to commit {commit_sha[:7]}!")
            except Exception as e:
                print(f"❌ Failed to comment on commit {commit_sha[:7]}: {e}")
    else:
        print("\nℹ️ GitHub credentials not fully set in environment (GITHUB_TOKEN or GITHUB_REPOSITORY missing). Skipping comment.")
else:
    print("\n⚠️ No GCS Podcast URL found in the agent's output.")