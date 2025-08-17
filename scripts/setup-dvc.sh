#!/bin/bash

# Setup script for DVC and S3 data storage

set -e

echo "🚀 Setting up DVC with S3..."

# Load environment variables from .env file
if [ -f ".env/.env" ]; then
    echo "📄 Loading environment variables from .env/.env"
    export $(cat .env/.env | grep -v '^#' | xargs)
else
    echo "⚠️ .env/.env file not found. Make sure DVC_S3_BUCKET is set."
fi

# Check if AWS credentials are set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    exit 1
fi

# Check if S3 bucket name is set
if [ -z "$DVC_S3_BUCKET" ]; then
    echo "❌ DVC_S3_BUCKET not found. Please set it in .env/.env file"
    exit 1
fi

echo "☁️ Using S3 bucket: $DVC_S3_BUCKET"

# Initialize DVC
echo "📁 Initializing DVC..."
dvc init --no-scm || echo "DVC already initialized, continuing..."

# Configure S3 remote
echo "☁️ Configuring S3 remote..."
dvc remote add -d storage s3://${DVC_S3_BUCKET}/semantic-segmentation-data || echo "Remote already configured, continuing..."

# Add data directories to DVC
echo "📊 Adding data directories to DVC..."
dvc add leftImg8bit/ || echo "leftImg8bit/ already tracked, continuing..."
dvc add gtFine/ || echo "gtFine/ already tracked, continuing..."

# Push data to S3
echo "⬆️ Pushing data to S3..."
dvc push

echo "✅ DVC setup complete!"
echo "📝 Don't forget to commit the .dvc files to git:"
echo "   git add .dvc/"
echo "   git commit -m 'Add DVC configuration'"
