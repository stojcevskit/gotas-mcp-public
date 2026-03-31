💧 Gotas Commerce MCP Server
This Model Context Protocol (MCP) server allows AI assistants (like Claude or Cursor) to directly manage USDT (BEP20) payments via Gotas Commerce.

✨ Features
🔗 Create Payment Links: Generate unique USDT (BEP20) links.

⏳ Wait for Payment: (New) Async polling to track payment status without blocking.

💰 Check Balance: Summary of all successfully completed payments.

📑 Transaction History: List recent payments with status and descriptions.

✅ Payment Status: Verify individual payments via Payment ID.

🚀 Quick Start (Docker)
The fastest way to run the server is using the official image from Docker Hub:

Bash
docker pull tiho64/gotas-mcp-public:latest
docker run -i --rm -e GOTAS_API_KEY=your_key -e USDT_ADDRESS=your_wallet tiho64/gotas-mcp-public:latest
🛠️ Claude Desktop Integration
Add this to your claude_desktop_config.json:

JSON
{
  "mcpServers": {
    "gotas-payment": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GOTAS_API_KEY=your_key", "-e", "USDT_ADDRESS=your_wallet", "tiho64/gotas-mcp-public:latest"]
    }
  }
}
🏗️ Local Installation
Clone and Install:

Bash
git clone https://github.com/stojcevskit/gotas-mcp.git
cd gotas-mcp
pip install -r requirements.txt
Configuration (.env):
Create a .env file in the root directory:

Code snippet
GOTAS_API_KEY=your_api_key_from_gotas
USDT_ADDRESS=your_BEP20_wallet_address
🌐 Live Deployment
Verified and live on MCPize: https://mcpize.com/mcp/gotas-commerce

📄 License
MIT License
