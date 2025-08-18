"""
Unit tests for the data service module.
"""

from unittest.mock import Mock, patch

from PIL import Image

from app.services.data_service import DataService


class TestDataService:
    """Test cases for the DataService class."""

    def setup_method(self):
        """Setup method for each test."""
        self.data_service = DataService()

    def test_data_service_initialization(self):
        """Test data service initialization."""
        assert self.data_service.original_images_dir == "leftImg8bit/val/frankfurt"
        assert self.data_service.ground_truth_dir == "gtFine/val/frankfurt"

    @patch("os.path.exists")
    @patch("os.listdir")
    def test_get_image_ids_success(self, mock_listdir, mock_exists):
        """Test successful image ID extraction."""
        mock_exists.return_value = True
        mock_listdir.return_value = [
            "frankfurt_000000_000294_leftImg8bit.png",
            "frankfurt_000000_000576_leftImg8bit.png",
            "frankfurt_000000_001016_leftImg8bit.png",
            "other_file.txt",
        ]

        ids = self.data_service.get_image_ids("test_directory")

        assert len(ids) == 3
        assert "frankfurt_000000_000294" in ids
        assert "frankfurt_000000_000576" in ids
        assert "frankfurt_000000_001016" in ids
        assert "other_file.txt" not in ids

    @patch("os.path.exists")
    def test_get_image_ids_directory_not_exists(self, mock_exists):
        """Test image ID extraction from non-existent directory."""
        mock_exists.return_value = False

        ids = self.data_service.get_image_ids("nonexistent_directory")

        assert ids == []

    @patch("os.path.exists")
    @patch("os.listdir")
    def test_get_image_ids_empty_directory(self, mock_listdir, mock_exists):
        """Test image ID extraction from empty directory."""
        mock_exists.return_value = True
        mock_listdir.return_value = []

        ids = self.data_service.get_image_ids("empty_directory")

        assert ids == []

    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("streamlit.error")
    def test_get_image_ids_exception_handling(
        self, mock_error, mock_listdir, mock_exists
    ):
        """Test image ID extraction with exception handling."""
        mock_exists.return_value = True
        mock_listdir.side_effect = PermissionError("Access denied")

        ids = self.data_service.get_image_ids("protected_directory")

        assert ids == []
        mock_error.assert_called_once()

    def test_get_image_path(self):
        """Test image path generation."""
        image_id = "frankfurt_000000_000294"
        expected_path = (
            "leftImg8bit/val/frankfurt/frankfurt_000000_000294_leftImg8bit.png"
        )

        path = self.data_service.get_image_path(image_id)

        assert path == expected_path

    def test_get_ground_truth_path(self):
        """Test ground truth path generation."""
        image_id = "frankfurt_000000_000294"
        expected_path = "gtFine/val/frankfurt/frankfurt_000000_000294_gtFine_color.png"

        path = self.data_service.get_ground_truth_path(image_id)

        assert path == expected_path

    @patch("os.path.exists")
    @patch("PIL.Image.open")
    def test_load_image_success(self, mock_image_open, mock_exists):
        """Test successful image loading."""
        mock_exists.return_value = True
        mock_image = Mock(spec=Image.Image)
        mock_image_open.return_value = mock_image

        image = self.data_service.load_image("test_image.png")

        assert image == mock_image
        mock_image_open.assert_called_once_with("test_image.png")

    @patch("os.path.exists")
    def test_load_image_file_not_found(self, mock_exists):
        """Test image loading with non-existent file."""
        mock_exists.return_value = False

        image = self.data_service.load_image("nonexistent.png")

        assert image is None

    @patch("os.path.exists")
    @patch("PIL.Image.open")
    def test_load_image_exception(self, mock_image_open, mock_exists):
        """Test image loading with exception."""
        mock_exists.return_value = True
        mock_image_open.side_effect = Exception("Corrupted image")

        image = self.data_service.load_image("corrupted.png")

        assert image is None

    @patch("os.path.exists")
    @patch("os.listdir")
    def test_validate_data_directories_success(self, mock_listdir, mock_exists):
        """Test successful data directory validation."""

        def exists_side_effect(path):
            return path in ["leftImg8bit/val/frankfurt", "gtFine/val/frankfurt"]

        mock_exists.side_effect = exists_side_effect
        mock_listdir.return_value = ["frankfurt_000000_000294_leftImg8bit.png"]

        is_valid, errors = self.data_service.validate_data_directories()

        assert is_valid is True
        assert len(errors) == 0

    @patch("os.path.exists")
    def test_validate_data_directories_missing_original(self, mock_exists):
        """Test validation with missing original images directory."""

        def exists_side_effect(path):
            return path == "gtFine/val/frankfurt"

        mock_exists.side_effect = exists_side_effect

        is_valid, errors = self.data_service.validate_data_directories()

        assert is_valid is False
        assert len(errors) == 1
        assert "Original images directory not found" in errors[0]

    @patch("os.path.exists")
    def test_validate_data_directories_missing_ground_truth(self, mock_exists):
        """Test validation with missing ground truth directory."""

        def exists_side_effect(path):
            return path == "leftImg8bit/val/frankfurt"

        mock_exists.side_effect = exists_side_effect

        is_valid, errors = self.data_service.validate_data_directories()

        assert is_valid is False
        assert len(errors) == 1
        assert "Ground truth directory not found" in errors[0]

    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("PIL.Image.open")
    def test_get_image_info_success(self, mock_image_open, mock_listdir, mock_exists):
        """Test successful image info retrieval."""

        def exists_side_effect(path):
            # Return True for the specific paths that get_image_info checks
            return path in [
                "leftImg8bit/val/frankfurt/test_id_leftImg8bit.png",
                "gtFine/val/frankfurt/test_id_gtFine_color.png",
            ]

        mock_exists.side_effect = exists_side_effect
        mock_listdir.return_value = []

        mock_image = Mock(spec=Image.Image)
        mock_image.size = (1024, 768)
        mock_image.mode = "RGB"
        mock_image_open.return_value = mock_image

        with patch("os.path.getsize", return_value=1024 * 1024):
            info = self.data_service.get_image_info("test_id")

        assert info is not None
        assert info["id"] == "test_id"
        assert info["size"] == (1024, 768)
        assert info["mode"] == "RGB"
        assert info["file_size"] == 1024 * 1024
        assert info["has_ground_truth"] is True

    @patch("os.path.exists")
    def test_get_image_info_not_found(self, mock_exists):
        """Test image info retrieval for non-existent image."""
        mock_exists.return_value = False

        info = self.data_service.get_image_info("nonexistent_id")

        assert info is None

    @patch("os.path.exists")
    @patch("os.listdir")
    def test_get_directory_stats_success(self, mock_listdir, mock_exists):
        """Test successful directory statistics retrieval."""

        def exists_side_effect(path):
            return path in ["leftImg8bit/val/frankfurt", "gtFine/val/frankfurt"]

        mock_exists.side_effect = exists_side_effect
        mock_listdir.side_effect = [
            [
                "frankfurt_000000_000294_leftImg8bit.png",
                "frankfurt_000000_000576_leftImg8bit.png",
            ],
            ["frankfurt_000000_000294_gtFine_color.png"],
        ]

        stats = self.data_service.get_directory_stats()

        assert stats["directories_exist"] is True
        assert stats["original_images_count"] == 2
        assert stats["ground_truth_count"] == 1
        assert stats["original_images_dir"] == "leftImg8bit/val/frankfurt"
        assert stats["ground_truth_dir"] == "gtFine/val/frankfurt"

    @patch("os.path.exists")
    def test_get_directory_stats_missing_directories(self, mock_exists):
        """Test directory statistics with missing directories."""
        mock_exists.return_value = False

        stats = self.data_service.get_directory_stats()

        assert stats["directories_exist"] is False
        assert stats["original_images_count"] == 0
        assert stats["ground_truth_count"] == 0
