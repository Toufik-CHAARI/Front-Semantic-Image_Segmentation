"""
Main application module for the Streamlit Semantic Image Segmentation app.
Orchestrates all services and components following separation of concerns.
"""

from typing import Optional, Tuple

import streamlit as st
from PIL import Image

from app.components.ui_components import ui_components
from app.services.api_service import api_service
from app.services.data_service import data_service


class SemanticSegmentationApp:
    """Main application class that orchestrates all components."""

    def __init__(self):
        """Initialize the application."""
        self.setup_ui()
        self.validate_environment()

    def setup_ui(self):
        """Setup the user interface."""
        ui_components.setup_page()
        ui_components.display_header()

    def validate_environment(self):
        """Validate the application environment."""
        # Check API health
        api_healthy = api_service.check_health()
        ui_components.display_api_status(api_healthy)

        # Check data directories
        data_valid, data_errors = data_service.validate_data_directories()
        ui_components.display_data_status(data_valid, data_errors)

        return api_healthy and data_valid

    def run(self):
        """Run the main application."""
        # Create sidebar
        ui_components.create_sidebar()

        # Main application logic
        self.handle_image_selection()

    def handle_image_selection(self):
        """Handle image selection and processing."""
        # Get available images
        available_images = data_service.get_available_images()

        # Create image selector
        selected_image_id = ui_components.create_image_selector(available_images)

        # Handle file upload
        uploaded_image = ui_components.create_file_uploader()

        # Process selected or uploaded image
        if selected_image_id:
            self.process_dataset_image(selected_image_id)
        elif uploaded_image:
            self.process_uploaded_image(uploaded_image)
        else:
            ui_components.display_info(
                "Please select an image from the dataset or upload your own image."
            )

    def process_dataset_image(self, image_id: str):
        """Process an image from the dataset."""
        # Get image info
        image_info = data_service.get_image_info(image_id)
        if image_info:
            ui_components.display_image_info(image_info)

        # Load images
        original_image = data_service.load_image(data_service.get_image_path(image_id))
        ground_truth = data_service.load_image(
            data_service.get_ground_truth_path(image_id)
        )

        if original_image:
            # Process prediction
            predicted_mask, metadata = self.get_prediction(
                data_service.get_image_path(image_id)
            )

            # Display results
            ui_components.display_images(original_image, predicted_mask, ground_truth)
            ui_components.display_prediction_metadata(metadata)

    def process_uploaded_image(self, image: Image.Image):
        """Process an uploaded image."""
        # Save uploaded image temporarily
        temp_path = self.save_uploaded_image(image)

        if temp_path:
            # Process prediction
            predicted_mask, metadata = self.get_prediction(temp_path)

            # Display results
            ui_components.display_images(image, predicted_mask)
            ui_components.display_prediction_metadata(metadata)

    def get_prediction(
        self, image_path: str
    ) -> Tuple[Optional[Image.Image], Optional[dict]]:
        """Get prediction from API."""
        try:
            with st.spinner("🔄 Processing image..."):
                predicted_mask, metadata = api_service.predict_mask(image_path)
                ui_components.display_success("Prediction completed successfully!")
                return predicted_mask, metadata
        except Exception as e:
            ui_components.display_error(str(e))
            return None, None

    def save_uploaded_image(self, image: Image.Image) -> Optional[str]:
        """Save uploaded image to temporary file."""
        try:
            import tempfile

            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            temp_path = temp_file.name
            temp_file.close()

            # Save image
            image.save(temp_path, "PNG")

            return temp_path
        except Exception as e:
            ui_components.display_error(f"Error saving uploaded image: {str(e)}")
            return None


def main():
    """Main entry point for the application."""
    try:
        app = SemanticSegmentationApp()
        app.run()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.error("Please check the logs for more details.")


if __name__ == "__main__":
    main()
