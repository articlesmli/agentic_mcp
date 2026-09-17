import os
import asyncio
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_mcp_adapters.tools import load_mcp_tools

# Initialize local Ollama model
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://172.20.0.1:11434")
print(f"Initialized Local LLM client pointing to {ollama_base_url}")
model = ChatOllama(model="llama3.1", base_url=ollama_base_url)

async def run_agent():
    server_url = "http://mcp-server:8000/sse"
    print(f"Connecting to MCP tool server at {server_url}...")
    
    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session handshake
            await session.initialize()
            
            # Convert MCP tools into LangChain/LangGraph-compatible tools automatically
            tools = await load_mcp_tools(session)
            print(f"Successfully loaded LangChain tools: {[t.name for t in tools]}")
            
            # Create the LangGraph React agent with Ollama and the converted MCP tools
            agent_app = create_react_agent(model, tools)
            
            # Execute a test run passing a prompt to the agent
            print("Executing test query against the agent...")
            response = await agent_app.ainvoke({
                "messages": [("user", "Can you check the logs at /app/src/server_tools.py for the keyword 'def'?")]
            })
            
            # Print the final output from the agent's message history
            print("\n--- Agent Response ---")
            for message in response["messages"]:
                message.pretty_print()

if __name__ == "__main__":
    asyncio.run(run_agent())