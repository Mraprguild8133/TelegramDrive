import json
import logging
import os
from google import genai
from google.genai import types
from typing import Optional, Any
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

class GeminiAI:
    """Handles AI assistant functionality using Gemini."""
    
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client."""
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini AI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None
        else:
            logger.warning("Gemini API key not configured")
    
    def is_configured(self) -> bool:
        """Check if Gemini AI is properly configured."""
        return self.client is not None
    
    async def chat(self, message: str, context: str = None) -> str:
        """General chat with AI assistant."""
        if not self.is_configured():
            return "❌ AI Assistant not configured. Please check API key."
        
        try:
            # Build prompt with context if provided
            full_prompt = message
            if context:
                full_prompt = f"Context: {context}\n\nUser question: {message}"
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt
            )
            
            return response.text or "Sorry, I couldn't process your request."
            
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            return f"❌ AI Assistant error: {str(e)}"
    
    async def analyze_file(self, file_obj: Any, file_type: str) -> Optional[str]:
        """Analyze uploaded file with AI."""
        if not self.is_configured():
            return None
        
        try:
            if file_type == 'photo':
                return await self._analyze_image(file_obj)
            elif file_type == 'document':
                return await self._analyze_document(file_obj)
            elif file_type == 'video':
                return await self._analyze_video(file_obj)
            else:
                return await self._analyze_general_file(file_obj, file_type)
                
        except Exception as e:
            logger.error(f"File analysis error: {e}")
            return None
    
    async def _analyze_image(self, photo_obj) -> str:
        """Analyze image file."""
        try:
            # Note: In real implementation, you'd download the file first
            # This is a placeholder for the analysis logic
            
            analysis_prompt = (
                "Analyze this image and provide:\n"
                "1. Description of what you see\n"
                "2. Key objects or elements\n"
                "3. Potential use cases\n"
                "4. Any text visible in the image"
            )
            
            # For now, return a general analysis since we can't access the actual image
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=f"Provide a template analysis for an uploaded image: {analysis_prompt}"
            )
            
            return response.text or "Could not analyze image."
            
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return "Failed to analyze image."
    
    async def _analyze_document(self, document_obj) -> str:
        """Analyze document file."""
        try:
            filename = getattr(document_obj, 'file_name', 'unknown')
            file_extension = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
            
            analysis_prompt = (
                f"This is a {file_extension} document named '{filename}'. "
                "Provide insights about:\n"
                "1. Likely content type based on filename\n"
                "2. Common use cases for this file type\n"
                "3. Recommended handling or viewing methods\n"
                "4. File format characteristics"
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=analysis_prompt
            )
            
            return response.text or "Could not analyze document."
            
        except Exception as e:
            logger.error(f"Document analysis error: {e}")
            return "Failed to analyze document."
    
    async def _analyze_video(self, video_obj) -> str:
        """Analyze video file."""
        try:
            # Note: Video analysis would require downloading and processing the file
            # This is a placeholder implementation
            
            file_size = getattr(video_obj, 'file_size', 0)
            duration = getattr(video_obj, 'duration', 0)
            
            analysis_prompt = (
                f"This is a video file with size {file_size} bytes and duration {duration} seconds. "
                "Provide insights about:\n"
                "1. Video characteristics\n"
                "2. Potential content type\n"
                "3. Recommended viewing or editing tools\n"
                "4. File handling suggestions"
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=analysis_prompt
            )
            
            return response.text or "Could not analyze video."
            
        except Exception as e:
            logger.error(f"Video analysis error: {e}")
            return "Failed to analyze video."
    
    async def _analyze_general_file(self, file_obj, file_type: str) -> str:
        """Analyze general file types."""
        try:
            filename = getattr(file_obj, 'file_name', f"{file_type}_file")
            file_size = getattr(file_obj, 'file_size', 0)
            
            analysis_prompt = (
                f"This is a {file_type} file named '{filename}' with size {file_size} bytes. "
                "Provide useful information about:\n"
                "1. File type characteristics\n"
                "2. Common applications that use this format\n"
                "3. Best practices for handling this file type\n"
                "4. Potential security considerations"
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=analysis_prompt
            )
            
            return response.text or "Could not analyze file."
            
        except Exception as e:
            logger.error(f"General file analysis error: {e}")
            return "Failed to analyze file."
    
    async def summarize_content(self, content: str, max_length: int = 200) -> str:
        """Summarize long content."""
        if not self.is_configured():
            return content[:max_length] + "..." if len(content) > max_length else content
        
        try:
            prompt = (
                f"Summarize the following content in {max_length} characters or less, "
                f"maintaining key information:\n\n{content}"
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            summary = response.text or content
            
            # Ensure it doesn't exceed max length
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"Content summarization error: {e}")
            return content[:max_length] + "..." if len(content) > max_length else content
    
    async def help_with_file_operations(self, operation: str, file_info: dict = None) -> str:
        """Provide help with file operations."""
        if not self.is_configured():
            return "AI Assistant not available for help."
        
        try:
            context = f"File operation: {operation}"
            if file_info:
                context += f"\nFile details: {json.dumps(file_info, indent=2)}"
            
            help_prompt = (
                f"{context}\n\n"
                "Provide helpful guidance for this file operation, including:\n"
                "1. Step-by-step instructions\n"
                "2. Common issues and solutions\n"
                "3. Best practices\n"
                "4. Alternative approaches if applicable"
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=help_prompt
            )
            
            return response.text or "Unable to provide help at this time."
            
        except Exception as e:
            logger.error(f"Help generation error: {e}")
            return f"Error generating help: {str(e)}"
