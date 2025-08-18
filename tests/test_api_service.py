"""
Unit tests for the API service module.
"""

import json
from unittest.mock import Mock, mock_open, patch

import pytest
import requests

from app.services.api_service import APIService


class TestAPIService:
    """Test cases for the APIService class."""

    def setup_method(self):
        """Setup method for each test."""
        self.api_service = APIService()

    def test_api_service_initialization(self):
        """Test API service initialization."""
        assert self.api_service.base_url == "http://13.36.249.197:8000"
        assert self.api_service.timeout == 60

    @patch("requests.get")
    def test_check_health_success(self, mock_get):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.api_service.check_health()
        assert result is True
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_check_health_failure(self, mock_get):
        """Test failed health check."""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        result = self.api_service.check_health()
        assert result is False

    @patch("requests.get")
    def test_check_health_404(self, mock_get):
        """Test health check with 404 response."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = self.api_service.check_health()
        assert result is False

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.path.getsize")
    @patch("requests.post")
    def test_predict_mask_success(
        self, mock_post, mock_getsize, mock_exists, mock_file
    ):
        """Test successful mask prediction."""
        # Setup mocks
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024  # 1MB

        # Create a mock image for the response
        from PIL import Image

        mock_image = Image.new("RGB", (100, 100), color="red")
        import io

        img_buffer = io.BytesIO()
        mock_image.save(img_buffer, format="PNG")
        img_data = img_buffer.getvalue()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = img_data
        mock_response.headers = {
            "x-image-stats": json.dumps(
                {"road": {"percentage": 45.2, "pixel_count": 1000}}
            ),
            "x-processing-time": "2.5s",
        }
        mock_post.return_value = mock_response

        # Test
        mask_image, metadata = self.api_service.predict_mask("test_image.png")

        # Assertions
        assert mask_image is not None
        assert metadata is not None
        assert metadata["file_size"] == 1024 * 1024
        assert metadata["status_code"] == 200
        assert metadata["processing_time"] == "2.5s"
        assert "image_stats" in metadata

    @patch("os.path.exists")
    def test_predict_mask_file_not_found(self, mock_exists):
        """Test prediction with non-existent file."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            self.api_service.predict_mask("nonexistent.png")

    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_predict_mask_file_too_large(self, mock_getsize, mock_exists):
        """Test prediction with file too large."""
        mock_exists.return_value = True
        mock_getsize.return_value = 20 * 1024 * 1024  # 20MB

        with pytest.raises(Exception, match="Image file is too large"):
            self.api_service.predict_mask("large_image.png")

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.path.getsize")
    @patch("requests.post")
    def test_predict_mask_api_error_500(
        self, mock_post, mock_getsize, mock_exists, mock_file
    ):
        """Test prediction with API 500 error."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="Server Error \\(500\\)"):
            self.api_service.predict_mask("test_image.png")

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.path.getsize")
    @patch("requests.post")
    def test_predict_mask_connection_error(
        self, mock_post, mock_getsize, mock_exists, mock_file
    ):
        """Test prediction with connection error."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024
        mock_post.side_effect = requests.exceptions.ConnectionError()

        with pytest.raises(Exception, match="Connection error"):
            self.api_service.predict_mask("test_image.png")

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.path.getsize")
    @patch("requests.post")
    def test_predict_mask_timeout(
        self, mock_post, mock_getsize, mock_exists, mock_file
    ):
        """Test prediction with timeout."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024
        mock_post.side_effect = requests.exceptions.Timeout()

        with pytest.raises(Exception, match="Request timeout"):
            self.api_service.predict_mask("test_image.png")

    def test_parse_response_metadata(self):
        """Test parsing response metadata."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "x-image-stats": json.dumps({"road": {"percentage": 45.2}}),
            "x-processing-time": "2.5s",
            "content-type": "image/png",
        }

        metadata = self.api_service._parse_response_metadata(mock_response, 1024)

        assert metadata["file_size"] == 1024
        assert metadata["status_code"] == 200
        assert metadata["processing_time"] == "2.5s"
        assert metadata["image_stats"] == {"road": {"percentage": 45.2}}
        assert "content-type" in metadata["headers"]

    def test_parse_response_metadata_invalid_json(self):
        """Test parsing metadata with invalid JSON."""
        mock_response = Mock()
        mock_response.headers = {
            "x-image-stats": "invalid_json",
            "x-processing-time": "2.5s",
        }

        metadata = self.api_service._parse_response_metadata(mock_response, 1024)

        assert metadata["image_stats"] == "invalid_json"
        assert metadata["processing_time"] == "2.5s"
