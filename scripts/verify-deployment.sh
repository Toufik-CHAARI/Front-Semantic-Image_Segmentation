#!/bin/bash

# Deployment Verification Script
# This script verifies that the deployment is working correctly

set -e

# Configuration
CONTAINER_NAME="streamlit-segmentation-container"
PORT=8501
MAX_RETRIES=10
RETRY_DELAY=10

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

# Check if container is running
check_container() {
    print_status "Checking container status..."
    
    if docker ps | grep -q $CONTAINER_NAME; then
        print_success "Container is running"
        docker ps | grep $CONTAINER_NAME
        return 0
    else
        print_error "Container is not running"
        docker ps -a | grep $CONTAINER_NAME || echo "Container not found"
        return 1
    fi
}

# Check container logs
check_logs() {
    print_status "Checking container logs..."
    
    if docker logs $CONTAINER_NAME 2>&1 | grep -q "Data files found"; then
        print_success "DVC data files found in logs"
    else
        print_warning "No data files confirmation in logs"
    fi
    
    if docker logs $CONTAINER_NAME 2>&1 | grep -q "Starting Streamlit application"; then
        print_success "Streamlit application started"
    else
        print_warning "No Streamlit start confirmation in logs"
    fi
    
    # Show recent logs
    echo ""
    print_status "Recent container logs:"
    docker logs $CONTAINER_NAME --tail 20
}

# Check data directories
check_data() {
    print_status "Checking data directories..."
    
    # Check leftImg8bit directory
    if docker exec $CONTAINER_NAME test -d leftImg8bit/val/frankfurt; then
        FILE_COUNT=$(docker exec $CONTAINER_NAME ls leftImg8bit/val/frankfurt | wc -l)
        if [ $FILE_COUNT -gt 0 ]; then
            print_success "leftImg8bit/val/frankfurt: $FILE_COUNT files found"
        else
            print_warning "leftImg8bit/val/frankfurt: directory exists but empty"
        fi
    else
        print_error "leftImg8bit/val/frankfurt: directory not found"
    fi
    
    # Check gtFine directory
    if docker exec $CONTAINER_NAME test -d gtFine/val/frankfurt; then
        FILE_COUNT=$(docker exec $CONTAINER_NAME ls gtFine/val/frankfurt | wc -l)
        if [ $FILE_COUNT -gt 0 ]; then
            print_success "gtFine/val/frankfurt: $FILE_COUNT files found"
        else
            print_warning "gtFine/val/frankfurt: directory exists but empty"
        fi
    else
        print_error "gtFine/val/frankfurt: directory not found"
    fi
}

# Check application health
check_health() {
    print_status "Checking application health..."
    
    for i in $(seq 1 $MAX_RETRIES); do
        if curl -f http://localhost:$PORT > /dev/null 2>&1; then
            print_success "Application is responding on port $PORT"
            return 0
        else
            print_warning "Health check attempt $i failed, retrying..."
            if [ $i -lt $MAX_RETRIES ]; then
                sleep $RETRY_DELAY
            fi
        fi
    done
    
    print_error "Application is not responding after $MAX_RETRIES attempts"
    return 1
}

# Check environment variables
check_env() {
    print_status "Checking environment variables..."
    
    DVC_BUCKET=$(docker exec $CONTAINER_NAME bash -c 'echo $DVC_S3_BUCKET')
    AWS_REGION=$(docker exec $CONTAINER_NAME bash -c 'echo $AWS_DEFAULT_REGION')
    AWS_ACCESS_KEY=$(docker exec $CONTAINER_NAME bash -c 'echo $AWS_ACCESS_KEY_ID')
    
    if [ ! -z "$DVC_BUCKET" ]; then
        print_success "DVC_S3_BUCKET: $DVC_BUCKET"
    else
        print_error "DVC_S3_BUCKET: not set"
    fi
    
    if [ ! -z "$AWS_REGION" ]; then
        print_success "AWS_DEFAULT_REGION: $AWS_REGION"
    else
        print_error "AWS_DEFAULT_REGION: not set"
    fi
    
    if [ ! -z "$AWS_ACCESS_KEY" ]; then
        print_success "AWS_ACCESS_KEY_ID: set"
    else
        print_error "AWS_ACCESS_KEY_ID: not set"
    fi
}

# Main verification function
verify_deployment() {
    print_status "Starting deployment verification..."
    echo ""
    
    # Check container
    if ! check_container; then
        print_error "Container verification failed"
        return 1
    fi
    
    echo ""
    
    # Check environment variables
    check_env
    
    echo ""
    
    # Check data
    check_data
    
    echo ""
    
    # Check logs
    check_logs
    
    echo ""
    
    # Check health
    if check_health; then
        print_success "🎉 Deployment verification completed successfully!"
        echo ""
        print_status "Application is ready at: http://localhost:$PORT"
        print_status "Container name: $CONTAINER_NAME"
        print_status "Status: 🚀 Running"
    else
        print_error "💥 Deployment verification failed!"
        return 1
    fi
}

# Show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -c, --container  Container name (default: streamlit-segmentation-container)"
    echo "  -p, --port     Port to check (default: 8501)"
    echo ""
    echo "Example:"
    echo "  $0"
    echo "  $0 --container my-container --port 8501"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -c|--container)
            CONTAINER_NAME="$2"
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

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install it first."
    exit 1
fi

# Run verification
verify_deployment
