# Claude MCP Setup

This script helps set up and configure Model Context Protocol (MCP) servers for Claude.

## Supported MCPs

- `@modelcontextprotocol/server-filesystem`: Basic file system operations
- `@patruff/server-terminator`: File deletion operations
- `@patruff/server-flux`: Image generation using Flux AI model
- `mcp-server-sqlite`: SQLite database operations

## Environment Variables

The script supports the following environment variables:
- `GITHUB_PERSONAL_ACCESS_TOKEN`: For GitHub operations
- `REPLICATE_API_TOKEN`: For using the Flux image generation model

## Usage

1. Make sure you have Python 3.x and Node.js installed
2. Run `python mcp_setup.py`
3. Enter API keys when prompted (or use --skip-prompts to skip)
