"""
UI Components module for handling Streamlit UI operations.
Separates UI logic from business logic.
"""

from typing import Any, Dict, List, Optional

import streamlit as st
from PIL import Image

from app.config import config


class UIComponents:
    """Class for handling UI components and display logic."""

    @staticmethod
    def setup_page() -> None:
        """Configure the Streamlit page settings."""
        st.set_page_config(
            page_title=config.PAGE_TITLE,
            page_icon=config.PAGE_ICON,
            layout=config.LAYOUT,  # type: ignore
        )

    @staticmethod
    def display_header() -> None:
        """Display the application header."""
        st.title("🎯 Semantic Image Segmentation")
        st.markdown("---")
        st.markdown(
            "Upload an image or select from the Cityscapes dataset to perform "
            "semantic segmentation."
        )

    @staticmethod
    def display_api_status(is_healthy: bool) -> None:
        """Display API health status."""
        if is_healthy:
            st.success("✅ API is healthy and responding")
        else:
            st.error("❌ API is not responding")

    @staticmethod
    def display_data_status(is_valid: bool, errors: List[str]) -> None:
        """Display data directory status."""
        if is_valid:
            st.success("✅ Data directories are valid")
        else:
            st.error("❌ Data directory issues found:")
            for error in errors:
                st.error(f"  - {error}")

    @staticmethod
    def create_image_selector(image_ids: List[str]) -> Optional[str]:
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
    def display_image_info(image_info: Optional[Dict[str, Any]]) -> None:
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
    def display_original_image(image: Image.Image, image_id: str) -> None:
        """Display the original image."""
        st.subheader("📸 Original Image")
        st.image(image, caption=f"Image ID: {image_id}", use_container_width=True)

    @staticmethod
    def display_ground_truth(image: Image.Image, image_id: str) -> None:
        """Display the ground truth image."""
        st.subheader("🎯 Ground Truth")
        st.image(image, caption=f"Ground Truth: {image_id}", use_container_width=True)

    @staticmethod
    def display_predicted_mask(
        mask_image: Image.Image, metadata: Optional[Dict[str, Any]]
    ) -> None:
        """Display the predicted segmentation mask."""
        st.subheader("🔮 Predicted Segmentation Mask")
        st.image(mask_image, caption="AI Prediction", use_container_width=True)

        if metadata:
            with st.expander("📊 Prediction Metadata"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(
                        f"**File Size:** {metadata.get('file_size', 'N/A'):,} bytes"
                    )
                    st.write(f"**Status Code:** {metadata.get('status_code', 'N/A')}")

                with col2:
                    if "processing_time" in metadata:
                        st.write(f"**Processing Time:** {metadata['processing_time']}")
                    if "image_stats" in metadata:
                        st.write("**Image Statistics:**")
                        st.json(metadata["image_stats"])

    @staticmethod
    def display_comparison(
        original: Image.Image,
        ground_truth: Optional[Image.Image],
        predicted: Image.Image,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Display a comparison of original, ground truth, and predicted images."""
        st.subheader("🔄 Image Comparison")

        if ground_truth:
            # Three-column layout
            col1, col2, col3 = st.columns(3)

            with col1:
                st.image(original, caption="Original", use_container_width=True)

            with col2:
                st.image(ground_truth, caption="Ground Truth", use_container_width=True)

            with col3:
                st.image(predicted, caption="Predicted", use_container_width=True)
        else:
            # Two-column layout
            col1, col2 = st.columns(2)

            with col1:
                st.image(original, caption="Original", use_container_width=True)

            with col2:
                st.image(predicted, caption="Predicted", use_container_width=True)

        # Display metadata if available
        if metadata:
            with st.expander("📊 Prediction Metadata"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(
                        f"**File Size:** {metadata.get('file_size', 'N/A'):,} bytes"
                    )
                    st.write(f"**Status Code:** {metadata.get('status_code', 'N/A')}")

                with col2:
                    if "processing_time" in metadata:
                        st.write(f"**Processing Time:** {metadata['processing_time']}")
                    if "image_stats" in metadata:
                        st.write("**Image Statistics:**")
                        st.json(metadata["image_stats"])

    @staticmethod
    def display_error_message(error: str) -> None:
        """Display an error message."""
        st.error(f"❌ Error: {error}")

    @staticmethod
    def display_success_message(message: str) -> None:
        """Display a success message."""
        st.success(f"✅ {message}")

    @staticmethod
    def display_warning_message(message: str) -> None:
        """Display a warning message."""
        st.warning(f"⚠️ {message}")

    @staticmethod
    def display_info_message(message: str) -> None:
        """Display an info message."""
        st.info(f"ℹ️ {message}")

    @staticmethod
    def create_download_button(
        image: Image.Image, filename: str, button_text: str
    ) -> None:
        """Create a download button for an image."""
        import io

        # Convert image to bytes
        img_buffer = io.BytesIO()
        image.save(img_buffer, format="PNG")
        img_bytes = img_buffer.getvalue()

        st.download_button(
            label=button_text,
            data=img_bytes,
            file_name=filename,
            mime="image/png",
        )

    @staticmethod
    def display_loading_spinner(text: str = "Processing...") -> Any:
        """Display a loading spinner."""
        return st.spinner(text)

    @staticmethod
    def display_progress_bar(progress: float, text: str = "Progress") -> None:
        """Display a progress bar."""
        st.progress(progress, text=text)
