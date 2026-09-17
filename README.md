# Local Agentic MCP (Model Context Protocol) with LangGraph & Ollama

A modular, privacy-first local AI agent framework that runs **100% on your machine** using Docker, Ollama, LangGraph, and the Model Context Protocol (MCP).

This project demonstrates how to decouple an AI agent's "brain" (LLM reasoning) from its "hands" (tools) using standardized MCP communication over Server-Sent Events (SSE).

---

## 🏗️ Architecture Overview

The system is split into two independent Docker containers communicating over a custom bridge network:

1. **`mcp-tool-server`**: A lightweight microservice that securely exposes custom local capabilities (e.g., reading and searching local logs via `analyze_local_logs`) using the Model Context Protocol.
2. **`mcp-agent-loop` (Orchestrator)**: A Python script utilizing **LangChain**, **LangGraph**, and **LangChain MCP Adapters** to dynamically discover tools, process user requests, and orchestrate local LLM calls.
3. **Ollama**: Runs locally on your host machine providing tool-capable intelligence (via `llama3.1`).

```text
+-------------------------------------------------------+
|                       Host Machine                    |
|                                                       |
|   +----------------+           +-------------------+  |
|   |     Ollama     |<----------|   Docker Bridge   |  |
|   |  (llama3.1)    |           |    (172.20.0.1)   |  |
|   +----------------+           +---------+---------+  |
|                                          |            |
+------------------------------------------|------------+
                                           |
+------------------------------------------|------------+
|                  Docker Network          |            |
|                                          v            |
|   +-----------------------+     SSE     +----------+  |
|   | mcp-agent-orchestrator|------------>|mcp-server|  |
|   |  (LangGraph / Agent)  |             +----------+  |
|   +-----------------------+                           |
+-------------------------------------------------------+

```

---

## 🚀 Prerequisites

Before getting started, ensure you have the following installed on your host machine:

* [Docker & Docker Compose](https://docs.docker.com/get-docker/)
* [Ollama](https://ollama.com/) running locally

---

## 📥 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/agentic-mcp.git
cd agentic-mcp

```

### 2. Pull a Tool-Compatible Local LLM

Because the agent uses native function/tool calling, ensure you have a tool-capable model pulled in Ollama:

```bash
ollama pull llama3.1

```

### 3. Configure Docker Network Gateway (Linux Setup)

On Linux, custom Docker bridge networks require an explicit gateway IP to talk to host services like Ollama. Find your Docker gateway IP:

```bash
docker network inspect agentic-mcp_default --format='{{range .IPAM.Config}}{{.Gateway}}{{end}}'

```

*(If it returns `172.20.0.1`, ensure your `src/agent_orchestrator.py` or environment variable points to `[http://172.20.0.1:11434](http://172.20.0.1:11434)`).*

### 4. Build and Run the Containers

Spin up the stack using Docker Compose:

```bash
docker compose up --build -d

```

To view the live agent execution logs and test query results:

```bash
docker compose logs -f agent-orchestrator

```

---

## 📂 Project Structure

```text
agentic-mcp/
├── Dockerfile                  # Container instructions for orchestrator
├── docker-compose.yml          # Multi-container orchestration setup
├── pyproject.toml              # Python project dependencies
└── src/
    ├── agent_orchestrator.py   # LangGraph React Agent loop & MCP client
    └── server_tools.py         # MCP tool definitions & server logic

```

---

## 💡 How It Works

1. **Initialization:** The orchestrator boots up, connects to Ollama on the host machine, and opens an SSE connection to the MCP tool server (`http://mcp-server:8000/sse`).
2. **Tool Discovery:** The orchestrator runs an initialization handshake via `session.initialize()` and automatically maps available MCP tools into LangChain-compatible schemas using `load_mcp_tools`.
3. **Execution:** When given a prompt (e.g., *"Can you check the logs at /app/src/server_tools.py for the keyword 'def'?"*), the LangGraph React agent evaluates the available tools, generates a structured tool call, retrieves the matching log lines from the tool server, and formulates a final, intelligent response.
