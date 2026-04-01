import streamlit as st
import json
import time
import os

# ── Page Config ──
st.set_page_config(
    page_title="FAQ Helper · Agentic AI",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from ui.styles import apply_custom_styles

# ── Custom CSS for Premium Look ──
apply_custom_styles()


# ── Sidebar ──
with st.sidebar:
    st.markdown("### 💡 FAQ Helper")
    st.caption("Agentic AI · Local & Remote")
    st.markdown("---")
    
    st.markdown("## ⚙️ LLM Configuration")
    provider = st.text_input("Provider", placeholder="openai, anthropic, ollama, gemini", help="LiteLLM provider prefix. Leave blank for direct API.")
    model_name = st.text_input("Model", value="gpt-4o", placeholder="gpt-4o, llama3, qwen")
    api_key = st.text_input("API Key", type="password", placeholder="sk-...", help="Optional for local providers like Ollama/LM Studio.")
    api_base = st.text_input("API Base URL", placeholder="http://localhost:1234/v1", help="Custom endpoint for proxies / local servers.")
    
    st.markdown("---")
    st.caption("Powered by LiteLLM · Works with any provider")


# ── Hero Header ──
st.markdown('<div class="hero-title">FAQ Helper</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Automatically explore your codebase and generate context-aware FAQs for your end users.</div>', unsafe_allow_html=True)


# ── Step 1: Project Setup ──
st.markdown("""
<div class="step-header">
    <div class="step-badge step-badge-active">1</div>
    <div class="step-title">Project Setup</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    project_name = st.text_input("Project Name", value="", help="Injected as context header into every AI prompt.")
with col2:
    about = st.text_area("About / Description", value="", height=100, help="Be as descriptive as possible — the AI reads this before generating FAQs.")

extra_prompt = st.text_area(
    "Additional Instructions (Optional)",
    value="",
    height=80,
    placeholder="e.g. Focus on billing-related features, ignore test files, generate FAQs in Hindi...",
    help="Any extra context or instructions you want the AI to follow during generation."
)


# ── Step 2: Source Folders ──
st.markdown("""
<div class="step-header">
    <div class="step-badge step-badge-active">2</div>
    <div class="step-title">Source Folders</div>
</div>
""", unsafe_allow_html=True)

target_paths_str = st.text_area(
    "Absolute Folder Paths (one per line)", 
    value="",
    height=80,
    help="The AI agent will use search_code + read_file inside these directories."
)

target_list_preview = [p.strip() for p in target_paths_str.split('\n') if p.strip()]
if target_list_preview:
    valid_count = 0
    invalid_dirs = []
    for p in target_list_preview:
        if os.path.isdir(p):
            valid_count += 1
        else:
            invalid_dirs.append(p)
            
    if invalid_dirs:
        for ip in invalid_dirs:
            st.error(f"Directory not found on disk: `{ip}`", icon="🚨")
    elif valid_count > 0:
        st.success(f"{valid_count} valid directory/directories targeted.", icon="✅")

routes_file = st.text_input(
    "Routes / Manifest File (Optional)",
    value="",
    placeholder="e.g. /home/user/project/client/src/router/index.ts",
    help="Path to a routes file, menu config, or any manifest that maps all pages/features. The agent reads this first to understand the full app structure before exploring."
)

if routes_file:
    if os.path.isfile(routes_file):
        st.success(f"Manifest file found.", icon="📄")
    else:
        st.error(f"File not found: `{routes_file}`", icon="🚨")


# ── Step 3: Generate ──
st.markdown("""
<div class="step-header">
    <div class="step-badge step-badge-active">3</div>
    <div class="step-title">Generate FAQs</div>
</div>
""", unsafe_allow_html=True)

generate_clicked = st.button("🚀 Run Agentic FAQ Generation", type="primary", use_container_width=True)

if generate_clicked:
    from core.agent import run_agentic_faq_generation
    
    target_list = [p.strip() for p in target_paths_str.split('\n') if p.strip()]
    full_model_name = f"{provider}/{model_name}" if provider else model_name
    
    if not full_model_name:
        st.error("Please provide a Model Name in the sidebar.")
    elif not target_list:
        st.error("Please provide at least one target folder.")
    else:
        with st.status(f"🤖 Agent running with `{full_model_name}`...", expanded=True) as status:
            start_time = time.time()
            final_json_str = run_agentic_faq_generation(
                model=full_model_name,
                api_key=api_key,
                api_base=api_base,
                project_name=project_name,
                about=about,
                target_folders=target_list,
                extra_prompt=extra_prompt,
                routes_file=routes_file
            )
            elapsed = round(time.time() - start_time, 1)
            status.update(label=f"✅ Complete in {elapsed}s", state="complete", expanded=False)
        
        # ── Step 4: Display Results ──
        st.markdown("""
        <div class="step-header">
            <div class="step-badge step-badge-done">✓</div>
            <div class="step-title">Generated FAQs</div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            import re
            clean_json = final_json_str.strip()
            
            # Find the JSON block if it's wrapped in markdown
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', clean_json, re.DOTALL)
            if json_match:
                clean_json = json_match.group(1).strip()
            else:
                # If no markdown block, try to find the first { and last }
                start_idx = clean_json.find('{')
                end_idx = clean_json.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    clean_json = clean_json[start_idx:end_idx+1].strip()
                
            data = json.loads(clean_json)
            faqs = data.get("faqs", [])
            
            # Metrics
            categories = list(set(f.get("category", "General") for f in faqs))
            st.markdown(f"""
            <div class="metrics-row">
                <div class="metric-card">
                    <div class="metric-value">{len(faqs)}</div>
                    <div class="metric-label">FAQs Generated</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{len(categories)}</div>
                    <div class="metric-label">Categories</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{elapsed}s</div>
                    <div class="metric-label">Time Taken</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Color map for categories
            colors = ["cat-teal", "cat-blue", "cat-amber", "cat-purple", "cat-red"]
            cat_color_map = {cat: colors[i % len(colors)] for i, cat in enumerate(categories)}
            
            # FAQ Cards
            for faq in faqs:
                cat = faq.get("category", "General")
                color_class = cat_color_map.get(cat, "cat-blue")
                st.markdown(f"""
                <div class="faq-card">
                    <div class="faq-q">
                        {faq.get('question', '')}
                        <span class="cat-badge {color_class}">{cat}</span>
                    </div>
                    <div class="faq-a">{faq.get('answer', '')}</div>
                    <div class="faq-source">📄 Source: {faq.get('source', 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Download Buttons
            st.markdown("---")
            dl_col1, dl_col2, dl_col3 = st.columns(3)
            with dl_col1:
                st.download_button(
                    "📥 Download JSON",
                    data=json.dumps(data, indent=2),
                    file_name=f"{project_name}_faqs.json",
                    mime="application/json",
                    use_container_width=True
                )
            with dl_col2:
                # Generate Markdown
                md_lines = [f"# {project_name} — FAQ\n"]
                for cat in categories:
                    md_lines.append(f"\n## {cat}\n")
                    for faq in faqs:
                        if faq.get("category") == cat:
                            md_lines.append(f"### {faq.get('question', '')}\n")
                            md_lines.append(f"{faq.get('answer', '')}\n")
                            md_lines.append(f"*Source: {faq.get('source', 'N/A')}*\n")
                md_content = "\n".join(md_lines)
                st.download_button(
                    "📥 Download Markdown",
                    data=md_content,
                    file_name=f"{project_name}_faqs.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with dl_col3:
                st.button("🔄 Regenerate", use_container_width=True)
                    
        except Exception as e:
            st.warning("⚠️ Could not parse agent's response as valid JSON.")
            st.code(final_json_str, language="text")
