---
name: script_writing
description: A skill to write co-host podcast scripts (Paul and Sarah) from research materials using Gemini.
---

# Script Writing Skill

This skill packages the logic to automatically generate highly engaging, punchy, conversational co-host podcast scripts (featuring co-hosts Paul and Sarah) from research files.

## Overview

Instead of running a python script, you (the agent) will write the script yourself:
1. Read the research/input markdown files in `content/`.
2. Perform a web search to gather extra context, latest developments, and interesting details on the tech/topics mentioned in the research files.
3. Write the co-host podcast script directly, strictly adhering to the **Script Guidelines** and **Formatting Rules** below.
4. Save the generated script directly to `script.md` in the working directory.

## Script Guidelines

Co-Hosts:
- **Paul**: Thoughtful, tech-savvy co-host.
- **Sarah**: Inquisitive, curious co-host.

Goals for the script:
1. **Dynamic Title**: Come up with a catchy, unique, and descriptive title for the episode and introduce it naturally.
2. **Natural Title Introduction**: The co-hosts MUST introduce the title of the show naturally early on during their introductory banter.
3. **Explain the Tech**: Walk through all the papers/files in the research, explaining the concepts in a fun, conversational way with short, choice bites.
4. **Surprising Facts**: Highlight key, shocking sticking points from the research that would surprise the listener.
5. **Target Length**: Write a short, highly punchy, and engaging conversation. It should be around 500 words. Avoid unnecessary filler and focus on the most interesting details.

## Formatting & Interaction Rules

- **NO MARKDOWN FORMATTING**: Do not use bold (no **Paul:** or **Sarah:**), do not use italics (no *DiffusionBlocks*), do not use markdown headers, bullet points, or lists. Output PURE raw text.
- **Start each line** with the speaker name and a colon: `Paul: ` or `Sarah: ` (do not bold these speaker tags).
- **Weave expressive emotion tags** in square brackets naturally mid-sentence where they actually occur in natural speech (e.g., `[laughter]`, `[giggle]`, `[sighs]`, `[excitedly]`, `[puzzled]`, `[chuckles]`).
- **Keep sentences short**, natural, and conversational with standard filler words and active banter.
- **Ground the script** in the research facts; do not fabricate.
