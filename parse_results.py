import json
import sys
import os

class StreamParser:
    def __init__(self, on_chunk=None):
        self.steps = {}
        self.on_chunk = on_chunk or self.default_on_chunk
        self.current_type = None

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

def parse_and_print_stream(stream):
    decoder = json.JSONDecoder()
    buffer = ""
    parser = StreamParser()
    
    while True:
        chunk = stream.read(4096)
        if not chunk:
            break
        buffer += chunk
        
        idx = 0
        length = len(buffer)
        while idx < length:
            while idx < length and buffer[idx].isspace():
                idx += 1
            if idx >= length:
                break
                
            try:
                obj, new_idx = decoder.raw_decode(buffer, idx)
                buffer = buffer[new_idx:]
                idx = 0
                length = len(buffer)
                
                parser.process_event(obj)
                    
            except json.JSONDecodeError:
                break

def main():
    target_file = "result.jsonl"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        
    if not os.path.exists(target_file):
        print(f"Error: {target_file} not found.", file=sys.stderr)
        sys.exit(1)
        
    with open(target_file, "r", encoding="utf-8") as f:
        parse_and_print_stream(f)
        print() # trailing newline

if __name__ == "__main__":
    main()

