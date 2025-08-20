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

    def set_webhook():
    """Set webhook URL for the bot"""
    try:
        webhook_url = request.json.get('url') if request.json else None
        if not webhook_url:
            return jsonify({'error': 'URL is required'}), 400
        
        success = bot.set_webhook(webhook_url)
        if success:
            return jsonify({'status': 'Webhook set successfully'})
        else:
            return jsonify({'error': 'Failed to set webhook'}), 500
    except Exception as e:
        logger.error(f"Set webhook error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/stats', methods=['GET'])
def stats():
    """Get bot statistics"""
    try:
        stats = bot.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({'error': 'Failed to get stats'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask app on port {port}")
    logger.info(f"Bot @{bot.bot_username} is ready to receive messages")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise

if __name__ == '__main__':
    main()
