import streamlit as st
import os
import requests
from PIL import Image
import io

# API base URL
API_BASE_URL = "http://13.36.249.197:8000"

# Paths to the image and mask folders (adjust if needed, e.g., mount in Docker)
ORIGINAL_IMAGES_DIR = "leftImg8bit/val/frankfurt"
GROUND_TRUTH_DIR = "gtFine/val/frankfurt"





# Function to check API health
def check_api_health():
    try:
        # Try to connect to the API root endpoint
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except Exception:
        return False

# Function to get list of image IDs from the original images directory
def get_image_ids(directory):
    if not os.path.exists(directory):
        return []
    ids = []
    for filename in os.listdir(directory):
        if filename.endswith("_leftImg8bit.png"):
            id_part = filename.replace("_leftImg8bit.png", "")
            ids.append(id_part)
    return sorted(ids)

# Function to call the API for prediction
def predict_mask(image_path):
    try:
        # Validate image file
        if not os.path.exists(image_path):
            st.error(f"Image file not found: {image_path}")
            return None, None
        
        file_size = os.path.getsize(image_path)
        
        # Check if file is too large (optional validation)
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            st.warning("Image file is quite large. This might cause issues.")
        
        with open(image_path, "rb") as f:
            # Use explicit content type specification which works better with the API
            files = {"file": ("image.png", f, "image/png")}
            response = requests.post(f"{API_BASE_URL}/api/segment", files=files, timeout=60)
        
        if response.status_code == 200:
            # Parse the image statistics from headers
            image_stats = None
            processing_time = None
            if 'x-image-stats' in response.headers:
                try:
                    import json
                    image_stats = json.loads(response.headers['x-image-stats'])
                except:
                    image_stats = response.headers['x-image-stats']
            
            if 'x-processing-time' in response.headers:
                processing_time = response.headers['x-processing-time']
            
            return Image.open(io.BytesIO(response.content)), {
                'file_size': file_size,
                'status_code': response.status_code,
                'processing_time': processing_time,
                'image_stats': image_stats,
                'headers': dict(response.headers)
            }
        elif response.status_code == 500:
            st.error("Server Error (500): The API server encountered an internal error while processing your image.")
            st.error("This could be due to:")
            st.error("- Image format not supported")
            st.error("- Image size too large")
            st.error("- Server processing error")
            st.error(f"Response: {response.text}")
            return None, None
        else:
            st.error(f"API error: {response.status_code} - {response.text}")
            return None, None
    except requests.exceptions.ConnectionError:
        st.error(f"Connection error: Could not connect to API at {API_BASE_URL}. Please check if the API server is running.")
        return None, None
    except requests.exceptions.Timeout:
        st.error("Request timeout: The API request took too long to complete.")
        return None, None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None, None

# Streamlit app
st.title("Semantic Image Segmentation Tester")

# API Health Check
st.sidebar.header("API Status")
if check_api_health():
    st.sidebar.success("✅ API is reachable")
else:
    st.sidebar.error("❌ API is not reachable")
    st.sidebar.info(f"API URL: {API_BASE_URL}")

# Get list of available image IDs
image_ids = get_image_ids(ORIGINAL_IMAGES_DIR)

if not image_ids:
    st.error(f"No images found in {ORIGINAL_IMAGES_DIR}. Please ensure the directory exists and contains images.")
else:
    # Select an image ID
    selected_id = st.selectbox("Select an Image ID", image_ids)

    if selected_id:
        # Paths to original image and ground truth mask
        original_path = os.path.join(ORIGINAL_IMAGES_DIR, f"{selected_id}_leftImg8bit.png")
        gt_path = os.path.join(GROUND_TRUTH_DIR, f"{selected_id}_gtFine_color.png")  # Use pre-colored ground truth

        # Display original image
        if os.path.exists(original_path):
            original_img = Image.open(original_path)
            st.subheader("Original Image")
            st.image(original_img, use_container_width=True)
        else:
            st.error(f"Original image not found: {original_path}")

        # Display ground truth mask
        if os.path.exists(gt_path):
            gt_img = Image.open(gt_path)
            st.subheader("Ground Truth Mask")
            st.image(gt_img, use_container_width=True)
        else:
            st.error(f"Ground truth mask not found: {gt_path}")
            # Fallback to label IDs if color version doesn't exist
            gt_label_path = os.path.join(GROUND_TRUTH_DIR, f"{selected_id}_gtFine_labelIds.png")
            if os.path.exists(gt_label_path):
                st.info("Color version not found, showing label IDs version instead.")
                gt_label_img = Image.open(gt_label_path)
                st.image(gt_label_img, use_container_width=True)
            else:
                st.error(f"No ground truth mask found for {selected_id}")

        # Button to launch prediction
        if st.button("Launch Prediction"):
            with st.spinner("Predicting..."):
                predicted_mask, prediction_info = predict_mask(original_path)
                if predicted_mask:
                    st.subheader("Predicted Mask")
                    st.image(predicted_mask, use_container_width=True)
                    
                    # Display prediction details in sidebar
                    st.sidebar.header("📊 Prediction Details")
                    
                    # File information
                    st.sidebar.subheader("📁 File Information")
                    file_size_mb = prediction_info['file_size'] / (1024 * 1024)
                    st.sidebar.metric("File Size", f"{file_size_mb:.2f} MB")
                    
                    # API response information
                    st.sidebar.subheader("🔗 API Response")
                    st.sidebar.metric("Status Code", prediction_info['status_code'])
                    if prediction_info['processing_time']:
                        processing_time_clean = prediction_info['processing_time'].replace('s', '')
                        st.sidebar.metric("Processing Time", f"{processing_time_clean} seconds")
                    
                    # Image statistics
                    if prediction_info['image_stats']:
                        st.sidebar.subheader("📈 Segmentation Statistics")
                        
                        # Create a more readable format for the statistics
                        if isinstance(prediction_info['image_stats'], dict):
                            for class_name, stats in prediction_info['image_stats'].items():
                                if isinstance(stats, dict) and 'percentage' in stats:
                                    percentage = stats['percentage']
                                    pixel_count = stats.get('pixel_count', 0)
                                    
                                    # Create a progress bar for each class
                                    st.sidebar.write(f"**{class_name.replace('_', ' ').title()}**")
                                    st.sidebar.progress(percentage / 100)
                                    st.sidebar.caption(f"{percentage:.1f}% ({pixel_count:,} pixels)")
                        else:
                            st.sidebar.text(str(prediction_info['image_stats']))
                    
                    # Raw headers (collapsible)
                    with st.sidebar.expander("🔧 Raw Response Headers"):
                        st.json(prediction_info['headers'])