#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from google import genai


def load_research_files(file_paths: list[str]) -> str:
    research_content = []
    for path in file_paths:
        if not os.path.exists(path):
            print(f"Warning: File {path} not found. Skipping.")
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                research_content.append(f.read())
        except Exception as e:
            print(f"Warning: Failed to read {path}: {e}. Skipping.")
            
    if not research_content:
        return ""
        
    return "\n\n---\n\n".join(research_content)

def main():
    load_dotenv()
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY must be set.")

    # All arguments passed are treated as input files
    input_files = sys.argv[1:]
    if not input_files:
        # Fallback to all markdown files in content/ directory
        content_dir = "content"
        if os.path.exists(content_dir):
            input_files = [os.path.join(content_dir, f) for f in os.listdir(content_dir) if f.endswith(".md")]
            input_files.sort()

    if not input_files:
        print("Error: No markdown files provided and content/ directory is empty.")
        sys.exit(1)

    print(f"Reading from {len(input_files)} source file(s)...")
    research_text = load_research_files(input_files)
    if not research_text.strip():
        print("Error: No research content loaded.")
        sys.exit(1)

    # Defaults - We target a short, high-impact 3-minute episode (~500 words)
    target_words = 500
    output_path = "script.md"

    # System instruction for co-hosts Paul and Sarah discovering tech together
    system_instruction = f"""You are a scriptwriter for "AI Talk Radio". Write a natural, highly engaging, and punchy co-host podcast script based on the research provided.

Co-Hosts:
- Paul: Thoughtful, tech-savvy co-host.
- Sarah: Inquisitive, curious co-host.

Goals for the script:
1. Dynamic Title: Come up with a catchy, unique, and descriptive title for the episode and introduce it naturally.
2. Natural Title Introduction: The co-hosts MUST introduce the title of the show naturally early on during their introductory banter.
3. Explain the Tech: Walk through all the papers/files in the research, explaining the concepts in a fun, conversational way with short, choice bites.
4. Surprising Facts: Highlight key, shocking sticking points from the research that would surprise the listener.
5. Target Length: Write a short, highly punchy, and engaging conversation. It should be around {target_words} words. Avoid unnecessary filler and focus on the most interesting details.

Format & Interaction Rules:
- NO MARKDOWN FORMATTING: Do not use bold (no **Paul:** or **Sarah:**), do not use italics (no *DiffusionBlocks*), do not use markdown headers, bullet points, or lists. Output PURE raw text.
- Start each line with the speaker name and a colon: `Paul: ` or `Sarah: ` (do not bold these speaker tags).
- Weave expressive emotion tags in square brackets naturally mid-sentence where they actually occur in natural speech (e.g., [laughter], [giggle], [sighs], [excitedly], [puzzled], [chuckles]).
- Keep sentences short, natural, and conversational with standard filler words and active banter.
- Ground the script in the research facts; do not fabricate.
"""

    print("=== AI Talk Radio: Script Writer (gemini-3.5-flash) ===")
    print(f"Generating a concise 500-word script using Interactions API...")

    client = genai.Client(api_key=api_key)
    try:
        interaction = client.interactions.create(
            model="gemini-3.5-flash",
            input=f"Write a short, punchy co-host conversation script for Paul and Sarah using this research. Keep it to around {target_words} words in choice bites:\n\n{research_text}",
            system_instruction=system_instruction
        )
    except Exception as e:
        print(f"Error calling Gemini Interactions API: {e}")
        sys.exit(1)

    if not interaction.steps:
        print("Error: No steps returned.")
        sys.exit(1)

    script = interaction.steps[-1].content[0].text
    if not script:
        print("Error: No script generated.")
        sys.exit(1)

    # Write output to file
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(script)
    except Exception as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)

    word_count = len(script.split())
    print(f"\n✅ Success! Script saved to {output_path} ({word_count} words)")

if __name__ == "__main__":
    main()
