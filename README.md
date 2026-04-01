# 💧 Gotas Commerce MCP Server

[![MCPize](https://img.shields.io/badge/Live%20on-MCPize-blue)](https://mcpize.com/mcp/gotas-commerce)

This Model Context Protocol (MCP) server allows AI assistants (like Claude or Cursor) to directly manage USDT (BEP20) payments via [Gotas Commerce](https://commerce.gotas.com).

## ✨ Features
- **Create Payment Links** – Generate unique USDT (BEP20) links.
- **Check Payment Status** – Verify individual payments via Payment ID.
- **Check Balance** – Summary of all successfully completed payments.
- **Transaction History** – List recent payments with status and descriptions.
- **Exchange Rate** – Current USDT/USD rate (live from CoinGecko).

## 🚀 Quick Start

### Via MCPize (recommended)
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gotas-payment": {
      "command": "npx",
      "args": ["-y", "mcpize", "run", "gotas-commerce"]
    }
  }
}


Via Docker

docker pull tiho64/gotas-mcp-public:latest
docker run -i --rm -e GOTAS_API_KEY=your_key -e USDT_ADDRESS=your_wallet tiho64/gotas-mcp-public:latest


🛠️ Claude Desktop Integration (Docker)

{
  "mcpServers": {
    "gotas-payment": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GOTAS_API_KEY=your_key", "-e", "USDT_ADDRESS=your_wallet", "tiho64/gotas-mcp-public:latest"]
    }
  }
}



🏗️ Local Installation

git clone https://github.com/stojcevskit/gotas-mcp-public.git
cd gotas-mcp-public
pip install -r requirements.txt

Create a .env file:

GOTAS_API_KEY=your_api_key_from_gotas
USDT_ADDRESS=your_BEP20_wallet_address


🌐 Live Deployment
Verified and live on MCPize: https://mcpize.com/mcp/gotas-commerce

📄 License
MIT



