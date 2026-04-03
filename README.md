# 💡 AI-Faqs: Agentic FAQ Generator

**AI-Faqs** is a high-performance, agentic AI tool designed to autonomously explore complex codebases and generate high-quality, end-user-focused documentation (FAQs). By tracing frontend UI components to backend logic, it uncovers business rules that are often invisible to traditional documentation tools.

---

## 🚀 Key Features

- **🧠 Agentic Exploration**: Actively explores projects using specialized tools (`list_dir`, `read_file`, `search_code`) to understand feature flows.
- **📂 Project-Centric Persistence**: Create named projects to save configurations, discovered routes, and generated FAQs. Sessions are restored automatically.
- **⏯️ Stop & Resume**: Pause generation at any time with the "Stop" flag and resume exactly where you left off.
- **🎨 Premium UI**: A modern, responsive Streamlit dashboard featuring custom typography (DM Sans), linear gradients, and real-time progress tracking.
- **🔗 Universal Model Support**: Powered by `litellm`, supporting OpenAI, Anthropic, Gemini, Ollama, LM Studio, and more.
- **🛡️ Sandboxed Execution**: All file operations are restricted to the provided project directories for maximum security.

---

## 🛠️ Project Structure

| Component | Description |
| :--- | :--- |
| `app.py` | Premium Streamlit dashboard & session management logic. |
| `core/agent.py` | The "brain" — handles the agentic loop, discovery, and FAQ orchestration. |
| `core/response_parser.py` | Advanced XML/JSON parser for models without native tool-calling. |
| `tools/executor.py` | Secure implementation of filesystem and search tools. |
| `projects/` | Persistent storage for project-specific configurations and results. |

---

## 🚦 Quick Start

### 1. Prerequisites
Ensure you have [uv](https://docs.astral.sh/uv/) installed for seamless dependency management.

### 2. Launch the Application
```bash
uv run streamlit run app.py
```

Access the dashboard at `http://localhost:8501`.

---

## 📖 Usage Guide

1. **Configure LLM**: Set your provider (e.g., `openai`, `gemini`), model name, and API details in the sidebar.
2. **Setup Project**:
   - Provide a **Project Name** (this creates a persistent session).
   - Define the **Project Mission** (helps the AI understand the business context).
   - List the **Absolute Paths** of folders to explore (e.g., `/home/user/my-erp/frontend`).
3. **Route Discovery**:
   - (Optional) Provide a `routes.json` or navigation file to jumpstart discovery.
   - Click **Run Route Discovery** to let the agent find all feature pages.
4. **FAQ Generation**:
   - Review discovered routes in the interactive grid.
   - Click **Run Agentic FAQ Generation** to start the analysis.
   - **Stop/Resume**: Use the "Stop" button to pause; the system will skip completed routes when you restart.
5. **Export**: Download your final documentation as **JSON** or **Markdown**.

---

## ⚙️ Advanced Settings

| Setting | Recommendation | Description |
| :--- | :--- | :--- |
| **Max FAQs per route** | 3-5 | Controls the depth of documentation for each feature. |
| **Agent Max Loops** | 12-18 | Limits reasoning steps to prevent infinite loops/cost overruns. |
| **Skip Completed** | Enabeld | Skips routes that already have FAQs in the project folder. |

---

## 📝 Performance Tips

- **Model Selection**: For best results in code analysis, use high-reasoning models like `gpt-4o`, `claude-3-5-sonnet`, or `gemini-1.5-pro`.
- **Context Description**: Providing a brief "Project Structure Description" in Step 1 significantly reduces discovery time.
- **Route Manifests**: If your project has a central `router.ts` or `menu.json`, providing its path in Step 2 ensures 100% discovery accuracy.