#!/usr/bin/env python3
import json
import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse
import dotenv

# Package Configuration
PACKAGES_TO_INSTALL = [
    "@modelcontextprotocol/server-filesystem",  # npm package
    "@modelcontextprotocol/server-memory",     # npm package
    "@modelcontextprotocol/server-brave-search", # npm package
    "@modelcontextprotocol/server-github",     # npm package
    "@patruff/server-terminator",              # npm package
    "@patruff/server-flux",                    # npm package
    "@patruff/server-gmail-drive",             # npm package
    "mcp-server-sqlite",                       # pip package
    "python-dotenv"                           # pip package - Added for .env support
]

# API Keys Configuration
API_KEYS = {
    "GIT_PAT_TOKEN": "",          # GitHub Personal Access Token
    "REPLICATE_API_TOKEN": "",    # Replicate AI API Token
    "BRAVE_API_KEY": ""           # Brave Search API Key
}

# MCP Server Configs that require API keys or credentials
MCP_API_REQUIREMENTS = {
    "github": ["GIT_PAT_TOKEN"],
    "terminator": ["GIT_PAT_TOKEN"],
    "flux": ["REPLICATE_API_TOKEN"],
    "brave-search": ["BRAVE_API_KEY"],
    "gmail-drive": ["GMAIL_DRIVE_CREDENTIALS"]  # Added Gmail/Drive requirement
}

def load_env_config():
    """Load configuration from .env file if it exists"""
    script_dir = Path(__file__).parent
    env_path = script_dir / ".env"
    
    if env_path.exists():
        print(f"Loading configuration from {env_path}")
        dotenv.load_dotenv(env_path)
        
        # Update API keys from environment variables
        env_keys = {
            "GIT_PAT_TOKEN": os.getenv("GIT_PAT_TOKEN"),
            "REPLICATE_API_TOKEN": os.getenv("REPLICATE_API_TOKEN"),
            "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")
        }
        
        # Remove None values
        return {k: v for k, v in env_keys.items() if v is not None}
    else:
        print("No .env file found, using default configuration")
        return {}

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

def check_gmail_drive_credentials():
    """Check if Gmail/Drive credentials exist"""
    home_dir = Path.home()
    gdrive_cred_file = home_dir / ".gdrive-server-credentials.json"
    gmail_cred_file = home_dir / ".gmail-server-credentials.json"
    gcp_oauth_file = home_dir / "gcp-oauth.keys.json"
    
    credentials_exist = (
        gdrive_cred_file.exists() and 
        gmail_cred_file.exists() and 
        gcp_oauth_file.exists()
    )
    
    if not credentials_exist:
        print("\nGmail/Drive credentials not found. Required files:")
        print(f"  GCP OAuth keys: {'✓' if gcp_oauth_file.exists() else '✗'} ({gcp_oauth_file})")
        print(f"  Drive credentials: {'✓' if gdrive_cred_file.exists() else '✗'} ({gdrive_cred_file})")
        print(f"  Gmail credentials: {'✓' if gmail_cred_file.exists() else '✗'} ({gmail_cred_file})")
        
    return credentials_exist

def setup_gmail_drive_auth():
    """Setup Gmail/Drive authentication"""
    script_dir = Path(__file__).parent
    gcp_oauth_file = script_dir / "gcp-oauth.keys.json"
    home_dir = Path.home()
    dest_file = home_dir / "gcp-oauth.keys.json"
    gdrive_cred_file = home_dir / ".gdrive-server-credentials.json"
    gmail_cred_file = home_dir / ".gmail-server-credentials.json"

    # Check if auth file exists in either location
    if dest_file.exists():
        print(f"Found existing GCP OAuth keys at {dest_file}")
    elif gcp_oauth_file.exists():
        try:
            shutil.copy2(gcp_oauth_file, dest_file)
            print(f"Copied GCP OAuth keys to {dest_file}")
        except Exception as e:
            print(f"Error copying file: {e}")
            return False
    else:
        print(f"Warning: GCP OAuth keys file not found at {gcp_oauth_file}")
        print(f"and not found at {dest_file}")
        print("Please place your gcp-oauth.keys.json in either location")
        return False

    # Get the package directory
    npm_cmd = find_npm()
    npm_root_result = subprocess.run(
        [npm_cmd, "root", "-g"], 
        capture_output=True,
        text=True,
        shell=(os.name == 'nt')
    )
    
    if npm_root_result.returncode != 0:
        print("Error getting npm root directory")
        return False
        
    npm_root = npm_root_result.stdout.strip()
    package_dir = Path(npm_root) / "@patruff" / "server-gmail-drive"
    index_js = package_dir / "dist" / "index.js"
    
    if not index_js.exists():
        print(f"\nError: index.js not found at: {index_js}")
        return False
        
    # Run the auth command
    node_path = "node" if os.name != 'nt' else r"C:\Program Files\nodejs\node.exe"
    auth_cmd = [node_path, str(index_js), "auth"]
    print(f"\nRunning auth command: {' '.join(auth_cmd)}")
    
    try:
        result = subprocess.run(
            auth_cmd, 
            capture_output=True,
            text=True,
            shell=(os.name == 'nt')
        )
        
        print("\nAuth command output:")
        print(result.stdout)
        if result.stderr:
            print("\nAuth command errors:")
            print(result.stderr)
            
    except Exception as e:
        print(f"\nError running auth command: {e}")
        return False

    # Check if credential files were created
    if gdrive_cred_file.exists() and gmail_cred_file.exists():
        print("\nCredential files created successfully!")
        return True
    else:
        print("\nWarning: Credential files not created:")
        print(f"  Drive credentials exist: {gdrive_cred_file.exists()}")
        print(f"  Gmail credentials exist: {gmail_cred_file.exists()}")
        return False

def check_api_keys(mcp_name, api_keys):
    """Check if required API keys are available for an MCP"""
    if mcp_name not in MCP_API_REQUIREMENTS:
        return True
    
    # Special handling for Gmail/Drive which uses credential files
    if mcp_name == "gmail-drive":
        return check_gmail_drive_credentials()
    
    required_keys = MCP_API_REQUIREMENTS[mcp_name]
    return all(api_keys.get(key) for key in required_keys)

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
                # MCPs without API requirements
                "filesystem": {
                    "command": "node" if os.name != 'nt' else r"C:\Program Files\nodejs\node.exe",
                    "args": [
                        str(Path(npm_root) / "@modelcontextprotocol" / "server-filesystem" / "dist" / "index.js"),
                        str(Path.home() / "anthropicFun")
                    ]
                },
                "memory": {
                    "command": "node" if os.name != 'nt' else r"C:\Program Files\nodejs\node.exe",
                    "args": [
                        str(Path(npm_root) / "@modelcontextprotocol" / "server-memory" / "dist" / "index.js")
                    ]
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

        # Add gmail-drive configuration if credentials exist
        if check_gmail_drive_credentials():
            config["mcpServers"]["gmail-drive"] = {
                "command": "node" if os.name != 'nt' else r"C:\Program Files\nodejs\node.exe",
                "args": [
                    str(Path(npm_root) / "@patruff" / "server-gmail-drive" / "dist" / "index.js")
                ]
            }
        else:
            print("Skipping Gmail/Drive MCP configuration due to missing credentials")

        # Add MCPs that require API keys if keys are available
        if check_api_keys("brave-search", api_keys):
            config["mcpServers"]["brave-search"] = {
                "command": "node" if os.name != 'nt' else r"C:\Program Files\nodejs\node.exe",
                "args": [
                    str(Path(npm_root) / "@modelcontextprotocol" / "server-brave-search" / "dist" / "index.js")
                ],
                "env": {
                    "BRAVE_API_KEY": api_keys.get("BRAVE_API_KEY", "")
                }
            }

        if check_api_keys("github", api_keys):
            config["mcpServers"]["github"] = {
                "command": "node" if os.name != 'nt' else r"C:\Program Files\nodejs\node.exe",
                "args": [
                    str(Path(npm_root) / "@modelcontextprotocol" / "server-github" / "dist" / "index.js")
                ],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": api_keys.get("GIT_PAT_TOKEN", "")
                }
            }

        if check_api_keys("terminator", api_keys):
            config["mcpServers"]["terminator"] = {
                "command": "node" if os.name != 'nt' else r"C:\Program Files\nodejs\node.exe",
                "args": [
                    str(Path(npm_root) / "@patruff" / "server-terminator" / "dist" / "index.js")
                ],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": api_keys.get("GIT_PAT_TOKEN", "")
                }
            }

        if check_api_keys("flux", api_keys):
            config["mcpServers"]["flux"] = {
                "command": "node" if os.name != 'nt' else r"C:\Program Files\nodejs\node.exe",
                "args": [
                    str(Path(npm_root) / "@patruff" / "server-flux" / "dist" / "index.js")
                ],
                "env": {
                    "REPLICATE_API_TOKEN": api_keys.get("REPLICATE_API_TOKEN", "")
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
            if not api_keys.get(key):  # Only prompt if key is empty
                value = input(f"Enter value for {key} (press Enter to skip): ")
                if value:
                    api_keys[key] = value

    # Install packages
    success = True
    for package in PACKAGES_TO_INSTALL:
        if not install_package(package):
            success = False
            print(f"Warning: Failed to install {package}")

    # Setup Gmail/Drive authentication if not skipped
    if not args.skip_auth:
        if setup_gmail_drive_auth():
            print("Gmail/Drive authentication setup initiated.")
            print("After completing authentication in your browser, you can use the Gmail/Drive MCP.")
        else:
            print("Warning: Gmail/Drive authentication setup failed")
            # Don't set success to False here as Gmail/Drive is optional

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
