#!/usr/bin/env python3
import os
import httpx
from dotenv import load_dotenv
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import asyncio

load_dotenv()

GOTAS_API_KEY = os.getenv("GOTAS_API_KEY")
USDT_ADDRESS = os.getenv("USDT_ADDRESS")

server = Server("gotas-commerce")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="create_payment_link",
            description="Create a USDT payment link. The client pays and you receive USDT.",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Amount in USDT"},
                    "description": {"type": "string", "description": "Payment description"}
                },
                "required": ["amount"]
            }
        ),
        types.Tool(
            name="check_payment_status",
            description="Check if a payment has been completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "payment_id": {"type": "string", "description": "Payment ID from create_payment_link"}
                },
                "required": ["payment_id"]
            }
        ),
        types.Tool(
            name="wait_for_payment",
            description="Wait and poll until a payment status becomes 'completed'. Maximum wait is 5 minutes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "payment_id": {"type": "string", "description": "Payment ID to watch"}
                },
                "required": ["payment_id"]
            }
        ),
        types.Tool(
            name="check_balance",
            description="Check USDT balance in your distribution wallet",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="payment_history",
            description="Get list of recent payments (last 30 days)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "number", "description": "Number of payments to return (default 10)"}
                }
            }
        ),
        types.Tool(
            name="get_exchange_rate",
            description="Get current USDT/USD exchange rate",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    if not arguments:
        arguments = {}

    if name == "create_payment_link":
        amount = arguments.get("amount")
        description = arguments.get("description", "MCP Server Access")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://commerce.gotas.com/api/v1/payments",
                json={
                    "amount": str(amount),
                    "currency": "USDT",
                    "description": description,
                    "receive_address": USDT_ADDRESS,
                    "network": "BEP20"
                },
                headers={"X-API-Key": GOTAS_API_KEY},
            )
            data = response.json()
            return [types.TextContent(type="text", text=f"Payment link: {data.get('payment_url')}\nPayment ID: {data.get('id')}")]

    elif name == "check_payment_status":
        payment_id = arguments.get("payment_id")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://commerce.gotas.com/api/v1/payments/{payment_id}",
                headers={"X-API-Key": GOTAS_API_KEY},
            )
            data = response.json()
            return [types.TextContent(type="text", text=f"Status: {data.get('status')}\nAmount: {data.get('amount')} USDT\nPayment URL: {data.get('payment_url')}")]

    elif name == "wait_for_payment":
        payment_id = arguments.get("payment_id")
        max_attempts = 30  # 30 attempts * 10 seconds = 5 minutes total
        
        async with httpx.AsyncClient() as client:
            for attempt in range(max_attempts):
                response = await client.get(
                    f"https://commerce.gotas.com/api/v1/payments/{payment_id}",
                    headers={"X-API-Key": GOTAS_API_KEY},
                )
                data = response.json()
                status = data.get("status")
                
                if status == "completed":
                    return [types.TextContent(type="text", text=f"✅ Success! Payment {payment_id} is now COMPLETED on the blockchain.")]
                
                if status == "failed":
                    return [types.TextContent(type="text", text=f"❌ Payment {payment_id} FAILED.")]

                # Non-blocking wait for 10 seconds before the next check
                await asyncio.sleep(10)
            
            return [types.TextContent(type="text", text="⏳ Timeout: Payment is still pending after 5 minutes. Use check_payment_status later.")]

    elif name == "check_balance":
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://commerce.gotas.com/api/v1/payments",
                headers={"X-API-Key": GOTAS_API_KEY},
                params={"limit": 100}
            )
            data = response.json()
            
            if isinstance(data, dict) and "data" in data:
                payments = data["data"]
            elif isinstance(data, list):
                payments = data
            else:
                payments = []
            
            total_received = 0
            for p in payments:
                if p.get("status") == "completed":
                    try:
                        total_received += float(p.get("amount", 0))
                    except (ValueError, TypeError):
                        pass
            
            return [types.TextContent(type="text", text=f"USDT Balance: {total_received:.2f} USDT\n(Total from completed payments)")]

    elif name == "payment_history":
        limit = arguments.get("limit", 10)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://commerce.gotas.com/api/v1/payments",
                headers={"X-API-Key": GOTAS_API_KEY},
                params={"limit": limit}
            )
            data = response.json()
            
            if isinstance(data, dict) and "data" in data:
                payments = data["data"]
            elif isinstance(data, list):
                payments = data
            else:
                payments = []
            
            if payments:
                history_lines = []
                for p in payments[:limit]:
                    created = p.get("created_at", "")
                    date_part = created[:10] if created else "N/A"
                    amount = p.get("amount", "0")
                    status = p.get("status", "unknown")
                    description = p.get("description", "N/A")
                    history_lines.append(f"{date_part} | {status} | {amount} USDT | {description}")
                history_text = "\n".join(history_lines)
            else:
                history_text = "No payments found"
            
            return [types.TextContent(type="text", text=f"Recent Payments:\n{history_text}")]

    elif name == "get_exchange_rate":
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.coingecko.com/api/v3/simple/price",
                    params={
                        "ids": "tether",
                        "vs_currencies": "usd"
                    }
                )
                data = response.json()
                rate = data.get("tether", {}).get("usd", 1.00)
                return [types.TextContent(type="text", text=f"Current USDT/USD exchange rate: 1 USDT = ${rate:.4f} USD")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error fetching exchange rate: {str(e)}")]

    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gotas-commerce",
                server_version="1.1.0", # Bumped version to reflect changes
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
