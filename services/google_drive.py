import logging
import os
import io
from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from config import GOOGLE_DRIVE_CLIENT_ID, GOOGLE_DRIVE_CLIENT_SECRET

logger = logging.getLogger(__name__)

class GoogleDriveManager:
    """Manages Google Drive integration for file uploads."""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self):
        self.client_id = GOOGLE_DRIVE_CLIENT_ID
        self.client_secret = GOOGLE_DRIVE_CLIENT_SECRET
        self.service = None
    
    def is_configured(self) -> bool:
        """Check if Google Drive is properly configured."""
        return bool(self.client_id and self.client_secret)
    
    async def initialize_service(self, credentials_data: dict = None):
        """Initialize Google Drive service with credentials."""
        try:
            if credentials_data:
                credentials = Credentials.from_authorized_user_info(
                    credentials_data, self.SCOPES
                )
            else:
                # For now, we'll use a simple service account approach
                # In production, you'd implement proper OAuth2 flow
                credentials = self._get_default_credentials()
            
            if credentials:
                self.service = build('drive', 'v3', credentials=credentials)
                logger.info("Google Drive service initialized successfully")
                return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {e}")
            
        return False
    
    def _get_default_credentials(self):
        """Get default credentials - simplified for demo."""
        # In a real implementation, you'd handle proper OAuth2 flow
        # This is a placeholder that returns None to indicate no credentials
        return None
    
    async def upload_file(self, file_obj, filename: str, folder_id: str = None) -> Optional[str]:
        """Upload file to Google Drive."""
        if not self.is_configured():
            logger.warning("Google Drive not configured")
            return None
        
        try:
            if not self.service:
                if not await self.initialize_service():
                    return None
            
            # Download file from Telegram
            file_content = await self._download_telegram_file(file_obj)
            if not file_content:
                return None
            
            # Prepare file metadata
            file_metadata = {
                'name': filename
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Create media upload
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype='application/octet-stream',
                resumable=True
            )
            
            # Upload file
            file_result = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            file_id = file_result.get('id')
            web_link = file_result.get('webViewLink')
            
            # Make file publicly accessible (optional)
            try:
                self.service.permissions().create(
                    fileId=file_id,
                    body={
                        'role': 'reader',
                        'type': 'anyone'
                    }
                ).execute()
                
                # Get public sharing link
                public_link = f"https://drive.google.com/file/d/{file_id}/view"
                
            except Exception as e:
                logger.warning(f"Failed to make file public: {e}")
                public_link = web_link
            
            logger.info(f"File uploaded to Google Drive: {public_link}")
            return public_link
            
        except Exception as e:
            logger.error(f"Google Drive upload error: {e}")
            return None
    
    async def _download_telegram_file(self, file_obj) -> Optional[bytes]:
        """Download file from Telegram."""
        try:
            # This would need to be implemented with the actual bot instance
            # For now, return None to indicate file not available
            logger.warning("Telegram file download not implemented in this context")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading Telegram file: {e}")
            return None
    
    async def create_folder(self, folder_name: str, parent_folder_id: str = None) -> Optional[str]:
        """Create a folder in Google Drive."""
        if not self.service:
            return None
        
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            logger.info(f"Created folder {folder_name} with ID: {folder_id}")
            return folder_id
            
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            return None
    
    async def list_files(self, folder_id: str = None, max_results: int = 10) -> list:
        """List files in Google Drive."""
        if not self.service:
            return []
        
        try:
            query = "trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                pageSize=max_results,
                fields="nextPageToken, files(id, name, size, mimeType, webViewLink)"
            ).execute()
            
            items = results.get('files', [])
            return items
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file from Google Drive."""
        if not self.service:
            return False
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted file from Google Drive: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file from Google Drive: {e}")
            return False
