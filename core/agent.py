import json
import logging
from litellm import completion
from tools.executor import execute_tool, TOOLS_SCHEMA, list_dir, read_file, search_code
from core.response_parser import parse_tool_calls_from_content, strip_tool_call_tags
import streamlit as st

logging.basicConfig(level=logging.INFO)


def _execute_parsed_tool(parsed_call: dict) -> dict:
    """Execute a tool call that was parsed from raw text content (not OpenAI format)."""
    name = parsed_call.get("name", "")
    args = parsed_call.get("arguments", {})
    
    if name == "list_dir":
        return list_dir(args.get("path", ""))
    elif name == "read_file":
        return read_file(args.get("path", ""))
    elif name == "search_code":
        return search_code(args.get("query", ""), args.get("path", ""))
    else:
        return {"error": f"Unknown tool: {name}"}


def run_agentic_faq_generation(
    model: str,
    api_key: str,
    api_base: str,
    project_name: str,
    about: str,
    target_folders: list[str],
    extra_prompt: str = "",
    routes_file: str = "",
):
    # ── Read routes/manifest file if provided ──
    routes_context = ""
    if routes_file:
        try:
            from pathlib import Path
            rf = Path(routes_file)
            if rf.is_file():
                raw = rf.read_text(encoding="utf-8", errors="replace")
                # Truncate if too large (keep first 40k chars)
                if len(raw) > 40000:
                    raw = raw[:40000] + "\n\n... [truncated] ..."
                routes_context = raw
                st.write(f"📄 Loaded routes manifest: `{routes_file}` ({len(raw)} chars)")
        except Exception as e:
            st.warning(f"Could not read routes file: {e}")

    system_prompt = f"""You are an expert Customer Support Specialist and Technical Writer.
Your goal is to explore the provided software repository and generate a comprehensive FAQ for the END USERS of the application.

Project Name: {project_name}
About: {about}
Root Target Folders to Search: {', '.join(target_folders)}

CRITICAL STRATEGY:
- Do NOT waste iterations just listing directories one by one. 
- FIRST, call search_code to find key patterns like "error", "validation", "required", "button", "submit", "login", "password", "invoice", "permission" across the root folders.
- THEN, call read_file on the most interesting files found by search_code.
- Use list_dir ONLY ONCE at the root level if needed, never drill down folder by folder.
- You have a maximum of 12 tool calls. Use them wisely.

After gathering enough information, produce the final output as valid JSON with this schema:
"""

    if extra_prompt:
        system_prompt += f"\n\nADDITIONAL USER INSTRUCTIONS:\n{extra_prompt}\n"

    schema_example = """
{
    "faqs": [
        {
            "category": "Topic Name",
            "question": "User-friendly Question",
            "answer": "Helpful non-technical answer",
            "source": "File where this was discovered"
        }
    ]
}

IMPORTANT: 
- DO NOT guess or hallucinate. Base everything on code found via your tools.
- When you output the final JSON, do not include ANY text or tool calls outside the JSON.
- Do not call any tools once you are generating the final JSON.
- Generate at least 5-10 FAQs.
"""
    full_system = system_prompt + schema_example

    # ── Build initial user message ──
    user_msg = "Please begin exploring the target folders with your tools and generate the final JSON FAQ."
    if routes_context:
        user_msg = f"""I have provided a routes/manifest file that maps out the entire application structure. Study it carefully to understand all the features, pages, and modules before you start exploring.

ROUTES / MANIFEST FILE CONTENT:
```
{routes_context}
```

Now use this as your guide. Call read_file on the most important component files listed in the routes to understand what each feature does, then generate the final JSON FAQ."""

    messages = [
        {"role": "system", "content": full_system},
        {"role": "user", "content": user_msg}
    ]
    
    st.info(f"Starting Agent logic with: {model}")
    max_loops = 15
    generated_json = None
    
    completion_args = {
        "model": model,
        "messages": messages,
        "tools": TOOLS_SCHEMA,
        "temperature": 0.7,
        "extra_body": {"model": model}
    }
    
    if api_key:
        completion_args["api_key"] = api_key
    if api_base:
        if not api_base.endswith("/v1"):
            api_base = api_base.rstrip("/") + "/v1"
        completion_args["api_base"] = api_base
    
    for i in range(max_loops):
        st.write(f"**Agent Iteration {i+1}**")
        response = completion(**completion_args)
        
        response_message = response.choices[0].message
        content = response_message.content or ""
        
        # ── Check 1: Standard OpenAI tool_calls ──
        if response_message.tool_calls:
            messages.append(response_message)
            for tool_call in response_message.tool_calls:
                st.write(f"🤖 Tool: `{tool_call.function.name}` | Args: `{tool_call.function.arguments}`")
                
                tool_result = execute_tool(tool_call)
                st.write(f"📥 Returned {len(str(tool_result))} chars")
                
                messages.append({
                    "role": "tool",
                    "name": tool_call.function.name,
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })
            continue
        
        # ── Check 2: Parse tool calls from raw text (Qwen/Nemotron XML format) ──
        parsed_calls = parse_tool_calls_from_content(content)
        if parsed_calls:
            messages.append({"role": "assistant", "content": content})
            
            for pc in parsed_calls:
                tool_name = pc["name"]
                tool_args = pc["arguments"]
                st.write(f"🤖 Tool (parsed): `{tool_name}` | Args: `{json.dumps(tool_args)}`")
                
                tool_result = _execute_parsed_tool(pc)
                st.write(f"📥 Returned {len(str(tool_result))} chars")
                
                messages.append({
                    "role": "user",
                    "content": f"Tool Result for {tool_name}:\n{json.dumps(tool_result)}"
                })
            continue
        
        # ── Check 3: No tool calls → this is the final answer ──
        # Strip any leftover tool call tags just in case
        clean_content = strip_tool_call_tags(content)
        if clean_content:
            generated_json = clean_content
            st.success("FAQ Generation Complete!")
            break
        else:
            # Empty response, push for answer
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": "Please output the final JSON FAQ now based on everything you have gathered."})
            continue

    if not generated_json:
        st.warning("Max loops reached, forcing final answer.")
        final_prompt = messages.copy()
        final_prompt.append({"role": "user", "content": "STOP calling tools. Output the final JSON result NOW based on all findings so far. No tool calls, only JSON."})
        
        fallback_args = {
            "model": model,
            "messages": final_prompt,
            "temperature": 0.2,
            "extra_body": {"model": model}
        }
        if api_key:
            fallback_args["api_key"] = api_key
        if api_base:
            fallback_args["api_base"] = api_base
            
        response = completion(**fallback_args)
        raw = response.choices[0].message.content or ""
        generated_json = strip_tool_call_tags(raw)
        
    return generated_json
