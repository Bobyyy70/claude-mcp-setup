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