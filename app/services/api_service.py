"""
API Service module for handling all API-related operations.
Separates API communication logic from the main application.
"""

import requests
import os
from typing import Optional, Dict, Any, Tuple
from PIL import Image
import io
import json
from app.config import config

class APIService:
    """Service class for handling API communications."""
    
    def __init__(self):
        self.base_url = config.API_BASE_URL
        self.timeout = config.REQUEST_TIMEOUT
    
    def check_health(self) -> bool:
        """
        Check if the API is healthy and responding.
        
        Returns:
            bool: True if API is healthy, False otherwise
        """
        try:
            response = requests.get(
                config.get_api_url("/"), 
                timeout=config.HEALTH_CHECK_TIMEOUT
            )
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
        except Exception:
            return False
    
    def predict_mask(self, image_path: str) -> Tuple[Optional[Image.Image], Optional[Dict[str, Any]]]:
        """
        Send an image to the API for segmentation prediction.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Tuple[Optional[Image.Image], Optional[Dict]]: 
                - Predicted mask image
                - Response metadata (processing time, file size, etc.)
        """
        try:
            # Validate image file
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            file_size = os.path.getsize(image_path)
            
            # Check file size
            if file_size > config.MAX_FILE_SIZE_MB * 1024 * 1024:
                raise ValueError(f"Image file is too large. Max size: {config.MAX_FILE_SIZE_MB}MB")
            
            # Prepare the request
            with open(image_path, "rb") as f:
                files = {"file": ("image.png", f, "image/png")}
                
                response = requests.post(
                    config.get_api_url("/api/segment"),
                    files=files,
                    timeout=self.timeout
                )
            
            # Handle response
            if response.status_code == 200:
                # Parse response metadata
                metadata = self._parse_response_metadata(response, file_size)
                
                # Convert response content to PIL Image
                mask_image = Image.open(io.BytesIO(response.content))
                
                return mask_image, metadata
                
            elif response.status_code == 500:
                raise Exception(f"Server Error (500): {response.text}")
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            raise Exception(f"Connection error: Could not connect to API at {self.base_url}")
        except requests.exceptions.Timeout:
            raise Exception("Request timeout: The API request took too long to complete")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def _parse_response_metadata(self, response: requests.Response, file_size: int) -> Dict[str, Any]:
        """
        Parse metadata from API response headers.
        
        Args:
            response (requests.Response): API response
            file_size (int): Original file size
            
        Returns:
            Dict[str, Any]: Parsed metadata
        """
        metadata = {
            'file_size': file_size,
            'status_code': response.status_code,
            'headers': dict(response.headers)
        }
        
        # Parse image statistics
        if 'x-image-stats' in response.headers:
            try:
                metadata['image_stats'] = json.loads(response.headers['x-image-stats'])
            except json.JSONDecodeError:
                metadata['image_stats'] = response.headers['x-image-stats']
        
        # Parse processing time
        if 'x-processing-time' in response.headers:
            metadata['processing_time'] = response.headers['x-processing-time']
        
        return metadata

# Global API service instance
api_service = APIService()
