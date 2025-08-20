from telegram import Update
from telegram.ext import ContextTypes
from services.url_shortener import URLShortener
from services.gemini_ai import GeminiAI
from utils.helpers import format_file_size
import logging

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = """
🚀 *Welcome to the Ultimate File Manager Bot!*

I can help you with:

📁 *File Management:*
• Upload files up to 5GB
• Download files with unique IDs
• Store files in Telegram channels for fast access
• Support all file formats

🔗 *URL Shortening:*
• Shorten long URLs using GPLinks

☁️ *Google Drive Integration:*
• Upload private files to your Google Drive
• Secure file storage with your credentials

🤖 *AI Assistant:*
• Get help with file analysis
• Ask questions about your files
• Powered by Gemini AI

*Commands:*
/help - Show detailed help
/upload - Upload a file
/download `<file_id>` - Download a file
/short `<url>` - Shorten a URL
/ai `<question>` - Ask AI assistant

Just send me any file to get started! 📎
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    help_text = """
📖 *Detailed Help Guide*

*File Operations:*
• Send any file (up to 5GB) to upload automatically
• Use /download `<file_id>` to retrieve files
• Files are stored in secure Telegram channels

*URL Shortening:*
• /short https://example.com/very/long/url
• Get shortened GPLinks URLs instantly

*Google Drive Upload:*
• Private files automatically uploaded to your Drive
• Requires Google Drive API credentials

*AI Assistant:*
• /ai What is this file about?
• /ai Analyze this document
• /ai Help me understand this image

*File Formats Supported:*
Documents, Images, Videos, Audio, Archives, Applications, and more!

*File Size Limit:* Up to 5GB per file

Need more help? Just ask the AI assistant! 🤖
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle upload command."""
    await update.message.reply_text(
        "📎 **Ready to Upload!**\n\n"
        "Simply send me any file and I'll:\n"
        "• Store it securely in Telegram channels\n"
        "• Provide you with a unique file ID\n"
        "• Upload to Google Drive if configured\n\n"
        "Maximum file size: 5GB"
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle download command."""
    if not context.args:
        await update.message.reply_text(
            "❌ **Missing File ID**\n\n"
            "Usage: `/download <file_id>`\n"
            "Example: `/download ABC123`"
        )
        return

    file_id = context.args[0]
    
    # Import here to avoid circular imports
    from services.file_manager import FileManager
    
    try:
        file_manager = FileManager()
        file_info = await file_manager.get_file_info(file_id)
        
        if not file_info:
            await update.message.reply_text(
                f"❌ **File Not Found**\n\n"
                f"No file found with ID: `{file_id}`"
            )
            return

        # Forward the file from storage channel
        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=file_info['channel_id'],
            message_id=file_info['message_id']
        )
        
        await update.message.reply_text(
            f"✅ **File Retrieved Successfully!**\n\n"
            f"📄 **Name:** {file_info['filename']}\n"
            f"📊 **Size:** {format_file_size(file_info['file_size'])}\n"
            f"🆔 **ID:** `{file_id}`"
        )

    except Exception as e:
        logger.error(f"Download error: {e}")
        await update.message.reply_text(
            "❌ **Download Failed**\n\n"
            "An error occurred while retrieving the file. Please try again."
        )

async def shorten_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL shortening command."""
    if not context.args:
        await update.message.reply_text(
            "❌ **Missing URL**\n\n"
            "Usage: `/short <url>`\n"
            "Example: `/short https://example.com/very/long/url`"
        )
        return

    url = ' '.join(context.args)
    
    try:
        url_shortener = URLShortener()
        short_url = await url_shortener.shorten_url(url)
        
        await update.message.reply_text(
            f"✅ **URL Shortened Successfully!**\n\n"
            f"🔗 **Original:** {url}\n"
            f"🔗 **Shortened:** {short_url}\n\n"
            f"Click to copy: `{short_url}`",
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"URL shortening error: {e}")
        await update.message.reply_text(
            "❌ **URL Shortening Failed**\n\n"
            "Please check if the URL is valid and try again."
        )

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle AI chat command."""
    if not context.args:
        await update.message.reply_text(
            "🤖 **AI Assistant Ready!**\n\n"
            "Ask me anything about your files or get general help!\n\n"
            "Usage: `/ai <your question>`\n"
            "Example: `/ai What is this document about?`"
        )
        return

    question = ' '.join(context.args)
    
    try:
        # Show typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action='typing'
        )
        
        gemini_ai = GeminiAI()
        response = await gemini_ai.chat(question)
        
        await update.message.reply_text(
            f"🤖 **AI Assistant Response:**\n\n{response}",
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"AI chat error: {e}")
        await update.message.reply_text(
            "❌ **AI Assistant Error**\n\n"
            "I'm having trouble processing your request. Please try again."
        )
