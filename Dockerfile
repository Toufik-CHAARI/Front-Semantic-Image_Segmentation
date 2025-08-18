# Use Python 3.11 slim image for better compatibility
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip for better package compatibility
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install DVC with S3 support (if not already in requirements.txt)
RUN pip install --no-cache-dir dvc[s3] || true

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p leftImg8bit/val/frankfurt gtFine/val/frankfurt

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Create entrypoint script to handle DVC setup
RUN echo '#!/bin/bash\n\
# Load environment variables if .env file exists\n\
if [ -f ".env/.env" ]; then\n\
    export $(cat .env/.env | grep -v "^#" | xargs)\n\
fi\n\
\n\
# Initialize DVC and pull data if bucket is configured\n\
if [ ! -z "$DVC_S3_BUCKET" ]; then\n\
    echo "Setting up DVC with bucket: $DVC_S3_BUCKET"\n\
    dvc init --no-scm || true\n\
    dvc remote add -d storage s3://${DVC_S3_BUCKET}/semantic-segmentation-data || true\n\
    echo "Pulling data from S3..."\n\
    dvc pull || echo "Warning: Could not pull data from S3"\n\
    echo "DVC setup completed"\n\
else\n\
    echo "Warning: DVC_S3_BUCKET not set, skipping data pull"\n\
fi\n\
\n\
# Verify data directories exist\n\
if [ -d "leftImg8bit/val/frankfurt" ] && [ "$(ls -A leftImg8bit/val/frankfurt)" ]; then\n\
    echo "✅ Data files found in leftImg8bit/val/frankfurt"\n\
else\n\
    echo "⚠️ No data files found in leftImg8bit/val/frankfurt"\n\
fi\n\
\n\
if [ -d "gtFine/val/frankfurt" ] && [ "$(ls -A gtFine/val/frankfurt)" ]; then\n\
    echo "✅ Data files found in gtFine/val/frankfurt"\n\
else\n\
    echo "⚠️ No data files found in gtFine/val/frankfurt"\n\
fi\n\
\n\
# Start Streamlit\n\
echo "🚀 Starting Streamlit application..."\n\
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Run the application
CMD ["/app/entrypoint.sh"]