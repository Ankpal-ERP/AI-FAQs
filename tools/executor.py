import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List

def chunk_content(text: str, max_chars: int = 50000) -> str:
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return text[:half] + f"\n\n... [{len(text) - max_chars} chars truncated] ...\n\n" + text[-half:]

def list_dir(path: str) -> Dict[str, Any]:
    """Lists files and directories in a given path."""
    target_path = Path(path)
    if not target_path.exists():
        return {"error": f"Path not found: {path}"}
    if not target_path.is_dir():
        return {"error": f"Not a directory: {path}"}
    
    entries = []
    try:
        for entry in target_path.iterdir():
            entries.append({
                "name": entry.name,
                "isDirectory": entry.is_dir(),
                "path": str(entry.absolute())
            })
        return {"success": True, "entries": entries}
    except Exception as e:
        return {"error": str(e)}

def read_file(path: str) -> Dict[str, Any]:
    """Reads a file and returns its content (with chunking for large files)."""
    target_path = Path(path)
    if not target_path.exists() or not target_path.is_file():
        return {"error": f"File not found: {path}"}
    
    try:
        content = target_path.read_text(encoding='utf-8', errors='replace')
        chunked = chunk_content(content)
        return {"success": True, "content": chunked}
    except Exception as e:
        return {"error": str(e)}

def search_code(query: str, path: str) -> Dict[str, Any]:
    """Uses ripgrep or grep to search for a string in a directory."""
    target_path = Path(path)
    if not target_path.exists() or not target_path.is_dir():
        return {"error": f"Directory not found: {path}"}
    
    try:
        # Try ripgrep first
        cmd = ["rg", "-n", query, str(target_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return {"success": True, "results": result.stdout[:50000]} # Limit output
        
        # Fallback to grep
        cmd = ["grep", "-rn", query, str(target_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return {"success": True, "results": result.stdout[:50000]}
            
        return {"success": True, "results": "No matches found."}
    except Exception as e:
        return {"error": str(e)}

import json

def load_tools_schema() -> List[Dict[str, Any]]:
    """Loads tools schema from tools.json file."""
    tools_file = Path(__file__).parent / "tools.json"
    if tools_file.exists():
        try:
            with open(tools_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("tools", [])
        except Exception as e:
            print(f"Error loading tools.json: {e}")
    return []

TOOLS_SCHEMA = load_tools_schema()

def execute_tool(tool_call) -> Dict[str, Any]:
    """Executes a tool call based on name and arguments."""
    import json
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    
    if name == "list_dir":
        return list_dir(args.get("path"))
    elif name == "read_file":
        return read_file(args.get("path"))
    elif name == "search_code":
        return search_code(args.get("query"), args.get("path"))
    else:
        return {"error": f"Unknown tool: {name}"}
