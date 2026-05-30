---
name: script_writing
description: A skill to write co-host podcast scripts (Paul and Sarah) from research materials using Gemini.
---

# Script Writing Skill

This skill packages the logic to automatically generate highly engaging, punchy, conversational co-host podcast scripts (featuring co-hosts Paul and Sarah) from research files.

## Overview

The **script_writing** skill automates the creation of natural conversational scripts. It:
1. Loads environment variables (from `.env` using `python-dotenv`).
2. Reads research/input markdown files.
3. Calls the Gemini Interactions API with a customized system prompt.
4. Generates a concise, high-impact script in short, choice bites (~500 words).
5. Saves the script to `script.md`.

## Setup & Prerequisites

Make sure the required dependencies are installed:
```bash
uv add google-genai python-dotenv
```

Ensure `GOOGLE_API_KEY` is set in your environment or in a `.env` file in the root directory.

## Script Writer Implementation

The Python script is located in `scripts/write_script.py`. It is a standalone script that accepts path arguments or automatically falls back to markdown files in the `content/` folder.

## How to Run

To run the skill and write a podcast script from your research:
```bash
uv run .agents/skills/script_writing/scripts/write_script.py [input_file1.md] [input_file2.md]
```
If no input files are specified, it automatically searches the `content/` directory for any markdown files.
