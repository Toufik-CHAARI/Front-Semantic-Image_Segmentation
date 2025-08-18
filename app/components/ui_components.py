"""
UI Components module for handling Streamlit UI operations.
Separates UI logic from business logic.
"""

from typing import Any, Dict, Optional

import streamlit as st
from PIL import Image

from app.config import config


class UIComponents:
    """Class for handling UI components and display logic."""

    @staticmethod
    def setup_page():
        """Configure the Streamlit page settings."""
        st.set_page_config(
            page_title=config.PAGE_TITLE,
            page_icon=config.PAGE_ICON,
            layout=config.LAYOUT,
        )

    @staticmethod
    def display_header():
        """Display the application header."""
        st.title("🎯 Semantic Image Segmentation")
        st.markdown("---")
        st.markdown(
            "Upload an image or select from the Cityscapes dataset to perform "
            "semantic segmentation."
        )

    @staticmethod
    def display_api_status(is_healthy: bool):
        """Display API health status."""
        if is_healthy:
            st.success("✅ API is healthy and responding")
        else:
            st.error("❌ API is not responding")

    @staticmethod
    def display_data_status(is_valid: bool, errors: list):
        """Display data directory status."""
        if is_valid:
            st.success("✅ Data directories are valid")
        else:
            st.error("❌ Data directory issues found:")
            for error in errors:
                st.error(f"  - {error}")

    @staticmethod
    def create_image_selector(image_ids: list) -> Optional[str]:
        """Create an image selector dropdown."""
        if not image_ids:
            st.warning("No images available. Please check your data directories.")
            return None

        selected_image = st.selectbox(
            "Select an image from the dataset:",
            image_ids,
            help="Choose an image from the Cityscapes dataset for segmentation",
        )

        return selected_image

    @staticmethod
    def create_file_uploader() -> Optional[Image.Image]:
        """Create a file uploader for custom images."""
        uploaded_file = st.file_uploader(
            "Or upload your own image:",
            type=["png", "jpg", "jpeg"],
            help="Upload a custom image for segmentation (PNG, JPG, JPEG)",
        )

        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                return image
            except Exception as e:
                st.error(f"Error loading uploaded image: {str(e)}")
                return None

        return None

    @staticmethod
    def display_image_info(image_info: Optional[Dict[str, Any]]):
        """Display information about the selected image."""
        if image_info:
            with st.expander("📊 Image Information"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Image ID:** {image_info['id']}")
                    st.write(
                        f"**Size:** {image_info['size'][0]} x {image_info['size'][1]}"
                    )
                    st.write(f"**Mode:** {image_info['mode']}")

                with col2:
                    st.write(f"**File Size:** {image_info['file_size']:,} bytes")
                    has_gt = "✅" if image_info["has_ground_truth"] else "❌"
                    st.write(f"**Has Ground Truth:** {has_gt}")

                    if image_info.get("ground_truth_size"):
                        gt_size = (
                            f"{image_info['ground_truth_size'][0]} x "
                            f"{image_info['ground_truth_size'][1]}"
                        )
                        st.write(f"**GT Size:** {gt_size}")

    @staticmethod
    def display_images(
        original_image: Image.Image,
        predicted_mask: Optional[Image.Image] = None,
        ground_truth: Optional[Image.Image] = None,
    ):
        """Display images in a grid layout."""
        cols = st.columns(3)

        with cols[0]:
            st.subheader("Original Image")
            st.image(original_image, use_column_width=True)

        with cols[1]:
            st.subheader("Predicted Mask")
            if predicted_mask:
                st.image(predicted_mask, use_column_width=True)
            else:
                st.info("No prediction available")

        with cols[2]:
            st.subheader("Ground Truth")
            if ground_truth:
                st.image(ground_truth, use_column_width=True)
            else:
                st.info("No ground truth available")

    @staticmethod
    def display_prediction_metadata(metadata: Optional[Dict[str, Any]]):
        """Display prediction metadata and statistics."""
        if metadata:
            with st.expander("📈 Prediction Statistics"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**File Size:** {metadata['file_size']:,} bytes")
                    st.write(f"**Status Code:** {metadata['status_code']}")

                    if "processing_time" in metadata:
                        st.write(f"**Processing Time:** {metadata['processing_time']}")

                with col2:
                    if "image_stats" in metadata:
                        stats = metadata["image_stats"]
                        if isinstance(stats, dict):
                            for key, value in stats.items():
                                st.write(f"**{key.title()}:** {value}")
                        else:
                            st.write(f"**Image Stats:** {stats}")

    @staticmethod
    def display_error(error_message: str):
        """Display error messages in a consistent format."""
        st.error(f"❌ {error_message}")

    @staticmethod
    def display_success(message: str):
        """Display success messages in a consistent format."""
        st.success(f"✅ {message}")

    @staticmethod
    def display_warning(message: str):
        """Display warning messages in a consistent format."""
        st.warning(f"⚠️ {message}")

    @staticmethod
    def display_info(message: str):
        """Display info messages in a consistent format."""
        st.info(f"ℹ️ {message}")

    @staticmethod
    def create_sidebar():
        """Create the sidebar with additional options."""
        with st.sidebar:
            st.header("⚙️ Settings")

            # API Configuration
            st.subheader("API Configuration")
            api_url = st.text_input(
                "API Base URL",
                value=config.API_BASE_URL,
                help="Base URL for the segmentation API",
            )

            # Data Configuration
            st.subheader("Data Configuration")
            st.write(f"**Images Directory:** {config.ORIGINAL_IMAGES_DIR}")
            st.write(f"**Ground Truth Directory:** {config.GROUND_TRUTH_DIR}")

            # Application Info
            st.subheader("ℹ️ About")
            st.write("Semantic Image Segmentation using Cityscapes dataset")
            st.write("Powered by Streamlit and remote API")

            return api_url


# Global UI components instance
ui_components = UIComponents()
