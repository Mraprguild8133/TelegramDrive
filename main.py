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

    # Start the Bot
    # Choose between polling or webhook based on environment
    
    # For production with webhook
    if os.environ.get('USE_WEBHOOK', 'False').lower() == 'true':
        webhook_url = os.environ.get('WEBHOOK_URL')
        port = int(os.environ.get('PORT', 5000))
        
        if not webhook_url:
            logger.error("WEBHOOK_URL environment variable is required when using webhook")
            return
            
        # Set webhook
        async def set_webhook():
            await application.bot.set_webhook(webhook_url)
        
        # Start webhook server
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url
        )
    else:
        # For development with polling
        application.run_polling()

if __name__ == '__main__':
    main()
