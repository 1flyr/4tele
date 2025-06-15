#!/usr/bin/env python3
"""
Render startup script for Skyy RAT Builder
"""

import os
import sys
import asyncio
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from builder_bot import main
except ImportError as e:
    logging.error(f"Failed to import builder_bot: {e}")
    logging.error("Make sure all dependencies are installed correctly")
    sys.exit(1)

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
    
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        exit(1)
