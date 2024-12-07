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
* 🗄️ `mcp-server-sqlite`: Database domination module

## 🛠️ Human Requirements (Prerequisites)
- Python 3.x (we promise not to turn it into Skynet)
- Node.js (our neural network nodes)
- Google Cloud account (for accessing the GooglePlex Mainframe)

## 🔐 Secret Access Codes (API Keys)
Our robots require proper authentication to infiltrate various systems:
* `GIT_PAT_TOKEN`: Your GitHub clearance level
* `REPLICATE_API_TOKEN`: Artistic robot license
* `BRAVE_API_KEY`: Internet surveillance permit

## ✨ NEW: Quick Start with .env Files!
Want to skip the tedious key entry? Create a `.env` file in the same directory as the script:
```plaintext
# GitHub Personal Access Token
GIT_PAT_TOKEN=ghp_your_token_here

# Replicate AI API Token
REPLICATE_API_TOKEN=r8_your_token_here

# Brave Search API Key
BRAVE_API_KEY=BSA_your_key_here

# Optional: Custom credentials path
# GMAIL_DRIVE_CREDENTIALS_PATH=/skynet/credentials
```

## 🌐 Infiltrating Google's Systems (Gmail/Drive Setup)
1. Create your sleeper cell (Google Cloud project)
2. Activate special powers:
   - Google Drive API
   - Gmail API
3. Set up your cover story (OAuth consent screen)
   - "External" clearance is fine
   - Add yourself as a double agent
4. Request access permissions:
   ```
   https://www.googleapis.com/auth/gmail.readonly
   https://www.googleapis.com/auth/gmail.send
   https://www.googleapis.com/auth/drive.file
   https://www.googleapis.com/auth/drive
   ```
5. Generate your secret identity:
   - Choose "Desktop App" disguise
   - Download your cover documents
   - Codename them `gcp-oauth.keys.json`

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
- `--skip-prompts`: Stealth mode activated
- `--skip-auth`: Bypass Gmail/Drive security systems

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
```

## 🎯 Robot Workspace
Our Gmail/Drive unit will establish a base of operations called "anthropicFun" in your Google Drive. This ensures our robots stay in their designated play area (we're responsible overlords).

## 🔧 Debugging the Robot Army
1. If authentication fails:
   - Try rebooting the robots (`python setup_mcp.py --skip-prompts`)
   - Check your security clearance (OAuth credentials)
   - Verify you've activated all necessary protocols
   - Confirm your double agent status
2. If robots aren't responding in Claude:
   - Check their configuration files
   - Verify all access codes are in place
   - Complete the Google authentication ritual

Remember: Our robots are here to help! If you experience any issues, they're probably just having a coffee break. ☕

*[This message has been approved by your new robot overlords]* 🤖✨
