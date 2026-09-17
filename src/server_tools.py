from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import os
import uvicorn

# Disable DNS rebinding protection for internal container-to-container networking
mcp = FastMCP(
    "LocalSpecializedToolServer",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False
    )
)

@mcp.tool()
def analyze_local_logs(log_path: str, keyword: str) -> str:
    """Search local container volumes for error indicators or target keywords."""
    if not os.path.exists(log_path):
        return f"Error: Path {log_path} does not exist inside the container."
    
    matches = []
    with open(log_path, "r") as f:
        for line in f:
            if keyword.lower() in line.lower():
                matches.append(line.strip())
                
    return f"Found {len(matches)} matching lines for '{keyword}': \n" + "\n".join(matches[:10])

if __name__ == "__main__":
    print("Starting MCP Tool Server via Uvicorn on port 8000...")
    app = mcp.sse_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)