from telegram import Update
from telegram.ext import ContextTypes
from services.file_manager import FileManager
from services.google_drive import GoogleDriveManager
from services.gemini_ai import GeminiAI
from config import MAX_FILE_SIZE
from utils.helpers import generate_file_id, format_file_size
import logging

logger = logging.getLogger(__name__)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads."""
    document = update.message.document
    await process_file_upload(update, context, document, 'document')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads."""
    photo = update.message.photo[-1]  # Get highest quality photo
    await process_file_upload(update, context, photo, 'photo')

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video uploads."""
    video = update.message.video
    await process_file_upload(update, context, video, 'video')

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle audio uploads."""
    audio = update.message.audio
    await process_file_upload(update, context, audio, 'audio')

async def process_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE, file_obj, file_type):
    """Process file upload with comprehensive handling."""
    try:
        # Get file information
        file_size = getattr(file_obj, 'file_size', 0)
        filename = getattr(file_obj, 'file_name', f"{file_type}_{file_obj.file_id}")
        
        # Check file size limit
        if file_size > MAX_FILE_SIZE:
            await update.message.reply_text(
                f"❌ **File Too Large**\n\n"
                f"File size: {format_file_size(file_size)}\n"
                f"Maximum allowed: {format_file_size(MAX_FILE_SIZE)}\n\n"
                f"Please upload a smaller file."
            )
            return

        # Send processing message
        processing_msg = await update.message.reply_text(
            "⏳ **Processing File Upload...**\n\n"
            f"📄 **Name:** {filename}\n"
            f"📊 **Size:** {format_file_size(file_size)}\n"
            f"📁 **Type:** {file_type.title()}\n\n"
            "Please wait while I upload and process your file..."
        )

        # Initialize file manager
        file_manager = FileManager()
        
        # Generate unique file ID
        file_id = generate_file_id()
        
        # Store file in Telegram channel
        stored_message = await file_manager.store_file_in_channel(
            context.bot, file_obj, file_id, filename, file_size, file_type
        )
        
        # Save file metadata to database
        await file_manager.save_file_metadata(
            file_id, filename, file_size, file_type, 
            stored_message.message_id, stored_message.chat.id
        )

        # Upload to Google Drive if configured
        google_drive_link = None
        try:
            google_drive = GoogleDriveManager()
            if google_drive.is_configured():
                google_drive_link = await google_drive.upload_file(file_obj, filename)
        except Exception as e:
            logger.warning(f"Google Drive upload failed: {e}")

        # Analyze file with AI if it's an image or document
        ai_analysis = None
        try:
            if file_type in ['photo', 'document']:
                gemini_ai = GeminiAI()
                ai_analysis = await gemini_ai.analyze_file(file_obj, file_type)
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")

        # Update success message
        success_message = (
            f"✅ **File Uploaded Successfully!**\n\n"
            f"📄 **Name:** {filename}\n"
            f"📊 **Size:** {format_file_size(file_size)}\n"
            f"📁 **Type:** {file_type.title()}\n"
            f"🆔 **File ID:** `{file_id}`\n\n"
            f"**Download:** `/download {file_id}`\n"
        )

        if google_drive_link:
            success_message += f"☁️ **Google Drive:** [View File]({google_drive_link})\n"

        if ai_analysis:
            success_message += f"\n🤖 **AI Analysis:**\n{ai_analysis[:200]}..."

        success_message += (
            f"\n\n💡 **Quick Actions:**\n"
            f"• Forward this file to others\n"
            f"• Ask AI about this file: `/ai analyze {file_id}`\n"
            f"• Download anytime with the file ID"
        )

        await processing_msg.edit_text(success_message, parse_mode='Markdown')

        # Forward original message for easy access
        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )

    except Exception as e:
        logger.error(f"File upload error: {e}")
        await update.message.reply_text(
            "❌ **Upload Failed**\n\n"
            "An error occurred while uploading your file. Please try again."
        )
