#!/usr/bin/env python3
import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

GOTAS_API_KEY = os.getenv("GOTAS_API_KEY")
USDT_ADDRESS = os.getenv("USDT_ADDRESS")

def handle_request(request):
    """Handle JSON-RPC requests from MCP client - PUBLIC VERSION (5 tools)"""
    
    if request.get("method") == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": [
                    {
                        "name": "create_payment_link",
                        "description": "Create a USDT payment link. The client pays and you receive USDT.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "amount": {"type": "number", "description": "Amount in USDT"},
                                "description": {"type": "string", "description": "Payment description"}
                            },
                            "required": ["amount"]
                        }
                    },
                    {
                        "name": "check_payment_status",
                        "description": "Check if a payment has been completed",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "payment_id": {"type": "string", "description": "Payment ID from create_payment_link"}
                            },
                            "required": ["payment_id"]
                        }
                    },
                    {
                        "name": "check_balance",
                        "description": "Check USDT balance in your distribution wallet",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "payment_history",
                        "description": "Get list of recent payments (last 30 days)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "limit": {"type": "number", "description": "Number of payments to return (default 10)"}
                            }
                        }
                    },
                    {
                        "name": "get_exchange_rate",
                        "description": "Get current USDT/USD exchange rate",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        }
    
    elif request.get("method") == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "create_payment_link":
            amount = args.get("amount")
            description = args.get("description", "MCP Server Access")
            
            with httpx.Client() as client:
                response = client.post(
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
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Payment link: {data.get('payment_url')}\nPayment ID: {data.get('id')}"
                            }
                        ]
                    }
                }
        
        elif tool_name == "check_payment_status":
            payment_id = args.get("payment_id")
            
            with httpx.Client() as client:
                response = client.get(
                    f"https://commerce.gotas.com/api/v1/payments/{payment_id}",
                    headers={"X-API-Key": GOTAS_API_KEY},
                )
                data = response.json()
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Status: {data.get('status')}\nAmount: {data.get('amount')} USDT\nPayment URL: {data.get('payment_url')}"
                            }
                        ]
                    }
                }
        
        elif tool_name == "check_balance":
            with httpx.Client() as client:
                response = client.get(
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
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"USDT Balance: {total_received:.2f} USDT\n(Total from completed payments)"
                            }
                        ]
                    }
                }
        
        elif tool_name == "payment_history":
            limit = args.get("limit", 10)
            
            with httpx.Client() as client:
                response = client.get(
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
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Recent Payments:\n{history_text}"
                            }
                        ]
                    }
                }
        
        elif tool_name == "get_exchange_rate":
            try:
                with httpx.Client() as client:
                    response = client.get(
                        "https://api.coingecko.com/api/v3/simple/price",
                        params={
                            "ids": "tether",
                            "vs_currencies": "usd"
                        }
                    )
                    data = response.json()
                    rate = data.get("tether", {}).get("usd", 1.00)
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Current USDT/USD exchange rate: 1 USDT = ${rate:.4f} USD"
                                }
                            ]
                        }
                    }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error fetching exchange rate: {str(e)}"
                            }
                        ]
                    }
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
            }
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -32601, "message": f"Method not found: {request.get('method')}"}
        }

def main():
    import sys
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32000, "message": str(e)}
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()
