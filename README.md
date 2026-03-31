# 💧 Gotas Commerce MCP Server

[![MCP](https://img.shields.io/badge/MCP-Protocol-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.11-yellow)](https://www.python.org/)

This **Model Context Protocol (MCP)** server allows AI assistants (like Claude or Cursor) to directly create and manage **USDT (BEP20)** payments via [Gotas Commerce](https://commerce.gotas.com.br/).

## ✨ Features
- 🔗 **Create Payment Links**: Generate unique USDT (BEP20) links.
- 💰 **Check Balance**: Summary of all successfully completed payments.
- 📑 **Transaction History**: List recent payments with status and descriptions.
- ✅ **Payment Status**: Verify individual payments via Payment ID.

## 🚀 Installation & Setup

1. **Clone and Install:**
```bash
git clone [https://github.com/stojcevskit/gotas-mcp-public.git](https://github.com/stojcevskit/gotas-mcp-public.git)
cd gotas-mcp-public
pip install -r requirements.txt
Configuration (.env):
Create a file named .env in the root directory and add:

Code snippet
GOTAS_API_KEY=your_api_key_from_gotas
USDT_ADDRESS=your_BEP20_wallet_address
Claude Desktop Integration:
Add this to your claude_desktop_config.json:

JSON
{
  "mcpServers": {
    "gotas-commerce": {
      "command": "python",
      "args": ["/absolute/path/to/gotas_mcp_public.py"],
      "env": {
        "GOTAS_API_KEY": "your_api_key",
        "USDT_ADDRESS": "your_wallet_address"
      }
    }
  }
}
🐳 Docker Support
Bash
docker build -f Dockerfile.public -t gotas-mcp .
docker run --env-file .env gotas-mcp
🌐 Live Deployment
Verified and live on MCPize: https://mcpize.com/mcp/gotas-commerce

📄 License
MIT License

