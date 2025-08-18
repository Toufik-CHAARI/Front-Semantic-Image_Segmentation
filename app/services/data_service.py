"""
Data Service module for handling data-related operations.
Manages file operations, DVC data, and image processing.
"""

import os
from typing import List, Optional, Tuple

import streamlit as st
from PIL import Image

from app.config import config


class DataService:
    """Service class for handling data operations."""

    def __init__(self):
        self.original_images_dir = config.ORIGINAL_IMAGES_DIR
        self.ground_truth_dir = config.GROUND_TRUTH_DIR

    def get_image_ids(self, directory: str) -> List[str]:
        """
        Get list of image IDs from a directory.

        Args:
            directory (str): Directory path to scan

        Returns:
            List[str]: List of image IDs
        """
        if not os.path.exists(directory):
            return []

        ids = []
        try:
            for filename in os.listdir(directory):
                if filename.endswith("_leftImg8bit.png"):
                    id_part = filename.replace("_leftImg8bit.png", "")
                    ids.append(id_part)
        except Exception as e:
            st.error(f"Error reading directory {directory}: {str(e)}")
            return []

        return sorted(ids)

    def get_available_images(self) -> List[str]:
        """
        Get list of available image IDs from the original images directory.

        Returns:
            List[str]: List of available image IDs
        """
        return self.get_image_ids(self.original_images_dir)

    def get_image_path(self, image_id: str) -> str:
        """
        Get the full path to an image file.

        Args:
            image_id (str): Image ID

        Returns:
            str: Full path to the image file
        """
        return os.path.join(self.original_images_dir, f"{image_id}_leftImg8bit.png")

    def get_ground_truth_path(self, image_id: str) -> str:
        """
        Get the full path to a ground truth file.

        Args:
            image_id (str): Image ID

        Returns:
            str: Full path to the ground truth file
        """
        return os.path.join(self.ground_truth_dir, f"{image_id}_gtFine_color.png")

    def load_image(self, image_path: str) -> Optional[Image.Image]:
        """
        Load an image from file.

        Args:
            image_path (str): Path to the image file

        Returns:
            Optional[Image.Image]: Loaded image or None if failed
        """
        try:
            if not os.path.exists(image_path):
                st.error(f"Image file not found: {image_path}")
                return None

            image = Image.open(image_path)
            return image
        except Exception as e:
            st.error(f"Error loading image {image_path}: {str(e)}")
            return None

    def validate_data_directories(self) -> Tuple[bool, List[str]]:
        """
        Validate that data directories exist and contain files.

        Returns:
            Tuple[bool, List[str]]:
                - True if directories are valid
                - List of error messages
        """
        errors = []

        # Check original images directory
        if not os.path.exists(self.original_images_dir):
            errors.append(
                f"Original images directory not found: {self.original_images_dir}"
            )
        else:
            image_count = len(self.get_available_images())
            if image_count == 0:
                errors.append(f"No images found in {self.original_images_dir}")

        # Check ground truth directory
        if not os.path.exists(self.ground_truth_dir):
            errors.append(f"Ground truth directory not found: {self.ground_truth_dir}")

        return len(errors) == 0, errors

    def get_image_info(self, image_id: str) -> Optional[dict]:
        """
        Get information about an image.

        Args:
            image_id (str): Image ID

        Returns:
            Optional[dict]: Image information or None if not found
        """
        image_path = self.get_image_path(image_id)
        ground_truth_path = self.get_ground_truth_path(image_id)

        if not os.path.exists(image_path):
            return None

        try:
            image = Image.open(image_path)
            info = {
                "id": image_id,
                "path": image_path,
                "size": image.size,
                "mode": image.mode,
                "file_size": os.path.getsize(image_path),
                "has_ground_truth": os.path.exists(ground_truth_path),
            }

            if info["has_ground_truth"]:
                gt_image = Image.open(ground_truth_path)
                info["ground_truth_size"] = gt_image.size
                info["ground_truth_mode"] = gt_image.mode

            return info
        except Exception as e:
            st.error(f"Error getting image info for {image_id}: {str(e)}")
            return None

    def get_directory_stats(self) -> dict:
        """
        Get statistics about the data directories.

        Returns:
            dict: Directory statistics
        """
        stats = {
            "original_images_dir": self.original_images_dir,
            "ground_truth_dir": self.ground_truth_dir,
            "original_images_count": 0,
            "ground_truth_count": 0,
            "directories_exist": False,
        }

        # Check if directories exist
        if os.path.exists(self.original_images_dir) and os.path.exists(
            self.ground_truth_dir
        ):
            stats["directories_exist"] = True

            # Count files
            try:
                original_files = [
                    f
                    for f in os.listdir(self.original_images_dir)
                    if f.endswith("_leftImg8bit.png")
                ]
                stats["original_images_count"] = len(original_files)

                ground_truth_files = [
                    f
                    for f in os.listdir(self.ground_truth_dir)
                    if f.endswith("_gtFine_color.png")
                ]
                stats["ground_truth_count"] = len(ground_truth_files)
            except Exception as e:
                st.error(f"Error counting files: {str(e)}")

        return stats


# Global data service instance
data_service = DataService()
