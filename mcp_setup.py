#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-dotenv"
# ]
# ///

import json
import os
import sys
import subprocess
from pathlib import Path
import argparse
import dotenv

# Package Configuration
PACKAGES_TO_INSTALL = {
    # npm packages that will be run with npx
    "npm": [
        "@modelcontextprotocol/server-filesystem",
        "@modelcontextprotocol/server-memory",
        "@modelcontextprotocol/server-brave-search",
        "@modelcontextprotocol/server-github",
        "@patruff/server-terminator",
        "@patruff/server-flux",
        "@patruff/server-gmail-drive",
        "@abhiz123/todoist-mcp-server"
    ],
    # Python packages that will be run with uvx
    "python": [
        "mcp-server-sqlite",
        "mcp-server-time",
        "python-dotenv"
    ]
}

# API Keys Configuration
API_KEYS = {
    "GIT_PAT_TOKEN": "",
    "REPLICATE_API_TOKEN": "",
    "BRAVE_API_KEY": "",
    "TODOIST_API_TOKEN": ""
}

# MCP Server Configs that require API keys or credentials
MCP_API_REQUIREMENTS = {
    "github": ["GIT_PAT_TOKEN"],
    "terminator": ["GIT_PAT_TOKEN"],
    "flux": ["REPLICATE_API_TOKEN"],
    "brave-search": ["BRAVE_API_KEY"],
    "gmail-drive": ["GMAIL_DRIVE_CREDENTIALS"],
    "todoist": ["TODOIST_API_TOKEN"]
}

def load_env_config():
    """Load configuration from .env file if it exists"""
    script_dir = Path(__file__).parent
    env_path = script_dir / ".env"
    
    if env_path.exists():
        print(f"Loading configuration from {env_path}")
        dotenv.load_dotenv(env_path)
        
        env_keys = {
            "GIT_PAT_TOKEN": os.getenv("GIT_PAT_TOKEN"),
            "REPLICATE_API_TOKEN": os.getenv("REPLICATE_API_TOKEN"),
            "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY"),
            "TODOIST_API_TOKEN": os.getenv("TODOIST_API_TOKEN")
        }
        
        return {k: v for k, v in env_keys.items() if v is not None}
    else:
        print("No .env file found, using default configuration")
        return {}

def install_package(package, package_type):
    """Install a package using npm or pip"""
    try:
        if package_type == "npm":
            print(f"Installing NPM package: {package}")
            subprocess.run(["npm", "install", "-g", package], check=True, shell=(os.name == 'nt'))
        else:
            print(f"Installing Python package: {package}")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        print(f"Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")
        return False
    except Exception as e:
        print(f"Error installing {package}: {e}")
        return False

def get_config_path():
    """Get Claude desktop config path"""
    if os.name == 'nt':  # Windows
        return Path(os.environ["APPDATA"]) / "Claude" / "claude_desktop_config.json"
    if sys.platform == 'darwin':  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    # Linux
    return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"

def check_gmail_drive_credentials():
    """Check if Gmail/Drive credentials exist"""
    home_dir = Path.home()
    return all(
        (home_dir / f).exists() for f in [
            ".gdrive-server-credentials.json",
            ".gmail-server-credentials.json",
            "gcp-oauth.keys.json"
        ]
    )

def check_api_keys(mcp_name, api_keys):
    """Check if required API keys are available for an MCP"""
    if mcp_name not in MCP_API_REQUIREMENTS:
        return True
    
    if mcp_name == "gmail-drive":
        return check_gmail_drive_credentials()
    
    required_keys = MCP_API_REQUIREMENTS[mcp_name]
    return all(api_keys.get(key) for key in required_keys)

def update_config(api_keys):
    """Update Claude desktop configuration"""
    config_path = get_config_path()
    
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            "mcpServers": {
                # NPX-based servers
                "filesystem": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-filesystem", str(Path.home() / "anthropicFun")]
                },
                "memory": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-memory"]
                },
                # UVX-based servers
                "sqlite": {
                    "command": "uvx",
                    "args": ["mcp-server-sqlite", "--db-path", "~/test.db"]
                },
                "time": {
                    "command": "uvx",
                    "args": ["mcp-server-time"]
                }
            }
        }

        # Add Todoist configuration if API key exists
        if check_api_keys("todoist", api_keys):
            config["mcpServers"]["todoist"] = {
                "command": "npx",
                "args": ["@abhiz123/todoist-mcp-server"],
                "env": {
                    "TODOIST_API_TOKEN": api_keys.get("TODOIST_API_TOKEN", "")
                }
            }

        # Add gmail-drive configuration if credentials exist
        if check_gmail_drive_credentials():
            config["mcpServers"]["gmail-drive"] = {
                "command": "npx",
                "args": ["@patruff/server-gmail-drive"]
            }

        # Add API-dependent servers if keys are available
        if check_api_keys("brave-search", api_keys):
            config["mcpServers"]["brave-search"] = {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-brave-search"],
                "env": {
                    "BRAVE_API_KEY": api_keys.get("BRAVE_API_KEY", "")
                }
            }

        if check_api_keys("github", api_keys):
            config["mcpServers"]["github"] = {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": api_keys.get("GIT_PAT_TOKEN", "")
                }
            }

        if check_api_keys("terminator", api_keys):
            config["mcpServers"]["terminator"] = {
                "command": "npx",
                "args": ["@patruff/server-terminator"],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": api_keys.get("GIT_PAT_TOKEN", "")
                }
            }

        if check_api_keys("flux", api_keys):
            config["mcpServers"]["flux"] = {
                "command": "npx",
                "args": ["@patruff/server-flux"],
                "env": {
                    "REPLICATE_API_TOKEN": api_keys.get("REPLICATE_API_TOKEN", "")
                }
            }

        # Load and merge existing config if it exists
        if config_path.exists():
            try:
                with open(config_path) as f:
                    existing_config = json.load(f)
                if "mcpServers" in existing_config:
                    existing_config["mcpServers"].update(config["mcpServers"])
                    config = existing_config
            except json.JSONDecodeError:
                print(f"Warning: Existing config was invalid, using default config")

        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Configuration updated successfully at {config_path}")
        return True
        
    except Exception as e:
        print(f"Error updating config: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Claude MCP Setup Script")
    parser.add_argument("--skip-prompts", action="store_true", help="Skip API key prompts")
    parser.add_argument("--skip-auth", action="store_true", help="Skip Gmail/Drive authentication")
    args = parser.parse_args()

    # Load API keys from .env file first
    api_keys = load_env_config()
    
    # Fill in any missing keys from default config
    for key in API_KEYS:
        if key not in api_keys:
            api_keys[key] = API_KEYS[key]

    # Only prompt for missing keys if not skipping prompts
    if not args.skip_prompts:
        for key in API_KEYS:
            if not api_keys.get(key):
                value = input(f"Enter value for {key} (press Enter to skip): ")
                if value:
                    api_keys[key] = value

    # Install packages
    success = True
    for pkg_type, packages in PACKAGES_TO_INSTALL.items():
        for package in packages:
            if not install_package(package, pkg_type):
                success = False
                print(f"Warning: Failed to install {package}")

    # Update configuration
    if not update_config(api_keys):
        success = False
        print("Warning: Failed to update configuration")
    elif api_keys:
        print("\nMCP Servers requiring API keys:")
        for mcp, required_keys in MCP_API_REQUIREMENTS.items():
            status = "Configured" if check_api_keys(mcp, api_keys) else "Missing API key(s)"
            print(f"- {mcp}: {status}")

    if success:
        print("\nSetup completed successfully!")
    else:
        print("\nSetup completed with some warnings. Please check the messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
