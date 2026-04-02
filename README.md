# 💡 AIRoutes - Agentic AI FAQ Helper

AIRoutes is a powerful, local-first **Agentic AI** tool built with Python and Streamlit. It autonomously explores a given codebase to synthesize high-quality, end-user documentation (FAQs) by making iterative decisions about which files to search and read.

It uses an advanced `litellm` backend, which means it supports nearly **any LLM provider** (OpenAI, Anthropic, Gemini, Ollama, LM Studio, vLLM, etc.) out-of-the-box.

---

## ✨ Features

- **Agentic Loop:** The AI isn't just a simple prompt-wrapper. It actively explores your project using tools (`list_dir`, `read_file`, `search_code`), determines what logic and concepts are important, and writes tailored FAQs.
- **Smart Chunking:** Built-in safeguards ensure that massive files and directories never blow out the context window.
- **Context Window Management:** Automatic trimming of old tool results to prevent context overflow during long agentic runs.
- **Open-Source Compatibility:** Includes a custom XML / JSON `response_parser.py` designed specifically to intercept "raw" tool calls from models that struggle with native JSON function calling (like local Qwen or Llama models).
- **Path Sandboxing:** File system access is restricted to your project directory for security.
- **Externalized Tool Schema:** The definitions for the agent's tools are stored in a standalone `tools.json` file.
- **Premium UI:** A beautiful, responsive Streamlit web interface with real-time progress tracking, stop/resume capability, and direct export (Markdown/JSON) options.

---

## 🚀 Quickstart

### Prerequisites

Ensure you have [uv](https://docs.astral.sh/uv/) installed on your machine. We use `uv` for blazing-fast dependency management.

### Installation & Running

1. **Run the Streamlit App:**
   ```bash
   uv run streamlit run app.py
   ```
   *`uv` will automatically read `pyproject.toml`, create a virtual environment, install the required packages (Streamlit, LiteLLM, Pydantic), and start the server.*

2. Open your browser to `http://localhost:8501`.

---

## 🛠️ Usage

1. **Configure the AI:** In the left sidebar, enter your LLM settings. For local, proxy-based models (like LM Studio or vLLM), enter the `Custom API Base URL` (e.g., `http://localhost:1234/v1`).
2. **Project Setup:** Provide a name and mission for your project.
3. **Add Folders:** Paste the **absolute paths** of folders you want the AI to explore — one per line. Add as many as you need (frontend, backend, shared libs, etc.).
4. **Explain Your Structure:** Describe how your codebase is organized so the AI knows what to look for.
5. **Custom Prompt (Optional):** Tell the AI any additional instructions for tone or focus.
6. **Fetch Routes:** The AI will explore your folders and discover feature-level files.
7. **Generate:** Hit "Run Agentic FAQ Generation". The AI traces each route through the codebase, reads code, and produces user-facing FAQs.
8. **Export:** Download the final result directly as JSON or Markdown.

---

## 📁 Project Structure

| File | Purpose |
| ---- | ------- |
| **`app.py`** | The main Streamlit dashboard UI. |
| **`core/agent.py`** | Contains the agentic loop, route discovery, and FAQ generation orchestrator. |
| **`core/response_parser.py`** | Fallback interceptor that catches raw XML/JSON tool calls from open-source models. |
| **`tools/executor.py`** | Sandboxed tool implementations (`read_file`, `search_code`, `list_dir`). |
| **`tools/tools.json`** | Externalized JSON schema defining the agent's available tools. |
| **`ui/styles.py`** | Extracted styling logic for the UI. |

---