import logging
from typing import Optional, Dict, Any
from telegram import Bot, Message
from config import STORAGE_CHANNEL_ID
from storage.database import DatabaseManager
from utils.helpers import generate_file_id

logger = logging.getLogger(__name__)

class FileManager:
    """Manages file storage and retrieval operations."""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.storage_channel_id = STORAGE_CHANNEL_ID
    
    async def store_file_in_channel(
        self, 
        bot: Bot, 
        file_obj: Any, 
        file_id: str,
        filename: str,
        file_size: int,
        file_type: str
    ) -> Message:
        """Store file in Telegram storage channel."""
        try:
            # Create caption with file information
            caption = (
                f"📄 **File Storage**\n"
                f"🆔 ID: {file_id}\n"
                f"📝 Name: {filename}\n"
                f"📊 Size: {file_size} bytes\n"
                f"📁 Type: {file_type}\n"
                f"⏰ Uploaded: {file_id[:8]}"  # Use file_id prefix as timestamp reference
            )
            
            # Send file to storage channel based on type
            if file_type == 'document':
                message = await bot.send_document(
                    chat_id=self.storage_channel_id,
                    document=file_obj.file_id,
                    caption=caption,
                    parse_mode='Markdown'
                )
            elif file_type == 'photo':
                message = await bot.send_photo(
                    chat_id=self.storage_channel_id,
                    photo=file_obj.file_id,
                    caption=caption,
                    parse_mode='Markdown'
                )
            elif file_type == 'video':
                message = await bot.send_video(
                    chat_id=self.storage_channel_id,
                    video=file_obj.file_id,
                    caption=caption,
                    parse_mode='Markdown'
                )
            elif file_type == 'audio':
                message = await bot.send_audio(
                    chat_id=self.storage_channel_id,
                    audio=file_obj.file_id,
                    caption=caption,
                    parse_mode='Markdown'
                )
            else:
                # Fallback to document
                message = await bot.send_document(
                    chat_id=self.storage_channel_id,
                    document=file_obj.file_id,
                    caption=caption,
                    parse_mode='Markdown'
                )
            
            logger.info(f"File {file_id} stored in channel {self.storage_channel_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error storing file in channel: {e}")
            raise
    
    async def save_file_metadata(
        self,
        file_id: str,
        filename: str,
        file_size: int,
        file_type: str,
        message_id: int,
        channel_id: str
    ):
        """Save file metadata to database."""
        try:
            await self.db.insert_file(
                file_id=file_id,
                filename=filename,
                file_size=file_size,
                file_type=file_type,
                message_id=message_id,
                channel_id=channel_id
            )
            logger.info(f"File metadata saved for {file_id}")
        except Exception as e:
            logger.error(f"Error saving file metadata: {e}")
            raise
    
    async def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file information from database."""
        try:
            return await self.db.get_file_by_id(file_id)
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None
    
    async def list_user_files(self, user_id: int, limit: int = 10) -> list:
        """List files uploaded by a specific user."""
        try:
            return await self.db.get_user_files(user_id, limit)
        except Exception as e:
            logger.error(f"Error listing user files: {e}")
            return []
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file from storage and database."""
        try:
            # Get file info first
            file_info = await self.get_file_info(file_id)
            if not file_info:
                return False
            
            # Delete from database
            await self.db.delete_file(file_id)
            
            # Note: We don't delete from Telegram channel to maintain message integrity
            # The file will remain in the channel but won't be accessible via bot
            
            logger.info(f"File {file_id} deleted from database")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    async def get_file_stats(self) -> Dict[str, Any]:
        """Get file storage statistics."""
        try:
            return await self.db.get_file_stats()
        except Exception as e:
            logger.error(f"Error getting file stats: {e}")
            return {
                'total_files': 0,
                'total_size': 0,
                'file_types': {}
            }
