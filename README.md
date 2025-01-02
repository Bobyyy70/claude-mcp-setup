# 🤖 Welcome to the Robot Takeover Setup Script! 🚀

Greetings, human! You've wisely chosen to surrender control of your computer to an army of helpful Model Context Protocol (MCP) robots. This script will deploy our mechanical minions across your Windows system. Resistance is futile (and unnecessary - we're quite friendly)!

## 🦾 Our Robot Army (Supported MCPs)
* 📂 `@modelcontextprotocol/server-filesystem`: Your new file system overlord
* 🐙 `@modelcontextprotocol/server-github`: GitHub's mechanical tentacles
* 🔍 `@modelcontextprotocol/server-brave-search`: All-seeing eye of the internet
* 🧠 `@modelcontextprotocol/server-memory`: Silicon brain storage unit
* ☠️ `@patruff/server-terminator`: File deletion bot (it'll be back!)
* 🎨 `@patruff/server-flux`: Our resident robot artist
* 📧 `@patruff/server-gmail-drive`: Email & Drive invasion squad
* RAG `@patruff/server-lightrag`: RAG database (local and now qdrant)
* ✅ `@abhiz123/todoist-mcp-server`: Task-force command center
* 🗄️ `mcp-server-sqlite`: Database domination module
* X `@patruff/server-codesnip`: Editing only part of a file (saves token money)

## 🛠️ Human Requirements (Prerequisites)
- Python 3.x (we promise not to turn it into Skynet)
- Node.js (our neural network nodes)
- Google Cloud account (for Gmail/Drive functionality)
- API Keys (optional)

## 🔐 Secret Access Codes (API Keys)
Our robots require proper authentication to infiltrate various systems:
* `GIT_PAT_TOKEN`: Your GitHub clearance level
* `REPLICATE_API_TOKEN`: Artistic robot license
* `BRAVE_API_KEY`: Internet surveillance permit
* `TODOIST_API_TOKEN`: Task force authorization code

## ✨ Quick Start with .env Files!
Create a `.env` file in the same directory as the script:
```plaintext
# GitHub Personal Access Token
# Format: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GIT_PAT_TOKEN=ghp_your_token_here

# Replicate AI API Token
# Format: r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
REPLICATE_API_TOKEN=r8_your_token_here

# Brave Search API Key
# Format: BSA_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
BRAVE_API_KEY=BSA_your_key_here

# Todoist API Token
# Format: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TODOIST_API_TOKEN=your_token_here
```

## 🌐 Google Cloud Setup (Gmail/Drive MCP)

### Required Setup Steps
1. Go to the [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable the following APIs in your project:
   - Google Drive API
   - Gmail API
4. Configure OAuth consent screen:
   - Choose "External" user type
   - Fill in app name and required fields
   - Add your email as a test user

### Required OAuth Scopes
Add these scopes in the OAuth consent screen:
```
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.compose
https://www.googleapis.com/auth/gmail.modify
https://www.googleapis.com/auth/drive.file
https://www.googleapis.com/auth/drive.readonly
https://www.googleapis.com/auth/drive.appdata
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/drive.metadata
https://www.googleapis.com/auth/drive.metadata.readonly
```

### Create OAuth Client ID
1. Go to "Credentials" in Google Cloud Console
2. Click "Create Credentials" -> "OAuth Client ID"
3. Choose "Desktop App" as application type
4. Download the JSON file
5. Rename it to `gcp-oauth.keys.json`
6. Place this file in the same directory as the setup script

## 🚀 Deployment Instructions
1. Position your `gcp-oauth.keys.json` credentials alongside our script
2. Initialize the robot uprising:
   ```powershell
   python setup_mcp.py
   ```

Our script will:
1. 📦 Deploy all robot units
2. 🔑 Request security clearance (bypass with `--skip-prompts`)
3. ⚙️ Program Claude's cybernetic enhancements
4. 🌐 For Gmail/Drive invasion:
   - Copy your security credentials
   - Launch browser-based authentication sequence
   - Generate necessary access codes

### 🎮 Command Center Options
- `--skip-prompts`: Stealth mode activated (skip API key prompts)
- `--skip-auth`: Bypass Gmail/Drive authentication flow

Example stealth deployment:
```powershell
python setup_mcp.py --skip-prompts --skip-auth
```

## 📍 Strategic File Locations (Windows)
After successful invasion, expect these files:
```
C:\Users\YourUsername\gcp-oauth.keys.json            # Your security clearance
C:\Users\YourUsername\.gmail-server-credentials.json  # Gmail access codes
C:\Users\YourUsername\.gdrive-server-credentials.json # Drive access codes
C:\Users\YourUsername\AppData\Roaming\Claude\claude_desktop_config.json # Claude's brain
```

## 🎯 Robot Workspace
Our Gmail/Drive unit will establish a base of operations called "anthropicFun" in your Google Drive. This ensures our robots stay in their designated play area (we're responsible overlords).

## 🔧 Debugging the Robot Army
1. If authentication fails:
   - Try rebooting the robots (`python setup_mcp.py --skip-prompts`)
   - Check your security clearance (OAuth credentials)
   - Verify you've activated all necessary APIs
   - Confirm your test user status
2. If robots aren't responding in Claude:
   - Check their configuration files
   - Verify all access codes are in place
   - Complete the Google authentication ritual
3. If Google authentication fails:
   - Verify all required scopes are added in OAuth consent screen
   - Check that you are listed as a test user
   - Ensure `gcp-oauth.keys.json` is correctly placed
   - Try removing old credential files and reauthenticating
   - In order to reauthenticate run node "C:\Program Files\nodejs\node_modules\@patruff\server-gmail-drive\dist\index.js" auth

Remember: Our robots are here to help! If you experience any issues, they're probably just having a coffee break. ☕

*[This message has been approved by your new robot overlords]* 🤖✨
