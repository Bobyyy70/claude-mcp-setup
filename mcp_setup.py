#!/usr/bin/env python3
import json
import os
import sys
import subprocess
from pathlib import Path
import argparse

# Package Configuration
PACKAGES_TO_INSTALL = [
    "@modelcontextprotocol/server-filesystem",  # npm package
    "@patruff/server-terminator",               # npm package
    "mcp-server-sqlite"                         # pip package
]

# API Keys Configuration
API_KEYS = {
    "GIT_PAT_TOKEN": "",  # GitHub Personal Access Token
}

def find_npm():
    """Find npm executable considering fnm setup"""
    if os.name == 'nt':  # Windows
        # Try fnm path first
        fnm_path = Path(os.environ["LOCALAPPDATA"]) / "fnm"
        if fnm_path.exists():
            # Run fnm env to get the current environment
            try:
                result = subprocess.run(['fnm', 'env', '--json'], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    env_data = json.loads(result.stdout)
                    # Update environment with fnm paths
                    os.environ.update(env_data)
                    return 'npm.cmd'  # Use npm.cmd on Windows when running through shell
            except:
                pass
    
    return 'npm'  # Default to regular npm

def install_package(package):
    """Install a package using npm or pip"""
    try:
        if package.startswith("@"):
            print(f"Installing NPM package: {package}")
            npm_cmd = find_npm()
            # Use shell=True on Windows for npm
            subprocess.run([npm_cmd, "install", "-g", package], check=True, shell=(os.name == 'nt'))
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

def update_config(api_keys):
    """Update Claude desktop configuration"""
    config_path = get_config_path()
    
    try:
        # Ensure config directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create default config
        npm_root = subprocess.run([find_npm(), "root", "-g"], 
                                capture_output=True, 
                                text=True, 
                                shell=(os.name == 'nt')).stdout.strip()

        config = {
            "mcpServers": {
                "filesystem": {
                    "command": "node" if os.name != 'nt' else r"C:\Program Files\nodejs\node.exe",
                    "args": [
                        str(Path(npm_root) / "@modelcontextprotocol" / "server-filesystem" / "dist" / "index.js"),
                        str(Path.home() / "anthropicFun")
                    ]
                },
                "terminator": {
                    "command": "node" if os.name != 'nt' else r"C:\Program Files\nodejs\node.exe",
                    "args": [
                        str(Path(npm_root) / "@patruff" / "server-terminator" / "dist" / "index.js")
                    ],
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": api_keys.get("GIT_PAT_TOKEN", "")
                    }
                },
                "sqlite": {
                    "command": "uv",
                    "args": [
                        "--directory",
                        "parent_of_servers_repo/servers/src/sqlite",
                        "run",
                        "mcp-server-sqlite",
                        "--db-path",
                        "~/test.db"
                    ]
                }
            }
        }

        # Load existing config if it exists
        if config_path.exists():
            try:
                with open(config_path) as f:
                    existing_config = json.load(f)
                # Merge existing mcpServers with new ones
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
    args = parser.parse_args()

    # Collect API keys
    api_keys = API_KEYS.copy()
    if not args.skip_prompts:
        for key in api_keys:
            value = input(f"Enter value for {key} (press Enter to skip): ")
            if value:
                api_keys[key] = value

    # Install packages
    success = True
    for package in PACKAGES_TO_INSTALL:
        if not install_package(package):
            success = False
            print(f"Warning: Failed to install {package}")

    # Update configuration
    if not update_config(api_keys):
        success = False
        print("Warning: Failed to update configuration")

    if success:
        print("Setup completed successfully!")
    else:
        print("Setup completed with some warnings. Please check the messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()