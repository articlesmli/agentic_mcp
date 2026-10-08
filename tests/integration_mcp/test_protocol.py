import os
import sys
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

@pytest.fixture
def server_parameters():
    env_config = os.environ.copy()
    
    current_working_dir = os.getcwd()
    src_path = os.path.join(current_working_dir, 'src')
    
    if "PYTHONPATH" in env_config:
        env_config["PYTHONPATH"] = f"{src_path}:{env_config['PYTHONPATH']}"
    else:
        env_config["PYTHONPATH"] = src_path

    # FIX: Use sys.executable to ensure it runs inside .venv_mcp
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "server_tools"],
        env=env_config
    )

@pytest.mark.asyncio
async def test_mcp_server_tool_contracts(server_parameters):
    async with stdio_client(server_parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            response = await session.list_tools()
            tools = response.tools
            
            assert len(tools) > 0, "The MCP server is not exposing any tools."
            
            target_tool_name = "analyze_local_logs" 
            tool_exists = any(t.name == target_tool_name for t in tools)
            assert tool_exists, f"Tool '{target_tool_name}' was not found on the MCP server."
            
            tool = next(t for t in tools if t.name == target_tool_name)
            assert hasattr(tool, "inputSchema"), "Tool is missing inputSchema definitions."
            properties = tool.inputSchema.get("properties", {})
            
            assert "log_path" in properties, f"Parameter 'log_path' missing from {target_tool_name} schema."
            assert "keyword" in properties, f"Parameter 'keyword' missing from {target_tool_name} schema."