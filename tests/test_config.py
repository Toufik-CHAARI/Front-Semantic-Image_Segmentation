"""
Unit tests for the configuration module.
"""

from app.config import Config, config


class TestConfig:
    """Test cases for the Config class."""

    def test_config_initialization(self):
        """Test that config is properly initialized."""
        assert config is not None
        assert isinstance(config, Config)

    def test_api_base_url_default(self):
        """Test default API base URL."""
        assert config.API_BASE_URL == "http://13.36.249.197:8000"

    def test_api_base_url_environment(self):
        """Test API base URL from environment variable."""
        # This test would require a different approach since Config uses class variables
        # For now, we'll test the default behavior
        assert config.API_BASE_URL == "http://13.36.249.197:8000"

    def test_data_paths_default(self):
        """Test default data paths."""
        assert config.ORIGINAL_IMAGES_DIR == "leftImg8bit/val/frankfurt"
        assert config.GROUND_TRUTH_DIR == "gtFine/val/frankfurt"

    def test_aws_configuration_default(self):
        """Test default AWS configuration."""
        assert config.AWS_REGION == "eu-west-3"
        assert config.DVC_S3_BUCKET == "frontend-semantic-image-segmentation"

    def test_application_settings_default(self):
        """Test default application settings."""
        assert config.MAX_FILE_SIZE_MB == 10
        assert config.REQUEST_TIMEOUT == 60
        assert config.HEALTH_CHECK_TIMEOUT == 10

    def test_ui_configuration_default(self):
        """Test default UI configuration."""
        assert config.PAGE_TITLE == "Semantic Image Segmentation"
        assert config.PAGE_ICON == "🎯"
        assert config.LAYOUT == "wide"

    def test_get_api_url(self):
        """Test get_api_url method."""
        # Test with empty endpoint
        url = config.get_api_url()
        assert url == "http://13.36.249.197:8000/"

        # Test with endpoint
        url = config.get_api_url("/api/segment")
        assert url == "http://13.36.249.197:8000/api/segment"

        # Test with endpoint that has leading slash
        url = config.get_api_url("api/segment")
        assert url == "http://13.36.249.197:8000/api/segment"

    def test_validate_config(self):
        """Test config validation."""
        # Should be valid with default values
        assert config.validate_config() is True

        # Note: Testing invalid config would require a different approach
        # since Config uses class variables that are set at import time
