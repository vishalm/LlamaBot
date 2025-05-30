import asyncio
import json
from typing import Optional

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client


async def handle_sampling_message(
    message: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    """Optional sampling callback for handling model requests."""
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello from MCP client!",
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn",
    )


async def demo_stdio_client():
    """Demonstrate MCP client using stdio transport."""
    print("=== MCP Stdio Client Demo ===")
    
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="python",  # Executable
        args=["mcp/mcp_server.py"],  # Server script
        env=None,  # Optional environment variables
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(
                read, write, sampling_callback=handle_sampling_message
            ) as session:
                # Initialize the connection
                print("Initializing connection...")
                await session.initialize()
                print("✓ Connection initialized")

                # List available prompts
                print("\n--- Listing Prompts ---")
                try:
                    prompts = await session.list_prompts()
                    if prompts.prompts:
                        for prompt in prompts.prompts:
                            print(f"Prompt: {prompt.name} - {prompt.description}")
                    else:
                        print("No prompts available")
                except Exception as e:
                    print(f"Error listing prompts: {e}")

                # List available resources
                print("\n--- Listing Resources ---")
                try:
                    resources = await session.list_resources()
                    if resources.resources:
                        for resource in resources.resources:
                            print(f"Resource: {resource.uri} - {resource.name}")
                    else:
                        print("No resources available")
                except Exception as e:
                    print(f"Error listing resources: {e}")

                # List available tools
                print("\n--- Listing Tools ---")
                try:
                    tools = await session.list_tools()
                    if tools.tools:
                        for tool in tools.tools:
                            print(f"Tool: {tool.name} - {tool.description}")
                    else:
                        print("No tools available")
                except Exception as e:
                    print(f"Error listing tools: {e}")

                # Try to get a prompt (if available)
                if prompts.prompts:
                    try:
                        prompt_name = prompts.prompts[0].name
                        print(f"\n--- Getting Prompt: {prompt_name} ---")
                        prompt_args = {}
                        if prompts.prompts[0].arguments:
                            # Simple example args
                            for arg in prompts.prompts[0].arguments:
                                if arg.required:
                                    prompt_args[arg.name] = "example_value"
                        
                        prompt_result = await session.get_prompt(prompt_name, arguments=prompt_args)
                        print(f"Prompt result: {prompt_result.description}")
                        for msg in prompt_result.messages:
                            print(f"  Message: {msg.content}")
                    except Exception as e:
                        print(f"Error getting prompt: {e}")

                # Try to read a resource (if available)
                if resources.resources:
                    try:
                        resource_uri = resources.resources[0].uri
                        print(f"\n--- Reading Resource: {resource_uri} ---")
                        content, mime_type = await session.read_resource(resource_uri)
                        print(f"Resource content (type: {mime_type}): {content[:200]}...")
                    except Exception as e:
                        print(f"Error reading resource: {e}")

                # Try to call a tool (if available)
                if tools.tools:
                    try:
                        tool_name = tools.tools[0].name
                        print(f"\n--- Calling Tool: {tool_name} ---")
                        
                        # Simple example arguments
                        tool_args = {}
                        if hasattr(tools.tools[0], 'inputSchema') and tools.tools[0].inputSchema:
                            # For demo purposes, provide simple default values
                            schema = tools.tools[0].inputSchema
                            if 'properties' in schema:
                                for prop_name, prop_def in schema['properties'].items():
                                    if prop_def.get('type') == 'string':
                                        tool_args[prop_name] = "example"
                                    elif prop_def.get('type') == 'integer':
                                        tool_args[prop_name] = 42
                                    elif prop_def.get('type') == 'number':
                                        tool_args[prop_name] = 3.14
                        
                        result = await session.call_tool(tool_name, arguments=tool_args)
                        print(f"Tool result: {result.content}")
                    except Exception as e:
                        print(f"Error calling tool: {e}")

    except Exception as e:
        print(f"Stdio client error: {e}")


async def demo_http_client(server_url: str = "http://localhost:8000/mcp"):
    """Demonstrate MCP client using HTTP transport."""
    print("\n=== MCP HTTP Client Demo ===")
    print(f"Attempting to connect to: {server_url}")
    
    try:
        # Connect to a streamable HTTP server
        async with streamablehttp_client(server_url) as (
            read_stream,
            write_stream,
            _,
        ):
            # Create a session using the client streams
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                print("Initializing HTTP connection...")
                await session.initialize()
                print("✓ HTTP Connection initialized")

                # List available tools
                print("\n--- Listing Tools (HTTP) ---")
                try:
                    tools = await session.list_tools()
                    if tools.tools:
                        for tool in tools.tools:
                            print(f"Tool: {tool.name} - {tool.description}")
                            
                        # Try calling the first tool with example data
                        if tools.tools:
                            tool_name = tools.tools[0].name
                            print(f"\n--- Calling Tool via HTTP: {tool_name} ---")
                            
                            # Example: if it's an echo tool
                            if "echo" in tool_name.lower():
                                result = await session.call_tool(tool_name, arguments={"message": "Hello via HTTP!"})
                                print(f"Tool result: {result.content}")
                            else:
                                # Try with generic arguments
                                result = await session.call_tool(tool_name, arguments={})
                                print(f"Tool result: {result.content}")
                    else:
                        print("No tools available")
                except Exception as e:
                    print(f"Error with HTTP operations: {e}")

                # List resources
                print("\n--- Listing Resources (HTTP) ---")
                try:
                    resources = await session.list_resources()
                    if resources.resources:
                        for resource in resources.resources:
                            print(f"Resource: {resource.uri} - {resource.name}")
                    else:
                        print("No resources available")
                except Exception as e:
                    print(f"Error listing resources via HTTP: {e}")

    except ConnectionError as e:
        print(f"HTTP connection failed: {e}")
        print(f"Make sure an MCP server is running at {server_url}")
        print("To start the server in HTTP mode, run:")
        print("  python mcp/mcp_server.py --transport streamable-http --port 8000")
    except Exception as e:
        print(f"HTTP client error: {e}")
        print(f"This might be because no server is running at {server_url}")
        print("To start the server in HTTP mode, run:")
        print("  python mcp/mcp_server.py --transport streamable-http --port 8000")


async def main():
    """Main function demonstrating both stdio and HTTP MCP clients."""
    print("MCP Client Examples")
    print("==================")
    print()
    print("This demo will test both stdio and HTTP transports.")
    print("For stdio: The server will be started automatically.")
    print("For HTTP: You need to start the server manually in another terminal.")
    print()
    
    # Demo stdio client
    print("1. Testing stdio transport...")
    await demo_stdio_client()
    
    # Demo HTTP client
    print("\n" + "="*50)
    print("2. Testing HTTP transport...")
    print("NOTE: For HTTP testing, start the server in another terminal with:")
    print("  python mcp/mcp_server.py --transport streamable-http --port 8000")
    print("Then press Enter to continue, or Ctrl+C to skip HTTP testing.")
    
    try:
        input()  # Wait for user to press Enter
        await demo_http_client()
    except KeyboardInterrupt:
        print("\nSkipping HTTP transport test.")
    
    print("\nMCP Client demo completed!")


if __name__ == "__main__":
    asyncio.run(main())