#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate the virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

# Run the MCP server with all passed arguments
python "$SCRIPT_DIR/mcp_server.py" "$@" 