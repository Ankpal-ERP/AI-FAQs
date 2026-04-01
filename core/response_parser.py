"""
Response parser for handling non-standard tool call formats from open-source models.

Handles:
1. Nemotron/XML format: <tool_call><function=name><parameter=key>value</parameter></function></tool_call>
2. Qwen JSON format: <tool_call>{"name": "...", "arguments": {...}}</tool_call>
3. Standard OpenAI format (passthrough)
"""

import re
import json
from typing import Dict, Any, Optional, List


# ── Nemotron / XML format ──────────────────────────────────────────────────
# Example: <tool_call> <function=list_dir> <parameter=path> /some/path </parameter> </function> </tool_call>
TOOL_CALL_PATTERN = re.compile(
    r'<tool_call>([\s\S]*?)</tool_call>',
    re.IGNORECASE
)

FUNCTION_PATTERN = re.compile(
    r'<function=(\w+)>([\s\S]*?)</function>',
    re.IGNORECASE
)

PARAMETER_PATTERN = re.compile(
    r'<parameter=(\w+)>([\s\S]*?)</parameter>',
    re.IGNORECASE
)


def _parse_xml_tool_call(content: str) -> Optional[Dict[str, Any]]:
    """Parse Nemotron/XML format tool calls from content.
    
    Format: <tool_call><function=name><parameter=key>value</parameter></function></tool_call>
    """
    tool_call_match = TOOL_CALL_PATTERN.search(content)
    if not tool_call_match:
        return None
    
    tool_call_body = tool_call_match.group(1)
    
    function_match = FUNCTION_PATTERN.search(tool_call_body)
    if not function_match:
        return None
    
    tool_name = function_match.group(1).strip()
    function_body = function_match.group(2)
    
    args: Dict[str, Any] = {}
    for param_match in PARAMETER_PATTERN.finditer(function_body):
        param_name = param_match.group(1).strip()
        param_value = param_match.group(2).strip()
        
        # Coerce types
        if param_value.lower() == "true":
            param_value = True
        elif param_value.lower() == "false":
            param_value = False
        elif param_value.lower() == "null" or param_value == "":
            param_value = None
        else:
            try:
                param_value = json.loads(param_value)
            except (json.JSONDecodeError, ValueError):
                try:
                    if '.' in param_value:
                        param_value = float(param_value)
                    else:
                        param_value = int(param_value)
                except ValueError:
                    pass  # Keep as string
    
        args[param_name] = param_value
    
    if not tool_name:
        return None
    
    return {
        "name": tool_name,
        "arguments": args,
    }


def _parse_qwen_json_tool_call(content: str) -> Optional[Dict[str, Any]]:
    """Parse Qwen JSON format tool calls from content.
    
    Format: <tool_call>{"name": "...", "arguments": {...}}</tool_call>
    """
    tool_call_match = TOOL_CALL_PATTERN.search(content)
    if not tool_call_match:
        return None
    
    tool_call_content = tool_call_match.group(1).strip()
    if not tool_call_content:
        return None
    
    try:
        parsed = json.loads(tool_call_content)
        if not isinstance(parsed, dict):
            return None
        
        tool_name = parsed.get("name")
        arguments = parsed.get("arguments", {})
        
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {"raw": arguments}
        
        if not isinstance(tool_name, str) or not tool_name:
            return None
        
        return {
            "name": tool_name,
            "arguments": arguments if isinstance(arguments, dict) else {},
        }
    except json.JSONDecodeError:
        return None


def parse_tool_calls_from_content(content: str) -> List[Dict[str, Any]]:
    """Try to extract tool calls from raw text content.
    
    Tries XML format first (Nemotron), then JSON format (Qwen).
    Returns a list of parsed tool call dicts, each with 'name' and 'arguments'.
    """
    if not content:
        return []
    
    results = []
    
    # Try XML format first (most specific)
    xml_call = _parse_xml_tool_call(content)
    if xml_call:
        results.append(xml_call)
        return results
    
    # Try Qwen JSON format
    json_call = _parse_qwen_json_tool_call(content)
    if json_call:
        results.append(json_call)
        return results
    
    return results


def strip_tool_call_tags(content: str) -> str:
    """Remove all <tool_call>...</tool_call> blocks from content."""
    return TOOL_CALL_PATTERN.sub('', content).strip()
