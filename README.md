# Claude MCP Setup

This script helps set up and configure Model Context Protocol (MCP) servers for Claude.

## Supported MCPs

* `@modelcontextprotocol/server-filesystem`: Basic file system operations
* `@modelcontextprotocol/server-github`: GitHub operations
* `@modelcontextprotocol/server-brave-search`: Brave search integration
* `@modelcontextprotocol/server-memory`: In-memory data storage
* `@patruff/server-terminator`: File deletion operations
* `@patruff/server-flux`: Image generation using Flux AI model
* `@patruff/server-gmail-drive`: Gmail and Google Drive integration
* `mcp-server-sqlite`: SQLite database operations

## Prerequisites

- Python 3.x
- Node.js
- Google Cloud account (for Gmail/Drive functionality)

## Environment Variables

The script supports the following environment variables:

* `GIT_PAT_TOKEN`: GitHub Personal Access Token for GitHub operations
* `REPLICATE_API_TOKEN`: For using the Flux image generation model
* `BRAVE_API_KEY`: For Brave search functionality

## Google Cloud Setup (for Gmail/Drive MCP)

1. Create a new Google Cloud project
2. Enable the following APIs:
   - Google Drive API
   - Gmail API
3. Configure an OAuth consent screen
   - "External" is fine for testing
   - Add yourself as a test user
4. Add OAuth scopes:
   ```
   https://www.googleapis.com/auth/gmail.readonly
   https://www.googleapis.com/auth/gmail.send
   https://www.googleapis.com/auth/gmail.compose
   https://www.googleapis.com/auth/drive.file
   https://www.googleapis.com/auth/drive.readonly
   https://www.googleapis.com/auth/drive.appdata
   https://www.googleapis.com/auth/drive
   https://www.googleapis.com/auth/drive.metadata
   ```
5. Create an OAuth Client ID
   - Select application type "Desktop App"
   - Download the JSON file
   - Rename it to `gcp-oauth.keys.json`

## Usage

1. Place `gcp-oauth.keys.json` in the same directory as the script (required for Gmail/Drive functionality)
2. Run the setup script:
   ```powershell
   python setup_mcp.py
   ```

The script will:
1. Install all MCP packages
2. Prompt for API keys (can be skipped with `--skip-prompts`)
3. Configure the Claude desktop with all MCPs
4. For Gmail/Drive:
   - Copy OAuth credentials to your home directory
   - Launch browser authentication flow
   - Generate necessary credential files

### Command Line Options

- `--skip-prompts`: Skip API key prompts
- `--skip-auth`: Skip Gmail/Drive authentication

Example:
```powershell
python setup_mcp.py --skip-prompts --skip-auth
```

## File Locations

After setup, the following files will be created:

### Windows
```
C:\Users\YourUsername\gcp-oauth.keys.json                  # Your OAuth client config
C:\Users\YourUsername\.gmail-server-credentials.json       # Generated after auth
C:\Users\YourUsername\.gdrive-server-credentials.json      # Generated after auth
```

### macOS/Linux
```
~/gcp-oauth.keys.json
~/.gmail-server-credentials.json
~/.gdrive-server-credentials.json
```

## MCP Workspace

The Gmail/Drive MCP will create and use an "anthropicFun" folder in your Google Drive for all file operations. This ensures that the MCP only has access to a specific workspace in your Drive.

## Troubleshooting

1. If authentication fails, try:
   - Running `python setup_mcp.py --skip-prompts` to reinstall packages
   - Checking that your OAuth credentials file is correctly named and placed
   - Verifying you've enabled the necessary Google Cloud APIs
   - Ensuring you've added yourself as a test user in the OAuth consent screen

2. If MCPs aren't working in Claude:
   - Check the Claude desktop configuration file
   - Verify all credential files exist in your home directory
   - Ensure you've completed the Google authentication flow

