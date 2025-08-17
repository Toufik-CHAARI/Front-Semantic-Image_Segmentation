#!/bin/bash

# Build and Run script for Semantic Segmentation App
# Supports both local development and CI/CD environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DOCKER_IMAGE_NAME="semantic-segmentation-app"
DOCKER_TAG="latest"
CONTAINER_NAME="semantic-segmentation-container"
PORT="8501"
REGISTRY=""

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

# Function to load environment variables
load_env_vars() {
    print_status "Loading environment variables..."
    
    # Check if we're in CI/CD environment (GitHub Actions)
    if [ -n "$GITHUB_ACTIONS" ]; then
        print_status "Detected CI/CD environment (GitHub Actions)"
        
        # Use GitHub secrets for CI/CD
        AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
        AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
        AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-"eu-west-3"}
        DVC_S3_BUCKET=${DVC_S3_BUCKET}
        
        # Set registry for ECR
        if [ -n "$ECR_REGISTRY" ]; then
            REGISTRY="${ECR_REGISTRY}/"
        fi
        
    else
        print_status "Detected local development environment"
        
        # Load from .env file for local development
        if [ -f ".env/.env" ]; then
            print_status "Loading variables from .env/.env"
            export $(cat .env/.env | grep -v '^#' | xargs)
        else
            print_warning ".env/.env file not found"
        fi
        
        # Use environment variables or defaults
        AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
        AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
        AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-"eu-west-3"}
        DVC_S3_BUCKET=${DVC_S3_BUCKET}
    fi
    
    # Validate required environment variables
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        print_error "AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
        exit 1
    fi
    
    if [ -z "$DVC_S3_BUCKET" ]; then
        print_error "DVC_S3_BUCKET not found. Please set it in .env/.env file or GitHub secrets"
        exit 1
    fi
    
    print_success "Environment variables loaded successfully"
    print_status "Using S3 bucket: $DVC_S3_BUCKET"
    print_status "Using AWS region: $AWS_DEFAULT_REGION"
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    
    # Set full image name
    FULL_IMAGE_NAME="${REGISTRY}${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
    
    # Build command
    docker build \
        --build-arg AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
        --build-arg AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
        --build-arg AWS_DEFAULT_REGION="$AWS_DEFAULT_REGION" \
        --build-arg DVC_S3_BUCKET="$DVC_S3_BUCKET" \
        -t "$FULL_IMAGE_NAME" \
        .
    
    print_success "Docker image built successfully: $FULL_IMAGE_NAME"
}

# Function to stop and remove existing container
cleanup_container() {
    print_status "Cleaning up existing container..."
    
    if docker ps -a --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
        print_status "Stopping existing container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME" || true
        docker rm "$CONTAINER_NAME" || true
        print_success "Container cleaned up"
    else
        print_status "No existing container found"
    fi
}

# Function to run Docker container
run_container() {
    print_status "Running Docker container..."
    
    # Set full image name
    FULL_IMAGE_NAME="${REGISTRY}${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
    
    # Run command
    docker run -d \
        --name "$CONTAINER_NAME" \
        --restart unless-stopped \
        -p "$PORT:8501" \
        -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
        -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
        -e AWS_DEFAULT_REGION="$AWS_DEFAULT_REGION" \
        -e DVC_S3_BUCKET="$DVC_S3_BUCKET" \
        "$FULL_IMAGE_NAME"
    
    print_success "Container started successfully"
}

# Function to check container health
check_health() {
    print_status "Checking container health..."
    
    # Wait for container to be ready
    sleep 10
    
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$CONTAINER_NAME.*healthy"; then
        print_success "Container is healthy and running"
        print_status "Application is available at: http://localhost:$PORT"
        return 0
    else
        print_warning "Container health check failed"
        print_status "Container logs:"
        docker logs "$CONTAINER_NAME"
        return 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  build     Build Docker image"
    echo "  run       Run Docker container"
    echo "  build-run Build and run (default)"
    echo "  stop      Stop and remove container"
    echo "  logs      Show container logs"
    echo "  status    Show container status"
    echo ""
    echo "Options:"
    echo "  -i, --image-name NAME    Docker image name (default: semantic-segmentation-app)"
    echo "  -t, --tag TAG           Docker tag (default: latest)"
    echo "  -c, --container NAME    Container name (default: semantic-segmentation-container)"
    echo "  -p, --port PORT         Port mapping (default: 8501)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  AWS_ACCESS_KEY_ID       AWS access key"
    echo "  AWS_SECRET_ACCESS_KEY   AWS secret key"
    echo "  AWS_DEFAULT_REGION      AWS region (default: eu-west-3)"
    echo "  DVC_S3_BUCKET           S3 bucket name for DVC"
}

# Parse command line arguments
COMMAND="build-run"

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--image-name)
            DOCKER_IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            DOCKER_TAG="$2"
            shift 2
            ;;
        -c|--container)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        build|run|build-run|stop|logs|status)
            COMMAND="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
case $COMMAND in
    build)
        load_env_vars
        build_image
        ;;
    run)
        load_env_vars
        cleanup_container
        run_container
        check_health
        ;;
    build-run)
        load_env_vars
        build_image
        cleanup_container
        run_container
        check_health
        ;;
    stop)
        cleanup_container
        print_success "Container stopped and removed"
        ;;
    logs)
        if docker ps -a --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
            docker logs "$CONTAINER_NAME"
        else
            print_error "Container $CONTAINER_NAME not found"
            exit 1
        fi
        ;;
    status)
        if docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "$CONTAINER_NAME"; then
            docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "$CONTAINER_NAME"
        else
            print_warning "Container $CONTAINER_NAME is not running"
            docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep "$CONTAINER_NAME" || true
        fi
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac
