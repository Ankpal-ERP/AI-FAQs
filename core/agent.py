import json
import logging
import os
from litellm import completion
from tools.executor import execute_tool_by_name, TOOLS_SCHEMA
from core.response_parser import parse_tool_calls_from_content

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("AIRoutes")

MAX_CONTEXT_CHARS = 120_000


def _estimate_context_size(messages: list) -> int:
    return sum(len(m.get("content", "")) for m in messages)


def _trim_context(messages: list) -> None:
    while _estimate_context_size(messages) > MAX_CONTEXT_CHARS and len(messages) > 4:
        trimmed = False
        for i in range(1, len(messages) - 2):
            content = messages[i].get("content", "")
            if len(content) > 2000 and messages[i]["role"] in ("tool", "user"):
                messages[i]["content"] = (
                    content[:500]
                    + "\n\n... [truncated to save context window] ...\n\n"
                    + content[-500:]
                )
                trimmed = True
                break
        if not trimmed:
            break


def _extract_json_object(text: str) -> dict | None:
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch == "{":
            try:
                obj, _ = decoder.raw_decode(text[i:])
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                continue
    return None


def _extract_json_array(text: str) -> list | None:
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch == "[":
            try:
                arr, _ = decoder.raw_decode(text[i:])
                if isinstance(arr, list):
                    return arr
            except json.JSONDecodeError:
                continue
    return None


def _run_agent_loop(model, api_key, api_base, messages, max_loops=10, temperature=0.2):
    logger.info("=" * 60)
    logger.info(f"🚀 MISSION START | Model: {model}")
    logger.info(f"PROMPT SUMMARY: {messages[0]['content'][:200]}...")
    logger.info("=" * 60)

    for i in range(max_loops):
        _trim_context(messages)

        try:
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if api_key:
                params["api_key"] = api_key
            if api_base:
                params["base_url"] = api_base
            if TOOLS_SCHEMA:
                params["tools"] = TOOLS_SCHEMA

            response = completion(**params)
            ai_msg = response.choices[0].message
            content = ai_msg.content or ""
            messages.append({"role": "assistant", "content": content})

            display_content = content[:150].replace("\n", " ")
            logger.info(f"🤖 [LOOP {i+1}] AI Response: {display_content}...")

            # Strategy 1: Native tool_calls
            if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
                for tc in ai_msg.tool_calls:
                    try:
                        tool_args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ Failed to parse tool args: {e}")
                        tool_args = {}

                    logger.info(f"🛠️ [TOOL] {tc.function.name} | Args: {tool_args}")
                    result = execute_tool_by_name(tc.function.name, tool_args)
                    messages.append({
                        "role": "tool",
                        "name": tc.function.name,
                        "tool_call_id": tc.id,
                        "content": json.dumps(result),
                    })
                logger.info("✅ Native tool calls executed.")
                continue

            # Strategy 2: Parsed tag-based calls
            parsed_calls = parse_tool_calls_from_content(content)
            if parsed_calls:
                for pc in parsed_calls:
                    name = pc.get("name", "")
                    args = pc.get("arguments", {})
                    logger.info(f"🛠️ [PARSED TOOL] {name} | Args: {args}")
                    result = execute_tool_by_name(name, args)
                    messages.append({
                        "role": "user",
                        "content": f"TOOL RESULT for {name}:\n{json.dumps(result, indent=2)}",
                    })
                logger.info("✅ Parsed tag-based tool calls executed.")
                continue

            # Strategy 3: Legacy 'YIELD TOOL CALL:' regex
            import re
            tool_match = re.search(r"YIELD TOOL CALL:\s*(\{.*?\})", content, re.DOTALL)
            if tool_match:
                try:
                    tool_json = json.loads(tool_match.group(1))
                    name = tool_json.get("name", "")
                    args = tool_json.get("arguments", {})
                    logger.info(f"🛠️ [LEGACY TOOL] {name} | Args: {args}")
                    result = execute_tool_by_name(name, args)
                    messages.append({
                        "role": "user",
                        "content": f"TOOL RESULT:\n{json.dumps(result, indent=2)}",
                    })
                    logger.info("✅ Legacy tool call executed.")
                    continue
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ Failed to parse legacy tool call: {e}")

            logger.info(f"🏆 Mission Complete in {i+1} loops.")
            return content

        except Exception as e:
            logger.error(f"❌ Error in loop {i+1}: {e}", exc_info=True)
            return json.dumps({"error": str(e)})

    logger.warning(f"⚠️ Agent loop exhausted after {max_loops} iterations.")
    return messages[-1]["content"]


def discover_routes(
    model,
    api_key,
    api_base,
    project_name,
    about,
    project_context,
    folders,
    routes_file,
    max_loops=15,
    temperature=0.2,
):
    routes_raw = ""
    if routes_file and os.path.isfile(routes_file):
        logger.info(f"📄 Reading user-provided routes file: {routes_file}")
        try:
            with open(routes_file, "r", encoding="utf-8") as f:
                content = f.read()  # Read ENTIRE file - no limit!
                routes_raw = (
                    f"\n\nUser-provided Routes File Content (Manifest):\n"
                    f"```\n{content}\n```"
                )
                logger.info(f"✓ Successfully read routes file ({len(content):,} chars)")
        except (OSError, IOError) as e:
            logger.error(f"❌ Could not read routes file: {e}")
            routes_raw = ""
    elif routes_file:
        logger.warning(f"⚠️ Routes file provided but doesn't exist: {routes_file}")
    else:
        logger.info("ℹ️ No routes file provided - will search automatically")

    if project_context and project_context.strip():
        context_section = f"""PROJECT STRUCTURE & CONTEXT (provided by user):
{project_context}"""
    else:
        context_section = """PROJECT STRUCTURE & CONTEXT:
No description was provided. You MUST use `list_dir` to explore the target folders.
Start broad, then drill into subdirectories to understand the layout."""

    # Add instruction to search for route files if not provided
    route_file_search_instruction = ""
    if routes_raw:
        # User provided a file - emphasize using it
        route_file_search_instruction = """
📁 USER HAS PROVIDED A ROUTES FILE - IT'S IN YOUR PROMPT ABOVE!

The file content is included as "User-provided Routes File Content (Manifest)".
This could be a menu JSON, routes config, or navigation file.
YOUR JOB: Parse it and extract ALL page/file paths mentioned in it.

Look for patterns like:
- Component imports: `() => import('@/pages/Masters/Charge/Index.vue')`
- Route paths: `{ path: '/charge', component: ... }`
- Menu items: `{ title: 'Charge', icon: '...', route: '...' }`
- Any references to .vue, .tsx, .jsx, .py files

EXTRACT all absolute file paths and return as JSON array.
"""
    else:
        # No file provided - search automatically
        route_file_search_instruction = """
CRITICAL WORKFLOW - FOLLOW THESE STEPS IN ORDER:

STEP 1 (Quick Scan): Search for route/navigation configuration files.
Look for: router/index.ts, routes.ts, navigation.ts, app-routing.module.ts, etc.
Check: /src/router/, /src/routes/, /app/router/, /config/
Use list_dir to find these files FAST.

STEP 2 (If Found): Use read_file to examine the route config file.
Extract ALL route paths from it. Return the JSON array immediately.

STEP 3 (If NOT Found): Don't waste time - go directly to target folders.
Use list_dir on each target folder to find page files (.vue, .tsx, .jsx, .py).
Focus on pages/, views/, screens/, components/ directories.

TIME LIMIT: Complete this in max 10 iterations. Be efficient!
"""

    system_prompt = f"""You are a Senior Architect analyzing the '{project_name}' project.
PROJECT MISSION:
{about if about else 'Not specified — infer from codebase.'}

{context_section}

TARGET FOLDERS TO EXPLORE: {', '.join(folders)}
{routes_raw}
{route_file_search_instruction}

{'='*60}
⚠️ CRITICAL INSTRUCTION - READ THIS FIRST: ⚠️

A user-provided routes file WAS included above (see "User-provided Routes File Content").
YOUR TASK: Extract ALL file paths from THAT file.
DO NOT ignore it. DO NOT explore randomly.
The file content is RIGHT THERE in your prompt - USE IT!

IF USER FILE EXISTS:
→ Parse it and extract all route/page file paths
→ Return them as JSON array immediately
→ DONE (no need to explore further)

IF NO USER FILE (only then):
→ Search for router/index.ts, routes.ts, etc.
→ If still not found, explore target folders for .vue/.tsx/.jsx files

{'='*60}

YOU HAVE TOOLS: 
- `list_dir`: Use ONLY if no user file provided
- `read_file`: Use to examine specific files if needed

OUTPUT FORMAT:
["/absolute/path/to/Page1.vue", "/absolute/path/to/Page2.vue"]
Return ONLY the JSON array, nothing else.

REMEMBER: If user provided a file above, JUST USE IT and return results!
"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Discover all unique feature page files and return the JSON array."},
    ]

    raw_json = _run_agent_loop(model, api_key, api_base, messages, max_loops=max_loops, temperature=temperature)

    try:
        result = _extract_json_array(raw_json)
        if result is not None:
            return result
        return json.loads(raw_json)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Failed to parse route discovery response: {e}")
        return []


def generate_faqs_for_route(
    model,
    api_key,
    api_base,
    project_name,
    about,
    project_context,
    folders,
    route_path,
    extra_prompt,
    max_faqs=4,
    max_loops=12,
    temperature=0.2,
):
    if project_context and project_context.strip():
        context_section = f"""PROJECT STRUCTURE & CONTEXT (Internal Use Only):
{project_context}"""
    else:
        context_section = """PROJECT STRUCTURE & CONTEXT:
No description was provided. Use your tools to explore the codebase.
Use `list_dir` to understand folder structure, `read_file` to examine source code,
and `search_code` to find related logic across the project."""

    system_prompt = f"""You are a Senior Product Expert and User Documentation Lead for '{project_name}'.
PROJECT MISSION:
{about if about else 'Not specified — infer from codebase.'}

{context_section}

PROJECT FOLDERS: {', '.join(folders)}

YOU HAVE TOOLS: Use `read_file` to examine source code, `search_code` to find related logic, `list_dir` to explore folders.

YOUR APPROACH:
1. Use `read_file` on {route_path} to understand the feature.
2. Use `search_code` to find related backend/API/service logic.
3. Trace the full feature flow to understand business rules and constraints.

YOUR MISSION:
Generate exactly {max_faqs} professional, high-quality FAQs for an END-USER based on your code analysis.

STRICT CONTENT RULES:
1. NO TECHNICAL JARGON: Never mention '.vue', '.ts', 'API endpoints', 'decorators', 'models', 'controllers', or 'database columns' in questions or answers.
2. USER-CENTRIC: Focus on business value. Explain 'What can I do here?' and 'What are the rules?'.
3. BACKEND INSIGHTS: Use the code you find to explain REAL constraints (e.g., 'You cannot delete a category if it has active products').
4. PERSONA: Write like a helpful Product Manager, not a developer.
5. DEPTH: Answers should be 2-4 sentences, specific, and actionable.

JSON SCHEMA (output ONLY this JSON, no surrounding text):
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
        {"role": "user", "content": f"Analyze {route_path} and its dependencies, then output the FAQs JSON."},
    ]

    raw_json = _run_agent_loop(model, api_key, api_base, messages, max_loops=max_loops, temperature=temperature)

    try:
        result = _extract_json_object(raw_json)
        if result is not None:
            return result
        return json.loads(raw_json)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Failed to parse FAQ generation response: {e}")
        return {"faqs": []}