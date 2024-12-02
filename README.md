# Claude MCP Setup for Windows

Easy setup script for installing and configuring Claude Model Context Protocol (MCP) servers on Windows.

## Prerequisites

1. Install Node.js and npm:
   - Download and install from [nodejs.org](https://nodejs.org/)
   - Or use a version manager like [fnm](https://github.com/Schniz/fnm)

2. Install Python:
   - Download and install from [python.org](https://python.org/)
   - Make sure to check "Add Python to PATH" during installation

3. Install Claude Desktop:
   - Download and install from [claude.ai/download](https://claude.ai/download)

## Installation Steps

1. Download `setup-mcp.py` from this repository

2. Open PowerShell and enable script execution:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

3. Run the setup script:
```powershell
python setup-mcp.py
```

The script will automatically:
1. Get your Windows username
2. Install all JavaScript MCPs via npm
3. Install all Python MCPs via pip
4. Update your `claude_desktop_config.json` with the correct configurations
5. Set up proper paths for all installed packages

After installation:
1. Restart Claude Desktop
2. Enjoy your new MCP tools!

## Adding API Keys

To add API keys:
1. Open `setup-mcp.py` in a text editor
2. Find the `API_KEYS` section at the top:
```python
API_KEYS = {
    "GIT_PAT_TOKEN": "",  # GitHub Personal Access Token
    # Add new API keys here like:
    # "OPENAI_API_KEY": "",
    # "AZURE_API_KEY": ""
}
```
3. Add your new API key
4. Run the script again

## Customization

### Adding New Packages
Edit the `PACKAGES_TO_INSTALL` array at the top of the script:
```python
PACKAGES_TO_INSTALL = [
    "@modelcontextprotocol/server-filesystem",  # npm package
    "@patruff/server-terminator",               # npm package
    "mcp-server-sqlite",                        # pip package
    # Add new packages here
    "@your/new-package",                        # npm package
    "your-python-package"                       # pip package
]
```

### Adding New MCP Configurations
MCPs are configured automatically based on installed packages. If you need custom configuration, you can modify the `update_config()` function in the script.

## Troubleshooting

1. If you get execution policy errors:
   - Make sure you ran the `Set-ExecutionPolicy` command in PowerShell
   - Try running PowerShell as Administrator

2. If npm commands fail:
   - Check that Node.js is installed: `node --version`
   - If using fnm, ensure it's properly set up: `fnm list`

3. If pip commands fail:
   - Check that Python is installed: `python --version`
   - Ensure pip is up to date: `python -m pip install --upgrade pip`

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT