#!/bin/bash

# Deployment script for EC2

set -e

echo "🚀 Deploying Semantic Segmentation App to EC2..."

# Load environment variables from .env file
if [ -f ".env/.env" ]; then
    echo "📄 Loading environment variables from .env/.env"
    export $(cat .env/.env | grep -v '^#' | xargs)
else
    echo "⚠️ .env/.env file not found. Make sure environment variables are set."
fi

# Pull latest image
echo "⬇️ Pulling latest Docker image..."
docker pull $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

# Stop and remove old container
echo "🛑 Stopping old container..."
docker stop semantic-segmentation-app || true
docker rm semantic-segmentation-app || true

# Run new container
echo "▶️ Starting new container..."
docker run -d \
  --name semantic-segmentation-app \
  --restart unless-stopped \
  -p 8501:8501 \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
  -e DVC_S3_BUCKET=$DVC_S3_BUCKET \
  $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

# Wait for container to be healthy
echo "⏳ Waiting for container to be healthy..."
sleep 10

# Check container status
if docker ps | grep -q semantic-segmentation-app; then
    echo "✅ Deployment successful!"
    echo "🌐 App is running at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"
else
    echo "❌ Deployment failed!"
    docker logs semantic-segmentation-app
    exit 1
fi

# Clean up old images
echo "🧹 Cleaning up old images..."
docker image prune -f

echo "🎉 Deployment complete!"
