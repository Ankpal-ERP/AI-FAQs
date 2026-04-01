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
st.markdown('<div class="hero-sub">Automatically explore your codebase and generate context-aware FAQs for your projects.</div>', unsafe_allow_html=True)

# ── Step 1: Project Setup ──
st.markdown("""
<div class="step-header">
    <div class="step-badge step-badge-active">1</div>
    <div class="step-title">Project Context</div>
</div>
""", unsafe_allow_html=True)

project_name = st.text_input("Project Name", value=st.session_state.get('project_name', ""), help="Context header for AI.")
about = st.text_input(
    "Overall Project Mission", 
    value=st.session_state.get('about', ""), 
    placeholder="e.g. ERP for business management...",
    help="General business goal."
)

col_fe, col_be = st.columns(2)
with col_fe:
    st.markdown("##### 🎨 Frontend")
    fe_context = st.text_area("Structure Mapping", value=st.session_state.get('fe_context', ""), height=80, key="fe_ctx")
    fe_folders_str = st.text_area("FE Folders (Target)", value=st.session_state.get('fe_folders_str', ""), height=68, key="fe_folders")

with col_be:
    st.markdown("##### ⚙️ Backend")
    be_context = st.text_area("Structure Mapping", value=st.session_state.get('be_context', ""), height=80, key="be_ctx")
    be_folders_str = st.text_area("BE Folders (Source)", value=st.session_state.get('be_folders_str', ""), height=68, key="be_folders")

extra_prompt = st.text_input(
    "Additional Generation Instructions (Optional)",
    value=st.session_state.get('extra_prompt', ""),
    key="gen_extra"
)

# ── Step 2: Route Discovery ──
st.markdown("""
<div class="step-header">
    <div class="step-badge step-badge-active">2</div>
    <div class="step-title">Fetch & Select Routes</div>
</div>
""", unsafe_allow_html=True)

routes_file = st.text_input("Routes / Manifest File (Optional)", value=st.session_state.get('routes_file', ""))

fetch_col1, fetch_col2 = st.columns([1, 4])
with fetch_col1:
    fetch_clicked = st.button("🔍 Fetch Routes", type="secondary", use_container_width=True)
with fetch_col2:
    if st.button("🗑️ Clear All Progress", use_container_width=True):
        if os.path.exists("faqs.json"): os.remove("faqs.json")
        if os.path.exists("routes.json"): os.remove("routes.json")
        st.session_state.discovered_routes = []
        st.rerun()

# Persistence logic
if 'discovered_routes' not in st.session_state:
    st.session_state.discovered_routes = []
    if os.path.exists("routes.json"):
        try:
            with open("routes.json", "r") as f:
                st.session_state.discovered_routes = json.load(f)
        except: pass

def get_completed_routes():
    if os.path.exists("faqs.json"):
        try:
            with open("faqs.json", "r") as f:
                data = json.load(f)
                return list(set(faq.get("source_path") for faq in data.get("faqs", []) if faq.get("source_path")))
        except: pass
    return []

if fetch_clicked:
    from core.agent import discover_routes
    fe_list = [p.strip() for p in fe_folders_str.split('\n') if p.strip()]
    full_model = f"{provider}/{model_name}" if provider else model_name
    
    with st.spinner("Discovering Frontend routes..."):
        routes = discover_routes(
            model=full_model,
            api_key=api_key,
            api_base=api_base,
            project_name=project_name,
            about=about,
            fe_context=fe_context,
            fe_folders=fe_list,
            routes_file=routes_file
        )
        st.session_state.discovered_routes = routes
        with open("routes.json", "w") as f:
            json.dump(routes, f)
        st.success(f"Successfully discovered {len(routes)} routes.")
        st.rerun()

completed_routes = get_completed_routes()

if st.session_state.discovered_routes:
    st.markdown("### 📊 Route Status")
    cols = st.columns(2)
    for i, route in enumerate(st.session_state.discovered_routes):
        is_done = route in completed_routes
        label = f"✅ {os.path.basename(route)}" if is_done else f"⏳ {os.path.basename(route)}"
        # Checkboxes are now passive status indicators
        cols[i % 2].checkbox(label, value=is_done, disabled=True, key=f"status_{route}")

# ── Step 3: Generate ──
st.markdown("""
<div class="step-header">
    <div class="step-badge step-badge-active">3</div>
    <div class="step-title">Generate FAQs</div>
</div>
""", unsafe_allow_html=True)

gen_col, stop_col = st.columns([3, 1])

# Generate button
with gen_col:
    run_gen = st.button("🚀 Run Agentic FAQ Generation", type="primary", use_container_width=True)

# Stop button
with stop_col:
    if st.button("🛑 Stop", type="secondary", use_container_width=True):
        with open("stop_flag", "w") as f: f.write("stop")
        st.info("Stopping after current route finishes...")

if run_gen:
    from core.agent import generate_faqs_for_route
    
    # Remove any old stop flag before starting
    if os.path.exists("stop_flag"): os.remove("stop_flag")
    
    if not st.session_state.discovered_routes:
        st.warning("Please fetch routes first in Step 2!")
    else:
        pending_routes = [r for r in st.session_state.discovered_routes if r not in completed_routes]
        
        if not pending_routes:
            st.success("All discovered routes are already complete!")
        else:
            full_model = f"{provider}/{model_name}" if provider else model_name
            fe_ctx, be_ctx = fe_context, be_context
            be_list = [p.strip() for p in be_folders_str.split('\n') if p.strip()]
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, route in enumerate(pending_routes):
                # CHECK FOR STOP SIGNAL
                if os.path.exists("stop_flag"):
                    os.remove("stop_flag")
                    st.warning("🛑 Generation stopped by user.")
                    break

                status_text.markdown(f"**🤖 AI is analyzing [{idx+1}/{len(pending_routes)}]:** `{os.path.basename(route)}` ...")
                
                new_data = generate_faqs_for_route(
                    model=full_model,
                    api_key=api_key,
                    api_base=api_base,
                    project_name=project_name,
                    about=about,
                    fe_context=fe_ctx,
                    be_context=be_ctx,
                    be_folders=be_list,
                    route_path=route,
                    extra_prompt=extra_prompt
                )
                
                # Atomic Read-Merge-Write
                current_all = {"faqs": []}
                if os.path.exists("faqs.json"):
                    try:
                        with open("faqs.json", "r") as f: current_all = json.load(f)
                    except: pass
                
                if "faqs" in new_data:
                    for f in new_data["faqs"]: f["source_path"] = route
                    current_all["faqs"].extend(new_data["faqs"])
                    with open("faqs.json", "w") as f: json.dump(current_all, f, indent=2)
                
                # Update progress bar
                progress_bar.progress((idx + 1) / len(pending_routes))
            
            st.success("Batch process finished or stopped.")
            time.sleep(1)
            st.rerun() # Refresh once all are done (or stopped)

# ── Display Final Results ──
if os.path.exists("faqs.json"):
    try:
        with open("faqs.json", "r") as f:
            final_data = json.load(f)
            faqs = final_data.get("faqs", [])
            
            if faqs:
                st.markdown("---")
                st.markdown("## 📊 Consolidated FAQs")
                
                # Metrics
                categories = list(set(f.get("category", "General") for f in faqs))
                st.markdown(f"**Found {len(faqs)} FAQs across {len(categories)} features.**")
                
                for faq in faqs:
                    with st.expander(f"❓ {faq.get('question')}"):
                        st.write(faq.get('answer'))
                        st.caption(f"Source: {faq.get('source')}")
                
                dl1, dl2 = st.columns(2)
                dl1.download_button("📥 Download JSON", data=json.dumps(final_data, indent=2), file_name="faqs.json", mime="application/json")
                
                md_output = f"# {project_name} FAQ\n\n"
                for f in faqs:
                    md_output += f"### {f.get('question')}\n{f.get('answer')}\n*Source: {f.get('source')}*\n\n"
                dl2.download_button("📥 Download Markdown", data=md_output, file_name="faqs.md", mime="text/markdown")
    except Exception as e:
        st.warning(f"⚠️ Error displaying FAQs: {e}")

