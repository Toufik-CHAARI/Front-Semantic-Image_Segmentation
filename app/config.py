"""
Configuration module for the Streamlit Semantic Image Segmentation application.
Centralizes all configuration settings and environment variables.
"""

import os
import streamlit as st
from typing import Optional

class Config:
    """Configuration class to manage all application settings."""
    
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://13.36.249.197:8000")
    
    # Data Paths
    ORIGINAL_IMAGES_DIR = os.getenv("ORIGINAL_IMAGES_DIR", "leftImg8bit/val/frankfurt")
    GROUND_TRUTH_DIR = os.getenv("GROUND_TRUTH_DIR", "gtFine/val/frankfurt")
    
    # AWS Configuration
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "eu-west-3")
    DVC_S3_BUCKET = os.getenv("DVC_S3_BUCKET", "frontend-semantic-image-segmentation")
    
    # Application Settings
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))
    HEALTH_CHECK_TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", "10"))
    
    # UI Configuration
    PAGE_TITLE = "Semantic Image Segmentation"
    PAGE_ICON = "🎯"
    LAYOUT = "wide"
    
    @classmethod
    def get_api_url(cls, endpoint: str = "") -> str:
        """Get the full API URL for a given endpoint."""
        return f"{cls.API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present."""
        required_vars = [
            cls.API_BASE_URL,
            cls.ORIGINAL_IMAGES_DIR,
            cls.GROUND_TRUTH_DIR
        ]
        return all(var for var in required_vars)

# Global configuration instance
config = Config()
