#!/usr/bin/env python3
"""
Telegram Group Manager Bot - Main Entry Point

This module serves as the main entry point for the Telegram group manager bot application.
It initializes and runs the bot with all necessary handlers and configurations.
"""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update, context):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Welcome to Telegram Group Manager Bot! 🤖\n\n"
        "Use /help to see available commands."
    )


async def help_command(update, context):
    """Send a message when the command /help is issued."""
    help_text = """
Available Commands:
/start - Start the bot
/help - Show this help message
/info - Get bot information

For more information, visit our documentation.
    """
    await update.message.reply_text(help_text)


async def info(update, context):
    """Send bot information."""
    await update.message.reply_text(
        "Telegram Group Manager Bot v1.0\n\n"
        "A powerful bot for managing Telegram groups effectively."
    )


def main():
    """Start the bot."""
    # Get token from environment variables
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info))
    
    # Start the Bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=["message", "edited_message"])


if __name__ == '__main__':
    main()
