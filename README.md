# 💡 AIRoutes - Agentic AI FAQ Helper

AIRoutes is a powerful, local-first **Agentic AI** tool built with Python and Streamlit. It autonomously explores a given codebase to synthesize high-quality, end-user documentation (FAQs) by making iterative decisions about which files to search and read.

It uses an advanced `litellm` backend, which means it supports nearly **any LLM provider** (OpenAI, Anthropic, Gemini, Ollama, LM Studio, vLLM, etc.) out-of-the-box.

---

## ✨ Features

- **Agentic Loop:** The AI isn't just a simple prompt-wrapper. It actively explores your project using tools (`list_dir`, `read_file`, `search_code`), determines what logic and concepts are important, and writes tailored FAQs.
- **Smart Chunking:** Built-in safeguards ensure that massive files and directories never blow out the context window.
- **Open-Source Compatibility:** Includes a custom XML / JSON `response_parser.py` designed specifically to intercept "raw" tool calls from models that struggle with native JSON function calling (like local Qwen or Llama models).
- **Externalized Tool Schema:** Drawing inspiration from advanced AI projects, the definitions for the agent's tools are stored in a standalone `tools.json` file.
- **Premium UI:** A beautiful, responsive Streamlit web interface with real-time directory validation, dynamic status updating, and direct export (Markdown/JSON) options.

---

## 🚀 Quickstart

### Prerequisites

Ensure you have [uv](https://docs.astral.sh/uv/) installed on your machine. We use `uv` for blazing-fast dependency management.

### Installation & Running

1. **Clone/Navigate** to the project directory:
   ```bash
   cd AIRoutes
   ```

2. **Run the Streamlit App:**
   ```bash
   uv run streamlit run app.py
   ```
   *`uv` will automatically read `pyproject.toml` (or `requirements.txt`), create a virtual environment, install the required packages (Streamlit, LiteLLM, Pydantic), and start the server.*

3. Open your browser to `http://localhost:8501`.

---

## 🛠️ Usage

1. **Configure the AI:** In the left sidebar, enter your LLM settings. For local, proxy-based models (like LM Studio or vLLM), enter the `Custom API Base URL` (e.g., `http://localhost:1234/v1`).
2. **Project Setup:** Provide a name and description of your project. The more descriptive the "About" section, the better the final FAQs will be.
3. **Target Folders:** Paste the **absolute paths** of the backend/frontend components you want the AI to read. Real-time validation will tell you if the path is valid!
4. **Custom Prompt (Optional):** Tell the AI if you want the FAQs directed at a specific topic, or written in a specific tone.
5. **Generate:** Hit "Run Agentic FAQ Generation". You will see a live breakdown of the agent executing searches and reading lines of code until it reaches its final answer. 
6. **Export:** Download the final result directly as JSON or Markdown.

---

## 📁 Project Structure

| File | Purpose |
| ---- | ------- |
| **`app.py`** | The main Streamlit dashboard UI. |
| **`agent.py`** | Contains the core `run_agentic_faq_generation` orchestrator that manages tool calls, API interaction, and system prompts. |
| **`tools.py`** | The Python functions the agent uses to interact with the host OS (`read_file`, `search_code`). |
| **`tools.json`** | The externalized JSON schema that defines what tools the Agent is allowed to use. |
| **`response_parser.py`** | Advanced fallback interceptor that catches raw XML/JSON output from open-source models and forces them to work like native tool calls. |

---

## 🔧 Extending the Tools

Want to give the Agent a new capability?
1. Open `tools.json` and add the JSON schema for your new tool.
2. Open `tools.py` and write the Python function to execute that capability.
3. Add the mapping inside the `execute_tool` function in `tools.py`.
