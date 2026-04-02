import streamlit as st
import json
import time
import os
import tempfile
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger("AI-Faqs")

# ── Page Config ──
st.set_page_config(
    page_title="AI-Faqs · Agentic AI",
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
    background: #0a0a0f !important;
    border-right: 1px solid #1e1e2e !important;
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
.route-grid-wrapper {
    margin: 1rem 0;
}
.route-grid-wrapper .stButton > button {
    border-radius: 8px !important;
    font-size: 0.92rem !important;
    font-family: 'DM Mono', monospace !important;
    padding: 0.55rem 0.85rem !important;
    transition: all 0.15s ease !important;
    border: 1px solid !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
.route-grid-wrapper .stButton > button[kind="primary"] {
    background: #f0faf5 !important;
    border-color: #a8ddc0 !important;
    color: #1a6040 !important;
}
.route-grid-wrapper .stButton > button[kind="primary"]:hover {
    background: #e0f5f0 !important;
    border-color: #88ccaa !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 8px rgba(0,0,0,0.08) !important;
}
.route-grid-wrapper .stButton > button[kind="secondary"]:disabled {
    background: #f8f8fd !important;
    border-color: #dcdcee !important;
    color: #6060a0 !important;
    opacity: 0.7 !important;
    cursor: not-allowed !important;
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
def _get_project_slug(project_name: str) -> str:
    """Generate a safe slug from project name for file naming."""
    slug = project_name.lower().strip()
    slug = "".join(c if c.isalnum() or c == "-" else "-" for c in slug)
    slug = "-".join(filter(None, slug.split("-")))
    return slug


def _get_project_files_dir(project_name: str) -> str:
    """Get/create directory for project-specific files."""
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects")
    project_dir = os.path.join(base_dir, project_name)
    os.makedirs(project_dir, exist_ok=True)
    return project_dir


def _get_project_file_paths(project_name: str):
    """Get file paths for a specific project (one session per project)."""
    if not project_name:
        # Fallback to old behavior if no project name
        return "routes.json", "faqs.json", None
    
    project_dir = _get_project_files_dir(project_name)
    slug = _get_project_slug(project_name)
    routes_file = os.path.join(project_dir, f"{slug}_routes.json")
    faqs_file = os.path.join(project_dir, f"{slug}_faqs.json")
    config_file = os.path.join(project_dir, f"{slug}_config.json")
    
    return routes_file, faqs_file, config_file


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


def get_completed_routes(faqs_file: str = None):
    if faqs_file is None:
        faqs_file = "faqs.json"
    data = _safe_load_json(faqs_file, default={"faqs": []})
    return list(
        set(
            faq.get("source_path")
            for faq in data.get("faqs", [])
            if faq.get("source_path")
        )
    )


def _save_project_config(config_file: str, config_data: dict) -> None:
    """Save project configuration to file."""
    if config_file:
        _atomic_write_json(config_file, config_data)


def _load_project_config(config_file: str, default=None) -> dict:
    """Load project configuration from file."""
    if default is None:
        default = {}
    if not config_file or not os.path.exists(config_file):
        return default
    return _safe_load_json(config_file, default)


def _load_existing_projects() -> list:
    """Load all existing projects (one session per project)."""
    projects_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects")
    if not os.path.exists(projects_dir):
        return []
    
    projects = []
    for project_name in sorted(os.listdir(projects_dir)):
        project_dir = os.path.join(projects_dir, project_name)
        if os.path.isdir(project_dir):
            # Count JSON files in project directory
            json_files = [f for f in os.listdir(project_dir) if f.endswith(".json")]
            has_routes = any("routes" in f for f in json_files)
            has_faqs = any("faqs" in f for f in json_files)
            has_config = any("config" in f for f in json_files)
            
            projects.append({
                "name": project_name,
                "has_routes": has_routes,
                "has_faqs": has_faqs,
                "has_config": has_config,
                "file_count": len(json_files),
            })
    return projects


def _render_route_grid(routes, completed, faqs_file_path):
    """Render route grid with clickable buttons to toggle completion status."""
    # Wrap in styled container
    st.markdown('<div class="route-grid-wrapper">', unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, route in enumerate(routes):
        name = os.path.basename(route)
        is_done = route in completed
        
        with cols[i % 3]:
            if is_done:
                # Green button = completed, click to mark incomplete
                if st.button(f"✅ {name}", key=f"route_{i}", use_container_width=True, help="Click to mark incomplete (will regenerate)"):
                    # Remove from FAQs so it regenerates
                    faq_data = _safe_load_json(faqs_file_path, {"faqs": []})
                    faq_data["faqs"] = [f for f in faq_data["faqs"] if f.get("source_path") != route]
                    _atomic_write_json(faqs_file_path, faq_data)
                    if "completed_routes_on_load" in st.session_state:
                        st.session_state.completed_routes_on_load = [
                            r for r in st.session_state.completed_routes_on_load if r != route
                        ]
                    st.toast(f"🔄 {name} marked for regeneration")
                    st.rerun()
            else:
                # Grey disabled button = pending
                st.button(f"⬜ {name}", key=f"route_{i}", use_container_width=True, disabled=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 0.5rem">
        <div style="font-family:'DM Mono',monospace;font-size:0.75rem;letter-spacing:0.15em;color:#444466;text-transform:uppercase;margin-bottom:8px">AI-Faqs</div>
        <div style="font-size:1.25rem;font-weight:600;color:#e0e0f5;letter-spacing:-0.01em">Agentic AI Engine</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Project Management
    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.75rem;letter-spacing:0.12em;color:#444466;text-transform:uppercase;margin-bottom:12px">Project</div>""", unsafe_allow_html=True)
    
    # Load existing projects
    existing_projects = _load_existing_projects()
    project_names = [p["name"] for p in existing_projects]
    
    # Project selection (one session per project)
    selected_project = st.selectbox(
        "Load Existing Project",
        options=[""] + project_names,
        format_func=lambda x: f"{x}" if x else "New Project",
        index=0
    )
    
    # Handle project selection change - auto-clear fields immediately
    if selected_project:
        # Clear all input fields when a project is selected
        if "folders_str" in st.session_state:
            del st.session_state.folders_str
        if "about" in st.session_state:
            del st.session_state.about
        if "project_context" in st.session_state:
            del st.session_state.project_context
        if "extra_prompt" in st.session_state:
            del st.session_state.extra_prompt
        if "routes_file" in st.session_state:
            del st.session_state.routes_file
        if "project_name" in st.session_state:
            del st.session_state.project_name
        
        # Load the project's files
        project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects", selected_project)
        if os.path.exists(project_dir):
            # Find routes and faqs files
            routes_file = None
            faqs_file = None
            for filename in os.listdir(project_dir):
                filepath = os.path.join(project_dir, filename)
                if filename.endswith(".json"):
                    if "routes" in filename:
                        routes_file = filepath
                    elif "faqs" in filename:
                        faqs_file = filepath
            
            # Load both routes and FAQs to show progress UI
            loaded_routes_data = None
            loaded_faqs_data = None
            
            # Load routes file
            if routes_file and os.path.exists(routes_file):
                loaded_routes_data = _safe_load_json(routes_file, [])
            
            # Load FAQs file
            if faqs_file and os.path.exists(faqs_file):
                loaded_faqs_data = _safe_load_json(faqs_file, {"faqs": []})
            
            # Combine routes from both sources
            all_routes = []
            completed_routes_set = set()
            
            # Add routes from routes file
            if loaded_routes_data and isinstance(loaded_routes_data, list):
                for r in loaded_routes_data:
                    if isinstance(r, str):
                        all_routes.append(r)
                    elif isinstance(r, dict) and "path" in r:
                        all_routes.append(r["path"])
                    elif isinstance(r, dict) and "file" in r:
                        all_routes.append(r["file"])
                    elif isinstance(r, dict) and "filepath" in r:
                        all_routes.append(r["filepath"])
            
            # Extract completed routes from FAQs
            if loaded_faqs_data and loaded_faqs_data.get("faqs"):
                for faq in loaded_faqs_data.get("faqs", []):
                    source_path = faq.get("source_path")
                    if source_path and source_path not in completed_routes_set:
                        completed_routes_set.add(source_path)
                        # Add to all_routes if not already there
                        if source_path not in all_routes:
                            all_routes.append(source_path)
            
            if all_routes:
                st.session_state.discovered_routes = all_routes
                st.session_state.completed_routes_on_load = list(completed_routes_set)
                
                # Show status message
                total = len(all_routes)
                completed = len(completed_routes_set)
                if completed > 0:
                    st.success(f"✓ Loaded {selected_project}: {completed}/{total} routes completed")
                else:
                    st.success(f"✓ Loaded routes from {selected_project}")
            
            # Load project configuration (folders, mission, structure, etc.)
            config_filepath = os.path.join(project_dir, f"{_get_project_slug(selected_project)}_config.json")
            loaded_config = _load_project_config(config_filepath)
            
            if loaded_config:
                # Restore all saved fields to session state
                if "folders_str" in loaded_config:
                    st.session_state.folders_str = loaded_config["folders_str"]
                if "about" in loaded_config:
                    st.session_state.about = loaded_config["about"]
                if "project_context" in loaded_config:
                    st.session_state.project_context = loaded_config["project_context"]
                if "extra_prompt" in loaded_config:
                    st.session_state.extra_prompt = loaded_config["extra_prompt"]
                if "routes_file" in loaded_config:
                    st.session_state.routes_file = loaded_config["routes_file"]
        
        # Pre-fill project name in main form
        if "project_name" not in st.session_state or not st.session_state.project_name:
            st.session_state.project_name = selected_project
    
    elif selected_project == "":
        # User switched to "New Project" - clear session state
        if "discovered_routes" in st.session_state:
            del st.session_state.discovered_routes
        if "completed_routes_on_load" in st.session_state:
            del st.session_state.completed_routes_on_load
        if "folders_str" in st.session_state:
            del st.session_state.folders_str
        if "about" in st.session_state:
            del st.session_state.about
        if "project_context" in st.session_state:
            del st.session_state.project_context
        if "extra_prompt" in st.session_state:
            del st.session_state.extra_prompt
        if "routes_file" in st.session_state:
            del st.session_state.routes_file
        if "project_name" in st.session_state:
            del st.session_state.project_name
    
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
    <div class="hero-eyebrow">Agentic Documentation Engine</div>
    <div class="hero-title">AI-<span>Faqs</span></div>
    <div class="hero-sub">Autonomously explore your codebase and generate context-aware, user-friendly documentation — powered by Agentic AI.</div>
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
# Get project-specific file paths
routes_file_path, faqs_file_path, config_file_path = _get_project_file_paths(project_name)

# Determine completed routes - use loaded session data if available, otherwise check FAQs file
_cr = st.session_state.get("completed_routes_on_load")
completed_routes = list(_cr if _cr is not None else get_completed_routes(faqs_file_path))

if "discovered_routes" not in st.session_state:
    st.session_state.discovered_routes = []
    # Try to load from project-specific routes file first
    loaded = _safe_load_json(routes_file_path, default=None)
    if loaded is not None and isinstance(loaded, list):
        st.session_state.discovered_routes = loaded
    # Fallback to old location if project file doesn't exist
    elif project_name:
        old_loaded = _safe_load_json("routes.json", default=None)
        if old_loaded is not None and isinstance(old_loaded, list):
            st.session_state.discovered_routes = old_loaded

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
    "Router / Navigation Config File (Optional)",
    value=st.session_state.get("routes_file", ""),
    placeholder="/project/src/router/index.ts",
    help="Leave empty for automatic detection. If provided, AI will use this file first."
)

# Show info if routes file is provided
if routes_file.strip():
    if os.path.exists(routes_file.strip()):
        st.success(f"✓ Found: {os.path.basename(routes_file.strip())} ({os.path.getsize(routes_file.strip()):,} bytes)")
    else:
        st.error(f"✗ File not found: {routes_file}")

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
        if os.path.exists(routes_file_path):
            os.remove(routes_file_path)
        st.session_state.discovered_routes = []
        st.rerun()
with c3:
    if st.button("🗑  Clear All", use_container_width=True):
        # Clear project-specific files
        if os.path.exists(routes_file_path):
            os.remove(routes_file_path)
        if os.path.exists(faqs_file_path):
            os.remove(faqs_file_path)
        # Also clear old files if they exist
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
            # Log what we're passing to the agent
            logger.info(f"🔍 Discover routes called with routes_file: {routes_file}")
            if routes_file and routes_file.strip():
                if os.path.exists(routes_file.strip()):
                    logger.info(f"✓ Routes file exists: {routes_file.strip()}")
                else:
                    logger.warning(f"⚠️ Routes file does NOT exist: {routes_file.strip()}")
            else:
                logger.info("ℹ️ No routes file provided - AI will search automatically")
            
            routes = discover_routes(
                model=full_model,
                api_key=api_key,
                api_base=api_base,
                project_name=project_name,
                about=about,
                project_context=project_context,
                folders=folder_list,
                routes_file=routes_file.strip() if routes_file else None,
            )
            
            # Ensure routes is a list of strings (file paths), not dicts
            if isinstance(routes, list):
                cleaned_routes = []
                for r in routes:
                    if isinstance(r, dict):
                        # Extract file path from dict if needed
                        if "path" in r:
                            cleaned_routes.append(r["path"])
                        elif "file" in r:
                            cleaned_routes.append(r["file"])
                        elif "filepath" in r:
                            cleaned_routes.append(r["filepath"])
                        else:
                            logger.warning(f"Skipping unknown dict format: {r}")
                    elif isinstance(r, str):
                        cleaned_routes.append(r)
                    else:
                        logger.warning(f"Skipping unknown type: {type(r)} - {r}")
                routes = cleaned_routes
            
            st.session_state.discovered_routes = routes
            _atomic_write_json(routes_file_path, routes)
            
            # Save project configuration for future sessions
            config_data = {
                "folders_str": folders_str,
                "about": about,
                "project_context": project_context,
                "extra_prompt": extra_prompt,
                "routes_file": routes_file.strip() if routes_file else "",
                "saved_at": datetime.now().isoformat(),
            }
            _save_project_config(config_file_path, config_data)

        if routes:
            st.success(f"✓  Discovered **{len(routes)} routes** across your project. Saved to `{os.path.basename(routes_file_path)}`")
        else:
            st.warning("No routes found. Try adjusting your folder paths or project context.")
        st.rerun()

# Route Status Grid
if st.session_state.discovered_routes:
    _cr = st.session_state.get("completed_routes_on_load")
    completed_routes_display = list(_cr if _cr is not None else get_completed_routes(faqs_file_path))
    _render_route_grid(st.session_state.discovered_routes, completed_routes_display, faqs_file_path)


# ── Step 3 ────────────────────────────────────────────────────────────────────
step3_ready = len(st.session_state.discovered_routes) > 0
faq_data_check = _safe_load_json(faqs_file_path, default=None)
# Fallback to old location if project file doesn't exist
if not faq_data_check and project_name:
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

        # Determine completed routes - use loaded session data or check FAQs file
        _cr = st.session_state.get("completed_routes_on_load")
        completed_routes = list(_cr if _cr is not None else get_completed_routes(faqs_file_path))
        
        # Always skip completed routes when generating (resume from where we left off)
        pending_routes = [r for r in st.session_state.discovered_routes if r not in completed_routes]

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
            failed_routes = []
            current_completed = list(completed_routes)
            
            # Update session state as we complete routes (for real-time UI updates)
            if "completed_routes_on_load" not in st.session_state:
                st.session_state.completed_routes_on_load = []

            for idx, route in enumerate(pending_routes):
                if _is_stopped():
                    _clear_stop_flag()
                    st.warning("🛑  Generation stopped by user.")
                    break

                # Show simple status indicator (no duplicate grid)
                status_placeholder.markdown(
                    f"<div style='font-size:0.85rem;color:#5050a0;font-family:DM Mono,monospace;padding:6px 0'>"
                    f"⚡ Processing <strong>{os.path.basename(route)}</strong> &nbsp;·&nbsp; "
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

                    current_all = _safe_load_json(faqs_file_path, default={"faqs": []})
                    if "faqs" not in current_all:
                        current_all["faqs"] = []

                    if "faqs" in new_data and new_data["faqs"]:
                        for faq in new_data["faqs"]:
                            faq["source_path"] = route
                        current_all["faqs"].extend(new_data["faqs"])
                        _atomic_write_json(faqs_file_path, current_all)
                        current_completed.append(route)
                        
                        # Update session state for real-time UI refresh
                        if route not in st.session_state.completed_routes_on_load:
                            st.session_state.completed_routes_on_load.append(route)
                        
                        logger.info(f"✅ Saved {len(new_data['faqs'])} FAQs for {os.path.basename(route)} to `{os.path.basename(faqs_file_path)}`")
                    else:
                        logger.warning(f"⚠️ No FAQs generated for {os.path.basename(route)}")

                except Exception as e:
                    logger.error(f"❌ Failed on route {route}: {e}", exc_info=True)
                    failed_routes.append((os.path.basename(route), str(e)))
                    st.warning(f"⚠️  Skipped `{os.path.basename(route)}`: {e}")

                progress_bar.progress((idx + 1) / len(pending_routes))

            status_placeholder.empty()

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
faq_data = _safe_load_json(faqs_file_path, default=None)
# Fallback to old location if project file doesn't exist
if not faq_data and project_name:
    faq_data = _safe_load_json("faqs.json", default=None)

if faq_data is not None:
    faqs = faq_data.get("faqs", [])

    if faqs:
        st.markdown("---")

        categories = sorted(set(f.get("category", "General") for f in faqs))
        sources = sorted(set(f.get("source", "") for f in faqs if f.get("source")))

        # Stats bar with file info
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
        <div style="font-size:0.75rem;color:#8080b0;font-family:'DM Mono',monospace;text-align:center;padding:0.5rem">
            📁 Data from: {os.path.basename(faqs_file_path)}
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

        # Use project name in filename
        download_filename_base = f"{_get_project_slug(project_name) if project_name else 'faq'}"
        
        d1.download_button(
            "📥  Download JSON",
            data=json.dumps(faq_data, indent=2),
            file_name=f"{download_filename_base}_faqs.json",
            mime="application/json",
            use_container_width=True
        )

        md_output = f"# {project_name or 'FAQ'} — Documentation\n\n"
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
            file_name=f"{download_filename_base}_faqs.md",
            mime="text/markdown",
            use_container_width=True
        )