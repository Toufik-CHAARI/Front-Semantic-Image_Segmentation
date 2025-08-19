"""
Main application module for the Streamlit Semantic Image Segmentation app.
Orchestrates the interaction between configuration, services, and UI components.
"""

import os
from typing import Optional

import streamlit as st
from PIL import Image

from app.components.ui_components import UIComponents
from app.services.api_service import api_service
from app.services.data_service import data_service


def initialize_app() -> None:
    """Initialize the Streamlit application."""
    UIComponents.setup_page()
    UIComponents.display_header()


def check_system_status() -> tuple[bool, bool, list[str]]:
    """
    Check the status of API and data directories.

    Returns:
        tuple[bool, bool, list[str]]: (api_healthy, data_valid, data_errors)
    """
    # Check API health
    api_healthy = api_service.check_health()

    # Check data directories
    data_valid, data_errors = data_service.validate_data_directories()

    return api_healthy, data_valid, data_errors


def display_system_status(
    api_healthy: bool, data_valid: bool, data_errors: list[str]
) -> None:
    """Display system status information."""
    # Display API status
    UIComponents.display_api_status(api_healthy)

    # Display data status
    UIComponents.display_data_status(data_valid, data_errors)


def handle_image_selection() -> tuple[Optional[str], Optional[Image.Image]]:
    """
    Handle image selection from dataset or file upload.

    Returns:
        tuple[Optional[str], Optional[Image.Image]]: (selected_id, uploaded_image)
    """
    # Get available images from dataset
    available_images = data_service.get_available_images()

    # Create image selector
    selected_image_id = UIComponents.create_image_selector(available_images)

    # Create file uploader
    uploaded_image = UIComponents.create_file_uploader()

    return selected_image_id, uploaded_image


def process_selected_image(
    image_id: str,
) -> tuple[Optional[Image.Image], Optional[Image.Image]]:
    """
    Process a selected image from the dataset.

    Args:
        image_id (str): ID of the selected image

    Returns:
        tuple[Optional[Image.Image], Optional[Image.Image]]: (
            original_image, ground_truth
        )
    """
    # Load original image
    image_path = data_service.get_image_path(image_id)
    original_image = data_service.load_image(image_path)

    if not original_image:
        return None, None

    # Load ground truth if available
    ground_truth_path = data_service.get_ground_truth_path(image_id)
    ground_truth = None
    if os.path.exists(ground_truth_path):
        ground_truth = data_service.load_image(ground_truth_path)

    return original_image, ground_truth


def process_uploaded_image(
    uploaded_image: Image.Image,
) -> tuple[Image.Image, None]:
    """
    Process an uploaded image.

    Args:
        uploaded_image (Image.Image): The uploaded image

    Returns:
        tuple[Image.Image, None]: (original_image, None for ground_truth)
    """
    return uploaded_image, None


def perform_segmentation(
    image_path: str,
) -> tuple[Optional[Image.Image], Optional[dict]]:
    """
    Perform segmentation on an image.

    Args:
        image_path (str): Path to the image file

    Returns:
        tuple[Optional[Image.Image], Optional[dict]]: (predicted_mask, metadata)
    """
    try:
        with UIComponents.display_loading_spinner("Performing segmentation..."):
            predicted_mask, metadata = api_service.predict_mask(image_path)
        return predicted_mask, metadata
    except Exception as e:
        UIComponents.display_error_message(str(e))
        return None, None


def display_results(
    original_image: Image.Image,
    predicted_mask: Optional[Image.Image],
    ground_truth: Optional[Image.Image],
    metadata: Optional[dict],
    image_id: Optional[str] = None,
) -> None:
    """
    Display segmentation results.

    Args:
        original_image (Image.Image): Original input image
        predicted_mask (Optional[Image.Image]): Predicted segmentation mask
        ground_truth (Optional[Image.Image]): Ground truth image (if available)
        metadata (Optional[dict]): Prediction metadata
        image_id (Optional[str]): Image ID for display purposes
    """
    if not predicted_mask:
        UIComponents.display_error_message("No prediction result available")
        return

    # Display original image
    if image_id:
        UIComponents.display_original_image(original_image, image_id)
    else:
        st.subheader("📸 Original Image")
        st.image(original_image, use_container_width=True)

    # Display ground truth if available
    if ground_truth:
        if image_id:
            UIComponents.display_ground_truth(ground_truth, image_id)
        else:
            st.subheader("🎯 Ground Truth")
            st.image(ground_truth, use_container_width=True)

    # Display predicted mask
    UIComponents.display_predicted_mask(predicted_mask, metadata)

    # Display comparison
    UIComponents.display_comparison(original_image, ground_truth, predicted_mask)

    # Create download buttons
    st.subheader("💾 Download Results")
    col1, col2 = st.columns(2)

    with col1:
        UIComponents.create_download_button(
            predicted_mask,
            f"predicted_mask_{image_id or 'uploaded'}.png",
            "Download Predicted Mask",
        )

    with col2:
        if ground_truth:
            UIComponents.create_download_button(
                ground_truth,
                f"ground_truth_{image_id}.png",
                "Download Ground Truth",
            )


def main() -> None:
    """Main application function."""
    # Initialize the app
    initialize_app()

    # Check system status
    api_healthy, data_valid, data_errors = check_system_status()
    display_system_status(api_healthy, data_valid, data_errors)

    # Early exit if API is not healthy
    if not api_healthy:
        UIComponents.display_error_message(
            "Cannot proceed without a healthy API connection. "
            "Please check the API server status."
        )
        return

    # Handle image selection
    selected_image_id, uploaded_image = handle_image_selection()

    # Process selected image
    if selected_image_id:
        original_image, ground_truth = process_selected_image(selected_image_id)

        if not original_image:
            UIComponents.display_error_message(
                f"Failed to load image: {selected_image_id}"
            )
            return

        # Get image info for display
        image_info = data_service.get_image_info(selected_image_id)
        if image_info:
            UIComponents.display_image_info(image_info)

        # Perform segmentation
        image_path = data_service.get_image_path(selected_image_id)
        predicted_mask, metadata = perform_segmentation(image_path)

        # Display results
        display_results(
            original_image, predicted_mask, ground_truth, metadata, selected_image_id
        )

    # Process uploaded image
    elif uploaded_image:
        original_image, ground_truth = process_uploaded_image(uploaded_image)

        # Save uploaded image temporarily
        temp_path = "temp_uploaded_image.png"
        uploaded_image.save(temp_path)

        try:
            # Perform segmentation
            predicted_mask, metadata = perform_segmentation(temp_path)

            # Display results
            display_results(original_image, predicted_mask, ground_truth, metadata)

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    else:
        UIComponents.display_info_message(
            "Please select an image from the dataset or upload your own image to begin."
        )


if __name__ == "__main__":
    main()
