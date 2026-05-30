#!/usr/bin/env python3
"""A script demonstrating how to stream and parse Gemini Interaction steps in real time.

This script spawns a managed agent, streams the events, dynamically
accumulates the events into structured steps, and prints the final
structured steps list at the end.

The Interaction API uses discriminated unions for both Step and Delta types,
keyed on the `type` field. Each delta variant (DeltaText, DeltaThoughtSummary,
DeltaCodeExecutionCall, DeltaCodeExecutionResult, DeltaArgumentsDelta, etc.)
has its own distinct shape — we match on `delta.type` to handle each cleanly.
"""

import json
import os
import warnings

from dotenv import load_dotenv
from google import genai
from google.genai import interactions
from rich import print as rprint

warnings.filterwarnings("ignore")

load_dotenv()

MAX_LOG_CHARS = 240


def preview(value):
    if hasattr(value, "model_dump"):
        value = value.model_dump(exclude_none=True)
    elif isinstance(value, list) and all(hasattr(item, "text") for item in value):
        value = "".join(item.text or "" for item in value)

    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(
            value,
            ensure_ascii=False,
            default=lambda obj: (
                obj.model_dump(exclude_none=True) if hasattr(obj, "model_dump") else str(obj)
            ),
        )

    return text if len(text) <= MAX_LOG_CHARS else text[:MAX_LOG_CHARS].rstrip() + "..."


def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        rprint("⚠️  Warning: GOOGLE_API_KEY is not set in your environment or .env file.")
        return

    client = genai.Client()

    rprint("🚀 Spawning managed agent in streaming mode...")
    try:
        response = client.interactions.create(
            agent="antigravity-preview-05-2026",
            input="Show me that you can execute code. Write a Python script to compute the 10th Fibonacci number.",
            stream=True,
            environment="remote",
        )

        steps = []
        raw_arguments_by_step = {}

        for chunk in response:
            match chunk.event_type:
                case "step.start":
                    index = chunk.index
                    step = chunk.step

                    while len(steps) <= index:
                        steps.append(None)
                    steps[index] = step

                    match step.type:
                        case "thought":
                            rprint("\n[bold yellow]Thinking...[/bold yellow]")
                        case "code_execution_call":
                            rprint("\n[bold blue]Running Code in Sandbox...[/bold blue]")
                        case "code_execution_result":
                            rprint("\n[bold cyan]Code Execution Result:[/bold cyan]")
                        case "function_call":
                            rprint(f"\n[bold blue]Function Call:[/bold blue] {step.name}")
                        case "function_result":
                            call = f" for {step.name}" if step.name else ""
                            rprint(f"\n[bold cyan]Function Result{call}:[/bold cyan]")
                        case "model_output":
                            rprint("\n[bold green]Agent Output > [/bold green]", end="", flush=True)
                        case _:
                            rprint(f"\n[bold magenta]Step Start: {step.type}[/bold magenta]")

                case "step.delta":
                    index = chunk.index
                    step = steps[index]
                    delta = chunk.delta

                    match delta.type:
                        case "thought_summary":
                            content = delta.content
                            text = getattr(content, "text", "") if content else ""
                            if text:
                                if not step.summary:
                                    step.summary = [content]
                                else:
                                    first_summary = step.summary[0]
                                    first_summary.text = (getattr(first_summary, "text", "") or "") + text

                                rprint(f"[yellow]{text}[/yellow]", end="", flush=True)

                        case "text":
                            if not step.content:
                                step.content = [interactions.TextContent(text="", type="text")]
                            step.content[-1].text = (step.content[-1].text or "") + delta.text
                            print(delta.text, end="", flush=True)

                        case "code_execution_call":
                            args = delta.arguments
                            if args and args.code:
                                if not step.arguments:
                                    step.arguments = args
                                else:
                                    step.arguments.code = (step.arguments.code or "") + args.code
                                rprint(f"[blue]$ {preview(args.code)}[/blue]")

                        case "code_execution_result":
                            step.result = (step.result or "") + (delta.result or "")
                            if delta.result:
                                rprint(f"[cyan]{preview(delta.result)}[/cyan]")

                        case "function_result":
                            if delta.name:
                                step.name = delta.name
                            if delta.result:
                                step.result = delta.result
                                name = f"{step.name}: " if step.name else ""
                                rprint(f"[cyan]{name}{preview(delta.result)}[/cyan]")

                        case "arguments_delta":
                            if delta.arguments:
                                raw_arguments_by_step[index] = (
                                    raw_arguments_by_step.get(index, "") + delta.arguments
                                )

                case "step.stop":
                    index = chunk.index
                    raw_arguments = raw_arguments_by_step.pop(index, None)
                    if raw_arguments is not None:
                        try:
                            steps[index].arguments = json.loads(raw_arguments)
                        except json.JSONDecodeError:
                            steps[index].arguments = raw_arguments
                        if steps[index].type == "function_call":
                            rprint(f"[blue]Args:[/blue] {preview(steps[index].arguments)}")

        rprint("\n\n[bold cyan]Final Structured Interaction Steps:[/bold cyan]")
        

    except Exception as e:
        rprint(f"\n❌ Error spawning agent: {e}")


if __name__ == "__main__":
    main()
