#!/usr/bin/env python3
"""
Simple MCP Server Example
Provides resources, tools, and prompts for testing MCP clients.
"""

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import json
import datetime
import argparse
import sys

# Create an MCP server
mcp = FastMCP("Demo Server")

# Tools
@mcp.tool()
def echo(message: str) -> str:
    """Echo a message back to the caller"""
    return f"Echo: {message}"


@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b


@mcp.tool()
def get_current_time() -> str:
    """Get the current date and time"""
    return datetime.datetime.now().isoformat()


@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """Calculate BMI given weight in kg and height in meters"""
    bmi = weight_kg / (height_m ** 2)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return f"BMI: {bmi:.2f} ({category})"


# Resources
@mcp.resource("config://server")
def get_server_config() -> str:
    """Get server configuration information"""
    config = {
        "server_name": "Demo Server",
        "version": "1.0.0",
        "capabilities": ["tools", "resources", "prompts"],
        "max_connections": 100
    }
    return json.dumps(config, indent=2)


@mcp.resource("data://users/{user_id}")
def get_user_data(user_id: str) -> str:
    """Get user data by ID"""
    # Mock user data
    users = {
        "1": {"name": "Alice", "email": "alice@example.com", "role": "admin"},
        "2": {"name": "Bob", "email": "bob@example.com", "role": "user"},
        "3": {"name": "Charlie", "email": "charlie@example.com", "role": "user"}
    }
    
    user = users.get(user_id, {"error": "User not found"})
    return json.dumps(user, indent=2)


@mcp.resource("system://status")
def get_system_status() -> str:
    """Get current system status"""
    status = {
        "status": "healthy",
        "uptime": "2 hours 15 minutes",
        "active_connections": 3,
        "last_updated": datetime.datetime.now().isoformat()
    }
    return json.dumps(status, indent=2)


# Prompts
@mcp.prompt()
def review_code(code: str) -> str:
    """Generate a code review prompt"""
    return f"Please review this code for best practices, potential bugs, and improvements:\n\n```\n{code}\n```"


@mcp.prompt()
def debug_error(error_message: str, context: str = "") -> list[base.Message]:
    """Generate a debugging prompt with context"""
    messages = [
        base.UserMessage("I'm encountering an error and need help debugging it."),
        base.UserMessage(f"Error: {error_message}"),
    ]
    
    if context:
        messages.append(base.UserMessage(f"Context: {context}"))
    
    messages.append(
        base.AssistantMessage("I'll help you debug this error. Let me analyze the information you've provided.")
    )
    
    return messages


@mcp.prompt()
def explain_concept(concept: str) -> str:
    """Generate a prompt to explain a technical concept"""
    return f"Please explain the concept of '{concept}' in simple terms with examples and use cases."


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP Demo Server")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "streamable-http"], 
        default="stdio",
        help="Transport method (default: stdio)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port for HTTP transport (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for HTTP transport (default: localhost)"
    )
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        print("Starting MCP server with stdio transport...", file=sys.stderr)
        mcp.run()
    elif args.transport == "streamable-http":
        print(f"Starting MCP server with HTTP transport on {args.host}:{args.port}...", file=sys.stderr)
        mcp.run(transport="streamable-http", host=args.host, port=args.port) 