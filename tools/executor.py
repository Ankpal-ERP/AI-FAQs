import os
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AI-Faqs")

# ── Path Sandboxing ──────────────────────────────────────────────────────────
_PROJECT_ROOT: Optional[str] = None


def set_project_root(root: str):
    """Set the project root to restrict all file operations within it."""
    global _PROJECT_ROOT
    resolved = str(Path(root).resolve())
    if not Path(resolved).is_dir():
        raise ValueError(f"Project root is not a valid directory: {root}")
    _PROJECT_ROOT = resolved
    logger.info(f"🔒 Path sandbox set to: {_PROJECT_ROOT}")


def _validate_path(path: str) -> str:
    """Resolve and validate that a path is within the project root."""
    resolved = str(Path(path).resolve())
    if _PROJECT_ROOT and not resolved.startswith(_PROJECT_ROOT):
        raise ValueError(
            f"Access denied: '{path}' is outside project root '{_PROJECT_ROOT}'"
        )
    return resolved


# ── Content Helpers ──────────────────────────────────────────────────────────
def chunk_content(text: str, max_chars: int = 50000) -> str:
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return (
        text[:half]
        + f"\n\n... [{len(text) - max_chars} chars truncated] ...\n\n"
        + text[-half:]
    )


# ── Tool Implementations ────────────────────────────────────────────────────
def list_dir(path: str) -> Dict[str, Any]:
    """Lists files and directories in a given path."""
    try:
        validated = _validate_path(path)
    except ValueError as e:
        return {"error": str(e)}

    target_path = Path(validated)
    if not target_path.exists():
        return {"error": f"Path not found: {path}"}
    if not target_path.is_dir():
        return {"error": f"Not a directory: {path}"}

    try:
        entries = []
        for entry in target_path.iterdir():
            entries.append(
                {
                    "name": entry.name,
                    "isDirectory": entry.is_dir(),
                    "path": str(entry.absolute()),
                }
            )
        return {"success": True, "entries": entries}
    except PermissionError as e:
        return {"error": f"Permission denied: {e}"}
    except OSError as e:
        return {"error": f"OS error: {e}"}


def read_file(path: str) -> Dict[str, Any]:
    """Reads a file and returns its content (with chunking for large files)."""
    try:
        validated = _validate_path(path)
    except ValueError as e:
        return {"error": str(e)}

    target_path = Path(validated)
    if not target_path.exists() or not target_path.is_file():
        return {"error": f"File not found: {path}"}

    try:
        content = target_path.read_text(encoding="utf-8", errors="replace")
        chunked = chunk_content(content)
        return {"success": True, "content": chunked}
    except PermissionError as e:
        return {"error": f"Permission denied: {e}"}
    except OSError as e:
        return {"error": f"OS error reading file: {e}"}


def search_code(query: str, path: str) -> Dict[str, Any]:
    """Uses ripgrep or grep to search for a string in a directory."""
    try:
        validated = _validate_path(path)
    except ValueError as e:
        return {"error": str(e)}

    target_path = Path(validated)
    if not target_path.exists() or not target_path.is_dir():
        return {"error": f"Directory not found: {path}"}

    try:
        # Try ripgrep first — use '--' to prevent query from being interpreted as flags
        cmd = ["rg", "-n", "--", query, str(target_path)]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, timeout=30
        )
        if result.returncode == 0:
            return {"success": True, "results": chunk_content(result.stdout, 50000)}

        # Fallback to grep
        cmd = ["grep", "-rn", "--", query, str(target_path)]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, timeout=30
        )
        if result.returncode == 0:
            return {"success": True, "results": chunk_content(result.stdout, 50000)}

        return {"success": True, "results": "No matches found."}
    except subprocess.TimeoutExpired:
        return {"error": "Search timed out after 30 seconds."}
    except FileNotFoundError:
        return {"error": "Neither 'rg' nor 'grep' found on this system."}
    except OSError as e:
        return {"error": f"Search error: {e}"}


# ── Tool Schema ──────────────────────────────────────────────────────────────
def load_tools_schema() -> List[Dict[str, Any]]:
    """Loads tools schema from tools.json file."""
    tools_file = Path(__file__).parent / "tools.json"
    if tools_file.exists():
        try:
            with open(tools_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("tools", [])
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Error loading tools.json: {e}")
    return []


TOOLS_SCHEMA = load_tools_schema()


# ── Unified Tool Dispatcher ─────────────────────────────────────────────────
def execute_tool_by_name(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Single, canonical tool dispatcher used by the agent loop.

    Accepts a tool name and a dict of arguments — works for both native
    tool_calls and manually-parsed calls from open-source models.
    """
    if name == "list_dir":
        return list_dir(args.get("path", ""))
    elif name == "read_file":
        return read_file(args.get("path", ""))
    elif name == "search_code":
        return search_code(args.get("query", ""), args.get("path", ""))
    else:
        return {"error": f"Unknown tool: {name}"}
