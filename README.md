# Claude MCP Setup for Windows

This repository contains a PowerShell script that automates the setup of Anthropic Claude Model Context Protocol (MCP) servers on Windows. It simplifies the installation process and configuration of various MCP servers used with Claude Desktop.

## Features

- Automatic installation of NPM and Python packages
- Dynamic configuration of MCP servers
- Flexible API key management
- Easy to extend with new MCPs

## Prerequisites

- [Claude Desktop](https://claude.ai/download) installed
- Node.js and npm installed
- Python and pip installed
- PowerShell 5.1 or later

## Installation

1. Download `setup-claude-mcps.ps1` from this repository
2. Right-click the script and select "Run with PowerShell" or run it from PowerShell terminal

## Usage

### Basic Usage
```powershell
.\setup-claude-mcps.ps1
```

### With GitHub Token
```powershell
.\setup-claude-mcps.ps1 -GIT_PAT_TOKEN "your-token"
```

### Skip API Key Prompts
```powershell
.\setup-claude-mcps.ps1 -skipPrompts
```

## Customization

### Adding New Packages
Edit the `$PACKAGES_TO_INSTALL` array at the top of the script:
```powershell
$PACKAGES_TO_INSTALL = @(
    "@modelcontextprotocol/server-filesystem",
    "@patruff/server-terminator",
    "mcp-server-sqlite",
    # Add new packages here
    "@your/new-package"
)
```

### Adding New API Keys
Add new keys to the `$API_KEYS` hashtable:
```powershell
$API_KEYS = @{
    GIT_PAT_TOKEN = ""  # GitHub Personal Access Token
    # Add new API keys here
    YOUR_NEW_KEY = ""
}
```

### Adding New MCP Configurations
Add new configurations to the `$MCP_CONFIGS` hashtable:
```powershell
$MCP_CONFIGS = @{
    your_new_mcp = @{
        command = "path/to/command"
        args = @(
            "arg1",
            "arg2"
        )
        env = @{
            YOUR_API_KEY = "{YOUR_NEW_KEY}"  # References key from $API_KEYS
        }
    }
}
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT