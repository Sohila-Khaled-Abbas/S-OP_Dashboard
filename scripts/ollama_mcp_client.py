#!/usr/bin/env python3
import asyncio
import os
import sys
import json
from typing import List, Dict, Any

try:
    import ollama
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("Error: Required dependencies not found.")
    print("Please run: pip install mcp ollama")
    sys.exit(1)

# Default configuration
DEFAULT_MODEL = "qwen2.5-coder:7b"
OLLAMA_HOST = "http://localhost:11434"

# Set up MCP server parameters for Power BI Modeling MCP
# On Windows, 'npx' is typically launched via 'npx.cmd' or 'npx' shell script.
# We'll use 'npx' but fall back to 'npx.cmd' if needed.
command = "npx"
if sys.platform == "win32":
    # Search for npx.cmd in PATH or default to npx
    import shutil
    npx_path = shutil.which("npx")
    if npx_path and npx_path.lower().endswith(".cmd"):
        command = npx_path
    else:
        command = "npx.cmd"

server_params = StdioServerParameters(
    command=command,
    args=["-y", "@microsoft/powerbi-modeling-mcp@latest", "--start"],
    env=os.environ.copy()
)

def mcp_to_ollama_tool(mcp_tool) -> Dict[str, Any]:
    """
    Converts an MCP tool definition to the format expected by Ollama.
    """
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description or "",
            "parameters": mcp_tool.inputSchema
        }
    }

async def execute_tool_call(session: ClientSession, name: str, arguments: Dict[str, Any]) -> str:
    """
    Executes a tool call on the MCP server and returns the result as a string.
    """
    try:
        print(f"\n[MCP] Executing tool '{name}' with arguments: {json.dumps(arguments)}")
        result = await session.call_tool(name, arguments)
        
        # Parse result contents (usually text or images)
        text_contents = []
        for content in result.content:
            if hasattr(content, 'text'):
                text_contents.append(content.text)
            elif isinstance(content, dict) and 'text' in content:
                text_contents.append(content['text'])
            else:
                text_contents.append(str(content))
        
        output = "\n".join(text_contents)
        print(f"[MCP] Tool execution completed (Result length: {len(output)} chars)")
        return output
    except Exception as e:
        error_msg = f"Error executing tool {name}: {str(e)}"
        print(f"[MCP] {error_msg}", file=sys.stderr)
        return error_msg

async def run_chat_loop():
    print("=" * 60)
    print(" Power BI Modeling MCP + Ollama local client starting...")
    print("=" * 60)
    
    # 1. Connect to the MCP Server
    print(f"Connecting to Power BI MCP server using command: {server_params.command} {' '.join(server_params.args)}")
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the MCP session
                print("Initializing MCP session...")
                await session.initialize()
                
                # Fetch available tools
                print("Fetching available tools from MCP server...")
                mcp_tools = await session.list_tools()
                
                if not mcp_tools.tools:
                    print("\nWarning: No tools exposed by the MCP server.")
                    print("Make sure you are running this from a directory with a Power BI Project (.pbip) file.")
                else:
                    print(f"Discovered {len(mcp_tools.tools)} tools from MCP server:")
                    for tool in mcp_tools.tools:
                        print(f"  - {tool.name}: {tool.description.split('.')[0] if tool.description else ''}")
                
                # Convert tools to Ollama format
                ollama_tools = [mcp_to_ollama_tool(t) for t in mcp_tools.tools]
                
                # 2. Select Ollama Model
                print("\nConnecting to Ollama...")
                client = ollama.AsyncClient(host=OLLAMA_HOST)
                
                # Verify connection and models
                try:
                    models_response = await client.list()
                    available_models = [m['model'] for m in models_response.get('models', [])]
                    print(f"Available Ollama models: {', '.join(available_models)}")
                    
                    model = DEFAULT_MODEL
                    if model not in available_models and available_models:
                        # Try to find a matching model prefix or fallback to first
                        matched = False
                        for m in available_models:
                            if "qwen2.5" in m or "llama3.1" in m:
                                model = m
                                matched = True
                                break
                        if not matched:
                            model = available_models[0]
                    print(f"Using Ollama model: {model}")
                except Exception as e:
                    print(f"Error connecting to Ollama: {str(e)}")
                    print("Please make sure Ollama is installed and running locally.")
                    return
                
                print("\nReady! Ask questions about your Power BI semantic model.")
                print("Type 'exit' or 'quit' to close.")
                print("-" * 60)
                
                messages = []
                
                while True:
                    try:
                        user_input = input("\nYou: ").strip()
                    except (KeyboardInterrupt, EOFError):
                        print("\nExiting...")
                        break
                        
                    if not user_input:
                        continue
                    if user_input.lower() in ['exit', 'quit']:
                        print("Goodbye!")
                        break
                        
                    messages.append({'role': 'user', 'content': user_input})
                    
                    # Process the chat interaction (handling tool calls recursively if needed)
                    while True:
                        print("Assistant is thinking...")
                        
                        try:
                            # We send the tools array to Ollama if we have any tools
                            response = await client.chat(
                                model=model,
                                messages=messages,
                                tools=ollama_tools if ollama_tools else None
                            )
                        except Exception as e:
                            print(f"\nError in Ollama chat: {str(e)}")
                            break
                            
                        assistant_message = response.get('message', {})
                        messages.append(assistant_message)
                        
                        tool_calls = assistant_message.get('tool_calls', [])
                        if not tool_calls:
                            # No tool calls, output the response text
                            print(f"\nAssistant: {assistant_message.get('content', '')}")
                            break
                        
                        # Process each tool call
                        for tool_call in tool_calls:
                            function_info = tool_call.get('function', {})
                            name = function_info.get('name')
                            arguments = function_info.get('arguments', {})
                            
                            # Execute the tool
                            tool_output = await execute_tool_call(session, name, arguments)
                            
                            # Append tool response
                            messages.append({
                                'role': 'tool',
                                'content': tool_output
                            })
                            
    except Exception as e:
        print(f"\nFatal MCP connection error: {str(e)}", file=sys.stderr)
        print("Please ensure Node.js is installed and the @microsoft/powerbi-modeling-mcp package is accessible.", file=sys.stderr)

if __name__ == "__main__":
    if sys.platform == "win32":
        # Configure event loop for subprocesses on Windows
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(run_chat_loop())
