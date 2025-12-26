#!/usr/bin/env python3
"""
Script to set up Telegram Bot webhook
"""
import asyncio
import os
import sys
from pathlib import Path

import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")

if not TELEGRAM_BOT_TOKEN:
    print("Error: TELEGRAM_BOT_TOKEN not found in environment variables")
    sys.exit(1)

if not TELEGRAM_WEBHOOK_URL:
    print("Error: TELEGRAM_WEBHOOK_URL not found in environment variables")
    sys.exit(1)


async def set_webhook():
    """Set up Telegram Bot webhook"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    
    data = {
        "url": TELEGRAM_WEBHOOK_URL,
        "allowed_updates": ["message", "callback_query", "my_chat_member"],
        "drop_pending_updates": True,
        "max_connections": 40,
        "secret_token": os.getenv("WEBHOOK_SECRET_TOKEN", "")
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json()
            
            if result.get("ok"):
                print(f"✅ Webhook set successfully!")
                print(f"   URL: {TELEGRAM_WEBHOOK_URL}")
                print(f"   Description: {result.get('description', 'N/A')}")
            else:
                print(f"❌ Failed to set webhook:")
                print(f"   Error: {result.get('description', 'Unknown error')}")
                return False
    
    return True


async def get_webhook_info():
    """Get current webhook information"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result = await response.json()
            
            if result.get("ok"):
                info = result.get("result", {})
                print("\n📋 Current webhook info:")
                print(f"   URL: {info.get('url', 'Not set')}")
                print(f"   Has custom certificate: {info.get('has_custom_certificate', False)}")
                print(f"   Pending updates: {info.get('pending_update_count', 0)}")
                print(f"   Last error date: {info.get('last_error_date', 'None')}")
                print(f"   Last error message: {info.get('last_error_message', 'None')}")
                print(f"   Max connections: {info.get('max_connections', 'Default')}")
                print(f"   Allowed updates: {info.get('allowed_updates', 'All')}")
            else:
                print(f"❌ Failed to get webhook info: {result.get('description')}")


async def delete_webhook():
    """Delete current webhook (for development/testing)"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    
    data = {"drop_pending_updates": True}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json()
            
            if result.get("ok"):
                print("✅ Webhook deleted successfully!")
            else:
                print(f"❌ Failed to delete webhook: {result.get('description')}")


async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python setup_webhook.py [set|info|delete]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "set":
        success = await set_webhook()
        if success:
            await get_webhook_info()
    elif command == "info":
        await get_webhook_info()
    elif command == "delete":
        await delete_webhook()
    else:
        print("Invalid command. Use: set, info, or delete")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())