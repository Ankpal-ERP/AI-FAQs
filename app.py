import streamlit as st
import json
import time
import os
import tempfile
import logging

logger = logging.getLogger("AIRoutes")

# ── Page Config ──
st.set_page_config(
    page_title="FAQ Helper · Agentic AI",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 960px;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: #0a0a0f;
    border-right: 1px solid #1e1e2e;
}
[data-testid="stSidebar"] * { color: #c8c8d8 !important; }
[data-testid="stSidebar"] .stTextInput label {
    color: #555577 !important;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stSidebar"] input {
    background: #111122 !important;
    border: 1px solid #2a2a3e !important;
    border-radius: 6px !important;
    color: #e0e0f0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.92rem !important;
}
[data-testid="stSidebar"] input:focus {
    border-color: #5555ff !important;
    box-shadow: 0 0 0 2px rgba(85,85,255,0.15) !important;
}

/* ─── Hero ─── */
.hero-wrap {
    padding: 2.5rem 0 2rem;
    border-bottom: 1px solid #f0f0f8;
    margin-bottom: 2rem;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    letter-spacing: 0.15em;
    color: #9090c0;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.hero-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #0f0f1a;
    letter-spacing: -0.03em;
    line-height: 1.15;
    margin-bottom: 0.5rem;
}
.hero-title span {
    background: linear-gradient(125deg, #3535cc, #7755ff, #aa44ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1.12rem;
    color: #6060a0;
    font-weight: 400;
    max-width: 540px;
    line-height: 1.6;
}

/* ─── Section Headers ─── */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 2.5rem 0 1.2rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #ededf5;
}
.section-num {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: #0f0f1a;
    color: white !important;
    font-size: 0.88rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-family: 'DM Mono', monospace;
}
.section-num.done {
    background: #1a7a4a;
}
.section-label {
    font-size: 1.12rem;
    font-weight: 600;
    color: #0f0f1a;
    letter-spacing: -0.01em;
}
.section-desc {
    font-size: 0.95rem;
    color: #8080b0;
    margin-left: auto;
}

/* ─── Field Labels ─── */
.stTextInput label, .stTextArea label {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #5050a0 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    font-family: 'DM Mono', monospace !important;
    margin-bottom: 4px !important;
}
.stTextInput input, .stTextArea textarea {
    border: 1.5px solid #e0e0f0 !important;
    border-radius: 8px !important;
    background: #fafafe !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.05rem !important;
    color: #0f0f1a !important;
    transition: border-color 0.18s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #5555ff !important;
    background: #fff !important;
    box-shadow: 0 0 0 3px rgba(85,85,255,0.08) !important;
}

/* ─── Buttons ─── */
.stButton > button[kind="primary"] {
    background: #0f0f1a !important;
    border: none !important;
    border-radius: 8px !important;
    color: white !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    padding: 0.6rem 1.5rem !important;
    letter-spacing: 0.01em;
    transition: background 0.18s, transform 0.12s !important;
}
.stButton > button[kind="primary"]:hover {
    background: #2a2a4a !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1.5px solid #d0d0e8 !important;
    border-radius: 8px !important;
    color: #5050a0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 1.0rem !important;
    transition: border-color 0.18s, background 0.18s !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #8080c0 !important;
    background: #f5f5fc !important;
}

/* ─── Status Grid ─── */
.route-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 8px;
    margin: 1rem 0;
}
.route-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0.55rem 0.85rem;
    border-radius: 8px;
    font-size: 0.92rem;
    font-family: 'DM Mono', monospace;
    border: 1px solid;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.route-pill.done {
    background: #f0faf5;
    border-color: #a8ddc0;
    color: #1a6040;
}
.route-pill.pending {
    background: #f8f8fd;
    border-color: #dcdcee;
    color: #6060a0;
}
.route-pill.active {
    background: #f0f0ff;
    border-color: #a0a0ff;
    color: #3030aa;
    animation: pulse-border 1.5s ease-in-out infinite;
}
@keyframes pulse-border {
    0%, 100% { border-color: #a0a0ff; }
    50% { border-color: #5555ff; }
}

/* ─── Stats Bar ─── */
.stats-bar {
    display: flex;
    gap: 1px;
    background: #e0e0f0;
    border-radius: 8px;
    overflow: hidden;
    margin: 1rem 0;
}
.stat-cell {
    flex: 1;
    background: #fff;
    padding: 0.85rem 1.2rem;
    text-align: center;
}
.stat-cell:first-child { border-radius: 8px 0 0 8px; }
.stat-cell:last-child { border-radius: 0 8px 8px 0; }
.stat-val {
    font-size: 1.75rem;
    font-weight: 700;
    color: #0f0f1a;
    letter-spacing: -0.03em;
    line-height: 1;
    margin-bottom: 3px;
}
.stat-key {
    font-size: 0.8rem;
    color: #8080b0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'DM Mono', monospace;
}

/* ─── FAQ Cards ─── */
.faq-list { margin-top: 1rem; }
.faq-item {
    border: 1.5px solid #e8e8f5;
    border-radius: 10px;
    margin-bottom: 10px;
    overflow: hidden;
    transition: border-color 0.18s, box-shadow 0.18s;
}
.faq-item:hover {
    border-color: #b0b0e8;
    box-shadow: 0 3px 14px rgba(85,85,180,0.06);
}
.faq-q-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 0.9rem 1.1rem;
    background: #fafafe;
}
.faq-q-icon {
    width: 24px;
    height: 24px;
    border-radius: 6px;
    background: #5555ff;
    color: white;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
    font-family: 'DM Mono', monospace;
}
.faq-q-text {
    font-size: 1.05rem;
    font-weight: 600;
    color: #0f0f1a;
    line-height: 1.4;
    flex: 1;
}
.faq-cat-tag {
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.04em;
    white-space: nowrap;
    flex-shrink: 0;
    background: #eeeefc;
    color: #4040aa;
    border: 1px solid #d8d8f0;
}
.faq-a-row {
    padding: 0.85rem 1.1rem 0.85rem 2.7rem;
    font-size: 0.98rem;
    color: #40407a;
    line-height: 1.7;
    border-top: 1px solid #f0f0f8;
}
.faq-src {
    padding: 0.4rem 1.1rem 0.6rem 2.7rem;
    font-size: 0.8rem;
    color: #a0a0c0;
    font-family: 'DM Mono', monospace;
    border-top: 1px solid #f5f5fa;
}

/* ─── Filter Bar ─── */
.filter-row {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}
.filter-btn {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    font-family: 'DM Mono', monospace;
    border: 1.5px solid #d8d8f0;
    background: white;
    color: #6060a0;
    cursor: pointer;
    transition: all 0.15s;
}
.filter-btn.active {
    background: #0f0f1a;
    border-color: #0f0f1a;
    color: white;
}

/* ─── Progress ─── */
.stProgress > div > div {
    background: linear-gradient(90deg, #3535cc, #aa44ff) !important;
    border-radius: 4px !important;
}
.stProgress > div {
    background: #e8e8f5 !important;
    border-radius: 4px !important;
}

/* ─── Alerts ─── */
.stSuccess {
    background: #f0faf5 !important;
    border: 1px solid #a8ddc0 !important;
    border-radius: 8px !important;
}
.stWarning {
    background: #fffbf0 !important;
    border: 1px solid #f0d090 !important;
    border-radius: 8px !important;
}
.stInfo {
    background: #f0f0ff !important;
    border: 1px solid #c0c0ff !important;
    border-radius: 8px !important;
}

/* ─── Download Buttons ─── */
.stDownloadButton > button {
    background: #fafafe !important;
    border: 1.5px solid #d0d0ec !important;
    border-radius: 8px !important;
    color: #4040a0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    transition: all 0.15s !important;
}
.stDownloadButton > button:hover {
    background: #f0f0fc !important;
    border-color: #8080cc !important;
}

/* ─── Divider ─── */
hr { border: none; border-top: 1px solid #ededf5; margin: 1.5rem 0; }

/* ─── Checkbox (route status) ─── */
[data-testid="stCheckbox"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────
def _atomic_write_json(filepath: str, data) -> None:
    dir_name = os.path.dirname(os.path.abspath(filepath))
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=dir_name, suffix=".tmp", delete=False
        ) as tmp:
            json.dump(data, tmp, indent=2)
            tmp_path = tmp.name
        os.replace(tmp_path, filepath)
    except Exception:
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def _safe_load_json(filepath: str, default=None):
    if default is None:
        default = {}
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.warning(f"Corrupted JSON in {filepath}: {e}")
        return default
    except OSError as e:
        logger.warning(f"Could not read {filepath}: {e}")
        return default


def _clear_stop_flag():
    if os.path.exists("stop_flag"):
        try:
            os.remove("stop_flag")
        except OSError:
            pass


def _set_stop_flag():
    try:
        with open("stop_flag", "w") as f:
            f.write("stop")
    except OSError as e:
        logger.warning(f"Could not write stop flag: {e}")


def _is_stopped() -> bool:
    return os.path.exists("stop_flag")


def get_completed_routes():
    data = _safe_load_json("faqs.json", default={"faqs": []})
    return list(
        set(
            faq.get("source_path")
            for faq in data.get("faqs", [])
            if faq.get("source_path")
        )
    )


def _render_route_grid(routes, completed, active=None):
    pills = ""
    for r in routes:
        name = os.path.basename(r)
        if r == active:
            cls = "active"
            icon = "⚡"
        elif r in completed:
            cls = "done"
            icon = "✓"
        else:
            cls = "pending"
            icon = "·"
        pills += f'<div class="route-pill {cls}" title="{r}">{icon} {name}</div>'
    st.markdown(f'<div class="route-grid">{pills}</div>', unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 0.5rem">
        <div style="font-family:'DM Mono',monospace;font-size:0.75rem;letter-spacing:0.15em;color:#444466;text-transform:uppercase;margin-bottom:8px">FAQ Helper</div>
        <div style="font-size:1.25rem;font-weight:600;color:#e0e0f5;letter-spacing:-0.01em">Agentic AI</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.75rem;letter-spacing:0.12em;color:#444466;text-transform:uppercase;margin-bottom:12px">LLM Configuration</div>""", unsafe_allow_html=True)

    provider = st.text_input("Provider", placeholder="openai · anthropic · ollama")
    model_name = st.text_input("Model *", value="openai/qwen", placeholder="gpt-4o · llama3")
    api_key = st.text_input("API Key *", type="password", placeholder="sk-...")
    api_base = st.text_input("API Base URL *", placeholder="http://localhost:1234/v1")

    st.markdown("---")

    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        max_faqs_per_route = st.slider("Max FAQs per route", min_value=2, max_value=8, value=4,
                                       help="Control how many FAQs are generated per route.")
        max_loops = st.slider("Agent max loops", min_value=5, max_value=20, value=18,
                              help="Maximum reasoning loops the agent can use per route.")
        skip_completed = st.checkbox("Skip already-completed routes", value=True,
                                     help="Resume from where you left off.")

    st.markdown("---")
    st.caption("Powered by LiteLLM · Works with any provider")


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">Agentic Documentation Tool</div>
    <div class="hero-title">FAQ <span>Helper</span></div>
    <div class="hero-sub">Autonomously explore your codebase and generate context-aware, user-friendly FAQs — powered by any LLM.</div>
</div>
""", unsafe_allow_html=True)


# ── Step 1 ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
    <div class="section-num">1</div>
    <div class="section-label">Project Context</div>
    <div class="section-desc">Tell the AI about your project</div>
</div>
""", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    project_name = st.text_input(
        "Project Name *",
        value=st.session_state.get("project_name", ""),
        placeholder="MyApp"
    )
with col_b:
    about = st.text_input(
        "Project Mission *",
        value=st.session_state.get("about", ""),
        placeholder="ERP for business management..."
    )

folders_str = st.text_area(
    "Project Folders * — one absolute path per line",
    value=st.session_state.get("folders_str", ""),
    height=90,
    placeholder="/home/user/project/frontend/\n/home/user/project/backend/"
)

# Validate folder paths instantly
has_folder_errors = False
folder_list = [p.strip() for p in folders_str.split("\n") if p.strip()]
if folders_str and not folder_list:
    st.error("Enter at least one folder path.")
    has_folder_errors = True
elif folder_list:
    for folder in folder_list:
        if not os.path.exists(folder):
            st.error(f"Path not found on disk: {folder}")
            has_folder_errors = True
        elif not os.path.isdir(folder):
            st.error(f"Path is not a directory: {folder}")
            has_folder_errors = True

project_context = st.text_area(
    "Project Structure Description",
    value=st.session_state.get("project_context", ""),
    height=90,
    placeholder="e.g. Vue 3 frontend with pages in /pages. NestJS backend with controllers in /src/modules..."
)

extra_prompt = st.text_input(
    "Extra Generation Instructions",
    value=st.session_state.get("extra_prompt", ""),
    placeholder="Focus on billing and subscription features..."
)


# ── Step 2 ────────────────────────────────────────────────────────────────────
completed_routes = get_completed_routes()

if "discovered_routes" not in st.session_state:
    st.session_state.discovered_routes = []
    loaded = _safe_load_json("routes.json", default=None)
    if loaded is not None and isinstance(loaded, list):
        st.session_state.discovered_routes = loaded

num_done = len([r for r in st.session_state.discovered_routes if r in completed_routes])
step2_done = len(st.session_state.discovered_routes) > 0

st.markdown(f"""
<div class="section-header">
    <div class="section-num {'done' if step2_done else ''}">2</div>
    <div class="section-label">Discover Routes</div>
    <div class="section-desc">{f'{len(st.session_state.discovered_routes)} found · {num_done} complete' if step2_done else 'Scan your codebase'}</div>
</div>
""", unsafe_allow_html=True)

routes_file = st.text_input(
    "Router / Navigation Config File",
    value=st.session_state.get("routes_file", ""),
    placeholder="/project/src/router/index.ts"
)

# Validate routes file instantly
has_routes_error = False
if routes_file.strip():
    if not os.path.exists(routes_file.strip()):
        st.error(f"Routes config file not found: {routes_file}")
        has_routes_error = True
    elif not os.path.isfile(routes_file.strip()):
        st.error(f"Routes config path is not a file: {routes_file}")
        has_routes_error = True

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    missing_required = not all([
        provider.strip(),
        model_name.strip(),
        api_key.strip(),
        api_base.strip(),
        project_name.strip(),
        about.strip()
    ])
    disable_fetch = has_folder_errors or has_routes_error or not folder_list or missing_required
    fetch_clicked = st.button("🔍  Discover Routes", type="primary", use_container_width=True, disabled=disable_fetch)
with c2:
    if st.button("↺  Clear Routes", use_container_width=True):
        if os.path.exists("routes.json"):
            os.remove("routes.json")
        st.session_state.discovered_routes = []
        st.rerun()
with c3:
    if st.button("🗑  Clear All", use_container_width=True):
        for f in ("faqs.json", "routes.json", "stop_flag"):
            if os.path.exists(f):
                os.remove(f)
        st.session_state.discovered_routes = []
        st.rerun()

if fetch_clicked:
    errors = []
    
    if not model_name.strip():
        errors.append("Enter a model name in the sidebar.")
    if not project_name.strip():
        errors.append("Enter a project name.")

    if errors:
        for e in errors:
            st.warning(e)
    else:
        from core.agent import discover_routes

        folder_list = [p.strip() for p in folders_str.split("\n") if p.strip()]
        full_model = f"{provider}/{model_name}" if provider else model_name

        with st.spinner("Agent is scanning your codebase for routes..."):
            routes = discover_routes(
                model=full_model,
                api_key=api_key,
                api_base=api_base,
                project_name=project_name,
                about=about,
                project_context=project_context,
                folders=folder_list,
                routes_file=routes_file,
            )
            st.session_state.discovered_routes = routes
            _atomic_write_json("routes.json", routes)

        if routes:
            st.success(f"✓  Discovered **{len(routes)} routes** across your project.")
        else:
            st.warning("No routes found. Try adjusting your folder paths or project context.")
        st.rerun()

# Route Status Grid
if st.session_state.discovered_routes:
    completed_routes = get_completed_routes()
    _render_route_grid(st.session_state.discovered_routes, completed_routes)


# ── Step 3 ────────────────────────────────────────────────────────────────────
step3_ready = len(st.session_state.discovered_routes) > 0
faq_data_check = _safe_load_json("faqs.json", default=None)
total_faqs = len(faq_data_check.get("faqs", [])) if faq_data_check else 0

st.markdown(f"""
<div class="section-header">
    <div class="section-num {'done' if total_faqs > 0 else ''}">3</div>
    <div class="section-label">Generate FAQs</div>
    <div class="section-desc">{f'{total_faqs} FAQs generated so far' if total_faqs > 0 else 'Run the AI agent'}</div>
</div>
""", unsafe_allow_html=True)

g1, g2 = st.columns([4, 1])
with g1:
    run_gen = st.button(
        "🚀  Run Agentic FAQ Generation",
        type="primary",
        use_container_width=True,
        disabled=not step3_ready or missing_required
    )
with g2:
    if st.button("🛑  Stop", use_container_width=True):
        _set_stop_flag()
        st.info("Stopping after current route finishes...")

if run_gen:
    if not model_name.strip():
        st.warning("⚠️  Please enter a model name in the sidebar.")
    elif not st.session_state.discovered_routes:
        st.warning("Please discover routes first in Step 2.")
    else:
        from core.agent import generate_faqs_for_route

        _clear_stop_flag()

        completed_routes = get_completed_routes()
        if skip_completed:
            pending_routes = [r for r in st.session_state.discovered_routes if r not in completed_routes]
        else:
            pending_routes = st.session_state.discovered_routes

        if not pending_routes:
            st.success("✓  All discovered routes are already complete!")
        else:
            full_model = f"{provider}/{model_name}" if provider else model_name
            folder_list = [p.strip() for p in folders_str.split("\n") if p.strip()]

            st.markdown("---")
            progress_col, meta_col = st.columns([3, 1])
            with meta_col:
                st.markdown(f"""
                <div style="text-align:right;padding-top:4px">
                    <div style="font-size:1.4rem;font-weight:700;color:#0f0f1a;line-height:1">{len(pending_routes)}</div>
                    <div style="font-size:0.7rem;color:#8080b0;font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:0.06em">routes pending</div>
                </div>
                """, unsafe_allow_html=True)

            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            route_grid_placeholder = st.empty()
            failed_routes = []
            current_completed = list(completed_routes)

            for idx, route in enumerate(pending_routes):
                if _is_stopped():
                    _clear_stop_flag()
                    st.warning("🛑  Generation stopped by user.")
                    break

                # Render active grid
                with route_grid_placeholder.container():
                    _render_route_grid(
                        st.session_state.discovered_routes,
                        current_completed,
                        active=route
                    )

                status_placeholder.markdown(
                    f"<div style='font-size:0.85rem;color:#5050a0;font-family:DM Mono,monospace;padding:6px 0'>"
                    f"⚡ Analyzing <strong>{os.path.basename(route)}</strong> &nbsp;·&nbsp; "
                    f"{idx+1} / {len(pending_routes)}</div>",
                    unsafe_allow_html=True
                )

                try:
                    new_data = generate_faqs_for_route(
                        model=full_model,
                        api_key=api_key,
                        api_base=api_base,
                        project_name=project_name,
                        about=about,
                        project_context=project_context,
                        folders=folder_list,
                        route_path=route,
                        extra_prompt=extra_prompt,
                        max_faqs=max_faqs_per_route,
                        max_loops=max_loops,
                    )

                    current_all = _safe_load_json("faqs.json", default={"faqs": []})
                    if "faqs" not in current_all:
                        current_all["faqs"] = []

                    if "faqs" in new_data and new_data["faqs"]:
                        for faq in new_data["faqs"]:
                            faq["source_path"] = route
                        current_all["faqs"].extend(new_data["faqs"])
                        _atomic_write_json("faqs.json", current_all)
                        current_completed.append(route)
                        logger.info(f"✅ Saved {len(new_data['faqs'])} FAQs for {os.path.basename(route)}")
                    else:
                        logger.warning(f"⚠️ No FAQs generated for {os.path.basename(route)}")

                except Exception as e:
                    logger.error(f"❌ Failed on route {route}: {e}", exc_info=True)
                    failed_routes.append((os.path.basename(route), str(e)))
                    st.warning(f"⚠️  Skipped `{os.path.basename(route)}`: {e}")

                progress_bar.progress((idx + 1) / len(pending_routes))

            status_placeholder.empty()

            # Final grid with all completed
            with route_grid_placeholder.container():
                _render_route_grid(st.session_state.discovered_routes, get_completed_routes())

            if failed_routes:
                st.warning(
                    f"Finished with {len(failed_routes)} error(s): "
                    + ", ".join(name for name, _ in failed_routes)
                )
            else:
                st.success(f"✓  Batch complete — FAQs generated for all {len(pending_routes)} routes!")

            time.sleep(0.8)
            st.rerun()


# ── Results Panel ─────────────────────────────────────────────────────────────
faq_data = _safe_load_json("faqs.json", default=None)
if faq_data is not None:
    faqs = faq_data.get("faqs", [])

    if faqs:
        st.markdown("---")

        categories = sorted(set(f.get("category", "General") for f in faqs))
        sources = sorted(set(f.get("source", "") for f in faqs if f.get("source")))

        # Stats bar
        st.markdown(f"""
        <div class="stats-bar">
            <div class="stat-cell">
                <div class="stat-val">{len(faqs)}</div>
                <div class="stat-key">Total FAQs</div>
            </div>
            <div class="stat-cell">
                <div class="stat-val">{len(categories)}</div>
                <div class="stat-key">Categories</div>
            </div>
            <div class="stat-cell">
                <div class="stat-val">{len(sources)}</div>
                <div class="stat-key">Source Files</div>
            </div>
            <div class="stat-cell">
                <div class="stat-val">{len(st.session_state.discovered_routes)}</div>
                <div class="stat-key">Routes Scanned</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Category filter
        st.markdown("**Filter by Category**")
        filter_cols = st.columns(min(len(categories) + 1, 6))
        selected_cat = st.session_state.get("faq_filter", "All")

        if filter_cols[0].button("All", key="cat_all", type="secondary" if selected_cat != "All" else "primary"):
            st.session_state.faq_filter = "All"
            st.rerun()

        for i, cat in enumerate(categories[:5]):
            short = cat[:14] + "…" if len(cat) > 15 else cat
            btn_type = "primary" if selected_cat == cat else "secondary"
            if filter_cols[i + 1].button(short, key=f"cat_{i}", type=btn_type):
                st.session_state.faq_filter = cat
                st.rerun()

        # Search
        search_q = st.text_input("🔎  Search FAQs", placeholder="Type to filter questions and answers...")

        # Filter logic
        filtered = faqs
        if selected_cat and selected_cat != "All":
            filtered = [f for f in filtered if f.get("category", "General") == selected_cat]
        if search_q.strip():
            q = search_q.lower()
            filtered = [
                f for f in filtered
                if q in f.get("question", "").lower() or q in f.get("answer", "").lower()
            ]

        st.markdown(f"<div style='font-size:0.8rem;color:#8080b0;margin:0.75rem 0 1rem;font-family:DM Mono,monospace'>Showing {len(filtered)} of {len(faqs)} FAQs</div>", unsafe_allow_html=True)

        # Render FAQ cards
        faq_html = '<div class="faq-list">'
        for i, faq in enumerate(filtered):
            cat = faq.get("category", "General")
            question = faq.get("question", "Untitled")
            answer = faq.get("answer", "No answer available.")
            source = faq.get("source", "Unknown")
            faq_html += f"""<div class="faq-item">
<div class="faq-q-row">
<div class="faq-q-icon">Q</div>
<div class="faq-q-text">{question}</div>
<div class="faq-cat-tag">{cat}</div>
</div>
<div class="faq-a-row">{answer}</div>
<div class="faq-src">📄 {source}</div>
</div>"""
        faq_html += "</div>"
        st.markdown(faq_html, unsafe_allow_html=True)

        # Downloads
        st.markdown("---")
        d1, d2 = st.columns(2)

        d1.download_button(
            "📥  Download JSON",
            data=json.dumps(faq_data, indent=2),
            file_name=f"{project_name or 'faq'}_faqs.json",
            mime="application/json",
            use_container_width=True
        )

        md_output = f"# {project_name} — FAQ\n\n"
        md_output += f"*{len(faqs)} questions across {len(categories)} categories*\n\n---\n\n"
        for cat in categories:
            cat_faqs = [f for f in faqs if f.get("category", "General") == cat]
            if cat_faqs:
                md_output += f"## {cat}\n\n"
                for f in cat_faqs:
                    md_output += f"### {f.get('question', '')}\n\n{f.get('answer', '')}\n\n*Source: {f.get('source', '')}*\n\n"

        d2.download_button(
            "📥  Download Markdown",
            data=md_output,
            file_name=f"{project_name or 'faq'}_faqs.md",
            mime="text/markdown",
            use_container_width=True
        )