# Power BI Modeling MCP + Ollama Integration Guide

This guide explains how to install the official **Power BI Modeling MCP** (Model Context Protocol) server on your device and integrate it with local **Ollama** models.

---

## 1. Prerequisites

### A. Install and Run Ollama
1. Download Ollama from the official website: [ollama.com](https://ollama.com).
2. Install Ollama and run it. You should see the Ollama icon in your system tray, confirming the daemon is running.
3. Open a terminal (PowerShell or Command Prompt) and pull a model that supports **tool calling** (this is critical for MCP servers). We recommend **Qwen 2.5 Coder** (7B) or **Llama 3.1** (8B):
   ```powershell
   ollama pull qwen2.5-coder:7b
   ```

### B. Install Node.js
The Power BI MCP server is distributed via npm. Make sure you have Node.js installed:
- Download from [nodejs.org](https://nodejs.org/).
- Verify installation in your terminal:
  ```powershell
  node -v
  npm -v
  ```

---

## 2. Integration Methods

We support two integration pathways: **VS Code + Cline** (for a GUI chatbot in your editor) or a **Custom Python CLI Client** (for terminal-based interactions).

### Option A: VS Code + Cline Extension (Recommended GUI)

**Cline** is a popular VS Code extension that supports local Ollama models and connects directly to custom MCP servers.

1. Open **VS Code** in this workspace folder.
2. Go to the Extensions Marketplace (`Ctrl+Shift+X`), search for **Cline**, and install it.
3. Open the Cline sidebar pane and click the **Settings** (gear) icon.
4. Configure Cline's LLM Provider:
   - **Provider**: Select **Ollama**.
   - **Ollama Base URL**: `http://localhost:11434`
   - **Model ID**: Select/type `qwen2.5-coder:7b` (or your pulled model).
5. Add the Power BI MCP Server to Cline:
   - Click **"Edit MCP Settings"** in Cline settings (this opens the `cline_mcp_settings.json` file).
   - Add the following configuration under the `mcpServers` block:
     ```json
     {
       "mcpServers": {
         "powerbi-modeling-mcp": {
           "command": "npx",
           "args": [
             "-y",
             "@microsoft/powerbi-modeling-mcp@latest",
             "--start"
           ]
         }
       }
     }
     ```
   - Save the file. Cline will automatically start the Power BI Modeling MCP server. You will see a green dot next to the server name, indicating it has loaded the tools successfully.
6. **Start Chatting**: You can now ask Cline in the chat:
   - *"What tables are in my semantic model?"*
   - *"Analyze the relationships in this Power BI project."*
   - *"Generate a DAX measure for total sales."*

---

### Option B: Standalone Python Client CLI Script

If you prefer to run a custom python script in your terminal that interacts with the Power BI Modeling MCP server and Ollama:

1. **Set up a Virtual Environment and Install Dependencies**:
   Open a terminal in the root of your project directory and run:
   ```powershell
   # Create a virtual environment
   python -m venv .venv

   # Activate the virtual environment
   .venv\Scripts\Activate.ps1

   # Install the required packages
   pip install mcp ollama
   ```

2. **Run the Script**:
   ```powershell
   python scripts/ollama_mcp_client.py
   ```

3. **How to interact**:
   The script starts the Power BI Modeling MCP server in the background and connects to Ollama. Once ready, it enters an interactive prompt where you can chat with the local model, and the model will automatically make tool calls to inspect or modify your local Power BI project definitions!

---

## 3. Important Safety Notes

> [!CAUTION]
> The Power BI Modeling MCP server interacts directly with the **TMDL (Tabular Model Definition Language)** files in your workspace (located under `S&OP_Dashboard.SemanticModel`). 
> - **Always commit your code to Git** before letting an AI model run write operations on your Power BI project files, so you can revert any unintended changes.
