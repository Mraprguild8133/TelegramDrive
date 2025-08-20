import sqlite3
import asyncio
import aiosqlite
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from config import DATABASE_PATH
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database for file storage metadata."""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self._ensure_database_directory()
    
    def _ensure_database_directory(self):
        """Ensure database directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    async def initialize_database(self):
        """Initialize database with required tables."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Files table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_id TEXT UNIQUE NOT NULL,
                        filename TEXT NOT NULL,
                        file_size INTEGER NOT NULL,
                        file_type TEXT NOT NULL,
                        mime_type TEXT,
                        message_id INTEGER NOT NULL,
                        channel_id TEXT NOT NULL,
                        user_id INTEGER,
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        download_count INTEGER DEFAULT 0,
                        google_drive_link TEXT,
                        is_private BOOLEAN DEFAULT 0,
                        is_deleted BOOLEAN DEFAULT 0
                    )
                ''')
                
                # URL shortening table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS shortened_urls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        original_url TEXT NOT NULL,
                        short_url TEXT UNIQUE NOT NULL,
                        alias TEXT,
                        user_id INTEGER,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        click_count INTEGER DEFAULT 0,
                        is_active BOOLEAN DEFAULT 1
                    )
                ''')
                
                # User sessions table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_uploads INTEGER DEFAULT 0,
                        total_downloads INTEGER DEFAULT 0,
                        storage_used INTEGER DEFAULT 0
                    )
                ''')
                
                # AI interactions table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS ai_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        query TEXT NOT NULL,
                        response TEXT NOT NULL,
                        interaction_type TEXT,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                await db.execute('CREATE INDEX IF NOT EXISTS idx_files_file_id ON files(file_id)')
                await db.execute('CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id)')
                await db.execute('CREATE INDEX IF NOT EXISTS idx_urls_short_url ON shortened_urls(short_url)')
                await db.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)')
                
                await db.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    async def insert_file(
        self,
        file_id: str,
        filename: str,
        file_size: int,
        file_type: str,
        message_id: int,
        channel_id: str,
        user_id: int = None,
        mime_type: str = None,
        google_drive_link: str = None,
        is_private: bool = False
    ):
        """Insert file record into database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO files 
                    (file_id, filename, file_size, file_type, message_id, channel_id, 
                     user_id, mime_type, google_drive_link, is_private)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_id, filename, file_size, file_type, message_id, channel_id,
                    user_id, mime_type, google_drive_link, is_private
                ))
                await db.commit()
                
                # Update user stats
                if user_id:
                    await self._update_user_stats(db, user_id, upload_increment=1, storage_increment=file_size)
                
                logger.info(f"File record inserted: {file_id}")
                
        except Exception as e:
            logger.error(f"Error inserting file record: {e}")
            raise
    
    async def get_file_by_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file information by file ID."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM files WHERE file_id = ? AND is_deleted = 0',
                    (file_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
                    
        except Exception as e:
            logger.error(f"Error getting file by ID: {e}")
            return None
    
    async def update_download_count(self, file_id: str, user_id: int = None):
        """Update download count for a file."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'UPDATE files SET download_count = download_count + 1 WHERE file_id = ?',
                    (file_id,)
                )
                
                # Update user download stats
                if user_id:
                    await self._update_user_stats(db, user_id, download_increment=1)
                
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error updating download count: {e}")
    
    async def get_user_files(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get files uploaded by a specific user."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM files 
                    WHERE user_id = ? AND is_deleted = 0
                    ORDER BY upload_date DESC 
                    LIMIT ? OFFSET ?
                ''', (user_id, limit, offset)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
                    
        except Exception as e:
            logger.error(f"Error getting user files: {e}")
            return []
    
    async def delete_file(self, file_id: str) -> bool:
        """Mark file as deleted (soft delete)."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    'UPDATE files SET is_deleted = 1 WHERE file_id = ?',
                    (file_id,)
                )
                await db.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    async def insert_shortened_url(
        self,
        original_url: str,
        short_url: str,
        user_id: int = None,
        alias: str = None
    ):
        """Insert shortened URL record."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO shortened_urls (original_url, short_url, alias, user_id)
                    VALUES (?, ?, ?, ?)
                ''', (original_url, short_url, alias, user_id))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error inserting shortened URL: {e}")
            raise
    
    async def get_file_stats(self) -> Dict[str, Any]:
        """Get file storage statistics."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total files and size
                async with db.execute(
                    'SELECT COUNT(*), SUM(file_size) FROM files WHERE is_deleted = 0'
                ) as cursor:
                    total_files, total_size = await cursor.fetchone()
                
                # File types distribution
                async with db.execute('''
                    SELECT file_type, COUNT(*) as count 
                    FROM files WHERE is_deleted = 0 
                    GROUP BY file_type
                ''') as cursor:
                    file_types = {row[0]: row[1] for row in await cursor.fetchall()}
                
                return {
                    'total_files': total_files or 0,
                    'total_size': total_size or 0,
                    'file_types': file_types
                }
                
        except Exception as e:
            logger.error(f"Error getting file stats: {e}")
            return {
                'total_files': 0,
                'total_size': 0,
                'file_types': {}
            }
    
    async def upsert_user_session(
        self,
        user_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None
    ):
        """Insert or update user session."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO user_sessions 
                    (user_id, username, first_name, last_name, last_activity,
                     total_uploads, total_downloads, storage_used)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP,
                           COALESCE((SELECT total_uploads FROM user_sessions WHERE user_id = ?), 0),
                           COALESCE((SELECT total_downloads FROM user_sessions WHERE user_id = ?), 0),
                           COALESCE((SELECT storage_used FROM user_sessions WHERE user_id = ?), 0))
                ''', (user_id, username, first_name, last_name, user_id, user_id, user_id))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error upserting user session: {e}")
    
    async def _update_user_stats(
        self,
        db: aiosqlite.Connection,
        user_id: int,
        upload_increment: int = 0,
        download_increment: int = 0,
        storage_increment: int = 0
    ):
        """Update user statistics."""
        try:
            await db.execute('''
                INSERT OR IGNORE INTO user_sessions (user_id) VALUES (?)
            ''', (user_id,))
            
            await db.execute('''
                UPDATE user_sessions 
                SET total_uploads = total_uploads + ?,
                    total_downloads = total_downloads + ?,
                    storage_used = storage_used + ?,
                    last_activity = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (upload_increment, download_increment, storage_increment, user_id))
            
        except Exception as e:
            logger.error(f"Error updating user stats: {e}")
    
    async def log_ai_interaction(
        self,
        user_id: int,
        query: str,
        response: str,
        interaction_type: str = 'general'
    ):
        """Log AI interaction for analytics."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO ai_interactions (user_id, query, response, interaction_type)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, query, response, interaction_type))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error logging AI interaction: {e}")

# Initialize database on import
async def init_db():
    """Initialize database on startup."""
    db_manager = DatabaseManager()
    await db_manager.initialize_database()

# Run initialization
try:
    asyncio.run(init_db())
except RuntimeError:
    # If event loop is already running (e.g., in Jupyter), create task instead
    pass
