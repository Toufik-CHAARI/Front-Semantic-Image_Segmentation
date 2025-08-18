#!/bin/bash

# Deploy Streamlit Segmentation App to EC2
# This script can be run locally or on the EC2 instance

set -e

# Configuration
AWS_REGION=${AWS_REGION:-"eu-west-3"}
ECR_REPOSITORY="streamlit-segmentation-app"
CONTAINER_NAME="streamlit-segmentation-container"
PORT=8501

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on EC2
check_ec2() {
    if curl -s http://169.254.169.254/latest/meta-data/instance-id > /dev/null 2>&1; then
        INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
        PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
        print_success "Running on EC2 instance: $INSTANCE_ID"
        print_status "Public IP: $PUBLIC_IP"
        return 0
    else
        print_warning "Not running on EC2 instance"
        return 1
    fi
}

# Get AWS Account ID
get_account_id() {
    print_status "Getting AWS Account ID..."
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    print_success "AWS Account ID: $ACCOUNT_ID"
    echo $ACCOUNT_ID
}

# Login to ECR
login_to_ecr() {
    print_status "Logging in to Amazon ECR..."
    ACCOUNT_ID=$(get_account_id)
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    print_success "Successfully logged in to ECR"
}

# Stop and remove existing container
cleanup_container() {
    print_status "Cleaning up existing container..."
    
    # Stop container if running
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        print_status "Stopping existing container..."
        docker stop $CONTAINER_NAME
        print_success "Container stopped"
    fi
    
    # Remove container if exists
    if docker ps -aq -f name=$CONTAINER_NAME | grep -q .; then
        print_status "Removing existing container..."
        docker rm $CONTAINER_NAME
        print_success "Container removed"
    fi
}

# Remove old image
cleanup_image() {
    print_status "Cleaning up old image..."
    ACCOUNT_ID=$(get_account_id)
    IMAGE_NAME="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:production"
    
    if docker images -q $IMAGE_NAME | grep -q .; then
        docker rmi $IMAGE_NAME
        print_success "Old image removed"
    else
        print_warning "No old image found to remove"
    fi
}

# Pull latest image
pull_image() {
    print_status "Pulling latest image from ECR..."
    ACCOUNT_ID=$(get_account_id)
    IMAGE_NAME="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:production"
    
    docker pull $IMAGE_NAME
    print_success "Latest image pulled successfully"
}

# Start new container
start_container() {
    print_status "Starting new container..."
    ACCOUNT_ID=$(get_account_id)
    IMAGE_NAME="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:production"
    
    # Environment variables
    ENV_VARS=""
    if [ ! -z "$AWS_ACCESS_KEY_ID" ]; then
        ENV_VARS="$ENV_VARS -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"
    fi
    if [ ! -z "$AWS_SECRET_ACCESS_KEY" ]; then
        ENV_VARS="$ENV_VARS -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY"
    fi
    if [ ! -z "$AWS_DEFAULT_REGION" ]; then
        ENV_VARS="$ENV_VARS -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION"
    fi
    if [ ! -z "$DVC_S3_BUCKET" ]; then
        ENV_VARS="$ENV_VARS -e DVC_S3_BUCKET=$DVC_S3_BUCKET"
    fi
    
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:$PORT \
        --restart=always \
        $ENV_VARS \
        $IMAGE_NAME
    
    print_success "Container started successfully"
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Wait for application to start
    print_status "Waiting for application to start..."
    sleep 20
    
    # Test health endpoint
    for i in {1..5}; do
        if curl -f http://localhost:$PORT > /dev/null 2>&1; then
            print_success "Health check passed!"
            return 0
        else
            print_warning "Health check attempt $i failed, retrying..."
            sleep 5
        fi
    done
    
    print_error "Health check failed after 5 attempts"
    print_status "Container logs:"
    docker logs $CONTAINER_NAME
    return 1
}

# Main deployment function
deploy() {
    print_status "Starting deployment process..."
    
    # Check if we're on EC2
    check_ec2
    
    # Login to ECR
    login_to_ecr
    
    # Cleanup
    cleanup_container
    cleanup_image
    
    # Pull and start
    pull_image
    start_container
    
    # Health check
    if health_check; then
        print_success "Deployment completed successfully!"
        
        # Get public IP if on EC2
        if check_ec2 > /dev/null 2>&1; then
            PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
            print_success "Application is accessible at: http://$PUBLIC_IP:$PORT"
        else
            print_success "Application is accessible at: http://localhost:$PORT"
        fi
    else
        print_error "Deployment failed!"
        exit 1
    fi
}

# Show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -r, --region   AWS region (default: eu-west-3)"
    echo "  -p, --port     Port to expose (default: 8501)"
    echo ""
    echo "Environment variables:"
    echo "  AWS_ACCESS_KEY_ID      AWS access key"
    echo "  AWS_SECRET_ACCESS_KEY  AWS secret key"
    echo "  AWS_DEFAULT_REGION     AWS region"
    echo "  DVC_S3_BUCKET          DVC S3 bucket name"
    echo ""
    echo "Example:"
    echo "  $0 --region eu-west-3 --port 8501"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install it first."
    exit 1
fi

# Run deployment
deploy
