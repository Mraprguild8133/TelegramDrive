import logging
import aiohttp
from typing import Optional
from config import GPLINKS_API_KEY, GPLINKS_BASE_URL

logger = logging.getLogger(__name__)

class URLShortener:
    """Handles URL shortening using GPLinks API."""
    
    def __init__(self):
        self.api_key = GPLINKS_API_KEY
        self.base_url = GPLINKS_BASE_URL
    
    def is_configured(self) -> bool:
        """Check if URL shortener is properly configured."""
        return bool(self.api_key and self.base_url)
    
    async def shorten_url(self, long_url: str, alias: str = None) -> Optional[str]:
        """Shorten a URL using GPLinks API."""
        if not self.is_configured():
            logger.warning("GPLinks not configured")
            return None
        
        try:
            # Validate URL format
            if not long_url.startswith(('http://', 'https://')):
                long_url = 'https://' + long_url
            
            # Prepare API request
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            payload = {
                'url': long_url,
                'domain': 'gplinks.com'  # Default domain
            }
            
            if alias:
                payload['alias'] = alias
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/shorten",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        short_url = data.get('shortenedUrl') or data.get('short_url') or data.get('url')
                        
                        if short_url:
                            logger.info(f"URL shortened successfully: {long_url} -> {short_url}")
                            return short_url
                        else:
                            logger.error("No shortened URL in response")
                            return None
                    
                    elif response.status == 401:
                        logger.error("GPLinks API authentication failed")
                        return None
                    
                    elif response.status == 422:
                        error_data = await response.json()
                        logger.error(f"GPLinks API validation error: {error_data}")
                        return None
                    
                    else:
                        logger.error(f"GPLinks API error: {response.status}")
                        return None
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error during URL shortening: {e}")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error during URL shortening: {e}")
            return None
    
    async def get_link_stats(self, short_url: str) -> Optional[dict]:
        """Get statistics for a shortened link."""
        if not self.is_configured():
            return None
        
        try:
            # Extract link ID from URL
            link_id = short_url.split('/')[-1]
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/links/{link_id}/stats",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'clicks': data.get('clicks', 0),
                            'unique_clicks': data.get('unique_clicks', 0),
                            'created_at': data.get('created_at'),
                            'original_url': data.get('original_url')
                        }
                    else:
                        logger.error(f"Failed to get link stats: {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"Error getting link stats: {e}")
            return None
    
    async def list_links(self, page: int = 1, limit: int = 10) -> list:
        """List user's shortened links."""
        if not self.is_configured():
            return []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Accept': 'application/json'
            }
            
            params = {
                'page': page,
                'limit': limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/links",
                    headers=headers,
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', [])
                    else:
                        logger.error(f"Failed to list links: {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"Error listing links: {e}")
            return []
    
    async def delete_link(self, link_id: str) -> bool:
        """Delete a shortened link."""
        if not self.is_configured():
            return False
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.base_url}/links/{link_id}",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        logger.info(f"Link deleted successfully: {link_id}")
                        return True
                    else:
                        logger.error(f"Failed to delete link: {response.status}")
                        return False
        
        except Exception as e:
            logger.error(f"Error deleting link: {e}")
            return False
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL for display purposes."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url[:30] + "..." if len(url) > 30 else url
