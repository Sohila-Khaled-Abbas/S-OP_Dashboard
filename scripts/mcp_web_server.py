#!/usr/bin/env python3
"""
Power BI MCP Web Interface — Local Server
==========================================
A FastAPI web server that bridges the Power BI Modeling MCP server
to a browser-based dashboard. Provides REST endpoints for model
exploration, DAX queries, measure management, and Ollama AI chat.

Usage:
    python scripts/mcp_web_server.py

Then open http://localhost:8765 in your browser.
"""

import asyncio
import json
import os
import shutil
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# MCP client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
WEB_DIR = Path(__file__).parent / "web"
HOST = "127.0.0.1"
PORT = 8765
OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5-coder:7b"

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
class AppState:
    """Holds the MCP session, tools, and connection info."""
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.tools: list = []
        self.ollama_tools: list = []
        self.connected: bool = False
        self.connection_name: Optional[str] = None
        self.model_name: Optional[str] = None
        self._read_stream = None
        self._write_stream = None
        self._client_cm = None
        self._session_cm = None

state = AppState()

# ---------------------------------------------------------------------------
# MCP server parameters
# ---------------------------------------------------------------------------
def _get_npx_command() -> str:
    if sys.platform == "win32":
        npx = shutil.which("npx")
        if npx and npx.lower().endswith(".cmd"):
            return npx
        return "npx.cmd"
    return "npx"

server_params = StdioServerParameters(
    command=_get_npx_command(),
    args=["-y", "@microsoft/powerbi-modeling-mcp@latest", "--start"],
    env={**os.environ.copy()},
)

# ---------------------------------------------------------------------------
# MCP lifecycle helpers
# ---------------------------------------------------------------------------
async def start_mcp_session():
    """Start the MCP subprocess and create a client session."""
    if state.session is not None:
        return  # already running

    state._client_cm = stdio_client(server_params)
    state._read_stream, state._write_stream = await state._client_cm.__aenter__()

    state._session_cm = ClientSession(state._read_stream, state._write_stream)
    state.session = await state._session_cm.__aenter__()

    await state.session.initialize()

    # Discover tools
    result = await state.session.list_tools()
    state.tools = result.tools if result.tools else []
    state.ollama_tools = [_mcp_to_ollama(t) for t in state.tools]
    print(f"[MCP] Session started — {len(state.tools)} tools discovered")


async def stop_mcp_session():
    """Gracefully shut down the MCP session."""
    try:
        if state._session_cm:
            await state._session_cm.__aexit__(None, None, None)
        if state._client_cm:
            await state._client_cm.__aexit__(None, None, None)
    except Exception:
        pass
    state.session = None
    state.tools = []
    state.ollama_tools = []
    state.connected = False
    state.connection_name = None
    print("[MCP] Session stopped")


async def call_mcp(tool_name: str, arguments: dict) -> dict:
    """Execute an MCP tool and return parsed JSON result."""
    if state.session is None:
        raise HTTPException(503, "MCP session not started")
    result = await state.session.call_tool(tool_name, arguments)
    texts = []
    for c in result.content:
        if hasattr(c, "text"):
            texts.append(c.text)
        elif isinstance(c, dict) and "text" in c:
            texts.append(c["text"])
        else:
            texts.append(str(c))
    combined = "\n".join(texts)
    try:
        return json.loads(combined)
    except json.JSONDecodeError:
        return {"raw": combined}


def _mcp_to_ollama(tool) -> dict:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_mcp_session()
    yield
    await stop_mcp_session()

app = FastAPI(title="Power BI MCP Dashboard", lifespan=lifespan)

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class ConnectRequest(BaseModel):
    connectionString: Optional[str] = None
    port: Optional[int] = None

class DAXRequest(BaseModel):
    query: str
    maxRows: Optional[int] = 1000

class MeasureRequest(BaseModel):
    name: str
    expression: str
    tableName: Optional[str] = None
    description: Optional[str] = None
    formatString: Optional[str] = None
    displayFolder: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    history: Optional[list] = []

# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.get("/api/status")
async def get_status():
    return {
        "mcp_running": state.session is not None,
        "connected": state.connected,
        "connection_name": state.connection_name,
        "tools_count": len(state.tools),
        "tools": [t.name for t in state.tools],
    }


@app.get("/api/instances")
async def list_instances():
    result = await call_mcp("connection_operations", {
        "request": {"operation": "ListLocalInstances"}
    })
    return result


@app.post("/api/connect")
async def connect(req: ConnectRequest):
    if req.connectionString:
        conn_str = req.connectionString
    elif req.port:
        conn_str = f"data source=localhost:{req.port};Application Name=MCP-WebUI"
    else:
        # Auto-detect: find first local instance
        instances = await call_mcp("connection_operations", {
            "request": {"operation": "ListLocalInstances"}
        })
        data = instances.get("data", [])
        if not data:
            raise HTTPException(404, "No local Power BI Desktop instances found")
        conn_str = data[0].get("connectionString", "")

    result = await call_mcp("connection_operations", {
        "request": {"operation": "Connect", "connectionString": conn_str}
    })
    state.connected = True
    state.connection_name = result.get("data", "")
    return result


@app.post("/api/disconnect")
async def disconnect():
    result = await call_mcp("connection_operations", {
        "request": {"operation": "Disconnect"}
    })
    state.connected = False
    state.connection_name = None
    return result


@app.post("/api/optimize/clear-cache")
async def clear_cache():
    return await call_mcp("dax_query_operations", {
        "request": {"operation": "ClearCache"}
    })


@app.post("/api/optimize/refresh-all")
async def refresh_all():
    # Retrieve all tables
    tables_resp = await call_mcp("table_operations", {
        "request": {"operation": "List"}
    })
    tables = tables_resp.get("data", [])
    results = []
    for t in tables:
        name = t.get("name")
        if name and name != "KeyMeasures" and not t.get("isHidden", False):
            try:
                await call_mcp("table_operations", {
                    "request": {
                        "operation": "RefreshWithXMLA",
                        "references": [{"name": name}]
                    }
                })
                results.append({"table": name, "status": "Success"})
            except Exception as e:
                results.append({"table": name, "status": "Error", "message": str(e)})
    return {"results": results}


@app.get("/api/model")
async def get_model():
    return await call_mcp("model_operations", {
        "request": {"operation": "Get"}
    })


@app.get("/api/tables")
async def list_tables():
    return await call_mcp("column_operations", {
        "request": {"operation": "List"}
    })


@app.get("/api/tables/{table_name}/schema")
async def get_table_schema(table_name: str):
    return await call_mcp("table_operations", {
        "request": {
            "operation": "GetSchema",
            "references": [{"name": table_name}]
        }
    })


@app.get("/api/measures")
async def list_measures():
    return await call_mcp("measure_operations", {
        "request": {"operation": "List"}
    })


@app.post("/api/measure")
async def create_or_update_measure(req: MeasureRequest):
    definition: Dict[str, Any] = {
        "name": req.name,
        "expression": req.expression,
    }
    if req.tableName:
        definition["tableName"] = req.tableName
    if req.description:
        definition["description"] = req.description
    if req.formatString:
        definition["formatString"] = req.formatString
    if req.displayFolder:
        definition["displayFolder"] = req.displayFolder

    # Try update first, fall back to create
    try:
        result = await call_mcp("measure_operations", {
            "request": {
                "operation": "Update",
                "definitions": [definition],
            }
        })
        return result
    except Exception:
        result = await call_mcp("measure_operations", {
            "request": {
                "operation": "Create",
                "definitions": [definition],
            }
        })
        return result


@app.get("/api/relationships")
async def list_relationships():
    return await call_mcp("relationship_operations", {
        "request": {"operation": "List"}
    })


@app.post("/api/dax")
async def execute_dax(req: DAXRequest):
    return await call_mcp("dax_query_operations", {
        "request": {
            "operation": "Execute",
            "query": req.query,
            "maxRows": req.maxRows,
        }
    })


@app.post("/api/chat")
async def chat_with_ollama(req: ChatRequest):
    """Send a message to Ollama with MCP tools for Power BI interaction."""
    try:
        import ollama as ollama_lib
    except ImportError:
        raise HTTPException(500, "ollama package not installed")

    client = ollama_lib.AsyncClient(host=OLLAMA_HOST)

    # Check available models
    try:
        models_resp = await client.list()
        available = [m.get("model", m.get("name", "")) for m in models_resp.get("models", [])]
        model = DEFAULT_MODEL
        if model not in available and available:
            model = available[0]
    except Exception as e:
        raise HTTPException(503, f"Cannot reach Ollama: {e}")

    # Build messages
    system_msg = (
        "You are a Power BI semantic model assistant. You have access to MCP tools "
        "that can query and modify the user's Power BI model. Use them to answer "
        "questions about tables, measures, relationships, and to execute DAX queries. "
        "Be concise and helpful. Format DAX results as markdown tables when possible."
    )
    messages = [{"role": "system", "content": system_msg}]
    messages.extend(req.history or [])
    messages.append({"role": "user", "content": req.message})

    max_iterations = 10
    for _ in range(max_iterations):
        response = await client.chat(
            model=model,
            messages=messages,
            tools=state.ollama_tools if state.ollama_tools else None,
        )
        assistant_msg = response.get("message", {})
        messages.append(assistant_msg)

        tool_calls = assistant_msg.get("tool_calls", [])
        if not tool_calls:
            return {
                "response": assistant_msg.get("content", ""),
                "model": model,
                "history": messages,
            }

        # Execute tool calls
        for tc in tool_calls:
            fn = tc.get("function", {})
            name = fn.get("name", "")
            args = fn.get("arguments", {})
            try:
                tool_result = await call_mcp(name, args)
                messages.append({
                    "role": "tool",
                    "content": json.dumps(tool_result, default=str),
                })
            except Exception as e:
                messages.append({
                    "role": "tool",
                    "content": f"Error: {str(e)}",
                })

    return {
        "response": "Reached maximum tool call iterations.",
        "model": model,
        "history": messages,
    }


# ---------------------------------------------------------------------------
# Static file serving
# ---------------------------------------------------------------------------
@app.get("/")
async def serve_index():
    index = WEB_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return HTMLResponse("<h1>Power BI MCP Dashboard</h1><p>Web UI files not found.</p>")

# Mount static assets
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    print(f"\n{'='*60}")
    print(f"  Power BI MCP Web Interface")
    print(f"  Open http://{HOST}:{PORT} in your browser")
    print(f"{'='*60}\n")

    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
