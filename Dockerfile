# Multi-stage build to keep the attack surface minimal
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim AS runner
WORKDIR /app
# Secure environment setting: prevent Python from writing pyc, buffer outputs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=builder /root/.local /root/.local
COPY ./agentic_mcp ./agentic_mcp

ENV PATH=/root/.local/bin:$PATH

# Create a non-root group and user for GxP runtime security
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser
RUN mkdir -p /app/data && chown -r mcpuser:mcpuser /app
USER mcpuser

EXPOSE 8000
# Run the server utilizing proper production execution transports (e.g. SSE over FastAPI)
CMD ["python", "-m", "agentic_mcp.server", "--host", "0.0.0.0", "--port", "8000"]
