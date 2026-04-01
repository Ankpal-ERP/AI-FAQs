import json
import logging
import re
from litellm import completion
from tools.executor import execute_tool, TOOLS_SCHEMA, list_dir, read_file, search_code
from core.response_parser import parse_tool_calls_from_content, strip_tool_call_tags
import streamlit as st
import os

# ── Logging Setup ──
# Configure logging to point exclusively to the console (StreamHandler).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("AIRoutes")

def _execute_parsed_tool(parsed_call: dict) -> dict:
    name = parsed_call.get("name", "")
    args = parsed_call.get("arguments", {})
    
    logger.info(f"🛠️ [TOOL EXECUTE] {name} | Args: {args}")
    
    if name == "list_dir":
        return list_dir(args.get("path", ""))
    elif name == "read_file":
        return read_file(args.get("path", ""))
    elif name == "search_code":
        return search_code(args.get("query", ""), args.get("path", ""))
    else:
        return {"error": f"Unknown tool: {name}"}

def _run_agent_loop(model, api_key, api_base, messages, max_loops=10):
    """The central agentic execution engine with terminal-only logging."""
    
    logger.info("="*60)
    logger.info(f"🚀 MISSION START | Model: {model}")
    logger.info(f"PROMPT SUMMARY: {messages[0]['content'][:200]}...")
    logger.info("="*60)

    for i in range(max_loops):
        try:
            params = {
                "model": model,  # This must be the full "provider/model" string
                "messages": messages,
                "temperature": 0.2,
                "extra_body": {"model": model} # Some providers expect the full name here too
            }
            if api_key: params["api_key"] = api_key
            if api_base: params["base_url"] = api_base
            
            response = completion(**params)
            ai_msg = response.choices[0].message
            content = ai_msg.content or ""
            messages.append({"role": "assistant", "content": content})
            
            # Print AI thought/output briefly to terminal
            display_content = content[:150].replace('\n', ' ')
            logger.info(f"🤖 [LOOP {i+1}] AI Response: {display_content}...")

            # Pattern for tool extraction (adjust if your model uses XML or different tags)
            # We'll support both standard LiteLLM tool_calls and manual JSON yield patterns
            if hasattr(ai_msg, 'tool_calls') and ai_msg.tool_calls:
                for tc in ai_msg.tool_calls:
                    tool_json = {"name": tc.function.name, "arguments": json.loads(tc.function.arguments)}
                    result = _execute_parsed_tool(tool_json)
                    messages.append({
                        "role": "tool",
                        "name": tc.function.name,
                        "tool_call_id": tc.id,
                        "content": json.dumps(result)
                    })
                logger.info(f"✅ Tools executed and returned to AI context.")
                continue

            # Check for manual JSON yield pattern if model doesn't use tool_calls properly
            tool_match = re.search(r'YIELD TOOL CALL:\s*({.*})', content, re.DOTALL)
            if tool_match:
                try:
                    tool_json = json.loads(tool_match.group(1))
                    result = _execute_parsed_tool(tool_json)
                    messages.append({"role": "user", "content": f"TOOL RESULT:\n{json.dumps(result, indent=2)}"})
                    logger.info(f"✅ Manual Tool result added to context.")
                    continue
                except:
                    pass
            
            # If no tools called, we assume the mission is complete
            logger.info(f"🏆 Mission Complete in {i+1} loops.")
            return content
            
        except Exception as e:
            logger.error(f"❌ Error in loop {i+1}: {e}")
            return str(e)
            
    return messages[-1]["content"]

def discover_routes(model, api_key, api_base, project_name, about, fe_context, fe_folders, routes_file):
    """Phase 1: Agent identifies all UI page/component files."""
    
    routes_raw = ""
    if routes_file and os.path.isfile(routes_file):
        try:
            routes_raw = f"\n\nUser-provided Routes File Content (Manifest):\n```\n{open(routes_file).read()[:30000]}\n```"
        except: pass

    system_prompt = f"""You are a Senior Architect analyzing the '{project_name}' project.
PROJECT MISSION:
{about}

FRONTEND STRUCTURE & MAPPING:
{fe_context}

TARGET FRONTEND FOLDERS: {', '.join(fe_folders)}
{routes_raw}

YOUR TASK:
Identify ALL key frontend page/component files (.vue, .tsx, .jsx) that represent unique end-user features.
Output a PURE JSON list of absolute file paths:
[
  "/path/to/Page1.vue",
  "/path/to/Page2.vue"
]
Only output the JSON array. Do not hallucinate.
"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Discovery all unique feature page files and return the JSON array."}
    ]
    
    raw_json = _run_agent_loop(model, api_key, api_base, messages, max_loops=5)
    try:
        import re
        match = re.search(r'\[.*\]', raw_json, re.DOTALL)
        return json.loads(match.group(0)) if match else json.loads(raw_json)
    except:
        return []

def generate_faqs_for_route(model, api_key, api_base, project_name, about, fe_context, be_context, be_folders, route_path, extra_prompt):
    """Phase 2: Agent traces a single route into the backend and writes FAQs."""
    
    system_prompt = f"""You are a Senior Product Expert and User Documentation Lead for '{project_name}'.
PROJECT MISSION:
{about}

TECHNICAL BACKGROUND (Internal Use Only):
FE Context: {fe_context}
BE Context: {be_context}
BE Folders: {', '.join(be_folders)}

YOUR MISSION:
Analyze the feature at {route_path} and its backend logic to generate 2-4 professional, high-quality FAQs for an END-USER.

STRICT CONTENT RULES:
1. NO TECHNICAL JARGON: Never mention '.vue', '.ts', 'API endpoints', 'decorators', 'models', 'controllers', or 'database columns' in the questions or answers.
2. USER-CENTRIC: Focus on the business value. Explain 'What can I do here?' and 'What are the rules?'.
3. BACKEND INSIGHTS: Use the backend code you find to explain REAL constraints (e.g., 'You cannot delete a category if it has active products').
4. PERSONA: Write like a helpful Product Manager, not a developer.

JSON SCHEMA:
{{
  "faqs": [
    {{
      "category": "Feature Name (e.g. Sales Invoicing)",
      "question": "Clear, user-friendly question?",
      "answer": "Professional, business-focused answer derived from your code analysis.",
      "source": "{os.path.basename(route_path)}"
    }}
  ]
}}
"""
    if extra_prompt:
        system_prompt += f"\nAdditional Instructions: {extra_prompt}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Analyze {route_path} and its backend dependencies, then output the FAQs JSON."}
    ]
    
    raw_json = _run_agent_loop(model, api_key, api_base, messages, max_loops=12)
    try:
        import re
        match = re.search(r'\{.*\}', raw_json, re.DOTALL)
        return json.loads(match.group(0)) if match else json.loads(raw_json)
    except:
        return {"faqs": []}
