import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.commands import start, help_command, upload, download, shorten_url, ai_chat
from bot.handlers import handle_document, handle_photo, handle_video, handle_audio
from config import BOT_TOKEN

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    import asyncio
    
    # Set up event loop for Windows/Linux compatibility
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("upload", upload))
    application.add_handler(CommandHandler("download", download))
    application.add_handler(CommandHandler("short", shorten_url))
    application.add_handler(CommandHandler("ai", ai_chat))

    # Register message handlers
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))

    # Start the bot
    logger.info("Starting bot...")
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        bot.stop_polling()
